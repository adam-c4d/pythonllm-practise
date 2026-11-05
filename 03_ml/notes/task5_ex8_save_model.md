# Task 5, Exercise 8: Save the model and use it (worked example)

Continue in `03_ml/titanic_model.ipynb`. Add a Markdown cell `## Exercise 8: Save and use the model`, then type these cells. The outputs are real (run on 2026-11-04, re-checked 2026-11-05).

**Add to the imports cell at the top:**
```python
import joblib
```

After this exercise, your whole imports cell should look like this. It's sorted the way Ruff likes (**Shift+Alt+O**): Python's own modules, a blank line, then installed packages.
```python
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
```

## Cell 1: Save the model to a file

```python
models_dir = Path("models")
models_dir.mkdir(exist_ok=True)
model_path = models_dir / "titanic_model.joblib"
joblib.dump(grid.best_estimator_, model_path)
print(f"Saved {model_path.name} ({model_path.stat().st_size / 1024:.0f} KB)")
```
```
Saved titanic_model.joblib (350 KB)
```
- **Why save?** Training happens once, in the notebook. Predicting happens many times, in an app. In Phase 4, your FastAPI server will load this file at start-up and answer requests, without the CSV or the notebook.
- **What's inside: the whole pipeline.** The learned medians, scaler means, encoder categories and all 100 trees, everything `fit` learned. The app sends raw passengers, and the file does all the cleaning and predicting.
- **`joblib`** is scikit-learn's recommended tool for saving models. It's a faster version of Python's `pickle` for big NumPy arrays.
- **`model_path.stat().st_size`** is the file size in bytes. `/ 1024` gives KB.
- **Git:** your `.gitignore` rules are commented out, so `git add .` commits this file too (350 KB, fine for a learning repo). The other computer then gets it with `git pull`, or rebuilds it with Restart → Run All. In real projects, model files are usually kept out of Git (`*.joblib` in `.gitignore`) and stored elsewhere, because they're big binaries that change every time you retrain.

## Cell 2: Load it back

```python
loaded = joblib.load(model_path)
same = (loaded.predict(X_test) == grid.predict(X_test)).all()
print("Same predictions as before:", same)
```
```
Same predictions as before: True
```
- **`joblib.load` rebuilds the exact same pipeline**, so all 179 test predictions match.
- ⚠️ **Only load model files you trust.** Loading a joblib or pickle file can run code hidden inside it. Never load one from an unknown upload or download. That matters when you build APIs.
- ⚠️ **Load it with the same scikit-learn version you saved it with** (1.9.1 here). Different versions may warn or break, which is one reason `environment.yml` pins the versions.

## Cell 3: Predict for new passengers

```python
new_passengers = pd.DataFrame([
    {"pclass": 1, "sex": "female", "age": 17, "sibsp": 1, "parch": 1,
     "fare": 100.0, "embarked": "S"},
    {"pclass": 3, "sex": "male", "age": 20, "sibsp": 0, "parch": 0,
     "fare": 8.05, "embarked": "S"},
    {"pclass": 2, "sex": "male", "age": 5, "sibsp": 1, "parch": 1,
     "fare": 26.0, "embarked": "S"},
    {"pclass": 3, "sex": "female", "age": None, "sibsp": 0, "parch": 0,
     "fare": 7.75, "embarked": "Q"},
])
display(new_passengers.assign(
    prediction=loaded.predict(new_passengers),
    survival_chance=loaded.predict_proba(new_passengers)[:, 1].round(2),
))
```
```
   pclass     sex   age  sibsp  parch    fare embarked  prediction  survival_chance
0       1  female  17.0      1      1  100.00        S           1             0.94
1       3    male  20.0      0      0    8.05        S           0             0.11
2       2    male   5.0      1      1   26.00        S           0             0.46
3       3  female   NaN      0      0    7.75        Q           1             0.76
```
- **A list of dicts → `pd.DataFrame`**, one dict per passenger. Each dict is split over 2 lines to stay under Ruff's 88-character limit; inside brackets Python ignores line breaks. This is exactly the shape of JSON that an API receives, so it's the bridge to Phase 4.
- **The columns must have the same names as `X_train`.** The pipeline finds columns by name, not by position.
- **`age: None` works:** pandas turns it into `NaN`, and the pipeline's imputer fills it with the learned 28.5. A 3rd-class woman from Queenstown gets **76%**.
- **The 5-year-old boy gets only 46%.** The training set has just **8 second-class boys, all aged 3 or under** (and all 8 survived). The trees learned an age cut-off around 3.5 (Exercise 6), and he's past it, so for him the model leans on "male", and males mostly died. It has never seen a boy like him. **A model is only as good as its examples**: it can't know what it was never shown.

## Cell 4: A preview of the `/predict` endpoint

```python
request = {"pclass": 2, "sex": "female", "age": 30, "sibsp": 0, "parch": 0,
           "fare": 13.0, "embarked": "X"}
chance = loaded.predict_proba(pd.DataFrame([request]))[0, 1]
print(f"Survival chance: {chance:.0%}")
```
```
Survival chance: 84%
```
- **This is what your FastAPI endpoint will do:** JSON in → dict → one-row DataFrame → `predict_proba` → JSON out. `[0, 1]` takes row 0 (the only passenger), column 1 (the survival chance).
- **`"embarked": "X"` is a port that doesn't exist**, and the model still answers. `OneHotEncoder(handle_unknown="ignore")` turned it into all zeros instead of crashing. In Phase 4, **Pydantic** will reject bad values like this *before* they reach the model, like a Laravel form request returning a 422. Both layers matter.

## Markdown answer cell

```markdown
## Exercise 8 answers
- **Saved** the tuned pipeline (cleaning + random forest) to `models/titanic_model.joblib` (about 350 KB). Running the notebook rebuilds it.
- **Loaded** it back: the same predictions on all 179 test passengers. Only load model files you trust, with the same scikit-learn version.
- **New passengers:** 1st-class girl (17) **0.94**, 3rd-class man (20) **0.11**, 2nd-class boy (5) **0.46** (the training set's 8 second-class boys were all 3 or under, so the model never saw one like him), 3rd-class woman with no age **0.76** (the pipeline filled the age itself).
- **API preview:** dict → `pd.DataFrame([request])` → `predict_proba` is exactly what the FastAPI `/predict` endpoint will do in Phase 4. An unknown port (`"X"`) doesn't crash the model, but the API should validate input first (Pydantic).
```

📚 **Learn more:** [Model persistence (joblib)](https://scikit-learn.org/stable/model_persistence.html) · [`predict_proba`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html#sklearn.linear_model.LogisticRegression.predict_proba)

## ✅ Task 5 done when
- [ ] All 8 exercises have their cells and an answers cell.
- [ ] **Restart → Run All** runs top to bottom with no errors (the grid search takes a few seconds).
- [ ] `output/` has `confusion_matrix.png` and `decision_tree.png`, and `models/` has `titanic_model.joblib`.

Then commit, push, and ask Claude to **"review all"**. That finishes Task 5. Next is Task 6 (regression: predicting numbers).
