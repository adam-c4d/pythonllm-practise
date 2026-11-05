# Task 6, Exercise 5: Log scales (worked example)

Continue in `03_ml/diamond_prices.ipynb`. Add a Markdown cell `## Exercise 5: Log scales`, then type these cells. The outputs are real (run on 2026-11-05).

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
import numpy as np
from sklearn.base import clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
```
The last 2 lines replace your existing `sklearn.compose` and `sklearn.preprocessing` lines.

**The idea:** on a normal axis, each step **adds** (1, 2, 3, 4). On a **log** axis, each step **multiplies** (1, 10, 100, 1,000). Diamond prices grow by *percentages*: a better grade adds about 20%, not a fixed $500. Percentages become straight lines on log scales.

## Cell 1: The same data on log scales

```python
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(X_test["carat"], y_test, s=4, alpha=0.2, color="#2a78d6")
ax.set(xscale="log", yscale="log",
       title="On log scales, the curve becomes a straight line",
       xlabel="Carat (log scale)", ylabel="Price (log scale)")
ax.set_xticks([0.25, 0.5, 1, 2, 4], labels=["0.25", "0.5", "1", "2", "4"])
ax.set_yticks([500, 1000, 2000, 5000, 10000, 20000],
              labels=["$500", "$1k", "$2k", "$5k", "$10k", "$20k"])
