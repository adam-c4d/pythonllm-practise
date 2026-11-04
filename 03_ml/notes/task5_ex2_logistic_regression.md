# Task 5, Exercise 2: Your first model, logistic regression (worked example)

Continue in `03_ml/titanic_model.ipynb`, below the Exercise 1 answers. Add a Markdown cell `## Exercise 2: Logistic regression`, then type these cells. The outputs are real (run on 2026-11-04).

**Add to the imports cell at the top:**
```python
import numpy as np
from sklearn.linear_model import LogisticRegression
```

## Cell 1: A table of complete number columns

```python
def simple_features(X):
    """Only the complete number columns, plus sex as 1/0."""
    table = X[["pclass", "sibsp", "parch", "fare"]].copy()
    table["is_male"] = (X["sex"] == "male").astype(int)
    return table


X_train_simple = simple_features(X_train)
X_test_simple = simple_features(X_test)
display(X_train_simple.head(3))
```
```
     pclass  sibsp  parch      fare  is_male
692       3      0      0   56.4958        1
481       2      0      0    0.0000        1
527       1      0      0  221.7792        1
```
- **Models only understand numbers, and they can't handle gaps.** `sex` is text, so it becomes `is_male` (1/0) as in Task 4. `age` and `embarked` have gaps, so they wait for Exercise 5.
- **One function for both sets.** The training and test tables **must** be built in exactly the same way, or the model sees different columns at test time. A function guarantees it. It's like one Laravel form request used by both `store` and `update`.
- **`.copy()`** makes `table` its own DataFrame, so adding `is_male` can never touch `X_train`.
- **2 blank lines after the function**, as PEP 8 asks.

## Cell 2: Train and score

```python
model = LogisticRegression()
model.fit(X_train_simple, y_train)
print(f"Train accuracy: {model.score(X_train_simple, y_train):.1%}")
print(f"Test accuracy:  {model.score(X_test_simple, y_test):.1%}")
```
```
Train accuracy: 79.5%
Test accuracy:  81.0%
```
- **`fit` is where the learning happens.** The model looks at 712 passengers and their answers, and finds the weights (Cell 4) that predict best.
- **It beats the baseline by 19.5 points** (61.5% → 81.0%), so it really learned something.
- **Training and test scores are close.** That means the model learned general patterns, not individual passengers (compare with the tree in Exercise 6). The test score is a bit *higher*, which is just luck with 179 people: 1 passenger is 0.56 points.
- **Why "logistic regression" for a yes/no question?** Despite the name, it's a classification model. It produces a **probability** between 0 and 1. The "regression" part is how it calculates that probability (Cell 5).

## Cell 3: Predictions and probabilities

```python
first5 = X_test_simple.head()
display(first5.assign(
    actual=y_test.head(),
    predicted=model.predict(first5),
    chance=model.predict_proba(first5)[:, 1].round(2),
))
```
```
     pclass  sibsp  parch     fare  is_male  actual  predicted  chance
565       3      2      0  24.1500        1       0          0    0.09
160       3      0      1  16.1000        1       0          0    0.10
553       3      0      0   7.2250        1       1          0    0.11
860       3      2      0  14.1083        1       0          0    0.08
241       3      1      0  15.5000        0       1          1    0.60
```
- **`predict_proba` returns 2 columns per passenger**: the chance of `0` (died) and the chance of `1` (survived). For the first passenger that's `[0.91, 0.09]`. **`[:, 1]`** is NumPy slicing from Task 4 Exercise 1: all rows, column 1, so you get the survival chance.
- **`predict` is just `predict_proba` with a cut-off at 0.5.** Above 0.5 → 1, otherwise → 0. Exercise 3 shows what happens when you move that cut-off.
- **4 of 5 are right.** Row 553, a third-class man, survived even though the model gave him only an 11% chance. Models find patterns, so the lucky exceptions will always be wrong.
- **`.assign(...)`** adds columns to a *new* DataFrame, just for display (as in Task 4).

## Cell 4: What did it learn?

```python
coefs = pd.Series(model.coef_[0], index=X_train_simple.columns).sort_values()
print(coefs.round(2))
print("Intercept:", model.intercept_.round(2))
```
```
is_male   -2.62
pclass    -0.82
sibsp     -0.18
parch     -0.09
fare       0.00
dtype: float64
Intercept: [2.98]
```
- **The model *is* these 6 numbers.** It learned one weight (**coefficient**) per column, plus a starting value (the **intercept**).
- **A negative weight pushes towards "died", and a positive weight pushes towards "survived".** `is_male` (−2.62) is the strongest push, and each step down in class (`pclass` +1) costs another 0.82.
- ⚠️ **You can't compare the sizes yet.** `fare` shows 0.00, but its real value is 0.0037 **per pound**, and fares go up to £512. Each column is in different units, so the weights are too. In Exercise 5, `StandardScaler` puts every column on the same scale, and the weights become comparable.
- `coef_[0]`: scikit-learn stores the weights in a 2D array (one row per class it predicts against), so `[0]` takes the only row.

## Cell 5 (optional): How the model computes the 60%

```python
passenger = first5.loc[241]
z = model.intercept_[0] + (passenger * model.coef_[0]).sum()
print(passenger.tolist())
print(f"Score z = {z:.2f}")
print(f"Chance  = {1 / (1 + np.exp(-z)):.2f}")
```
```
[3.0, 1.0, 0.0, 15.5, 0.0]
Score z = 0.39
Chance  = 0.60
```
No magic, just 2 steps:
1. **A weighted sum.** Start at 2.98, then add each value × its weight: 3 × (−0.82) for class, 1 × (−0.18) for one sibling, 15.5 × 0.0037 for the fare, and 0 × (−2.62) because she isn't male. The result is **0.39**. `passenger * model.coef_[0]` multiplies the two arrays element by element (vectorised, Task 4 Exercise 1).
2. **Squash it into 0–1** with the **sigmoid** function, `1 / (1 + e^-z)`. A big negative z → near 0, z = 0 → 0.5, a big positive z → near 1. So 0.39 → **60%**.

That's all `fit` did: it searched for the 6 numbers that make these chances match the 712 real outcomes as closely as possible.

## Markdown answer cell

```markdown
## Exercise 2 answers
- **Features:** `pclass`, `sibsp`, `parch`, `fare` and `is_male`, built by one function so training and test tables match.
- **Accuracy:** train 79.5%, test **81.0%**, which is 19.5 points above the baseline. The two scores are close, so the model learned general patterns.
- **First 5 test passengers:** 4 of 5 right. The woman in row 241 gets a 60% chance, so she is predicted to survive, and she did.
- **Biggest push:** `is_male` (−2.62), then `pclass` (−0.82 per class). The weights can't be compared yet because the columns use different units (fare is per pound).
- **How it predicts:** a weighted sum of the features, squashed into 0–1 by the sigmoid function. Above 0.5 → "survived".
```

Then commit, push, and ask Claude for **"Ex 3"** (is 81% good? the confusion matrix).
