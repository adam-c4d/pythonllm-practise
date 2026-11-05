# Task 6: Predicting a number: diamond prices (Phase 3)

**Goal:** predict the **price** of a diamond from its weight and grades. In Task 5 you predicted a category (survived yes/no); predicting a number is called **regression**. On the way you'll learn how to measure errors in dollars, why a straight line fails on curved data, how log scales fix it, and why gradient boosting is the usual winner on tables.

**Why it matters:** most business ML is regression: prices, delivery times, sales next month, how long a customer stays. The workflow is the same as Task 5 (split → baseline → pipeline → cross-validate → save); only the scores and some models change. The saved model is a second `/predict` endpoint for Phase 4.

**Data:** 53,940 diamonds with their prices in US dollars, at [data/diamonds.csv](data/diamonds.csv) (the `diamonds` dataset that ships with seaborn).

| Column | Meaning |
|---|---|
| `carat` | weight (1 carat = 0.2 g) |
| `cut` | how well it's cut: Fair, Good, Very Good, Premium, **Ideal** (best) |
| `color` | J (most yellow) … **D** (colourless, best) |
| `clarity` | flaws inside: I1 (worst), SI2, SI1, VS2, VS1, VVS2, VVS1, **IF** (no flaws, best) |
| `depth`, `table` | shape proportions, in % |
| `x`, `y`, `z` | length, width and height in mm |
| `price` | price in US dollars (the target) |

```
03_ml/
├── TASK_6.md
├── diamond_prices.ipynb   ← Exercises 1–8 (new notebook)
├── data/diamonds.csv
├── notes/                 ← worked examples (task6_ex1_... to task6_ex8_...)
├── output/                ← charts, rebuilt by running the notebook
└── models/                ← the saved model, rebuilt by running the notebook
```

**Use these settings everywhere,** so your numbers match the expected answers:
- `train_test_split(X, y, test_size=0.2, random_state=42)`. No `stratify` this time (Exercise 1 explains why).
- `random_state=42` for every forest and boosting model

**Words you'll meet:**

| Word | Meaning |
|---|---|
| **regression** | predicting a number (a price) instead of a category |
| **error / residual** | actual − predicted, for one row |
| **MAE** | mean absolute error: the average error in dollars, ignoring the sign. The easiest score to explain to a manager. |
| **RMSE** | root mean squared error: like MAE, but big misses count extra |
| **R²** | the share of the price differences the model explains: 0 = no better than the average, 1 = perfect |
| **log scale** | an axis where each step multiplies (×10) instead of adds (+10) |

---

## Exercise 1: Load, look at the price, split, baseline

1. Load the CSV. Print its shape, the number of missing values, and how many rows have a size of 0 mm in `x`, `y` or `z`.
2. Print the cheapest, median, mean and most expensive price, and the share of diamonds under $2,500. Draw a histogram of `price` with the median and mean marked, and save it as `output/price_histogram.png`.
3. Make `X` from 6 features: `carat`, `cut`, `color`, `clarity`, `depth`, `table`. Make `y` from `price`. Split (settings above).
4. Make a **baseline**: `DummyRegressor(strategy="mean")`, which always predicts the average training price. Score it with `mean_absolute_error` on the test set.
5. In a Markdown cell, explain why `x`, `y`, `z` are left out and why there's no `stratify`.

✅ Expected: `(53940, 10)`, 0 missing values, 20 rows with a 0 mm size. Prices from **$326** to **$18,823**; median **$2,401**, mean **$3,933**; 51% are under $2,500. Train `(43152, 6)`, test `(10788, 6)`. The baseline predicts **$3,939** for every diamond, with an MAE of **$3,021**.

📚 Look up: `DummyRegressor`, `mean_absolute_error`, mean vs median.

## Exercise 2: A straight line (carat only)

1. Train `LinearRegression()` on `X_train[["carat"]]` only. Print the line as `price = intercept + slope × carat`.
2. Predict the price of diamonds of 0.2, 0.3, 0.5, 1 and 2 carats.
3. Write an `evaluate(name, predictions)` function that prints MAE, RMSE and R² on the test set. Use it for the baseline and the line. Count the negative predictions.

✅ Expected: `price = -2,262 + 7,769 × carat`. A 0.2 carat diamond gets **−$708**. Line: MAE **$1,010**, RMSE **$1,550**, R² **0.849** (baseline: $3,021, $3,987, 0.000). There are **339** negative prices in the test set.

📚 Look up: `LinearRegression`, `root_mean_squared_error`, `r2_score`.

## Exercise 3: Look at the errors

1. Draw the test diamonds (`carat` vs `price`) as a scatter plot with the line on top, and save it as `output/carat_line.png`.
2. Compute the errors (`y_test` − predictions) and show their count and mean for the carat bands 0–0.5, 0.5–1, 1–1.5, 1.5–2 and 2–5.5.

✅ Expected: the mean error is **+$353** for 0–0.5 carat (the line is too low), **−$548** for 0.5–1 (too high), and **+$884** for 1.5–2 (too low again). Errors with a pattern mean the model has the wrong **shape**: prices curve upwards, but a line can't.

📚 Look up: `plt.scatter`, residuals, `pd.cut`.

## Exercise 4: All features, and the cut puzzle

