# Task 6, Exercise 6: Trees and gradient boosting (worked example)

Continue in `03_ml/diamond_prices.ipynb`. Add a Markdown cell `## Exercise 6: Trees and gradient boosting`, then type these cells. The outputs are real (run on 2026-11-05). Timings depend on your computer.

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
import pickle
import time

from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)
```
`pickle` and `time` are part of Python, so they go in the first group with `from pathlib import Path`. The `sklearn.preprocessing` block replaces your existing line (Ruff wraps it like this once it's over 88 characters).

## Cell 1: Grades in order

```python
grades = [
    ["Fair", "Good", "Very Good", "Premium", "Ideal"],        # cut, worst → best
    ["J", "I", "H", "G", "F", "E", "D"],                       # color
    ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"],  # clarity
]
tree_preprocess = ColumnTransformer([
    ("num", "passthrough", numeric),
    ("cat", OrdinalEncoder(categories=grades), categorical),
])
sample = X_train.head(3)
display(sample)
display(pd.DataFrame(tree_preprocess.fit(X_train).transform(sample),
                     columns=tree_preprocess.get_feature_names_out(),
                     index=sample.index))
```
```
       carat        cut color clarity  depth  table
26546   2.01       Good     F     SI2   58.1   64.0
9159    1.01  Very Good     E     SI2   60.0   60.0
14131   1.10    Premium     H     VS2   62.5   58.0

       num__carat  num__depth  num__table  cat__cut  cat__color  cat__clarity
26546        2.01        58.1        64.0       1.0         4.0           1.0
9159         1.01        60.0        60.0       2.0         5.0           1.0
14131        1.10        62.5        58.0       3.0         2.0           3.0
```
- **`OrdinalEncoder(categories=grades)` replaces each grade with its position in your list.** Good = 1, Very Good = 2, Premium = 3; colour F = 4, E = 5, H = 2; SI2 = 1, VS2 = 3. You give one list per column, in the same order as `categorical`, sorted worst → best.
- **Why not one-hot, as for the Titanic ports?** The grades have a real **order**, and ports don't (Queenstown isn't "more" than Cherbourg). With numbers in order, a tree can ask "clarity ≥ VS1?" in one question instead of several yes/no columns. It's also 3 columns instead of 20: the forest below trains in about 1 s this way, and about 29 s with one-hot.
- **`"passthrough"`** sends `carat`, `depth` and `table` through unchanged. **Trees don't need scaling**, because a split like "carat ≤ 1.0" works the same in any unit (Task 5 Exercise 6).
- **`tree_preprocess.fit(X_train)` here is only for the display.** The models below get their own clone of it.

## Cell 2: A random forest and gradient boosting

```python
def tree_model(estimator):
    """The ordered-grades cleaning step, followed by any tree model."""
    return Pipeline([("prep", clone(tree_preprocess)), ("model", estimator)])


trees = {
    "random forest": tree_model(RandomForestRegressor(random_state=42, n_jobs=-1)),
    "gradient boosting": tree_model(HistGradientBoostingRegressor(random_state=42)),
}
for name, model in trees.items():
    start = time.perf_counter()
    model.fit(X_train, y_train)
    seconds = time.perf_counter() - start
    train_mae = mean_absolute_error(y_train, model.predict(X_train))
    print(f"{name}: trained in {seconds:.1f} s, train MAE ${train_mae:,.0f}")
    evaluate(name, model.predict(X_test))
```
```
random forest: trained in 0.9 s, train MAE $111
random forest            MAE $   280   RMSE $   554   R² 0.981
gradient boosting: trained in 0.2 s, train MAE $272
gradient boosting        MAE $   286   RMSE $   553   R² 0.981
```
- **`tree_model()` is Task 5's `make_model()`** with the tree cleaning step: one function, a fresh clone each time.
- **`time.perf_counter()` is a stopwatch.** It returns seconds as a decimal number; end − start = how long `fit` took.
- **`n_jobs=-1`** builds the forest's trees on all your CPU cores at once. They don't depend on each other, so they can be built in parallel.
- **Both beat the best linear model:** MAE $400 → **$280–286**, R² **0.981**. Trees can follow the curve directly, so they don't need the log trick.
- **The forest has a big train/test gap** ($111 vs $280): each tree grows until it memorises its rows (Task 5's overfitting). Averaging 100 of them still gives a strong test score. **Boosting's gap is small** ($272 vs $286).
- **What is gradient boosting?** It builds small trees **one after another**, and each new tree learns to fix the errors the earlier trees still make. It's like a team where each new member focuses on the cases the others got wrong. **"Hist"** means it first sorts each column's values into at most 255 bins (a histogram), which makes it very fast on big tables. It's scikit-learn's version of XGBoost and LightGBM, the usual winners on tabular data.

## Cell 3: What the forest uses

```python
forest = trees["random forest"]
importance = pd.Series(forest["model"].feature_importances_,
                       index=forest["prep"].get_feature_names_out())
print(importance.sort_values(ascending=False).round(3))
```
```
num__carat      0.885
cat__clarity    0.067
cat__color      0.033
num__depth      0.008
num__table      0.004
cat__cut        0.003
dtype: float64
```
- **Weight does almost all the work (0.885).** Then clarity and colour; cut barely matters once the size is known (it was only 1.18× in Exercise 5).
- **`depth` and `table` add almost nothing.** They were in the model "just in case", and now you know.

## Cell 4: How big would each model be as a file?

```python
for name, model in trees.items():
    print(f"{name}: {len(pickle.dumps(model)) / 1e6:,.1f} MB")
```
```
random forest: 338.6 MB
gradient boosting: 0.4 MB
```
- **`pickle.dumps(model)`** turns the model into bytes in memory: the same thing `joblib.dump` writes to a file, without touching the disk. `len(...)` counts the bytes, and `/ 1e6` turns them into MB.
- **The forest is 338.6 MB:** 100 trees, each about 31 levels deep with about 23,500 leaves, because each tree memorises its training rows. **Boosting is 0.4 MB:** 100 small trees with at most 31 leaves each.
- ⚠️ **Don't save the forest in `models/`.** GitHub refuses files over 100 MB, and your `.gitignore` is off, so `git add .` would commit it and `git push` would fail. An API would also need 339 MB of memory just to load it.
- **Same accuracy, 800 times smaller and 4 times faster**, so gradient boosting is the model to take forward.

## Markdown answer cell

```markdown
## Exercise 6 answers
- **Ordered grades:** `OrdinalEncoder(categories=...)` turns each grade into its position, worst = 0 (Good → 1, Very Good → 2, Premium → 3). Trees don't need scaling or one-hot, and 3 columns train much faster than 20.
- **Random forest:** train MAE $111, test MAE **$280**, R² 0.981 (about 1 s). **Gradient boosting:** train $272, test **$286**, R² 0.981 (about 0.2 s). Both beat the log-scale line ($400).
- **Importances:** carat **0.885**, clarity 0.067, colour 0.033; cut, depth and table almost nothing.
- **File size:** forest **338.6 MB** vs boosting 0.4 MB. Same accuracy, so boosting is the one to use (and the forest is too big for GitHub).
```

📚 **Learn more:** [User guide: histogram-based gradient boosting](https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting) · [`HistGradientBoostingRegressor`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html) · [`RandomForestRegressor`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html) · [`OrdinalEncoder`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OrdinalEncoder.html)

Then commit, push, and ask Claude for **"check, then ex 7"** (cross-validation and tuning).
