# Task 5, Exercise 6: Decision trees, random forests and overfitting (worked example)

Continue in `03_ml/titanic_model.ipynb`. Add a Markdown cell `## Exercise 6: Trees and overfitting`, then type these cells. The outputs are real (run on 2026-11-04).

**Add to the imports cell at the top:**
```python
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree
```

## Cell 1: A pipeline factory, then a tree with no limits

```python
def make_model(estimator):
    """The Exercise 5 cleaning steps, followed by any model."""
    return Pipeline([("prep", clone(preprocess)), ("model", estimator)])


tree = make_model(DecisionTreeClassifier(random_state=42))
tree.fit(X_train, y_train)
print(f"Train accuracy: {tree.score(X_train, y_train):.1%}")
print(f"Test accuracy:  {tree.score(X_test, y_test):.1%}")
```
```
Train accuracy: 98.3%
Test accuracy:  81.6%
```
- **`make_model` is a factory function:** give it any model, and it returns a fresh pipeline with the Exercise 5 cleaning in front. It's like `app()->make(...)` in Laravel, which builds a new instance every time. You'll use it for every model from now on.
- **`clone(preprocess)`** makes a fresh, *unfitted* copy of the cleaning steps. Without it, every pipeline would share (and keep re-fitting) the same `preprocess` object, because `=` never copies (Task 4 Exercise 4).
- **Swapping the model is one line**, thanks to the shared `fit` / `predict` / `score` contract (Exercise 1).
- **98.3% on training but 81.6% on test: that gap is overfitting.** With no limit, the tree keeps asking questions until almost every training passenger has a leaf of their own (this one is 23 questions deep, with 152 leaves). It **memorised** the 712 training passengers, including their luck, instead of learning general rules. It's like a student who memorises last year's exam answers: perfect on those questions, ordinary on new ones.

## Cell 2: Limit the depth

```python
rows = []
for depth in [2, 3, 4, 5, 6, 8]:
    m = make_model(DecisionTreeClassifier(max_depth=depth, random_state=42))
    m.fit(X_train, y_train)
    rows.append({"max_depth": depth,
                 "train": m.score(X_train, y_train),
                 "test": m.score(X_test, y_test)})
display(pd.DataFrame(rows).round(3))
```
```
   max_depth  train   test
0          2  0.805  0.760
1          3  0.833  0.793
2          4  0.841  0.793
3          5  0.865  0.765
4          6  0.886  0.804
5          8  0.917  0.816
```
- **`max_depth`** caps how many questions the tree may ask in a row.
- **The training score climbs with every extra level** (0.805 → 0.917). A deeper tree can always fit the training data better.
- **The test score jumps around** (0.760, 0.793, 0.765, 0.804, 0.816). It doesn't follow the training score, and the differences are only a few passengers each. You can't pick the best depth from one small test set. Exercise 7 fixes that with cross-validation.
- **A list of dicts → `pd.DataFrame(rows)`** is a handy way to build a results table in a loop: one dict per row.

## Cell 3: Look at a small tree

```python
small_tree = make_model(DecisionTreeClassifier(max_depth=3, random_state=42))
small_tree.fit(X_train, y_train)
plt.figure(figsize=(16, 7))
plot_tree(
    small_tree.named_steps["model"],
    feature_names=small_tree.named_steps["prep"].get_feature_names_out(),
    class_names=["died", "survived"],
    filled=True, rounded=True, fontsize=9,
)
plt.title("Decision tree (depth 3)")
plt.savefig(output_dir / "decision_tree.png", bbox_inches="tight")
plt.show()
```
**What you should see:** an upside-down tree of 15 boxes. Orange boxes lean "died" and blue boxes lean "survived"; the stronger the colour, the surer the box. Each box shows its question, `samples` (passengers reaching it) and `value` ([died, survived] counts).

