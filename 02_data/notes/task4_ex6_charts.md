# Task 4, Exercise 6: Charts (worked example)

Continue in `02_data/titanic_eda.ipynb`, below the Exercise 5 answers. Add a Markdown cell `## Exercise 6: Charts`, then type these cells. The printed outputs are real (run on 2026-11-03), and each chart is described so you can check yours.

## First: add 2 imports to the top cell

Keep every import in Cell 1 of the notebook, as in Exercise 1:

```python
from pathlib import Path

from matplotlib.ticker import PercentFormatter
```
(`pandas`, `numpy`, `matplotlib.pyplot` and `seaborn` are already there.)

## Cell 1: Chart settings

```python
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

BLUE, ORANGE, RED, GRAY = "#2a78d6", "#eb6834", "#e34948", "#f0efec"
```
- The first two lines and `output_dir` are the same as in Task 3: no top or right border, and a folder for the PNGs. `exist_ok=True` means "don't fail if it already exists", like `mkdir -p`.
- **UPPER_CASE names are constants**, set once and never changed, like PHP `const` or a value in a Laravel `config/` file. To change a colour, change one line.
- **`A, B = x, y` unpacks a tuple**: four names get four values in one line.
- Why these colours: blue and orange are easy to tell apart, including for colour-blind readers (I ran them through a colour-blindness checker). Blue ↔ red with gray in the middle is for the heatmap, where the two colours mean opposite directions.

## Cell 2: Age histogram

```python
sns.histplot(df_raw["age"], bins=range(0, 85, 5), color=BLUE, edgecolor="white")
plt.title("Age of passengers (714 with a recorded age)")
plt.xlabel("Age (years)")
plt.ylabel("Passengers")
plt.savefig(output_dir / "age_histogram.png", bbox_inches="tight")
plt.show()
```
**What you should see:** a hump peaking at 20–25 (114 people), a small bump of 40 young children at 0–5, a dip at 5–15, and a long thin tail to 80.

- **A histogram shows how values are spread out.** It counts how many fall into each bin. `bins=range(0, 85, 5)` sets the bin edges every 5 years (0, 5, 10, … 80), so each bar is a 5-year age band.
- **`df_raw["age"]`, not `df["age"]`.** You learned this in Exercise 5: the question is about age itself, so use the real ages. The title says how many people that is.
- `edgecolor="white"` draws a thin gap between bars, so they don't merge into one block.
- **`savefig` before `show`**, as in Task 3.
- **What the shape tells you:** about two thirds of passengers (473 of 714) were 15–40. The bump at 0–5 matches the "women and children first" story: there were enough young children to matter.

### Optional: see what the filled ages do (not saved)

```python
sns.histplot(df["age"], bins=range(0, 85, 5), color=BLUE, edgecolor="white")
plt.title("Age with the 177 filled-in ages (not saved)")
plt.show()
```
The 20–25 bar jumps from **114 to 250**, because of the 136 guesses of 24. The 35–40 bar grows from 72 to 102 (30 guesses of 37). This is the Exercise 5 warning in picture form.

## Cell 3: Survival rate by class and sex

```python
ax = sns.barplot(data=df, x="pclass", y="survived", hue="sex",
                 palette={"female": BLUE, "male": ORANGE}, gap=0.1)
ax.yaxis.set_major_formatter(PercentFormatter(1))
plt.title("Survival rate by class and sex")
plt.xlabel("Class")
plt.ylabel("Survived")
plt.savefig(output_dir / "survival_by_class_sex.png", bbox_inches="tight")
plt.show()
```
**What you should see:** 3 pairs of bars (blue female, orange male) for classes 1, 2 and 3. The female bars are about 97%, 92% and 50%; the male bars are about 37%, 16% and 14%. Each bar has a short black line on top.

