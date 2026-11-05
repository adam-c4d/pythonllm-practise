# Task 5, Exercise 1: X, y, split, and a baseline (worked example)

Create `03_ml/titanic_model.ipynb` (you'll use it for all 8 exercises) and select the **dsllm** kernel. Add a Markdown cell `## Exercise 1: X, y, split, and a baseline`, then type these cells. The outputs are real (run on 2026-11-04).

## The big idea first

**Normal programming:** you write the rules.
```python
if sex == "female" and pclass < 3:
    return "survived"
```
**Machine learning:** you give the computer **examples with answers** (712 passengers, and whether each one survived), and an algorithm **learns the rules itself**. Then you check those rules on passengers it has never seen.

Every scikit-learn model works the same way, with 3 methods:

| Method | What it does |
|---|---|
| `model.fit(X, y)` | **learn** from examples |
| `model.predict(X)` | **apply** what it learned to new rows |
| `model.score(X, y)` | predict, then compare with the real answers (accuracy) |

**Laravel analogy for the whole library:** scikit-learn models are like Laravel's cache drivers. Redis, file and database caches all implement the same `Cache` contract, so you swap the driver and your code stays the same. Every sklearn model implements `fit` / `predict` / `score`, so in Exercise 6 you'll swap a logistic regression for a decision tree by changing **one line**.

## Cell 1: Imports

```python
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
```
scikit-learn is installed as `scikit-learn` but imported as **`sklearn`**. Each tool lives in a submodule, so you import exactly what you need. You'll add more imports to this cell in later exercises.

## Cell 2: Features (X) and target (y)

```python
df = pd.read_csv("../02_data/data/titanic.csv")
features = ["pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]
X = df[features]
y = df["survived"]
print("X:", X.shape)
print("y:", y.shape)
display(X.head(3))
```
```
X: (891, 7)
y: (891,)
   pclass     sex   age  sibsp  parch     fare embarked
0       3    male  22.0      1      0   7.2500        S
1       1  female  38.0      1      0  71.2833        C
2       3  female  26.0      0      0   7.9250        S
```
- **`../`** means "go up one folder". The notebook is in `03_ml/`, and the data is in `02_data/data/`. There's one copy of the data, shared by both phases.
- **`X` is the inputs** (a table: 891 rows × 7 columns) and **`y` is the answers** (one column). The capital `X` and small `y` are a maths convention (a matrix vs a vector). Every ML tutorial uses them.
- **Raw data on purpose.** `age` and `embarked` still have gaps. In Exercise 5 the model will learn to fill them itself, which avoids a subtle form of cheating (Exercise 4).

**Why the other 8 columns are left out:**

| Column | Reason |
|---|---|
| `survived` | it's the target, `y` |
| `alive` | it **is** the answer in words, so using it would be data leakage (Task 4, Exercise 3) |
| `class`, `embark_town` | copies of `pclass` and `embarked` |
| `who`, `adult_male`, `alone` | calculated from `sex`, `age`, `sibsp` and `parch`, which the model already has |
| `deck` | 77% missing |

## Cell 3: Split into training and test sets

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print("Train:", X_train.shape, " Test:", X_test.shape)
print(f"Survival rate - train: {y_train.mean():.1%}, test: {y_test.mean():.1%}")
print("First 5 training rows:", X_train.index[:5].tolist())
```
```
Train: (712, 7)  Test: (179, 7)
Survival rate - train: 38.3%, test: 38.5%
First 5 training rows: [692, 481, 527, 855, 801]
```
- **Why split?** It's an exam. If students study the exact exam questions, a perfect score proves nothing. The model learns from the **training set (80%, 712 passengers)**. The **test set (20%, 179)** stays hidden until the end, to show how it does on passengers it has never seen.
- **4 results at once:** `train_test_split` returns 4 things, and Python unpacks them into 4 names, as with `BLUE, ORANGE = ...` in Task 4.
- **The rows are shuffled** before splitting (row 692 comes first). Real data is often sorted, for example by date, and you don't want all the late rows in the test set.
- **`random_state=42`** fixes the shuffle, like the NumPy seed in Task 4 Exercise 1. You get the same split every time, and so does anyone who runs your notebook. (42 is just a programmers' joke from *The Hitchhiker's Guide to the Galaxy*. Any number works.)
- **`stratify=y`** keeps the **same share of survivors** in both sets: 38.3% and 38.5%.

## Cell 4: What `stratify` protects you from

```python
_, _, _, y_test_random = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Without stratify, test survival rate: {y_test_random.mean():.1%}")
```
```
Without stratify, test survival rate: 41.3%
```
- Without `stratify`, chance alone puts **41.3%** survivors in the test set, compared with 38.4% overall. With only 179 test passengers, a few extra survivors noticeably change every score you measure.
- **`_` is the Python name for "I don't need this value".** Only `y_test_random` is kept here.

## Cell 5: A baseline to beat

```python
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)
print("Predictions for 5 test passengers:", baseline.predict(X_test.head()))
print(f"Baseline accuracy on the test set: {baseline.score(X_test, y_test):.1%}")
```
```
Predictions for 5 test passengers: [0 0 0 0 0]
Baseline accuracy on the test set: 61.5%
```
- **`DummyClassifier` is a "model" with no brain.** `fit` only learns which answer is most common in `y_train` (0 = died), and `predict` always gives that answer, whatever the passenger looks like.
- **`score` gives accuracy:** the share of right answers. The test set has 110 deaths and 69 survivors, so "always died" is right 110 / 179 = **61.5%** of the time.
- **Why bother?** "My model is 61% accurate" *sounds* good, but a model that knows nothing gets 61%. **Every number you report must be compared with the baseline.** In Exercise 2, logistic regression gets 81%, so it really learned about 20 points' worth of something.
- Notice that you used the same `fit` / `predict` / `score` as every other model. That's the shared contract.

## Markdown answer cell

```markdown
## Exercise 1 answers
- **X** = 7 features (`pclass`, `sex`, `age`, `sibsp`, `parch`, `fare`, `embarked`); **y** = `survived`.
- **Left out:** `alive` (it is the answer: leakage), `class` and `embark_town` (copies), `who`, `adult_male` and `alone` (calculated from other features), `deck` (77% missing).
- **Split:** 712 training rows and 179 test rows (80/20). `stratify=y` keeps the survival rate equal: 38.3% vs 38.5%. Without it, the test set gets 41.3%.
- **Baseline:** always predicting "died" scores **61.5%**, so a real model must beat that to have learned anything.
```

📚 **Learn more:** [`train_test_split`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html) · [`DummyClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html) · [scikit-learn: Getting started](https://scikit-learn.org/stable/getting_started.html)

Then commit, push, and ask Claude for **"Ex 2"** (your first real model: logistic regression).
