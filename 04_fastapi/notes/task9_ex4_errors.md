# Task 9, Exercise 4: Errors: bad input (422) and a missing model (503) (worked example)

Continue in `04_fastapi/task9/`, in `main.py` (finished files: [examples/task9/ex4/](../examples/task9/ex4/)). The outputs below are real (run on 2026-11-23).

**The idea:** a model API can fail in 2 different ways, and the client must be able to tell them apart:

| What went wrong | Whose fault | Status code | Laravel |
|---|---|---|---|
| The diamond is invalid (`cut: "Excellent"`, `carat: 0`) | the **client's** | **422** Unprocessable Entity | FormRequest validation failed |
| The model isn't loaded | the **server's**, for now | **503** Service Unavailable | `php artisan down` (maintenance mode) |

Part A explores the 422s you already get for free. Part B makes the server start **without** a model and answer 503, instead of refusing to start (Exercise 1).

## Part A: the 422s Pydantic gives you

Nothing to type: try these in `/docs` against your Exercise 3 code. Each sends the 0.5 carat example with **one** change.

`"cut": "Excellent"` (not a real grade):
```
422 Unprocessable Entity
{
  "detail": [
    {
      "type": "literal_error",
      "loc": [
        "body",
        "cut"
      ],
      "msg": "Input should be 'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal'",
      "input": "Excellent",
      "ctx": {
        "expected": "'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal'"
      }
    }
  ]
}
```
`"carat": 0`:
```
422 → "type": "greater_than", "loc": ["body", "carat"], "msg": "Input should be greater than 0"
```
`depth` left out:
```
422 → "type": "missing", "loc": ["body", "depth"], "msg": "Field required"
```
`"carat": "big"`:
```
422 → "type": "float_parsing", "loc": ["body", "carat"],
      "msg": "Input should be a valid number, unable to parse string as a number"
```
In a batch, the second diamond with `"cut": "Excellent"`:
```
422 → "loc": ["body", 1, "cut"]
```
Extra fields, `"colour": "E", "price": 99` added to a valid diamond:
```
200 OK
{
  "price": 1773
}
```

**What to notice:**
- **`loc` says exactly where the problem is.** `["body", 1, "cut"]` means "in the body, item number 1 (the second, counting from 0), field `cut`". A client can show the error next to the right field, as Laravel's `$errors->get('cut')` does.
- **`type` is a fixed code** (`literal_error`, `greater_than`, `missing`, `float_parsing`) that programs can check. `msg` is for humans.
- **Without Pydantic, `"cut": "Excellent"` would reach the model and crash it** (`ValueError` in Task 6 Ex 8, so a **500** here). 422 says "your fault, fix your input". 500 says "our server broke". Always aim for the honest code.
- **Unknown fields are ignored by default.** `colour` (British spelling) and `price` are dropped, and the prediction is still made. That's usually what you want. To reject them, add `"extra": "forbid"` to `model_config`.

## Part B: start without a model, answer 503

Replace the top of `main.py` down to `/health` with this (new lines: `os`, `Depends`, `HTTPException`, `Pipeline`, the `try` block, `get_model` and `Model`):
```python
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import Body, Depends, FastAPI, HTTPException
from sklearn.pipeline import Pipeline

from schemas import BatchPrediction, DiamondIn, Prediction

ROOT = Path(__file__).resolve().parents[2]  # the repo folder
MODEL_FILE = ROOT / "03_ml" / "models" / "diamond_price_model.joblib"

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = Path(os.getenv("MODEL_PATH", MODEL_FILE))
    start = time.perf_counter()
    try:
        ml_models["price"] = joblib.load(model_path)
    except FileNotFoundError:
        print(f"WARNING: no model at {model_path}. /predict will answer 503.")
    else:
        seconds = time.perf_counter() - start
        print(f"Loaded {model_path.name} in {seconds:.2f} s")
    yield
    ml_models.clear()
    print("Model unloaded")


app = FastAPI(title="Diamond Price API", lifespan=lifespan)


def get_model() -> Pipeline:
    if "price" not in ml_models:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run 03_ml/diamond_prices.ipynb (Exercise 8) "
            "to create it, then restart the server.",
        )
    return ml_models["price"]


Model = Annotated[Pipeline, Depends(get_model)]
```
Then let both prediction routes **ask for** the model instead of reaching into the dict:
```python
@app.post("/predict")
def predict(diamond: DiamondIn, model: Model) -> Prediction:
    rows = pd.DataFrame([diamond.model_dump()])
    price = model.predict(rows)[0]
    return Prediction(price=round(price))


@app.post("/predict/batch")
def predict_batch(
    diamonds: Annotated[list[DiamondIn], Body(min_length=1, max_length=1000)],
    model: Model,
) -> BatchPrediction:
    rows = pd.DataFrame([d.model_dump() for d in diamonds])
    prices = model.predict(rows)
    return BatchPrediction(count=len(prices), prices=[round(p) for p in prices])
```
`/health` doesn't change.