- **Why seaborn's default averaging is right this time (the question in the spec):** `barplot` shows the **mean** of `y` for each group. `survived` is 0/1, so the mean **is** the survival rate. It's the same table as your `pivot_table` in Exercise 5, drawn as bars. In Task 3, you wanted **totals**, so you had to override the default with `estimator="sum"`.
- **`hue="sex"`** splits each class into one bar per sex. That gives you two groupings in one chart.
- **`palette={"female": BLUE, "male": ORANGE}`** is a dict, so each sex always gets the same colour, even if the order changes. Colour should follow the *thing*, not its position.
- **`gap=0.1`** leaves a small space between the two bars in each pair.
- **`PercentFormatter(1)`** shows the y-axis as percentages: `1` means "1.0 is 100%", so 0.5 becomes 50%.
- **The black lines are 95% confidence intervals:** the range where the true rate probably lies, given how many people are in the group. **Longer line = less certain.** Third-class women (144 people, rate 50%) have a long line; first-class women (96.8%) have a short one. seaborn computes these by resampling the data at random, so the lines can change slightly between runs. Use `errorbar=None` to hide them, as in Task 3.
- **What it shows:** women beat men in every class, and the gap is largest in second class (92% vs 16%).

## Cell 4: Fare by class (box plot)

```python
sns.boxplot(data=df, x="pclass", y="fare", color=BLUE, fill=False)
plt.title("Fare by class")
plt.xlabel("Class")
plt.ylabel("Fare (£)")
plt.savefig(output_dir / "fare_by_class.png", bbox_inches="tight")
plt.show()
print(df.groupby("pclass")["fare"].median())
```
```
pclass
1    60.2875
2    14.2500
3     8.0500
Name: fare, dtype: float64
```
**What you should see:** three blue outline boxes. The first-class box is tall (about £31–£94) with dots up to £512; the second- and third-class boxes are flat near the bottom.

How to read a box plot:

| Part | Meaning |
|---|---|
| **Line inside the box** | the **median** (50%) |
| **Box** | the middle half of the passengers, from the 25th to the 75th percentile (the same numbers as in `describe()`) |
| **Whiskers** (the lines out of the box) | the normal range, up to 1.5 × the box height beyond the box |
| **Dots** | **outliers**, beyond the whiskers |

- **One colour for all boxes.** The x-axis already says which class each box is, so colouring them differently would repeat that information. **`fill=False`** draws outlines instead of three heavy solid blocks.
- **The top dot at £512 is three dots on top of each other**, the shared booking from Exercise 3. The highest third-class dot, £69.55, is the family of 11 from Exercise 5: `fare` is the price of the **ticket**, and one ticket covered the whole family. That's why third class has so many "outliers".
- **Why the boxes are squashed:** the £512 tickets stretch the y-axis, so the second- and third-class boxes look flat. The printed medians give the real gap: **£60.29 vs £14.25 vs £8.05.** A first-class ticket cost about 7 times as much as a third-class one.

## Cell 5: Correlations

```python
df["is_male"] = (df["sex"] == "male").astype(int)
num_cols = ["survived", "is_male", "pclass", "fare", "age", "sibsp", "parch"]
corr = df[num_cols].corr()
corr["survived"].drop("survived").sort_values().round(2)
```
```
is_male   -0.54
pclass    -0.34
age       -0.05
sibsp     -0.04
parch      0.08
fare       0.26
Name: survived, dtype: float64
```
- **`corr()` needs numbers, and `sex` is text.** `df["sex"] == "male"` gives True/False, and **`.astype(int)`** turns that into 1/0, like MySQL storing a boolean as `TINYINT(1)`.
- **Correlation** is a number from **−1 to +1**:
  - **+1:** the two columns rise together.
  - **−1:** one rises while the other falls.
  - **0:** there's no *straight-line* link.
- `corr()` returns a 7 × 7 table with every column against every other one. `corr["survived"]` takes one column of it, and `.drop("survived")` removes the obvious 1.00 of `survived` with itself.
- **Reading the numbers:**
  - **`is_male` −0.54:** being male (1) goes with *not* surviving (0). This is the strongest link.
  - **`pclass` −0.34:** a higher class number (third class) goes with lower survival.
  - **`fare` +0.26:** more expensive tickets go with higher survival.
- **`num_cols` is a new name** because `cols` from Exercise 3 is still used in Exercise 4. Reusing a name for something else would break things if you re-ran cells in a different order.