ax.minorticks_off()
ax.spines[["top", "right"]].set_visible(False)
plt.savefig(output_dir / "log_scales.png", bbox_inches="tight")
plt.show()
```
The chart: the same 10,788 diamonds, now as a **straight, rising band** from about $400 at 0.25 carats to about $18,000 at 2 carats.

- **`xscale="log", yscale="log"`** makes both axes multiply. On the x-axis, 0.25 → 0.5 → 1 → 2 → 4 are equal steps, because each one doubles.
- **`set_xticks(..., labels=...)`** chooses which ticks to show and what to write there; otherwise matplotlib writes `10⁰` and `10⁻¹`. **`minorticks_off()`** hides the small in-between ticks.
- **There's only one series, so there's no legend.** The title says what it is.
- **A straight band on log–log axes means "+1% carat → always about the same % more price"**, at any size. A straight line can learn that, as long as it learns it in log units.

## Cell 2: Fit the line on log scales

```python
log_preprocess = ColumnTransformer([
    ("log", FunctionTransformer(np.log, feature_names_out="one-to-one"), ["carat"]),
    ("num", StandardScaler(), ["depth", "table"]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])
log_linear = TransformedTargetRegressor(
    regressor=Pipeline([("prep", log_preprocess), ("model", LinearRegression())]),
    func=np.log,
    inverse_func=np.exp,
)
log_linear.fit(X_train, y_train)
log_pred = log_linear.predict(X_test)
evaluate("linear on log scales", log_pred)
print("Negative prices predicted:", (log_pred < 0).sum())
```
```
linear on log scales     MAE $   400   RMSE $   820   R² 0.958
Negative prices predicted: 0
```
- **`FunctionTransformer(np.log)`** turns any function into a pipeline step: here, `carat` → `log(carat)`. `feature_names_out="one-to-one"` keeps the column name, so `get_feature_names_out()` still works in Cell 3.
- **The `ColumnTransformer` now has 3 branches:** log for `carat`, scaling for `depth` and `table`, and one-hot for the grades.
- **`TransformedTargetRegressor` logs the target.** In `fit`, it trains the pipeline on `np.log(y_train)`. In `predict`, it runs `np.exp()` on the answers, so you get dollars back. You never handle log prices yourself.
- **Laravel analogy:** it's like an Eloquent mutator and accessor pair. The mutator stores `log(price)`, the accessor returns `exp(...)`, and your code only ever sees dollars.
- **MAE halves: $802 → $400.** R² 0.915 → **0.958**.
- **0 negative prices:** `exp()` of any number is positive, so the model *can't* predict a negative price any more.

## Cell 3: The weights are now percentages

```python
inner = log_linear.regressor_
log_coefs = pd.Series(inner["model"].coef_,
                      index=inner["prep"].get_feature_names_out())
k = log_coefs["log__carat"]
print(f"carat: 1% heavier → {k:.2f}% pricier; twice as heavy → {2 ** k:.1f}× the price")
for better, worse in [("cut_Ideal", "cut_Fair"),
                      ("color_D", "color_J"),
                      ("clarity_IF", "clarity_I1")]:
    ratio = np.exp(log_coefs[f"cat__{better}"] - log_coefs[f"cat__{worse}"])
    print(f"{better} vs {worse}: {ratio:.2f}× the price")
```
```
carat: 1% heavier → 1.89% pricier; twice as heavy → 3.7× the price
cut_Ideal vs cut_Fair: 1.18× the price
color_D vs color_J: 1.67× the price
clarity_IF vs clarity_I1: 3.07× the price
```
- **`regressor_` (with `_`) is the fitted copy.** `TransformedTargetRegressor` clones the pipeline you gave it and fits the clone. The trailing `_` is scikit-learn's "learned during fit" sign again.
- **The carat weight, 1.89, is a percentage rate:** 1% more weight → 1.89% more price. Doubling multiplies the price by 2^1.89 = **3.7×**, not 2×. That's why the price curve bends upwards.
- **Grade weights become ratios:** `exp(weight difference)` = how many times the price. **At the same size**, Ideal is **1.18×** Fair (+18%), D is **1.67×** J, and IF is **3.07×** I1.
- **That's why fixed-dollar weights failed:** "+18%" is $90 on a $500 diamond and $1,800 on a $10,000 one.

## Cell 4: A trap: log the price but not the carat

```python
half_log = TransformedTargetRegressor(
    regressor=Pipeline([("prep", clone(preprocess)), ("model", LinearRegression())]),
    func=np.log,
    inverse_func=np.exp,
)
half_log.fit(X_train, y_train)
half_pred = half_log.predict(X_test)
evaluate("log price only", half_pred)
biggest = half_pred.argmax()
print(f"Biggest prediction: ${half_pred[biggest]:,.0f} for a "
      f"{X_test['carat'].iloc[biggest]} carat diamond "
      f"(real price ${y_test.iloc[biggest]:,})")
```
```
log price only           MAE $ 1,859   RMSE $17,816   R² -18.968
Biggest prediction: $1,005,632 for a 4.01 carat diamond (real price $15,223)
```
- **`clone(preprocess)`** makes a fresh, unfitted copy. `preprocess` is already inside `linear`, and fitting it again in a second pipeline would change `linear` too. That's the Task 5 `make_model()` lesson.
- **R² is −18.97: far worse than always guessing the mean.** One 4.01 carat diamond gets **$1 million**.
- **Why:** with only the price logged, the model learns `log(price) = a + b × carat`, which means `price = eᵃ × e^(b × carat)`. That's an **exponential** curve in carat. It fits where most diamonds are (0.3–2 carats), then shoots up for the few big ones.
- **The lesson:** transform so the relationship becomes a straight line, and *check* with a chart (Cell 1 shows that both axes need logs). Also look at RMSE and the biggest error, not only MAE: here MAE ($1,859) looks bad but not crazy, while RMSE ($17,816) shows the explosion.
- **`argmax()`** gives the *position* of the biggest value; **`.iloc[biggest]`** gets the row at that position from `X_test` and `y_test`.

## Markdown answer cell

```markdown
## Exercise 5 answers
- **Chart:** on log–log axes the curved cloud becomes a straight band, so "+1% carat" always means about the same % more price.
- **Linear on log scales** (`FunctionTransformer(np.log)` on carat + `TransformedTargetRegressor` on price): MAE **$400** (half of $802), RMSE $820, R² **0.958**, **0** negative prices (`exp` is always positive).
- **Weights as ratios:** twice the carat = **3.7×** the price; at the same size Ideal = 1.18× Fair, D = 1.67× J, IF = 3.07× I1. Grades multiply the price; they don't add a fixed amount.
- **Trap:** logging only the price makes price exponential in carat: R² **−18.97**, and a 4.01 carat diamond is predicted at $1,005,632 (real $15,223). Check the shape with a chart and look at RMSE, not only MAE.
```

📚 **Learn more:** [User guide: transforming the target](https://scikit-learn.org/stable/modules/compose.html#transforming-target-in-regression) · [`TransformedTargetRegressor`](https://scikit-learn.org/stable/modules/generated/sklearn.compose.TransformedTargetRegressor.html) · [`FunctionTransformer`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.FunctionTransformer.html) · [`Axes.set_xscale`](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xscale.html)

Then commit, push, and ask Claude for **"check, then ex 6"** (trees and gradient boosting).
