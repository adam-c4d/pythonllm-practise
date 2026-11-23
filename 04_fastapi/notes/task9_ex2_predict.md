# Task 9, Exercise 2: `POST /predict`: one diamond in, one price out (worked example)

Continue in `04_fastapi/task9/`: change `main.py` and add `schemas.py` (finished files: [examples/task9/ex2/](../examples/task9/ex2/)). The outputs below are real (run on 2026-11-23).

**The idea:** a client sends one diamond as JSON. **Pydantic** checks it (Task 8), you turn it into a **one-row DataFrame** (the shape the model was trained on in Task 6), call `model.predict`, and send the price back as JSON. This route is the heart of "a model behind an API".

- **Laravel analogy:** a controller action with a FormRequest (`DiamondIn`), that calls a service (`model.predict`) and returns an API Resource (`Prediction`).

## Step 1: `schemas.py`

```python
from typing import Literal

from pydantic import BaseModel, Field

Cut = Literal["Fair", "Good", "Very Good", "Premium", "Ideal"]
Color = Literal["J", "I", "H", "G", "F", "E", "D"]
Clarity = Literal["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]


class DiamondIn(BaseModel):
    carat: float = Field(gt=0, le=6, description="Weight (1 carat = 0.2 g)")
    cut: Cut
    color: Color
    clarity: Clarity
    depth: float = Field(ge=40, le=80, description="Total depth in %")
    table: float = Field(ge=40, le=100, description="Width of the top in %")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
                 "depth": 61.5, "table": 56.0}
            ]
        }
    }


class Prediction(BaseModel):
    price: int = Field(description="Predicted price in US dollars")
```
- **The 6 fields are exactly the model's 6 inputs.** The saved pipeline remembers them: `model.feature_names_in_` is `['carat' 'cut' 'color' 'clarity' 'depth' 'table']`. No `price` (that's what we predict), and no `x`, `y`, `z` (Task 6 left them out).
- **The same `Literal` grades as Task 8.** This matters more now. In Task 6 Ex 8, an unknown grade made `predict` crash with a `ValueError`. Here Pydantic rejects it with a 422 before the model ever sees it.
- **The limits** (`carat` 0–6, `depth` 40–80, `table` 40–100) are a bit wider than the training data (carat 0.2–5.01, depth 43–79, table 43–95). A model can't be trusted far outside what it learned from, so you stop nonsense such as `carat: 500` at the door.
- **`model_config = {"json_schema_extra": {"examples": [...]}}`** puts a ready-made example in `/docs`. **Try it out** is then filled with a real diamond instead of `"string"` and `0`.
- **`Prediction`**: a model for the reply too, so `/docs` shows exactly what comes back.

## Step 2: add `/predict` to `main.py`

Add 2 imports (then Shift+Alt+O to sort them):
```python
import pandas as pd

from schemas import DiamondIn, Prediction
```
and a route at the bottom:
```python
@app.post("/predict")
def predict(diamond: DiamondIn) -> Prediction:
    rows = pd.DataFrame([diamond.model_dump()])
    price = ml_models["price"].predict(rows)[0]
    return Prediction(price=round(price))
```

Try it in `/docs` (the example is already filled in), or:
```http
POST http://127.0.0.1:8001/predict
Content-Type: application/json

{"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1", "depth": 61.5, "table": 56.0}
```
```
200 OK
{
  "price": 1773
}
```
(As in Task 8, send bodies from `/docs`: Windows PowerShell 5.1 strips the `"` quotes that `curl.exe` would need. Exercise 3 calls the API from Python instead.)

A big diamond with the worst colour and clarity:
```http
POST http://127.0.0.1:8001/predict
Content-Type: application/json

{"carat": 2.0, "cut": "Good", "color": "J", "clarity": "I1", "depth": 63.0, "table": 59.0}
```
```
200 OK
{
  "price": 6713
}
```
**Same numbers as Task 6 Exercise 8** ($1,773 and $6,713). The API is the notebook's model, now usable by any program over HTTP.

## Why each part works

- **`diamond: DiamondIn`**: one Pydantic parameter = the JSON body (Task 8 Ex 3). Bad JSON never reaches your code: FastAPI answers 422 (more in Exercise 4).
- **`diamond.model_dump()`** turns the model into a plain dict: `{"carat": 0.5, "cut": "Ideal", ...}`.
- **`pd.DataFrame([ ... ])`**: a **list** with one dict = a DataFrame with **one row**. The pipeline needs a DataFrame with named columns, because its `ColumnTransformer` picks columns by name (`carat`, `cut`, ...), just as in Task 6.
- **`.predict(rows)`** always returns an array, one price per row. **`[0]`** takes the first (and only) one.
- **`round(price)`** turns the NumPy float `1772.6...` into the Python `int` `1773`. Cents don't mean much for a guess that's 8.3% off on average (Task 6 Ex 8).
- **`-> Prediction`**: the return type is also the response model. FastAPI checks the reply against it and documents it in `/docs`.
- **No `cost`-style secrets here**, but the in/out split is the same habit as Task 8: one model for what comes in, one for what goes out.

## Recap
- Request body → `model_dump()` → one-row DataFrame → `model.predict(...)[0]` → response model.
- The Pydantic fields mirror the model's training columns. `Literal` and `Field` limits stop bad input before it reaches the model.
- `json_schema_extra` examples make `/docs` ready to try.
- Same predictions as the notebook: the API is just a new way to call the same model.

📚 **Learn more:** [FastAPI: Request Body](https://fastapi.tiangolo.com/tutorial/body/) · [FastAPI: Declare Request Example Data](https://fastapi.tiangolo.com/tutorial/schema-extra-example/) · [Pydantic: Fields](https://docs.pydantic.dev/latest/concepts/fields/) · [`Pipeline.predict`](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)