**How to read it.** Start at the top and go **left if the question is True**:
1. **`cat__sex_female <= 0.5`**, which means "is male?". **Left (459 men):** 374 died, 85 survived. **Right (253 women):** 65 died, 188 survived.
2. **Men:** the next question is **`num__age <= -2.002`**. In real units, that's **age ≤ 3.5 years**. 12 of 12 little boys with fewer than 3 siblings survived. For older men, first class (`pclass ≤ 1.5`) is 33 of 91 survived, and second and third class only 39 of 353.
3. **Women:** the next question is **`num__pclass <= 0.229`**, which means first or second class: 130 of 137 survived. In third class, it depends on the port: 26 of 71 from Southampton survived, against 32 of 45 from the other ports.

**The model found "women and children first", and the class divide, by itself.**

- **`gini`** measures how mixed a box is: 0 = everyone the same, 0.5 = half and half. The tree picks each question to make the boxes below it as "pure" as possible.
- **Why `-2.002` and not 3.5?** The tree sees the *scaled* columns from the pipeline. To convert back: `value × std + mean` = −2.002 × 13.02 + 29.56 ≈ 3.5 years. **Trees don't need scaling**, because they only compare values with a threshold. You can leave it in the pipeline (the scores are identical) but it makes the thresholds harder to read.
- **`named_steps["model"]`** takes the tree out of the pipeline, because `plot_tree` needs the bare tree.

## Cell 4: A random forest

```python
forest = make_model(RandomForestClassifier(random_state=42))
forest.fit(X_train, y_train)
print(f"Train accuracy: {forest.score(X_train, y_train):.1%}")
print(f"Test accuracy:  {forest.score(X_test, y_test):.1%}")
importance = pd.Series(
    forest.named_steps["model"].feature_importances_,
    index=forest.named_steps["prep"].get_feature_names_out(),
).sort_values(ascending=False)
print(importance.round(3))
```
```
Train accuracy: 98.3%
Test accuracy:  81.6%
num__fare          0.259
num__age           0.244
cat__sex_male      0.159
cat__sex_female    0.131
num__pclass        0.085
num__sibsp         0.047
num__parch         0.040
cat__embarked_S    0.014
cat__embarked_C    0.013
cat__embarked_Q    0.008
dtype: float64
```
- **A random forest is 100 trees that vote.** Each tree trains on a random sample of the passengers and looks at a random subset of the columns at each question, so the trees make *different* mistakes, and the vote cancels many of them out. It's the "wisdom of crowds".
- **It still overfits (98.3% on training)** because each of its trees is unlimited. In Exercise 7 you'll limit them.
- **`feature_importances_`** says how much each column helped the trees' questions, adding up to 1.0. **Sex is split over two columns**: 0.159 + 0.131 = **0.29**, the biggest.
- ⚠️ **Treat these numbers with care.** This kind of importance favours columns with **many different values** (`fare` and `age` have hundreds, `sex` has 2), because they offer more possible questions. The logistic regression weights (Exercise 5) and Task 4's survival rates both say sex matters most. `sklearn.inspection.permutation_importance` is a fairer method, for later.

## Markdown answer cell

```markdown
## Exercise 6 answers
- **Unlimited tree:** train 98.3%, test 81.6%. The big gap is **overfitting**: 23 levels and 152 leaves memorise the training passengers.
- **Depth limits:** the training score rises with depth (0.805 at depth 2 → 0.917 at depth 8), but the test score jumps around (0.760–0.816), so one small test set can't choose the depth.
- **Depth-3 tree:** first question "is male?", then age ≤ 3.5 for men and class for women. It found "women and children first" by itself. Its thresholds are in scaled units (−2.0 = 3.5 years); trees don't need scaling.
- **Random forest:** 100 voting trees, train 98.3% / test 81.6%. Importances: fare 0.26, age 0.24, sex 0.29 in total (0.16 + 0.13). Impurity importance favours columns with many values, so read it with care.
```

📚 **Learn more:** [User guide: decision trees](https://scikit-learn.org/stable/modules/tree.html) · [`DecisionTreeClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html) · [`RandomForestClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) · [`plot_tree`](https://scikit-learn.org/stable/modules/generated/sklearn.tree.plot_tree.html)

Then commit, push, and ask Claude for **"Ex 7"** (cross-validation and tuning).
