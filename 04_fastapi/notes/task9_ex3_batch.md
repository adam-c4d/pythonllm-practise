# Task 9, Exercise 3: `POST /predict/batch`: many diamonds in one request (worked example)

Continue in `04_fastapi/task9/`: change `main.py` and `schemas.py`, and add `time_batch.py` (finished files: [examples/task9/ex3/](../examples/task9/ex3/)). The outputs below are real (run on 2026-11-23).

**The idea:** a shop wants prices for its whole stock, say 500 diamonds. Calling `/predict` 500 times means 500 HTTP round trips, 500 validations, 500 one-row DataFrames and 500 calls to the model. A **batch** route takes a JSON **list**, builds **one** DataFrame and calls `predict` **once**. Models are built to work on many rows at once (vectorised, like NumPy in Task 4), so it's far faster.

- **Laravel analogy:** `Product::insert([...500 rows...])` instead of 500 `Product::create()` calls. Same result, one round trip.

## Step 1: a reply model, in `schemas.py`

```python
class BatchPrediction(BaseModel):
    count: int
    prices: list[int]
```

## Step 2: the route, in `main.py`

Update 2 imports:
```python
from typing import Annotated

from fastapi import Body, FastAPI

from schemas import BatchPrediction, DiamondIn, Prediction
```
and add:
```python
@app.post("/predict/batch")
def predict_batch(
    diamonds: Annotated[list[DiamondIn], Body(min_length=1, max_length=1000)],
) -> BatchPrediction:
    rows = pd.DataFrame([d.model_dump() for d in diamonds])
    prices = ml_models["price"].predict(rows)
    return BatchPrediction(count=len(prices), prices=[round(p) for p in prices])
```

```http
POST http://127.0.0.1:8001/predict/batch
Content-Type: application/json

[
  {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1", "depth": 61.5, "table": 56.0},
  {"carat": 2.0, "cut": "Good", "color": "J", "clarity": "I1", "depth": 63.0, "table": 59.0}
]
```
```
200 OK
{
  "count": 2,
  "prices": [
    1773,
    6713
  ]
}
```
Same 2 prices as Exercise 2, in the same order as the request.

An empty list:
```http
POST http://127.0.0.1:8001/predict/batch
Content-Type: application/json

[]
```
```
422 Unprocessable Entity
{
  "detail": [
    {
      "type": "too_short",
      "loc": [
        "body"
      ],
      "msg": "List should have at least 1 item after validation, not 0",
      "input": [],
      "ctx": {
        "field_type": "List",
        "min_length": 1,
        "actual_length": 0
      }
    }
  ]
}
```
With 1,001 diamonds you get `"type": "too_long"`, `"msg": "List should have at most 1000 items after validation, not 1001"`.

### Why each part works
- **`list[DiamondIn]`**: the body is a JSON array, and Pydantic checks **every** item with the `DiamondIn` rules.
- **`Body(min_length=1, max_length=1000)`** limits the list's length. Without `Body(...)`, FastAPI would still read the list from the body. `Body` is needed only to add the rules. `Annotated[type, rules]` is the same pattern as `Query(ge=1)` in Task 8.
- **Why a maximum?** Without one, a client could send 10 million rows and use up the server's memory (8 GB on your work PC). Every public batch endpoint has a limit, like Laravel's `'items' => 'array|max:1000'`.
- **`[d.model_dump() for d in diamonds]`**: a list of dicts → one DataFrame with one row per diamond.
- **`predict(rows)`** returns all prices at once, as a NumPy array in the same order as the rows.
- **`[round(p) for p in prices]`** turns each NumPy float into a Python `int`.

## Step 3: measure it, `time_batch.py`

A script **outside** the API that acts as a client. Put it in `task9/`:
```python
import time
from pathlib import Path

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]  # the repo folder
URL = "http://127.0.0.1:8001"
FEATURES = ["carat", "cut", "color", "clarity", "depth", "table"]

df = pd.read_csv(ROOT / "03_ml" / "data" / "diamonds.csv")
diamonds = df[FEATURES].head(500).to_dict("records")

with httpx.Client(base_url=URL) as client:
    start = time.perf_counter()
    one_by_one = [client.post("/predict", json=d).json()["price"] for d in diamonds]
    single_seconds = time.perf_counter() - start

    start = time.perf_counter()
    batch = client.post("/predict/batch", json=diamonds).json()["prices"]
    batch_seconds = time.perf_counter() - start

print(f"{len(diamonds)} requests to /predict:   {single_seconds:.2f} s")
print(f"1 request to /predict/batch: {batch_seconds:.2f} s")
print(f"Batch is {single_seconds / batch_seconds:.0f}x faster")
print("Same prices:", one_by_one == batch)
```
Keep the server running in the first terminal. In a **second** `(dsllm)` terminal, inside `04_fastapi/task9/`:
```powershell
python time_batch.py
```
```
500 requests to /predict:   1.98 s
1 request to /predict/batch: 0.01 s
Batch is 176x faster
Same prices: True
```
A second run gave `1.95 s`, `0.01 s` and `214x`. The batch time is so small that the "x faster" number jumps around, but it's always **100x or more**. The server terminal shows 500 `POST /predict` lines and 1 `POST /predict/batch` line.

### Why each part works
- **`df[FEATURES].head(500).to_dict("records")`**: the first 500 diamonds, as a list of dicts (one per row). That's the same JSON shape the API expects.
- **`httpx.Client(base_url=URL)`** is a reusable HTTP client, Python's equivalent of Laravel's `Http::baseUrl(...)`. `client.post("/predict", json=d)` sends `d` as a JSON body. The `with` block reuses one connection and closes it at the end.
- **`.json()["price"]`** reads the reply as a dict and takes the price.
- **Why ~4 ms per single request?** Each one pays for the HTTP round trip, JSON parsing, validation, a new DataFrame and a `predict` call. The model's own maths is a tiny part. The batch pays those costs **once** for 500 rows.
- **`Same prices: True`**: the batch gives exactly the same answers. Batching changes the speed, not the result.

**Where this matters later:** LLM and embedding APIs work the same way. In Phase 5 you'll send many texts to the embedding model in one call rather than one call per text.

## Recap
- A batch route takes `list[Model]`, builds one DataFrame and calls `predict` once.
- `Annotated[list[DiamondIn], Body(min_length=1, max_length=1000)]` validates every item **and** limits the size.
- 500 single calls ≈ 2 s; 1 batch call ≈ 0.01 s. Same prices.
- `httpx.Client` is how Python code calls an API, as `Http::` does in Laravel.

📚 **Learn more:** [FastAPI: Body - Nested Models (list bodies)](https://fastapi.tiangolo.com/tutorial/body-nested-models/) · [FastAPI: Body - Multiple Parameters (`Body`)](https://fastapi.tiangolo.com/tutorial/body-multiple-params/) · [HTTPX quickstart](https://www.python-httpx.org/quickstart/) · [`DataFrame.to_dict`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html)