### Try it: with the model

Start the server as usual. Everything works as before: `/predict` → `{"price": 1773}`.

### Try it: without the model

Stop the server (Ctrl+C). Point `MODEL_PATH` at a file that doesn't exist, and start again **in the same terminal**:
```powershell
$env:MODEL_PATH = "missing.joblib"
fastapi dev main.py --port 8001
```
```
INFO:     Waiting for application startup.
WARNING: no model at missing.joblib. /predict will answer 503.
INFO:     Application startup complete.
```
The server **starts** this time. (The `WARNING` line and the replies below are from running the app with `TestClient`; the `INFO` lines are the usual `fastapi dev` ones.)
```http
GET http://127.0.0.1:8001/health
```
```
200 OK
{
  "status": "no model",
  "model_loaded": false
}
```
```http
POST http://127.0.0.1:8001/predict
Content-Type: application/json

{"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1", "depth": 61.5, "table": 56.0}
```
```
503 Service Unavailable
{
  "detail": "Model not loaded. Run 03_ml/diamond_prices.ipynb (Exercise 8) to create it, then restart the server."
}
```
`/predict/batch` gives the same 503. Clean up afterwards, then restart:
```powershell
Remove-Item Env:MODEL_PATH
```

**A surprise worth knowing:** without the model, even `"cut": "Excellent"` gets **503**, not 422. FastAPI runs the dependencies (`get_model`) while it collects the route's parameters. An `HTTPException` stops everything at once, and the body's validation errors would only be reported at the end. In practice that's fine: when the service is down, "come back later" is the more useful answer.

## Why each part works

- **`os.getenv("MODEL_PATH", MODEL_FILE)`** reads an environment variable, with the normal path as the default. It's Laravel's `env('MODEL_PATH', ...)`. A server can then load a different model file (a newer version, say) without a code change. `Path(...)` around it turns the string into a `Path`, so `.name` works either way.
- **`try / except FileNotFoundError / else`** (Task 2): `except` runs if loading failed, `else` only if it worked. Catch **only** `FileNotFoundError`, the problem you expect. A corrupt file or a scikit-learn version clash still crashes loudly, which is what you want for a bug you didn't expect.
- **`get_model` is a dependency** (Task 8 Ex 5): FastAPI runs it before the route. It either returns the model or raises 503. This is like route model binding returning 404, but for the model. The check lives in **one** place instead of an `if` in every route.
- **`Model = Annotated[Pipeline, Depends(get_model)]`**: the same alias trick as `Pagination` and `FoundDiamond` in Task 8. Each route just writes `model: Model`.
- **`Pipeline`** is the type of the saved object: Task 6 saved a scikit-learn `Pipeline` (a `ColumnTransformer` with an `OrdinalEncoder`, then a `HistGradientBoostingRegressor`). The type hint is for you and your editor. FastAPI doesn't validate dependency return values.
- **503 vs 500:** 503 means "temporarily unavailable, try again later". Load balancers and Kubernetes understand it: they stop sending traffic to this copy of the app until `/health` says `"model_loaded": true`. A 500 would look like a bug.
- **Why start at all without a model?** `/health` can still say what's wrong, `/summary` (Exercise 5) doesn't need the model, and a deploy can't get stuck in a crash loop.
- **Long strings:** two string literals next to each other inside `(...)` are joined into one. That keeps the lines under 88 characters for Ruff.

## Recap
- 422 = the client's fault (Pydantic does it for you; `loc` and `type` say exactly what's wrong). 503 = the service isn't ready. 500 = a bug.
- Load the model in `try / except FileNotFoundError / else`, so the server starts anyway and `/health` reports it.
- A `get_model` dependency gives every route the model or a 503, from one place.
- `os.getenv("MODEL_PATH", default)` makes the model file a setting. `$env:NAME = ...` sets it, and `Remove-Item Env:NAME` removes it.

📚 **Learn more:** [FastAPI: Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) · [FastAPI: Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) · [Pydantic: validation errors](https://docs.pydantic.dev/latest/errors/validation_errors/) · [`os.getenv`](https://docs.python.org/3/library/os.html#os.getenv) · [MDN: 503 Service Unavailable](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/503)
