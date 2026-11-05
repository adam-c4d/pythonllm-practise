# Task 6, Exercise 4: All features, and the cut puzzle (worked example)

Continue in `03_ml/diamond_prices.ipynb`. Add a Markdown cell `## Exercise 4: All features, and the cut puzzle`, then type these cells. The outputs are real (run on 2026-11-05).

**Add to the imports cell at the top** (then Shift+Alt+O to sort):
```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
```

## Cell 1: The puzzle

```python
display(df.groupby("cut")[["price", "carat"]].mean().round(2).sort_values("price"))
```
```
             price  carat
cut
Ideal      3457.54   0.70
Good       3928.86   0.85
Very Good  3981.76   0.81
Fair       4358.76   1.05
Premium    4584.26   0.89
```
- **Ideal, the best cut, has the lowest average price.** Fair, the worst, costs $900 more. Does a better cut make a diamond cheaper?
- **No: look at the carat column.** Ideal diamonds weigh 0.70 carats on average, and Fair ones 1.05. Weight drives price far more than cut, so this table mostly compares **sizes**, not cuts.
- **This is called confounding:** a third variable (size) is linked to both things you're comparing. It's the same trap as Task 4's "expensive tickets survived": fare only looked important because it went with first class.
- **To compare cuts fairly, you need "at the same size".** A model with all the features does exactly that: each weight measures one feature *while the others stay the same*.

## Cell 2: A pipeline with all 6 features

```python
numeric = ["carat", "depth", "table"]
categorical = ["cut", "color", "clarity"]
preprocess = ColumnTransformer([
    ("num", StandardScaler(), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])
linear = Pipeline([("prep", preprocess), ("model", LinearRegression())])
linear.fit(X_train, y_train)
linear_pred = linear.predict(X_test)
evaluate("linear (all features)", linear_pred)
print("Negative prices predicted:", (linear_pred < 0).sum())
```
```
linear (all features)    MAE $   802   RMSE $ 1,160   R² 0.915
Negative prices predicted: 1034
```
- **This is Task 5's pipeline, minus the imputers.** There are no gaps, so each branch is just one step (`StandardScaler()` or `OneHotEncoder(...)`), not a small `Pipeline` of two steps.
- **One-hot turns the 3 grade columns into 20 yes/no columns** (5 cuts + 7 colours + 8 clarities).
- **Better:** MAE $1,010 → **$802**, and R² 0.849 → **0.915**.
- **But there are now 1,034 negative prices** (339 before). The weights are **fixed dollar amounts**: "I1 clarity = −$3,800", whatever the size. For a $500 diamond, that pushes the price far below zero. In reality, a grade changes the price by a *percentage*. Exercise 5 fixes this.

## Cell 3: The puzzle solved

```python
coefs = pd.Series(linear["model"].coef_,
                  index=linear["prep"].get_feature_names_out())
for group in categorical:
    print(coefs.filter(like=f"{group}_").sort_values().round(0), "\n")
```
```
cat__cut_Fair        -631.0
cat__cut_Good          -4.0
cat__cut_Very Good    170.0
cat__cut_Premium      194.0
cat__cut_Ideal        271.0
dtype: float64

cat__color_J   -1495.0
cat__color_I    -620.0
cat__color_H    -162.0
cat__color_G     311.0
cat__color_F     522.0
cat__color_E     613.0
cat__color_D     831.0
dtype: float64

cat__clarity_I1     -3800.0
cat__clarity_SI2    -1178.0
cat__clarity_SI1     -219.0
cat__clarity_VS2      407.0
cat__clarity_VS1      727.0
cat__clarity_VVS2    1166.0
cat__clarity_VVS1    1271.0
cat__clarity_IF      1626.0
dtype: float64
```
- **`linear["model"]` is a shortcut for `linear.named_steps["model"]`.** A pipeline can be indexed by step name, like a dict.
- **`coefs.filter(like="cut_")`** keeps the rows whose label contains `cut_`. The loop prints one group at a time, and `"\n"` adds a blank line between them.
- **The puzzle is solved.** At the same size, colour and clarity, **Ideal is worth $902 more than Fair** (271 − (−631)). The order is now right in all 3 groups: Fair < … < Ideal, J < … < D, I1 < … < IF.
- **Compare weights only within a group.** The 5 cut columns always add up to 1 (every diamond has exactly one cut), so the model could shift all 5 up and the intercept down without changing any prediction. Only the *differences* (Ideal − Fair) mean something.
- **Clarity matters most among the grades:** IF vs I1 is $5,426, colour D vs J is $2,326, and cut Ideal vs Fair is $902.

## Markdown answer cell

```markdown
## Exercise 4 answers
- **Puzzle:** Ideal (the best cut) is the cheapest on average ($3,458), because Ideal diamonds are small (0.70 carat vs 1.05 for Fair). Size is a **confounder**, so the simple average compares sizes, not cuts.
- **All 6 features** (scaled numbers + one-hot grades → linear regression): MAE **$802**, RMSE $1,160, R² **0.915**, better than carat alone ($1,010).
- **Solved:** at the same size, Ideal is worth **$902 more** than Fair; D beats J by $2,326 and IF beats I1 by $5,426. Compare weights only within a group.
- **Still wrong:** 1,034 negative prices, because the grade weights are fixed dollar amounts, not percentages.
```

Then commit, push, and ask Claude for **"check, then ex 5"** (log scales).
