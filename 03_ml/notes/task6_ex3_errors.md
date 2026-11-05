# Task 6, Exercise 3: Look at the errors (worked example)

Continue in `03_ml/diamond_prices.ipynb`. Add a Markdown cell `## Exercise 3: Look at the errors`, then type these cells. The outputs are real (run on 2026-11-05). No new imports.

**Why this step:** a score like "MAE $1,010" tells you *how much* the model is wrong, not *where* or *why*. Looking at the errors tells you what to fix next.

## Cell 1: Draw the line over the data

```python
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(X_test["carat"], y_test, s=4, alpha=0.2, color="#2a78d6",
           label="test diamonds")
ends = pd.DataFrame({"carat": [0.2, 3.0]})
ax.plot(ends["carat"], line.predict(ends), color="#eb6834", linewidth=2,
        label="straight line")
ax.axhline(0, color="#c3c2b7", linewidth=1)
ax.set(title="A straight line can't follow the curve",
       xlabel="Carat (weight)", ylabel="Price ($)")
ax.legend(frameon=False, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
plt.savefig(output_dir / "carat_line.png", bbox_inches="tight")
plt.show()
```
The chart: a blue cloud of 10,788 dots that **curves upwards**, and an orange straight line through it. The line starts below the grey zero line at 0.2 carats.

- **`s=4` makes the dots small, and `alpha=0.2` makes them 80% transparent.** Where thousands of dots overlap, the colour gets darker, so you can see where most diamonds are.
- **A straight line only needs 2 points**, so `ends` holds the carats 0.2 and 3.0, and `line.predict(ends)` gives their prices. The column is called `carat`, the same as in training.
- **`ax.axhline(0)`** draws a horizontal line at $0, so the negative predictions are easy to see.
- **`label=` + `ax.legend()`** names the 2 things on the chart. `frameon=False` drops the box, and `loc="upper left"` puts the legend where there are no dots.

**What it shows:**
- **The data curves; the line can't.** The line is **too low** for small diamonds (it even goes below $0), **too high** around 0.5–1 carat, and **too low** again around 1.5–2 carats.
- **Vertical stripes at 1.0, 1.5 and 2.0 carats:** sellers cut stones to "magic" weights, because 1.0 carat sells for much more than 0.99.
- **A flat top around $18,800:** this dataset has no diamond above $18,823, so the cloud stops there.

## Cell 2: Errors by size

```python
errors = y_test - line_pred
bands = pd.cut(X_test["carat"], [0, 0.5, 1, 1.5, 2, 5.5])
display(errors.groupby(bands, observed=True).agg(["count", "mean"]).round(0))
```
```
            count   mean
carat
(0.0, 0.5]   3834  353.0
(0.5, 1.0]   3478 -548.0
(1.0, 1.5]   2370 -216.0
(1.5, 2.0]    727  884.0
(2.0, 5.5]    379  489.0
```
- **error = actual − predicted.** It's also called a **residual**. A positive error means the real price is *higher* than predicted, so the line is too low.
- **`pd.cut(..., [0, 0.5, 1, 1.5, 2, 5.5])`** puts each carat into a band (Task 4). `(0.5, 1.0]` means "over 0.5, up to and including 1.0".
- **`errors.groupby(bands, ...)`** groups one Series by another one with the same index, row by row. `observed=True` keeps only the bands that exist (Task 4).
- **The signs go + − − + +.** Over all diamonds the errors average about $0 (least squares makes sure of that), but by size they don't: **they follow the curve.**

**The rule:** if the errors have a **pattern** (here, the size decides whether you're too high or too low), the model has the wrong **shape**, and a better model can learn that pattern. A good model's errors look like random noise around 0 in every group.

## Markdown answer cell

```markdown
## Exercise 3 answers
- **Chart:** prices curve upwards with carat, but the line is straight. It's too low for small diamonds (even below $0), too high around 0.5–1 carat and too low again around 1.5–2 carats.
- **Mean error by size:** +$353 (0–0.5 carat), −$548 (0.5–1), −$216 (1–1.5), **+$884** (1.5–2), +$489 (over 2).
- **Lesson:** errors with a pattern mean the model has the wrong shape. Also visible: stripes at 1.0, 1.5 and 2.0 carats ("magic" weights) and no prices above $18,823.
```

📚 **Learn more:** [`Axes.scatter`](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.scatter.html) · [`pandas.cut`](https://pandas.pydata.org/docs/reference/api/pandas.cut.html) · [`PredictionErrorDisplay`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.PredictionErrorDisplay.html) (scikit-learn's ready-made error chart)

Then commit, push, and ask Claude for **"check, then ex 4"** (all features, and the cut puzzle).
