# Task 5, Exercise 4: Data leakage (worked example)

Continue in `03_ml/titanic_model.ipynb`. Add a Markdown cell `## Exercise 4: Data leakage`, then type these cells. The outputs are real (run on 2026-11-04). No new imports.

**Data leakage** means the model gets information during training that it won't have when it's used for real. The scores look great, and then the model fails in production. It's one of the most common and most expensive mistakes in ML, and interviewers love asking about it.

## Cell 1: The obvious kind, a feature that *is* the answer

```python
alive = (df["alive"] == "yes").astype(int)
X_train_leak = X_train_simple.assign(alive=alive)
X_test_leak = X_test_simple.assign(alive=alive)
leaky = LogisticRegression().fit(X_train_leak, y_train)
print(f"Test accuracy with 'alive': {leaky.score(X_test_leak, y_test):.1%}")
print(pd.Series(leaky.coef_[0], index=X_train_leak.columns).round(2))
```
```
Test accuracy with 'alive': 100.0%
pclass    -0.35
sibsp     -0.08
parch     -0.01
fare       0.00
is_male   -1.05
alive      7.18
dtype: float64
```
- **`assign(alive=alive)` lines up by row label.** `alive` has all 891 rows, but `assign` only takes the values whose labels are in `X_train_simple` (712) or `X_test_simple` (179). That's index alignment from Task 4 Exercise 4.
- **`LogisticRegression().fit(...)`** works in one line because `fit` returns the model itself, so you can create, train and save it at once.
- **100% looks perfect, and it's useless.** `alive` *is* `survived` written as "yes"/"no". The weight for `alive` (7.18) dwarfs everything else: the model just copies the answer. And when you predict a *new* passenger, you don't know `alive`. That's the thing you're trying to predict.

**Real-world versions of this mistake:**
- Predicting whether a customer will cancel, using a `cancellation_date` column.
- Predicting loan defaults, using `sent_to_collections`.
- Predicting a hospital diagnosis, using a treatment that's only given *after* that diagnosis.

**The question to ask about every feature:** *would I know this value at the moment I need the prediction?* If not, drop it.

⚠️ **A 100% score (or 99%) is a warning sign, not a success.** Real problems are messy. When a score looks too good, look for leakage first.

## Cell 2: The subtle kind, test data sneaking into the preparation

```python
print("Median age, all 891 rows:  ", df["age"].median())
print("Median age, training rows: ", X_train["age"].median())
```
```
Median age, all 891 rows:   28.0
Median age, training rows:  28.5
```
- In Task 4 you filled missing ages using the **whole** dataset. If you did that *before* splitting, the 28.0 would include the ages of the 179 **test** passengers. So the test set would quietly help prepare the training data.
- The difference here is small (28.0 vs 28.5), but the principle matters. With scaling, encoding or time-based data, this kind of leak can add several percentage points of *fake* accuracy.
- **Exam analogy:** it's the teacher glancing at the exam answers while writing the study guide. Even a glance makes the exam result less trustworthy.

**The rule: anything that *learns* from data (a median, a mean, a list of categories, a model) learns from the training set only. Then it's applied unchanged to the test set.** Doing that by hand for every step is error-prone. In Exercise 5, a `Pipeline` does it automatically.

## Markdown answer cell

```markdown
## Exercise 4 answers
- **Adding `alive` gives 100% test accuracy**, and the model is useless: `alive` is the answer in words (weight 7.18 vs −1.05 for `is_male`), and it's unknown for a new passenger. A score that looks too good is a sign of leakage.
- **Two kinds of leakage:**
  - **(a) A feature that is the answer**, or that is only known after the event (`alive`, `cancellation_date`). Ask: would I know this value when I need the prediction?
  - **(b) Test data used in preparation**, such as filling missing ages with the median of all 891 rows (28.0) instead of the training rows only (28.5).
- **The fix for (b):** fit every preparation step on the training set only, then apply it to the test set. A `Pipeline` does this automatically (Exercise 5).
```

Then commit, push, and ask Claude for **"Ex 5"** (pipelines).
