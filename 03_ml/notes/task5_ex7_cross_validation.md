# Task 5, Exercise 7: Cross-validation and tuning (worked example)

Continue in `03_ml/titanic_model.ipynb`. Add a Markdown cell `## Exercise 7: Cross-validation and tuning`, then type these cells. The outputs are real (run on 2026-11-04).

**Change one line in the imports cell:**
```python
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
```

**The problem so far:** every comparison used the same 179 test passengers. One passenger is 0.56 points, so the scores jumped around and you couldn't tell models apart (Exercises 5 and 6). Worse, if you keep checking against the test set to choose settings, you're tuning the model to the test set, which is a slow form of leakage.

## Cell 1: Cross-validation

```python
candidates = {
    "logistic regression": LogisticRegression(),
    "tree (depth 3)": DecisionTreeClassifier(max_depth=3, random_state=42),
    "tree (no limit)": DecisionTreeClassifier(random_state=42),
    "random forest": RandomForestClassifier(random_state=42),
}
for name, estimator in candidates.items():
    scores = cross_val_score(make_model(estimator), X_train, y_train, cv=5)
    print(f"{name:<20} {scores.mean():.1%} ± {scores.std():.1%}",
          f"  folds: {scores.round(3)}")
```
```
logistic regression  79.6% ± 1.9%   folds: [0.79  0.762 0.803 0.817 0.81 ]
tree (depth 3)       80.8% ± 3.1%   folds: [0.811 0.748 0.831 0.831 0.817]
tree (no limit)      77.8% ± 3.6%   folds: [0.762 0.72  0.789 0.789 0.831]
random forest        79.1% ± 4.5%   folds: [0.79  0.713 0.838 0.831 0.782]
```
**How 5-fold cross-validation works.** It uses only the **training set** (712 rows), cut into 5 parts:
```
fold 1:  [test] [train] [train] [train] [train]
fold 2:  [train] [test] [train] [train] [train]
fold 3:  [train] [train] [test] [train] [train]
fold 4:  [train] [train] [train] [test] [train]
fold 5:  [train] [train] [train] [train] [test]
```
- The model is trained 5 times, each time on 4 parts, and scored on the 5th. **Every training passenger is used for scoring exactly once**, so the average is based on all 712 people, not 179.
- **`± std`** shows how much the 5 scores differ. A small spread means the model is stable.
- **`cross_val_score`** builds a fresh copy of the pipeline for each fold, so the cleaning steps are re-fitted on each fold's training part. No leakage, again thanks to the pipeline.
- For classification, `cv=5` keeps the survival rate the same in every fold (like `stratify`).
- **`{name:<20}`** pads the name to 20 characters, so the columns line up (format specs from Task 2).

**What it reveals:**
- **The unlimited tree is now the worst (77.8%).** Its 81.6% test score in Exercise 6 was luck; cross-validation shows the overfitting.
- **The depth-3 tree is best on average (80.8%)**, and logistic regression is the most stable (± 1.9%).
- **The random forest swings the most (± 4.5%)** because its unlimited trees overfit. It needs limits, which is what tuning is for.

## Cell 2: Tune the random forest with a grid search

```python
grid = GridSearchCV(
    make_model(RandomForestClassifier(random_state=42)),
    param_grid={
        "model__max_depth": [3, 5, 7, None],
        "model__min_samples_leaf": [1, 3, 5],
    },
    cv=5,
)
grid.fit(X_train, y_train)
print("Best settings:", grid.best_params_)
print(f"Best CV accuracy: {grid.best_score_:.1%}")
```
```
Best settings: {'model__max_depth': 5, 'model__min_samples_leaf': 5}
Best CV accuracy: 82.9%
```
- **Hyperparameters** are settings *you* choose before training (`max_depth`, `min_samples_leaf`). **Parameters** are what the model learns (the tree's questions, the weights).
- **`GridSearchCV` tries every combination:** 4 depths × 3 leaf sizes = 12 settings, each cross-validated 5 times, so that's 60 fits. Then it **refits the best setting on all 712 training rows**. That refitted pipeline is `grid.best_estimator_`, and `grid` itself now predicts with it.
- **`model__max_depth`** uses a double underscore: "the `max_depth` of the step named `model`". It's like Laravel's dot notation, `config('model.max_depth')`.
- **`min_samples_leaf=5`** means every leaf must hold at least 5 passengers, so the trees can't make a leaf for one lucky person. **The limits beat the default by almost 4 points** (79.1% → 82.9%).
- It takes a few seconds. That's 60 forests of 100 trees each.

## Cell 3: The top 5 settings

```python
results = pd.DataFrame(grid.cv_results_)
display(results[["param_model__max_depth", "param_model__min_samples_leaf",
                 "mean_test_score", "std_test_score", "rank_test_score"]]
        .sort_values("rank_test_score").head(5).round(3))
```
```
   param_model__max_depth  param_model__min_samples_leaf  mean_test_score  std_test_score  rank_test_score
5                       5                              5            0.829           0.028                1
3                       5                              1            0.823           0.031                2
11                   None                              5            0.823           0.025                3
10                   None                              3            0.822           0.025                4
4                       5                              3            0.817           0.027                5
```
- **`cv_results_`** holds every setting's scores. It's a dict, so it turns straight into a DataFrame.
- **The top settings are within about 1 point of each other.** Any of them would do. In this column, "test" means the held-out *fold*, not your test set.
- **Brackets let a long chain run over several lines**, one step per line.

## Cell 4: The final exam, once

```python
print(f"Test accuracy (once, at the end): {grid.score(X_test, y_test):.1%}")
```
```
Test accuracy (once, at the end): 79.9%
```
- **This is the first time the tuned model sees the test set**, and you report this number. No more tuning after this. Otherwise the test set stops being an unseen exam.
- **Why is it lower than the CV score (82.9%)?**
  1. **The test set is small.** 79.9% is 143 of 179 right. The gap of 3 points is about **5 passengers** (1 passenger = 0.56 points).
  2. **Picking the best of 12 settings flatters the winner a little.** Part of its 82.9% is luck in the folds (the "winner's curse"), so a slightly lower score on new data is normal.
- **Honest result:** this model is about **80–83% accurate**, roughly 20 points above the baseline. The test set confirms that range; it doesn't need to beat the CV score.

## Markdown answer cell

```markdown
## Exercise 7 answers
- **5-fold cross-validation** (training set only): logistic regression 79.6% ± 1.9%, depth-3 tree 80.8% ± 3.1%, unlimited tree **77.8%** ± 3.6% (the overfitting shows here; its 81.6% test score was luck), random forest 79.1% ± 4.5%.
- **Grid search** (12 settings × 5 folds = 60 fits): best `max_depth=5`, `min_samples_leaf=5`, CV **82.9%**. Limiting the trees beats the default forest by about 4 points.
- **Test score, once:** **79.9%** (143 of 179). It's lower than CV because the test set is small (1 passenger = 0.56 points, so the gap is about 5 passengers) and the best of 12 settings is slightly flattered by luck.
- **Rule:** choose models and settings with cross-validation; touch the test set once, at the end.
```

📚 **Learn more:** [User guide: cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) · [User guide: tuning with grid search](https://scikit-learn.org/stable/modules/grid_search.html) · [`GridSearchCV`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)

Then commit, push, and ask Claude for **"Ex 8"** (save the model and use it).