## Cell 6: Correlation heatmap

```python
lower = corr.iloc[1:, :-1]
mask = np.triu(np.ones_like(lower, dtype=bool), k=1)
plt.figure(figsize=(7, 6))
sns.heatmap(lower, mask=mask, annot=True, fmt=".2f", vmin=-1, vmax=1,
            cmap=sns.blend_palette([BLUE, GRAY, RED], as_cmap=True),
            linewidths=2, linecolor="white", square=True)
plt.title("Correlation between the number columns")
plt.savefig(output_dir / "correlation_heatmap.png", bbox_inches="tight")
plt.show()
```
**What you should see:** a staircase-shaped triangle of coloured squares, each with a number. The first column, `survived`, shows −0.54 (blue), −0.34 (light blue) and 0.26 (light red). Other strong squares are `fare`/`pclass` −0.55 (blue) and `parch`/`sibsp` 0.41 (red).

- **Why trim the table?** A correlation table is a mirror: `fare` vs `pclass` is the same as `pclass` vs `fare`. The diagonal is always 1.00 (each column against itself), and those squares would be the brightest red on the chart while telling you nothing. So:
  - **`corr.iloc[1:, :-1]`** drops the first row and the last column. `.iloc` selects by **position**, like NumPy slicing in Exercise 1 (`.loc` selects by label).
  - **`np.triu(..., k=1)`** makes a True/False grid that is True above the diagonal. In `heatmap`, **`mask=True` means "hide this square"**, so each pair appears exactly once.
  - Now the **first column is "everything against `survived`"**, which is the question you care about.
- **`annot=True, fmt=".2f"`** writes the number in each square with 2 decimals.
- **`vmin=-1, vmax=1`** fixes the colour scale at −1 to +1, so 0 is always the gray middle. Without it, seaborn stretches the colours to fit your data, and a weak 0.4 could look as strong as a 1.0.
- **`cmap=sns.blend_palette([BLUE, GRAY, RED], as_cmap=True)`** is a **diverging** colour scale: blue means negative, red means positive, and gray means none. Two opposite colours for two opposite directions.
- **`plt.figure(figsize=(7, 6))`** makes a bigger figure (width, height in inches), so the numbers fit.

**Two limits of correlation** (worth one line each in Exercise 7):
1. **It only sees straight lines.** `sibsp` and `parch` are near 0, and even `family_size` vs `survived` is just **0.02** (`df["family_size"].corr(df["survived"])`). But Exercise 5 showed a strong *up-then-down* pattern: alone 30%, small families 58%, large families 16%. The ups and downs cancel out. **A correlation near 0 doesn't mean "no relationship".**
2. **Correlation isn't causation.** `fare` and `pclass` are linked (−0.55), so the expensive tickets may matter only *because* they were first class. And remember the filled ages: real ages give `age`/`pclass` −0.37, but your filled ages give −0.41. Filling by class made that link look stronger.

## Markdown answer cell

```markdown
## Exercise 6 answers
- **Age** (real ages): about two thirds of passengers were 15–40, the peak is 20–25 (114 people), there's a bump of 40 children aged 0–5, and very few were over 60.
- **Survival by class and sex:** averaging is right here because `survived` is 0/1, so each bar's mean **is** the survival rate (in Task 3 we wanted totals, so `estimator="sum"`). Women beat men in every class; the gap is biggest in 2nd class (92% vs 16%).
- **Fare by class:** medians £60.29 / £14.25 / £8.05. First class has the widest spread and the £512 outliers (one shared booking). Third-class "outliers" are family tickets: fare is per ticket, not per person.
- **Correlation with survived:** `is_male` −0.54, `pclass` −0.34, `fare` +0.26; the rest are near 0.
- **Limits:** correlation only sees straight-line links (family size is 0.02, but Ex 5 shows a strong up-then-down pattern), and it isn't causation (`fare` is tied to `pclass`, −0.55).
```

Then **Restart → Run All**, check that `02_data/output/` has the 4 new PNGs, commit, push, and ask Claude for **"Ex 7"** (the write-up: 5 findings and 1 limitation).
