# Task 6, Exercise 2: A straight line, carat only (worked example)

Continue in `03_ml/diamond_prices.ipynb`. Add a Markdown cell `## Exercise 2: A straight line (carat only)`, then type these cells. The outputs are real (run on 2026-11-05).

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
```
The second line replaces your old `from sklearn.metrics import mean_absolute_error`.

## Cell 1: Fit a line

```python
line = LinearRegression()
line.fit(X_train[["carat"]], y_train)
print(f"price = {line.intercept_:,.0f} + {line.coef_[0]:,.0f} × carat")
```
```
price = -2,262 + 7,769 × carat
```
- **`X_train[["carat"]]` uses double brackets**, so it's a one-column table, not a Series (Task 3: `[[...]]` vs `[...]`). scikit-learn always wants a table for `X`, even with one feature.
- **This is school maths: `y = a + b × x`.** The **slope** (`coef_`) says each extra carat adds **$7,769**. The **intercept** (`intercept_`) is the price at 0 carats, −$2,262. It means nothing by itself (there's no 0-carat diamond); it just places the line.
- **`coef_` is an array with one weight per feature**, so `coef_[0]` is the carat weight. It's the same weighted sum as Task 5's logistic regression, without the sigmoid squeeze: the sum *is* the prediction.
- **How does it choose the line?** "Least squares": of all possible lines, it picks the one where the **sum of squared errors** on the training rows is smallest. It's one formula, so `fit` is instant.

## Cell 2: Predict a few sizes

```python
sizes = pd.DataFrame({"carat": [0.2, 0.3, 0.5, 1.0, 2.0]})
display(sizes.assign(predicted_price=line.predict(sizes).round(0)))
```
```
   carat  predicted_price
0    0.2           -708.0
1    0.3             69.0
2    0.5           1623.0
3    1.0           5507.0
4    2.0          13276.0
```
- **The column must be called `carat`**, the same name as in training. Otherwise scikit-learn warns that `X` doesn't have the expected feature names.
- **A 0.2 carat diamond gets −$708: a negative price.** A straight line keeps going below zero, and the data has no idea that prices can't be negative. Note this down; Exercise 5 fixes it.
- **Doubling from 1 to 2 carats adds a fixed $7,769.** Real diamond prices don't work like that, as Exercise 3 shows.

## Cell 3: Score it

```python
def evaluate(name, predictions):
    """Print the 3 regression scores for one model on the test set."""
    mae = mean_absolute_error(y_test, predictions)
    rmse = root_mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    print(f"{name:<24} MAE ${mae:>6,.0f}   RMSE ${rmse:>6,.0f}   R² {r2:.3f}")


line_pred = line.predict(X_test[["carat"]])
evaluate("baseline (mean)", baseline.predict(X_test))
evaluate("line (carat only)", line_pred)
print("Negative prices predicted:", (line_pred < 0).sum())
```
```
baseline (mean)          MAE $ 3,021   RMSE $ 3,987   R² -0.000
line (carat only)        MAE $ 1,010   RMSE $ 1,550   R² 0.849
Negative prices predicted: 339
```
The 3 regression scores:

| Score | How it's computed | How to read it |
|---|---|---|
| **MAE** | average of \|error\| | "on average, $1,010 off". Easy to explain. |
| **RMSE** | square every error, average them, take the square root | also in dollars, but big misses count extra. It's always ≥ MAE; a big gap means a few large misses. |
| **R²** | 1 − (model's squared errors ÷ the baseline's squared errors) | the share of the price differences the model explains: **0.849 = 85%**. 0 = no better than the mean, 1 = perfect, and **below 0 = worse than the mean** (you'll see one in Exercise 5). |

- **The line cuts the error by two thirds**, from $3,021 to $1,010, using only the weight.
- **The baseline's R² is "−0.000" by definition**, because R² compares a model with the mean. It's very slightly below 0 because the training mean ($3,939) isn't exactly the test mean ($3,906).
- **`evaluate()` is reused in every exercise**, the same idea as `simple_features()` in Task 5: one function, so every model is scored the same way. It reads `y_test` from the notebook; in a script you'd pass it in as a parameter.
- **`{name:<24}`** pads the name to 24 characters; **`{mae:>6,.0f}`** right-aligns the number in 6 characters with a comma. The columns line up.
- **339 test diamonds (3%) get a negative price.**

## Markdown answer cell

```markdown
## Exercise 2 answers
- **Line:** price = −2,262 + 7,769 × carat. Each carat adds $7,769; the intercept only places the line.
- **Predictions:** 0.2 carat → **−$708** (a negative price), 1 carat → $5,507, 2 carats → $13,276.
- **Scores:** MAE **$1,010**, RMSE $1,550, R² **0.849** vs the baseline's $3,021, $3,987 and 0. Weight alone explains 85% of the price differences.
- **Problem:** 339 test diamonds get a negative price. A straight line doesn't know that prices can't go below 0.
```

Then commit, push, and ask Claude for **"check, then ex 3"** (look at the errors).
