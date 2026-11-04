# Task 5: Your first machine learning model (Phase 3)

**Goal:** train a model that predicts whether a Titanic passenger survived. On the way you'll learn the full scikit-learn workflow: split the data, beat a baseline, measure the model properly, avoid data leakage, put cleaning inside a pipeline, compare models fairly, and save the winner to a file.

**Why it matters:** this is the `/predict` part of your capstone. In Phase 4 you'll load the file you save in Exercise 8 into a FastAPI app. The same workflow (split → pipeline → cross-validate → save) applies to every tabular ML problem, from loan approvals to customer churn.

**Data:** the same Titanic CSV as Task 4, at [../02_data/data/titanic.csv](../02_data/data/titanic.csv). Load the **raw** file. This time the model does its own cleaning (Exercise 5), so don't reuse your cleaned `df` from Task 4.

```
03_ml/
├── TASK_5.md
├── titanic_model.ipynb    ← Exercises 1–8
├── notes/                 ← worked examples
├── output/                ← charts (git-ignored)
└── models/                ← the saved model (git-ignored, rebuilt by running the notebook)
```

**Use these settings everywhere,** so your numbers match the expected answers:
- `train_test_split(..., test_size=0.2, random_state=42, stratify=y)`
- `random_state=42` for every tree and forest

**Words you'll meet:**

| Word | Meaning |
|---|---|
| **feature** | an input column the model learns from (`X`) |
| **target** | the column you want to predict (`y`, here `survived`) |
| **training set** | the rows the model learns from |
| **test set** | rows hidden from the model, used once to check it, like an exam it hasn't seen |
| **classification** | predicting a category (survived: yes/no). Predicting a number, such as a price, is **regression** (Task 6). |

---

## Exercise 1: X, y, split, and a baseline to beat

1. Load the CSV. Make `X` from 7 feature columns: `pclass`, `sex`, `age`, `sibsp`, `parch`, `fare`, `embarked`. Make `y` from `survived`. In a Markdown cell, say why each of the other 8 columns is left out.
2. Split into training and test sets (80/20, settings above). Compare the survival rate in each. Then split again **without** `stratify` and compare.
3. Make a **baseline**: `DummyClassifier(strategy="most_frequent")`, which always predicts the most common answer. Score it on the test set.

✅ Expected: train `(712, 7)`, test `(179, 7)`. Survival rate 38.3% (train) and 38.5% (test); without `stratify`, the test rate is 41.3%. The baseline always predicts 0 (died) and scores **61.5%**. Every real model has to beat that.

📚 Look up: `train_test_split(stratify=)`, `DummyClassifier`, `fit` / `predict` / `score`.

## Exercise 2: Your first model (logistic regression)

1. Write a small function that turns `X` into a table of **only complete number columns**: `pclass`, `sibsp`, `parch`, `fare`, plus `is_male` (1/0 from `sex`). Apply it to `X_train` and `X_test`. (`age` and `embarked` have gaps, so they wait for Exercise 5.)
2. Train `LogisticRegression()` on the training table. Score it on **both** the training and the test set.
3. Show `predict` and `predict_proba` for the first 5 test passengers next to their real `y_test` values.
4. Print the learned coefficients (`coef_`) with their column names. Which feature pushes survival down the most?

✅ Expected: train **79.5%**, test **81.0%**, about 20 points above the baseline. The first 5 predictions are `[0 0 0 0 1]` vs actual `[0 0 1 0 1]`, and the woman in row 241 gets a 60% chance. The biggest coefficient is `is_male` (**−2.62**).

📚 Look up: `LogisticRegression`, `predict_proba`, `coef_`.

## Exercise 3: Is 81% good? Confusion matrix, precision and recall

1. Make a `confusion_matrix(y_test, predictions)` and explain each of its 4 numbers in words.
2. Print `classification_report(..., target_names=["died", "survived"])`.
3. Draw it with `ConfusionMatrixDisplay.from_predictions` and save it as `output/confusion_matrix.png`.

✅ Expected: `[[99 11] [23 46]]`. That's 99 deaths predicted correctly, 11 false alarms, 23 survivors missed and 46 survivors found. For "survived": precision **0.81**, recall **0.67**, so the model misses a third of the survivors.

📚 Look up: `confusion_matrix`, `classification_report`, precision vs recall.

## Exercise 4: Data leakage

1. Add `alive` (1/0) to your Exercise 2 table, then train and score again. Why is the result "perfect", and why is it useless?
2. Compare the median age of all 891 passengers with the median of `X_train` only.
3. In a Markdown cell, explain the 2 kinds of leakage: **(a)** a feature that *is* the answer, and **(b)** preparing the data with information from the test set, such as filling in missing ages with a median computed before the split.

