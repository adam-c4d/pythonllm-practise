# Task 6, Exercise 7: Cross-validation and tuning (worked example)

Continue in `03_ml/diamond_prices.ipynb`. Add a Markdown cell `## Exercise 7: Cross-validation and tuning`, then type these cells. The outputs are real (run on 2026-11-05). The whole exercise takes about 20 seconds.

**Change the `sklearn.model_selection` line in the imports cell** (the order stays sorted):
```python
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
```

## Cell 1: Compare 4 models fairly

```python
candidates = {
    "linear (all features)": clone(linear),
    "linear on log scales": clone(log_linear),
    "random forest": tree_model(RandomForestRegressor(random_state=42, n_jobs=-1)),
    "gradient boosting": tree_model(HistGradientBoostingRegressor(random_state=42)),
}
for name, model in candidates.items():
    scores = -cross_val_score(
        model, X_train, y_train, cv=5, scoring="neg_mean_absolute_error"
    )
    print(f"{name:<24} MAE ${scores.mean():,.0f} ± {scores.std():,.0f}")
```
```
linear (all features)    MAE $806 ± 7
linear on log scales     MAE $404 ± 4
random forest            MAE $287 ± 5
gradient boosting        MAE $286 ± 6
```
- **The same 5-fold cross-validation as Task 5 Exercise 7**, on the training set only. `clone(linear)` and `clone(log_linear)` are unfitted copies of the models from Exercises 4 and 5.
- **`scoring="neg_mean_absolute_error"`**: scikit-learn always treats the **highest** score as the best (that's how `GridSearchCV` picks a winner). For an error, lower is better, so it reports the error **negated**: −$286 is "higher" than −$806. The minus in front of `cross_val_score` turns it back into positive dollars.
- **The ± is tiny** ($4–7, under 2%), compared with ±2–4 points in Task 5. Each fold has about 8,600 diamonds, so the scores hardly change from fold to fold. With this much data, one test set is also reliable.
- **Forest and boosting tie** ($287 vs $286), so the smaller, faster one wins: gradient boosting.

## Cell 2: Tune gradient boosting

```python
grid = GridSearchCV(
    tree_model(HistGradientBoostingRegressor(random_state=42)),
    param_grid={
        "model__learning_rate": [0.05, 0.1, 0.2],
        "model__max_leaf_nodes": [15, 31, 63],
    },
    cv=5,
    scoring="neg_mean_absolute_error",
)
grid.fit(X_train, y_train)
print("Best settings:", grid.best_params_)
print(f"Best CV MAE: ${-grid.best_score_:,.0f}")
```
```
Best settings: {'model__learning_rate': 0.1, 'model__max_leaf_nodes': 63}
Best CV MAE: $282
```
- **`learning_rate`:** how much of its correction each new tree applies (default 0.1). Small = careful steps that need more trees; big = fast but rougher.
- **`max_leaf_nodes`:** how detailed each small tree may be (default 31). 63 lets each tree make finer price groups.
- **9 settings × 5 folds = 45 fits, then a refit on all the training rows**, in about 10 seconds.
- **Early stopping:** on more than 10,000 rows, `HistGradientBoostingRegressor` keeps 10% of its training rows aside and **stops adding trees** when they stop helping (`early_stopping="auto"`). The tuned model stopped at 79 of its 100 trees, which also protects it from overfitting.
- **Tuning gained $4** ($286 → $282). The defaults were already good, which is common for gradient boosting.

## Cell 3: The final exam, once

```python
best = grid.best_estimator_
best_pred = best.predict(X_test)
evaluate("tuned gradient boosting", best_pred)
```
```
tuned gradient boosting  MAE $   285   RMSE $   554   R² 0.981
```
- **Test MAE $285 vs CV $282:** almost the same. Compare that with Task 5's 3-point gap. With 10,788 test diamonds, luck hardly moves the score.
- **This is the number you report.** Don't tune any more after this.

**The whole journey (test MAE):**

| Step | MAE |
|---|---|
| Baseline (always the mean) | $3,021 |
| Line, carat only | $1,010 |
| Line, all features | $802 |
| Line on log scales | $400 |
| Gradient boosting | $286 |
| Tuned gradient boosting | **$285** |

**The big wins came from the right shape and the right model** (10× better); tuning added about 1%. When a model disappoints, look at the data and the errors first, and the settings last.

## Markdown answer cell

```markdown
## Exercise 7 answers
- **5-fold CV MAE** (training set only): linear $806 ± 7, log scales $404 ± 4, random forest $287 ± 5, gradient boosting **$286** ± 6. The ± is tiny because each fold has about 8,600 diamonds.
- **Negative scores:** scikit-learn always maximises the score, so errors are reported negated; `-cross_val_score(...)` turns them back into dollars.
- **Grid search** (9 settings × 5 folds): best `learning_rate=0.1`, `max_leaf_nodes=63`, CV **$282**, only $4 better than the defaults.
- **Test, once:** MAE **$285**, RMSE $554, R² **0.981**, almost the same as CV (a big test set means little luck).
- **Lesson:** baseline $3,021 → $285. The right shape (log scales) and model (boosting) did the work; tuning added about 1%.
```

📚 **Learn more:** [User guide: the `scoring` parameter](https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter) · [`cross_val_score`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_score.html) · [`GridSearchCV`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)

Then commit, push, and ask Claude for **"check, then ex 8"** (errors in %, save and use the model).
