# Task 6, Exercise 1: Load, look at the price, split, baseline (worked example)

**Make a new notebook** `03_ml/diamond_prices.ipynb`: Ctrl+Shift+P → "Create: New Jupyter Notebook", save it in `03_ml/`, and pick the **dsllm** kernel. Add a Markdown cell `# Task 6: Diamond prices`, then `## Exercise 1: Load, look at the price, split, baseline`. The outputs below are real (run on 2026-11-05).

**What's new since Task 5:** the model now returns a **number**, not yes/no. Task 5's model was like a Laravel `Gate::allows()` check (true/false); this one is like a price-calculator service that returns an amount. The workflow stays the same: split → baseline → model → measure.

## Cell 1: Imports

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
```
- **`DummyRegressor`** is the number version of Task 5's `DummyClassifier`. In scikit-learn, models that predict numbers end in `Regressor` (or `Regression`), and models that predict categories end in `Classifier`.
- Later exercises add more imports. **Add them to this cell**, then press **Shift+Alt+O** to sort them.

## Cell 2: Load and look

```python
df = pd.read_csv("data/diamonds.csv")
print(df.shape)
print("Missing values:", df.isna().sum().sum())
print("Rows with a size of 0 mm:", (df[["x", "y", "z"]] == 0).any(axis=1).sum())
display(df.head())
```
```
(53940, 10)
Missing values: 0
Rows with a size of 0 mm: 20
   carat      cut color clarity  depth  table  price     x     y     z
0   0.23    Ideal     E     SI2   61.5   55.0    326  3.95  3.98  2.43
1   0.21  Premium     E     SI1   59.8   61.0    326  3.89  3.84  2.31
2   0.23     Good     E     VS1   56.9   65.0    327  4.05  4.07  2.31
3   0.29  Premium     I     VS2   62.4   58.0    334  4.20  4.23  2.63
4   0.31     Good     J     SI2   63.3   58.0    335  4.34  4.35  2.75
```
- **The path is relative to the notebook**, which lives in `03_ml/`, so `data/diamonds.csv` means `03_ml/data/diamonds.csv`.
- **`isna().sum().sum()`:** the first `sum()` counts gaps per column, and the second adds those up. **0 gaps**, so this time you don't need a `SimpleImputer`.
- **`(df[["x", "y", "z"]] == 0)`** compares every cell with 0 and gives a table of `True`/`False`. **`.any(axis=1)`** asks, row by row, "is any of the 3 `True`?" (`axis=1` means across the columns). **`.sum()`** counts the `True` rows.
- **20 diamonds have a length, width or height of 0 mm.** That's impossible, so they're data-entry errors. Exercise 1's Markdown cell decides what to do about them.
- **`cut`, `color` and `clarity` are text grades**, and `price` is a whole number of dollars.

## Cell 3: The target, price

```python
price = df["price"]
print(f"Cheapest: ${price.min():,}   Median: ${price.median():,.0f}   "
      f"Mean: ${price.mean():,.0f}   Most expensive: ${price.max():,}")
print(f"Diamonds under $2,500: {(price < 2500).mean():.0%}")
```
```
Cheapest: $326   Median: $2,401   Mean: $3,933   Most expensive: $18,823
Diamonds under $2,500: 51%
```
- **`:,` adds thousands separators** to a whole number; **`:,.0f`** does the same for a decimal and rounds it. Two f-strings next to each other inside `print(...)` join into one line.
- **The mean ($3,933) is much bigger than the median ($2,401).** That's the sign of a **right-skewed** column: most values are small, and a few very large ones pull the mean up. Salaries work the same way: one CEO raises the average, but not the median.
- **`(price < 2500).mean()`** is the Task 5 trick: the mean of `True`/`False` is the share of `True`. Half the diamonds cost under $2,500.

## Cell 4: Draw it

```python
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(price, bins=60, color="#2a78d6", edgecolor="white", linewidth=0.5)
top = ax.get_ylim()[1]
for value, label, height in [(price.median(), "median", 0.92),
                             (price.mean(), "mean", 0.78)]:
    ax.axvline(value, color="#52514e", linewidth=1, linestyle="--")
    ax.text(value, top * height, f" {label} ${value:,.0f}", color="#52514e")
ax.set(title="Most diamonds are cheap; a few are very expensive",
       xlabel="Price ($)", ylabel="Number of diamonds")
