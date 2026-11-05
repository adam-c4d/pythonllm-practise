# Task 5, Exercise 5: Pipelines, cleaning inside the model (worked example)

Continue in `03_ml/titanic_model.ipynb`. Add a Markdown cell `## Exercise 5: Pipelines`, then type these cells. The outputs are real (run on 2026-11-04).

**Add to the imports cell at the top:**
```python
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
```

**Laravel analogy:** Laravel has `Illuminate\Pipeline`, the same idea that powers middleware. A request is sent *through* a list of steps, and each step changes it and passes it on. A scikit-learn `Pipeline` sends your data through cleaning steps and then into the model. A `ColumnTransformer` is like route groups: different columns get different middleware.

## Cell 1: The cleaning steps

```python
numeric = ["pclass", "age", "sibsp", "parch", "fare"]
categorical = ["sex", "embarked"]

numeric_steps = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
])
categorical_steps = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])
preprocess = ColumnTransformer([
    ("num", numeric_steps, numeric),
    ("cat", categorical_steps, categorical),
])
```
No output yet: this only **describes** the steps. Nothing has learned anything.

| Step | What it learns in `fit` | What it does in `transform` |
|---|---|---|
| `SimpleImputer(strategy="median")` | the median of each number column | fills gaps with it |
| `StandardScaler()` | each column's mean and standard deviation | turns values into "standard units": `(value − mean) / std`, so every column has mean 0 and std 1 |
| `SimpleImputer(strategy="most_frequent")` | the most common value (`S` for `embarked`) | fills gaps with it |
| `OneHotEncoder(handle_unknown="ignore")` | the list of categories in each column | one 0/1 column per category |

- **Each step is a `("name", step)` pair.** You use the names later to look inside (Cell 3).
- **Why scale?** Logistic regression weights only become comparable when every column uses the same units (the `fare` problem from Exercise 2). It also helps the model train faster.
- **Why one-hot instead of S = 0, C = 1, Q = 2?** Numbers imply an order and a distance, as if Queenstown were "twice" Cherbourg. One-hot gives each port its own yes/no column, with no fake order.
- **`handle_unknown="ignore"`:** if a new category appears later (a typo like `"X"` from your API), the encoder outputs all zeros instead of crashing. Exercise 8 tests this.

## Cell 2: Put the cleaning and the model together

```python
pipe = Pipeline([("prep", preprocess), ("model", LogisticRegression())])
pipe.fit(X_train, y_train)
print(f"Train accuracy: {pipe.score(X_train, y_train):.1%}")
print(f"Test accuracy:  {pipe.score(X_test, y_test):.1%}")
```
```
Train accuracy: 80.8%
Test accuracy:  80.4%
```
- **You pass the raw `X_train`**, with text, gaps and all. The pipeline does the rest.
- **`pipe.fit`** learns the medians, means and categories from the **training set only**, transforms it, and trains the model. **`pipe.score(X_test, ...)`** applies the *already learned* steps to the test set. That's exactly the leakage rule from Exercise 4, enforced for you.
- **A pipeline behaves like one model**: it has the same `fit` / `predict` / `score`. That's why you can save the whole thing as one file in Exercise 8.
- **It uses all 7 features now**, but the test score is 80.4% vs 81.0% in Exercise 2. That's just 1 passenger (144 vs 145 correct). More features don't automatically mean a better model, and a 179-row test set is too small to tell such close models apart. Exercise 7 compares them fairly.

## Cell 3: Look inside

```python
prep = pipe.named_steps["prep"]
names = prep.get_feature_names_out()
print(names)
medians = prep.named_transformers_["num"].named_steps["impute"].statistics_
print("Learned medians:", dict(zip(numeric, medians, strict=True)))
```
```
['num__pclass' 'num__age' 'num__sibsp' 'num__parch' 'num__fare'
 'cat__sex_female' 'cat__sex_male' 'cat__embarked_C' 'cat__embarked_Q'
 'cat__embarked_S']
Learned medians: {'pclass': np.float64(3.0), 'age': np.float64(28.5), 'sibsp': np.float64(0.0), 'parch': np.float64(0.0), 'fare': np.float64(14.4542)}
```
- **7 columns became 10:** 5 number columns, plus `sex` → 2 columns and `embarked` → 3 columns. The `num__` / `cat__` prefixes are the names you gave in the `ColumnTransformer`.
- **`named_steps["prep"]`** gets a step by its name, like a dict. **`named_transformers_["num"]`** gets one branch of the `ColumnTransformer`. The trailing `_` in `named_transformers_` and `statistics_` is scikit-learn's convention for **"learned during `fit`"**.
- **The age median is 28.5, not 28.0.** That's the proof the pipeline only looked at the training rows.
- `np.float64(3.0)` is just how NumPy numbers print inside a dict. It's the same as `3.0`.

