# Task 6, Exercise 8: Errors in %, save, and use the model (worked example)

Continue in `03_ml/diamond_prices.ipynb`. Add a Markdown cell `## Exercise 8: Errors in %, save, and use the model`, then type these cells. The outputs are real (run on 2026-11-05).

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
import joblib
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
    root_mean_squared_error,
)
```
The `sklearn.metrics` block replaces your existing line. After this exercise, your whole imports cell should look like this:
```python
import pickle
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)
```

## Cell 1: How wrong, in percent?

```python
print(f"Average % error: {mean_absolute_percentage_error(y_test, best_pred):.1%}")
check = pd.DataFrame({"actual": y_test, "predicted": best_pred})
check["error"] = (check["predicted"] - check["actual"]).abs()
check["pct_error"] = check["error"] / check["actual"]
price_bands = pd.cut(check["actual"], [0, 1000, 2500, 5000, 10000, 20000])
display(check.groupby(price_bands, observed=True).agg(
    diamonds=("error", "size"),
    mae=("error", "mean"),
    pct_error=("pct_error", "mean"),
).round(2))
```
```
Average % error: 8.3%
                diamonds      mae  pct_error
actual
(0, 1000]           2967    76.58       0.11
(1000, 2500]        2544   114.56       0.07
(2500, 5000]        2400   265.56       0.07
(5000, 10000]       1844   469.17       0.07
(10000, 20000]      1033  1017.47       0.07
```
- **`mean_absolute_percentage_error` (MAPE)** is the average of |error| ÷ actual price. It returns 0.083, and `:.1%` prints 8.3%.
- **`check` puts the actual and predicted prices side by side**; `.abs()` drops the sign, as MAE does.
- **Named aggregation:** `diamonds=("error", "size")` means "a new column called `diamonds` = the number of rows in `error`". Each `name=("column", "function")` pair is like SQL's `COUNT(*) AS diamonds, AVG(error) AS mae`.
- **The dollar error grows with the price** ($77 for diamonds under $1,000, $1,017 over $10,000), **but the % error stays about 7%.** The cheapest diamonds are a bit worse (11%), because $77 is a lot on a $600 stone.
- **So "about ±7%" describes this model better than "±$285".** $285 is a big miss on a $500 diamond and a tiny one on a $15,000 one, as the Exercise 1 histogram warned. Quote errors the way your users think about prices.

## Cell 2: Save the model

```python
models_dir = Path("models")
models_dir.mkdir(exist_ok=True)
model_path = models_dir / "diamond_price_model.joblib"
joblib.dump(best, model_path)
print(f"Saved {model_path.name} ({model_path.stat().st_size / 1024:.0f} KB)")
```
```
Saved diamond_price_model.joblib (566 KB)
```
- **The same as Task 5 Exercise 8.** The file holds the whole pipeline: the grade order and all the boosting trees.
- **566 KB, not 0.4 MB as in Exercise 6:** the tuned trees can have up to 63 leaves instead of 31. It's small enough for Git and for an API.

## Cell 3: Price 3 new diamonds

```python
loaded = joblib.load(model_path)
new_diamonds = pd.DataFrame([
    {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
     "depth": 61.5, "table": 56.0},
    {"carat": 1.0, "cut": "Premium", "color": "G", "clarity": "SI1",
     "depth": 62.0, "table": 58.0},
    {"carat": 2.0, "cut": "Good", "color": "J", "clarity": "I1",
     "depth": 63.0, "table": 59.0},
])
display(new_diamonds.assign(predicted_price=loaded.predict(new_diamonds).round(0)))
```
```
   carat      cut color clarity  depth  table  predicted_price
0    0.5    Ideal     E     VS1   61.5   56.0           1773.0
1    1.0  Premium     G     SI1   62.0   58.0           4588.0
2    2.0     Good     J      I1   63.0   59.0           6713.0
```
- **A list of dicts → a DataFrame**: one dict per diamond, the shape of the JSON a `/predict` endpoint will receive in Phase 4.
- **The 2-carat diamond costs only $6,713**, although the line from Exercise 2 said $13,276 for 2 carats. It has the worst colour (J) and the worst clarity (I1), and Exercise 5 showed that IF is worth about 3× I1. The tree model learned those effects on its own.

## Cell 4: A grade that doesn't exist

```python
bad = new_diamonds.head(1).assign(cut="Excellent")
try:
    loaded.predict(bad)
except ValueError as error:
    print("Rejected:", error)
```
```
Rejected: Found unknown categories ['Excellent'] in column 0 during transform
```
- **`OrdinalEncoder` refuses a grade it doesn't know.** "Column 0" is the first grade column, `cut`. `try` / `except ValueError as error` catches the error and prints its message instead of crashing (Task 2).
- **That's the opposite of Task 5**, where `OneHotEncoder(handle_unknown="ignore")` silently turned an unknown port into zeros. For a price quote, refusing is safer than a silent guess.
- **In Phase 4, Pydantic will reject it first**, with a 422 response and a clear message, using `Literal["Fair", "Good", "Very Good", "Premium", "Ideal"]`. It's the same idea as Laravel's `Rule::in([...])`: bad input never reaches the model.

## Markdown answer cell

```markdown
## Exercise 8 answers
- **% error:** **8.3%** on average. The dollar error grows with price ($77 under $1k, $1,017 over $10k), but the % error stays about **7%** (11% for the cheapest), so "±7%" describes the model better than "±$285".
- **Saved** the tuned boosting pipeline to `models/diamond_price_model.joblib` (**566 KB**).
- **New diamonds:** 0.5 ct Ideal E VS1 **$1,773**, 1.0 ct Premium G SI1 **$4,588**, 2.0 ct Good J I1 **$6,713** (worst colour and clarity, so far below the straight line's $13,276).
- **Unknown grade:** `"Excellent"` is rejected with a `ValueError`. In the API, Pydantic should reject it first (422), like Laravel's `Rule::in`.
```

📚 **Learn more:** [`mean_absolute_percentage_error`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html) · [pandas: named aggregation](https://pandas.pydata.org/docs/user_guide/groupby.html#named-aggregation) · [Model persistence (joblib)](https://scikit-learn.org/stable/model_persistence.html)

## ✅ Task 6 done when
- [ ] All 8 exercises have their cells and an answers cell.
- [ ] **Restart → Run All** runs top to bottom with no errors (about 30 seconds).
- [ ] `output/` has `price_histogram.png`, `carat_line.png` and `log_scales.png`, and `models/` has `diamond_price_model.joblib`.

Then commit, push, and ask Claude to **"review all"**. That finishes Task 6.