1. Show the mean `price` and `carat` per `cut`, sorted by price. Which cut is the cheapest on average, and why?
2. Build a pipeline: `StandardScaler` for `carat`, `depth`, `table`; `OneHotEncoder(handle_unknown="ignore")` for `cut`, `color`, `clarity`; then `LinearRegression()`. Score it and count the negative predictions.
3. Print the learned weights for each group of grades.

✅ Expected: **Ideal**, the best cut, is the cheapest on average (**$3,458**) because Ideal diamonds are small (0.70 carat vs 1.05 for Fair). Pipeline: MAE **$802**, RMSE $1,160, R² **0.915**, and still 1,034 negative prices. With size held equal, the weights put **Ideal $902 above Fair**, D above J, and IF above I1. The puzzle is solved.

📚 Look up: confounding, `Series.filter(like=)`, `pipe["model"]`.

## Exercise 5: Log scales

1. Draw the test diamonds again with **both** axes on a log scale, and save it as `output/log_scales.png`.
2. Fit the line on log scales: take `np.log` of `carat` inside the `ColumnTransformer` with `FunctionTransformer`, and of the price with `TransformedTargetRegressor(func=np.log, inverse_func=np.exp)`.
3. Turn the weights into percentages and ratios: what does twice the carat do to the price? What is Ideal vs Fair worth, D vs J, and IF vs I1?
4. **The trap:** log only the price, not the carat. What happens to the biggest diamonds?

✅ Expected: on log scales the cloud is a straight band. Log model: MAE **$400**, RMSE $820, R² **0.958**, and **0** negative prices. Twice the carat = **3.7×** the price. Ideal vs Fair **1.18×**, D vs J **1.67×**, IF vs I1 **3.07×**. The trap: R² **−18.97**, and a 4.01 carat diamond is predicted at **$1,005,632** (real price $15,223).

📚 Look up: `FunctionTransformer`, `TransformedTargetRegressor`, `np.log` / `np.exp`.

## Exercise 6: Trees and gradient boosting

1. Trees don't need scaling or one-hot. Encode the grades in order with `OrdinalEncoder(categories=...)` (worst = 0), pass the numbers through unchanged, and show 3 rows before and after.
2. Train `RandomForestRegressor(random_state=42, n_jobs=-1)` and `HistGradientBoostingRegressor(random_state=42)`. Time each fit and compare train vs test MAE.
3. Show the forest's `feature_importances_`.
4. How big would each model be as a file? Use `len(pickle.dumps(model))`. Don't save the forest to disk.

✅ Expected: Good → 1, Very Good → 2, Premium → 3. Forest: train MAE $111, test MAE **$280**, R² **0.981**, about 1 s. Boosting: train MAE $272, test MAE **$286**, R² 0.981, about 0.2 s. Carat has importance **0.885**. The forest is **338.6 MB**; boosting is 0.4 MB.

📚 Look up: `OrdinalEncoder`, `RandomForestRegressor`, `HistGradientBoostingRegressor`, `time.perf_counter`.

## Exercise 7: Cross-validation and tuning

1. Compare 4 models with `cross_val_score(..., cv=5, scoring="neg_mean_absolute_error")`: linear (all features), linear on log scales, random forest and gradient boosting. Why is the score negative?
2. Tune gradient boosting with `GridSearchCV`: `learning_rate` in `[0.05, 0.1, 0.2]` × `max_leaf_nodes` in `[15, 31, 63]`.
3. Score the best model on the test set, **once**.

✅ Expected: CV MAE: linear **$806** ± 7, log scales **$404** ± 4, forest **$287** ± 5, boosting **$286** ± 6. Best: `learning_rate=0.1`, `max_leaf_nodes=63`, CV **$282**. Test: MAE **$285**, RMSE $554, R² **0.981**. Tuning gained only about $4; the big wins came from the right shape and model.

📚 Look up: `scoring="neg_mean_absolute_error"`, `GridSearchCV`.

## Exercise 8: Errors in %, save, and use the model

1. Print the average % error with `mean_absolute_percentage_error`. Then show the number of diamonds, MAE and mean % error for the price bands $0–1k, 1–2.5k, 2.5–5k, 5–10k and 10–20k.
2. Save the tuned model to `models/diamond_price_model.joblib`.
3. Load it and price these 3 diamonds (a list of dicts → DataFrame):

   | carat | cut | color | clarity | depth | table |
   |---|---|---|---|---|---|
   | 0.5 | Ideal | E | VS1 | 61.5 | 56.0 |
   | 1.0 | Premium | G | SI1 | 62.0 | 58.0 |
   | 2.0 | Good | J | I1 | 63.0 | 59.0 |

4. Try a cut that doesn't exist (`"Excellent"`) inside `try` / `except ValueError`.

✅ Expected: average error **8.3%**. The dollar error grows with the price ($77 under $1k, $1,017 over $10k), but the % error stays about **7%** (11% for the cheapest). The file is about **566 KB**. Prices: **$1,773**, **$4,588**, **$6,713**. `"Excellent"` is rejected: `Found unknown categories ['Excellent'] in column 0 during transform`.

📚 Look up: `mean_absolute_percentage_error`, named aggregation in `groupby().agg`.

---

## How to work
1. Make a new notebook, `03_ml/diamond_prices.ipynb`. Do the exercises in order, and commit after each one.
2. The worked examples are in [notes/](notes/) (`task6_ex1_...` to `task6_ex8_...`).
3. When you're done, ask Claude to **"review all"**.