## Cell 4: Before and after cleaning

```python
sample = X_train.head(3)
display(sample)
display(
    pd.DataFrame(prep.transform(sample), columns=names, index=sample.index).round(2)
)
```
```
     pclass   sex  age  sibsp  parch      fare embarked
692       3  male  NaN      0      0   56.4958        S
481       2  male  NaN      0      0    0.0000        S
527       1  male  NaN      0      0  221.7792        S

     num__pclass  num__age  num__sibsp  num__parch  num__fare  cat__sex_female  cat__sex_male  cat__embarked_C  cat__embarked_Q  cat__embarked_S
692         0.83     -0.08       -0.47       -0.47       0.51              0.0            1.0              0.0              0.0              1.0
481        -0.37     -0.08       -0.47       -0.47      -0.66              0.0            1.0              0.0              0.0              1.0
527        -1.57     -0.08       -0.47       -0.47       3.96              0.0            1.0              0.0              0.0              1.0
```
- **All 3 ages were missing.** They became 28.5, then scaled: (28.5 − 29.56) / 13.02 = **−0.08**, just below the average age.
- **`fare` 221.78 became 3.96:** almost 4 standard deviations above the average fare, an expensive ticket. **0 is "average"**, negative is below average, and positive is above.
- **`male` → `sex_female` 0, `sex_male` 1**, and **`S` → 0, 0, 1** across the three port columns.
- `transform` returns a plain NumPy array, so `pd.DataFrame(..., columns=names, index=...)` puts the names and row labels back for display.

## Cell 5: Now the weights are comparable

```python
coefs = pd.Series(pipe.named_steps["model"].coef_[0], index=names).sort_values()
print(coefs.round(2))
```
```
cat__sex_male     -1.32
num__pclass       -0.92
num__age          -0.50
cat__embarked_S   -0.36
num__sibsp        -0.26
num__parch        -0.07
cat__embarked_C    0.03
num__fare          0.10
cat__embarked_Q    0.30
cat__sex_female    1.30
dtype: float64
```
- **Every column is in standard units now**, so a bigger weight really means a bigger effect. Sex is the strongest (male −1.32, female +1.30), then class (−0.92 per standard unit), then **age (−0.50): older passengers were less likely to survive.** That's a pattern the Exercise 2 model couldn't see.
- **`fare` is only +0.10** once class is in the model. Expensive tickets mostly mattered *because* they were first class (Task 4 Exercise 6: correlation isn't causation).

## Markdown answer cell

```markdown
## Exercise 5 answers
- **Pipeline:** numbers → fill with the median → scale; text → fill with the most common value → one-hot. Then logistic regression. It's fitted on the **raw** `X_train`.
- **Accuracy:** train 80.8%, test **80.4%** (144 of 179), 1 passenger fewer than Exercise 2, so the 179-row test set can't tell these models apart.
- **Inside:** 7 columns become 10 after one-hot (`sex` → 2, `embarked` → 3). The learned medians are `[3, 28.5, 0, 0, 14.4542]`. The **28.5** (not 28.0) proves it only learned from the training rows, so no leakage.
- **Scaled weights are comparable:** sex is strongest (±1.3), then class (−0.92) and age (−0.50); fare adds little (+0.10) once class is known.
```

📚 **Learn more:** [User guide: pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html) · [`ColumnTransformer`](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html) · [`SimpleImputer`](https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html) · [`OneHotEncoder`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html)

Then commit, push, and ask Claude for **"Ex 6"** (decision trees and overfitting).
