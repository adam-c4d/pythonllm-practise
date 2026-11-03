# Task 4, Exercise 4: Clean (worked example)

Continue in `02_data/titanic_eda.ipynb`, below the Exercise 3 answers. Add a Markdown cell `## Exercise 4: Clean`, then type these cells. The outputs are real (run on 2026-11-03).

The goal: a cleaned copy `df` with shape `(891, 11)` and 0 missing values, while **`df_raw` stays untouched**.

## Cell 1: Drop the columns you don't need

```python
df = df_raw.drop(columns=["class", "alive", "embark_town", "deck"])
print("df:    ", df.shape)
print("df_raw:", df_raw.shape)
print(list(df.columns))
```
```
df:     (891, 11)
df_raw: (891, 15)
['survived', 'pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked', 'who', 'adult_male', 'alone']
```
- **`drop(columns=[...])` returns a new DataFrame.** `df_raw` still has 15 columns. It's like Laravel's `$collection->except([...])`, which returns a new collection and leaves the original alone.
- The 3 redundant columns are the ones you found in Exercise 3. `deck` goes because 77% of it is missing: too little data to fill in honestly.

> ⚠️ **Why not `df = df_raw` and then drop?** In Python, `=` never copies. It gives the **same object** a second name, just like `$b = $a` for an *object* in PHP (you'd need `clone $a`). Change `df`, and `df_raw` changes too:
> ```python
> a = pd.DataFrame({"x": [1.0, None]})
> b = a                      # same object, two names
> b["x"] = b["x"].fillna(0)
> print(a["x"].tolist())     # [1.0, 0.0]  ← a changed too!
> print(b is a)              # True
> ```
> To make a real copy, use `.copy()`. You don't need it here because `drop()` already returns a new DataFrame.

## Cell 2: Why fill age by class, not with one median?

```python
print(df.groupby("pclass")["age"].median())
print("Overall median:", df["age"].median())
print(df.loc[df["age"].isna(), "pclass"].value_counts().sort_index())
```
```
pclass
1    37.0
2    29.0
3    24.0
Name: age, dtype: float64
Overall median: 28.0
pclass
1     30
2     11
3    136
Name: count, dtype: int64
```
- **First-class passengers were older** (median 37) than third-class ones (median 24). If you used one median (28) for everyone, a missing first-class age would be guessed 9 years too young.
- **Most missing ages (136 of 177) are in third class.** So the choice of fill value matters most there.
- **Why the median, not the mean?** The median ignores extremes, as you saw with `fare` in Exercise 2.

## Cell 3: `transform`: one value per row, not per group

```python
class_median = df.groupby("pclass")["age"].transform("median")
print(class_median.shape)
display(df[["pclass", "age"]].assign(class_median=class_median).head(6))
```
```
(891,)
   pclass   age  class_median
0       3  22.0          24.0
1       1  38.0          37.0
2       3  26.0          24.0
3       1  35.0          37.0
4       3  35.0          24.0
5       3   NaN          24.0
```
The difference between the two, and the most important idea in this exercise:

| | Result | SQL equivalent |
|---|---|---|
| `groupby("pclass")["age"].median()` | **3 rows**, one per class | `SELECT pclass, AVG(age) ... GROUP BY pclass` |
| `groupby("pclass")["age"].transform("median")` | **891 rows**, each row gets *its own class's* median | `AVG(age) OVER (PARTITION BY pclass)`, a window function |

- `transform` returns a Series with **the same length and the same index (row labels) as `df`**. Row 5 is third class, so it gets 24.0, ready to fill its `NaN`.
- **`.assign(class_median=...)`** returns a new DataFrame with an extra column. Here it's only used to show the values side by side. `df` doesn't change.

## Cell 4: Fill the missing ages

```python
was_missing = df["age"].isna()      # remember which rows were empty
df["age"] = df["age"].fillna(class_median)
print("Missing ages now:", df["age"].isna().sum())
df.loc[was_missing, ["pclass", "age"]].value_counts()
```
```
Missing ages now: 0
pclass  age 
3       24.0    136
1       37.0     30
2       29.0     11
Name: count, dtype: int64
```
- **`fillna(class_median)`** fills each `NaN` with the value from `class_median` **at the same row label**. Rows that already had an age keep it. pandas lines rows up by their index, not by position.
- **`was_missing` is saved *before* filling.** Afterwards, you can't tell a guessed 24 from a real 24. The check confirms that every guess is exactly its class median: 136 × 24, 30 × 37 and 11 × 29.

> 💡 **In VS Code it shows as `(np.int64(3), np.float64(24.0))` | 136 instead.** The data is the same. Only the display differs. The output above is pandas' text view (what `print()` shows). VS Code draws its own table for the *last line* of a cell. It squashes the two-level index (`pclass`, `age`) into one tuple per row and shows each part with `repr()`. Since NumPy 2, `repr()` of a NumPy number is `np.int64(3)`, not `3`. For a clean table, end the cell with `print(...)` or `.reset_index()`:
> ```python
> df.loc[was_missing, ["pclass", "age"]].value_counts().reset_index()
> ```
> ```
>    pclass   age  count
> 0       3  24.0    136
> 1       1  37.0     30
> 2       2  29.0     11
> ```

> ⚠️ **pandas 3 trap: `inplace=True` on a column does nothing.** This *looks* like it should work, but it leaves all 177 ages missing:
> ```python
> df["age"].fillna(class_median, inplace=True)   # ❌ silently does nothing
> ```
> pandas 3 shows `ChainedAssignmentError: A value is being set on a copy of a DataFrame or Series through chained assignment...`. `df["age"]` hands you a copy, so you fill the copy and then throw it away. **Always assign back:** `df["age"] = df["age"].fillna(...)`.

## Cell 5: Fill the 2 missing ports

```python
display(df_raw.loc[df_raw["embarked"].isna(), cols])
port = df["embarked"].mode()[0]
print("Most common port:", port)
df["embarked"] = df["embarked"].fillna(port)
```
```
     survived  pclass     sex   age  sibsp  parch  fare embarked
61          1       1  female  38.0      0      0  80.0      NaN
829         1       1  female  62.0      0      0  80.0      NaN
Most common port: S
```
- **Look before you fill.** Both are first-class women, alone, who paid the same £80 and survived, so they were most likely travelling together on one ticket. (Historical records say they boarded at Southampton, so this guess happens to be right.) `cols` is the list you made in Exercise 3.
- **`mode()` is the most common value.** It returns a **Series**, not a single value (`0    S`), because two values can tie. **`[0]`** takes the first one.
- For text columns, there's no median, so the **mode** is the usual fill.

## Cell 6: Final check

```python
print("Shape:", df.shape)
print("Missing values in df:    ", df.isna().sum().sum())
print("Missing values in df_raw:", df_raw.isna().sum().sum())
```
```
Shape: (891, 11)
Missing values in df:     0
Missing values in df_raw: 869
```
- **`.sum().sum()`:** the first `sum()` counts per column (11 numbers), and the second adds those up to one total.
- `df_raw` still has all its gaps (177 age + 688 deck + 2 embarked + 2 embark_town = 869). The original is safe, so you can always compare with it.

## Cell 7: The side effect of filling

```python
pd.DataFrame({
    "before": df_raw["age"].describe(),
    "after": df["age"].describe(),
}).round(2)
```
```
       before   after
count  714.00  891.00
mean    29.70   29.07
std     14.53   13.24
min      0.42    0.42
25%     20.12   22.00
50%     28.00   26.00
75%     38.00   37.00
max     80.00   80.00
```
- **Filling isn't free.** 177 guesses landed on only 3 values (24, 29 and 37). The **spread shrinks** (std 14.53 → 13.24), and the median moves from 28 to 26 because 136 guesses of 24 pile up below it.
- The filled data looks **more certain than it really is.** That's fine for a model's inputs (Phase 3), but not for questions *about* age. In Exercise 5 you'll group ages using **`df_raw["age"]`**, and you'll see how much the 177 guesses distort the groups.
- 💡 In Phase 3, scikit-learn's `SimpleImputer` does this same fill, and a common trick is to keep a `was_missing` flag column so the model knows which ages were guessed.

## Markdown answer cell

```markdown
## Exercise 4 answers
- **Dropped:** `class`, `alive`, `embark_town` (redundant) and `deck` (77% missing). `drop()` returns a new DataFrame, so `df_raw` is unchanged (891, 15).
- **Age:** filled with the **median of each passenger's class** (1st 37, 2nd 29, 3rd 24) using `groupby().transform("median")`, because first-class passengers were older. 136 of the 177 missing ages were third class.
- **Embarked:** the 2 missing values (two first-class women on the same £80 fare) filled with the mode, `S`.
- **Result:** `df` is (891, 11) with 0 missing values.
- **Side effect:** filling shrinks the spread of age (std 14.53 → 13.24) and moves the median from 28 to 26, so use `df_raw["age"]` when the question is about age itself.
```

Then **Restart → Run All**, commit, push, and ask Claude for **"Ex 5"** (ask questions: survival by sex, class, age group and family size).
