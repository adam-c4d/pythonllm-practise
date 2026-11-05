# Task 5, Exercise 3: Is 81% good? Confusion matrix, precision and recall (worked example)

Continue in `03_ml/titanic_model.ipynb`. Add a Markdown cell `## Exercise 3: Confusion matrix, precision and recall`, then type these cells. The outputs are real (run on 2026-11-04).

**Add to the imports cell at the top:**
```python
from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
)
```
(`from pathlib import Path` goes first, because it's part of Python itself. A long import can be wrapped in brackets, one name per line.)

## Cell 1: The confusion matrix

```python
predictions = model.predict(X_test_simple)
cm = confusion_matrix(y_test, predictions)
print(cm)
```
```
[[99 11]
 [23 46]]
```
**Rows are what really happened, and columns are what the model predicted:**

| | predicted died | predicted survived |
|---|---|---|
| **really died (110)** | **99** correct ("true negatives") | **11** false alarms ("false positives") |
| **really survived (69)** | **23** missed ("false negatives") | **46** found ("true positives") |

- Accuracy is the diagonal: (99 + 46) / 179 = **81.0%**, the same as `score`.
- But accuracy hides **which** mistakes the model makes. Here it misses 23 survivors but raises only 11 false alarms, so it errs on the side of "died".

## Cell 2: Precision and recall

```python
print(classification_report(y_test, predictions, target_names=["died", "survived"]))
```
```
              precision    recall  f1-score   support

        died       0.81      0.90      0.85       110
    survived       0.81      0.67      0.73        69

    accuracy                           0.81       179
   macro avg       0.81      0.78      0.79       179
weighted avg       0.81      0.81      0.81       179
```
Read the **"survived"** row:
- **Precision 0.81:** *when the model says "survived", how often is it right?* 46 of its 57 "survived" predictions were right (46 / (46 + 11)).
- **Recall 0.67:** *of the people who really survived, how many did it find?* It found 46 of 69 (46 / (46 + 23)). **It misses a third of the survivors.**
- **F1 0.73:** one number that balances precision and recall. It's low if either one is low.
- **Support:** how many real cases there are (69 survivors and 110 deaths in the test set).
- **macro avg** averages the two rows equally, while **weighted avg** weights them by support.

**Which matters more depends on the cost of each mistake.** Laravel example: a model that flags fraudulent orders.
- **Low precision** means many good customers get blocked (false alarms), so they get angry.
- **Low recall** means many frauds slip through, so you lose money.

A spam filter wants high **precision**: never bin a real email. A cancer screening test wants high **recall**: never miss a case.

## Cell 3: Draw it

```python
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

ConfusionMatrixDisplay.from_predictions(
    y_test, predictions, display_labels=["died", "survived"],
    cmap="Blues", colorbar=False,
)
plt.title("Logistic regression on 179 test passengers")
plt.savefig(output_dir / "confusion_matrix.png", bbox_inches="tight")
plt.show()
```
**What you should see:** a 2 × 2 grid with "True label" (died, survived) down the side and "Predicted label" along the bottom. The darkest blue square is 99 (top left), then 46 (bottom right); the pale squares are 23 and 11.

- `from_predictions` takes the real answers and the predictions, and does the counting itself.
- `cmap="Blues"` is a one-colour scale: a darker square means more people.

## Cell 4: Moving the 0.5 cut-off

```python
chance = model.predict_proba(X_test_simple)[:, 1]
for threshold in [0.3, 0.4, 0.5, 0.6, 0.7]:
    pred = (chance >= threshold).astype(int)
    print(f"threshold {threshold}: "
          f"precision {precision_score(y_test, pred):.2f}, "
          f"recall {recall_score(y_test, pred):.2f}, "
          f"predicted survivors {pred.sum()}")
```
```
threshold 0.3: precision 0.62, recall 0.81, predicted survivors 91
threshold 0.4: precision 0.65, recall 0.77, predicted survivors 82
threshold 0.5: precision 0.81, recall 0.67, predicted survivors 57
threshold 0.6: precision 0.86, recall 0.55, predicted survivors 44
threshold 0.7: precision 0.94, recall 0.46, predicted survivors 34
```
- **`predict` always uses 0.5, but you can choose your own cut-off.** `chance >= threshold` gives True/False for every passenger, and `.astype(int)` turns that into 1/0 predictions.
- **It's a trade-off.** A **low** cut-off says "survived" more often: it finds more survivors (recall 0.81) but raises more false alarms (precision 0.62). A **high** cut-off is pickier: when it says "survived" it's right 94% of the time, but it finds fewer than half.
- **There's no perfect setting.** You pick the cut-off from the cost of each mistake (the fraud example above), not from accuracy. That's a business decision, and the reason to report precision and recall instead of only accuracy.

## Markdown answer cell

```markdown
## Exercise 3 answers
- **Confusion matrix** `[[99 11] [23 46]]`: 99 deaths predicted correctly, 11 false alarms (predicted survived, died), 23 survivors missed (predicted died, survived), 46 survivors found.
- **Survived:** precision **0.81** (when it says "survived", it's right 81% of the time), recall **0.67** (it finds only 2 in 3 survivors).
- **Accuracy hides this:** 81% sounds good, but the model misses a third of the survivors.
- **The cut-off is a trade-off:** 0.3 gives recall 0.81 but precision 0.62; 0.7 gives precision 0.94 but recall 0.46. Choose it from the cost of each mistake.
```

📚 **Learn more:** [`confusion_matrix`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html) · [`classification_report`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html) · [`ConfusionMatrixDisplay`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html) · [User guide: classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)

Then commit, push, and ask Claude for **"Ex 4"** (data leakage).