ax.spines[["top", "right"]].set_visible(False)
plt.savefig(output_dir / "price_histogram.png", bbox_inches="tight")
plt.show()
```
The chart: a tall wall of bars under $1,000, then a long, thin tail to the right up to $18,823, with dashed lines at the median ($2,401) and the mean ($3,933).

- **`fig, ax = plt.subplots()`** is matplotlib's object style. `ax` is one chart, and you call methods on it (`ax.hist`, `ax.set`). Task 4 used `plt.` functions and seaborn. Both work, but the `ax` style is clearer once a figure has more than one chart.
- **`bins=60`** draws 60 bars, each about $300 wide. **`edgecolor="white"`** leaves a thin gap between the bars.
- **The loop draws 2 reference lines from a list of tuples.** Each tuple is unpacked into `value, label, height`. `ax.get_ylim()[1]` is the top of the y-axis, so the labels sit at 92% and 78% of the chart's height and don't overlap.
- **`ax.set(title=..., xlabel=..., ylabel=...)`** sets several properties in one call. **`ax.spines[["top", "right"]]`** removes the top and right border lines, so the chart looks less boxed in.
- **Why it matters:** a $500 error is a disaster for a $400 diamond and a rounding error for a $15,000 one. Keep that in mind: Exercise 8 measures errors in percent.

## Cell 5: X, y and the split

```python
features = ["carat", "cut", "color", "clarity", "depth", "table"]
X = df[features]
y = df["price"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print("Train:", X_train.shape, " Test:", X_test.shape)
print(f"Mean price - train: ${y_train.mean():,.0f}, test: ${y_test.mean():,.0f}")
```
```
Train: (43152, 6)  Test: (10788, 6)
Mean price - train: $3,939, test: $3,906
```
- **The same split as Task 5, without `stratify`.** `stratify` keeps the share of each *category* equal in both sets. Price has **11,602 different values**, and many appear only once. Try `stratify=y`, and scikit-learn stops with `The least populated classes in y have only 1 member`.
- **You don't need it here.** With 54k rows, a random split is already balanced: the mean price is $3,939 in training vs $3,906 in testing.
- **The test set has 10,788 diamonds**, 60 times more than Titanic's 179. One diamond is worth 0.009 percentage points, so the scores here will be much more stable than in Task 5.
- **The parentheses let the long `train_test_split` line wrap** without going over Ruff's 88 characters.

## Cell 6: A baseline to beat

```python
baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train, y_train)
print("Baseline predicts:", baseline.predict(X_test.head(3)))
baseline_mae = mean_absolute_error(y_test, baseline.predict(X_test))
print(f"Baseline MAE: ${baseline_mae:,.0f}")
```
```
Baseline predicts: [3939.49070727 3939.49070727 3939.49070727]
Baseline MAE: $3,021
```
- **`fit` learns one number: the mean training price, $3,939.49.** `predict` returns it for every diamond. It ignores `X` completely, just like `DummyClassifier` did.
- **MAE (mean absolute error)** is the average of |actual − predicted|. The minus sign is dropped, because being $500 too high is as bad as being $500 too low. **"On average, this guess is $3,021 off."** You can say that to a manager as it is, and that's why MAE is the main score in this task.
- **Every real model has to beat $3,021.**
- **Why the mean and not the median?** `strategy="median"` predicts $2,401 and gets a *lower* MAE ($2,790), because the median is the single number with the smallest average absolute error. The mean is the usual baseline, because it's also the reference point for R² (Exercise 2).

## Markdown answer cell

```markdown
## Exercise 1 answers
- **Data:** 53,940 diamonds, 10 columns, 0 missing values. 20 rows have a size of 0 mm, which is impossible (data-entry errors).
- **Price:** $326 to $18,823. The median ($2,401) is far below the mean ($3,933): most diamonds are cheap and a few expensive ones pull the mean up (right-skewed). 51% cost under $2,500.
- **X** = `carat`, `cut`, `color`, `clarity`, `depth`, `table`; **y** = `price`. **Left out:** `x`, `y`, `z` are the size in mm, which `carat` (the weight) already measures, and they contain the 20 impossible zeros.
- **No `stratify`:** price is a number with 11,602 different values, so there are no categories to balance. With 54k rows a random split is already balanced ($3,939 vs $3,906 mean).
- **Baseline:** always predicts the mean, $3,939. **MAE $3,021**. Every real model must beat this.
```

Then commit, push, and ask Claude for **"check, then ex 2"** (a straight line: your first regression model).