✅ Expected: test accuracy **100%**. Median age: 28.0 for all rows vs **28.5** for the training rows.

📚 Look up: "data leakage machine learning".

## Exercise 5: Pipelines (cleaning inside the model)

1. Build a `ColumnTransformer`:
   - **Number columns** (`pclass`, `age`, `sibsp`, `parch`, `fare`): `SimpleImputer(strategy="median")`, then `StandardScaler()`.
   - **Text columns** (`sex`, `embarked`): `SimpleImputer(strategy="most_frequent")`, then `OneHotEncoder(handle_unknown="ignore")`.
2. Put it in a `Pipeline` with `LogisticRegression()`. Fit it on the **raw** `X_train` (gaps and all), and score it on both sets.
3. Look inside: list the feature names after one-hot encoding, and print the medians the imputer learned.

✅ Expected: train **80.8%**, test **80.4%** (144 of 179). There are 10 columns after encoding (`num__pclass` … `cat__sex_female`, `cat__sex_male`, `cat__embarked_C`, `cat__embarked_Q`, `cat__embarked_S`). The learned medians are `[3, 28.5, 0, 0, 14.4542]`, and the 28.5 proves the pipeline only looked at the training set.

📚 Look up: `Pipeline`, `ColumnTransformer`, `SimpleImputer`, `StandardScaler`, `OneHotEncoder`.

## Exercise 6: Decision trees, random forests and overfitting

1. Swap the model for `DecisionTreeClassifier(random_state=42)` with no depth limit. Compare its training and test scores.
2. In a loop, try `max_depth` 2, 3, 4, 5, 6 and 8. Show the training and test scores as a table.
3. Draw the depth-3 tree with `plot_tree` and save it as `output/decision_tree.png`. What does it ask first?
4. Try `RandomForestClassifier(random_state=42)` and show its `feature_importances_` with the feature names.

✅ Expected:
- Unlimited tree: train **98.3%**, test **81.6%**. It memorised the training set.
- Depth 3: train 83.3%, test 79.3%.
- The first question is `sex_female`; for men, the next question is age. The model found "women and children first" on its own.
- Random forest: train 98.3%, test 81.6%. The top importances are `fare` 0.26 and `age` 0.24, then `sex_male` 0.16 + `sex_female` 0.13. Add the two sex columns together and sex is the biggest (0.29).

📚 Look up: `DecisionTreeClassifier(max_depth=)`, `plot_tree`, `RandomForestClassifier`, overfitting.

## Exercise 7: Cross-validation and tuning

1. Use `cross_val_score(pipeline, X_train, y_train, cv=5)` for 4 models: logistic regression, tree with depth 3, unlimited tree and random forest. Show each model's mean and standard deviation.
2. Tune the random forest with `GridSearchCV`: `max_depth` in `[3, 5, 7, None]` × `min_samples_leaf` in `[1, 3, 5]`, with `cv=5`.
3. Score the best model on the test set, **once**.

✅ Expected:
- Cross-validation means: logistic regression **79.6%**, depth-3 tree **80.8%**, unlimited tree **77.8%** (the overfitting shows here), random forest **79.1%**.
- Grid search best: `max_depth=5`, `min_samples_leaf=5`, CV **82.9%**.
- Test score: **79.9%**. It's lower than the CV score, and that's normal. Explain why. (Hint: how many passengers is 1 percentage point of a 179-row test set?)

📚 Look up: `cross_val_score`, `GridSearchCV`, `best_params_`, `best_estimator_`.

## Exercise 8: Save the model and use it

1. Save `grid.best_estimator_` with `joblib.dump` to `models/titanic_model.joblib` (create the folder first).
2. In a new cell, `joblib.load` it and check that it gives the same predictions on `X_test` as before.
3. Predict for these 4 new passengers. Build them as a list of dicts, then turn it into a DataFrame:

   | pclass | sex | age | sibsp | parch | fare | embarked |
   |---|---|---|---|---|---|---|
   | 1 | female | 17 | 1 | 1 | 100.0 | S |
   | 3 | male | 20 | 0 | 0 | 8.05 | S |
   | 2 | male | 5 | 1 | 1 | 26.0 | S |
   | 3 | female | `None` | 0 | 0 | 7.75 | Q |

✅ Expected: the file is about 350 KB, and the predictions match. Survival chances: **0.94**, **0.11**, **0.46** and **0.76**. The last passenger has no age, and the pipeline fills it in itself. This is exactly what your FastAPI `/predict` endpoint will do in Phase 4.

📚 Look up: `joblib.dump`, `joblib.load`.

---

## How to work
1. Do the exercises in order, and commit after each one.
2. If you're stuck, ask Claude for an explanation or a worked example.
3. When you're done, ask Claude to **"review ex1"** (or "review all").
