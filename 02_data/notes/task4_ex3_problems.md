# Task 4, Exercise 3: Spot the problems (worked example)

Continue in `02_data/titanic_eda.ipynb`, below the Exercise 2 answers. Add a Markdown cell `## Exercise 3: Spot the problems`, then type these cells. The outputs are real (run on 2026-11-03). Notebooks show tables as formatted HTML; they're shown as plain text here.

> 💡 **`print()` vs `display()`:** `print()` is for text and numbers. For DataFrames, use **`display(...)`**, the notebook's built-in way to show a formatted table. Unlike the "only the last line shows" rule, `display()` works on any line, so one cell can show several tables.

## Part 1: Redundant columns

### Cell 1: `pclass` vs `class`

```python
pd.crosstab(df_raw["pclass"], df_raw["class"])
```
```
class   First  Second  Third
pclass                      
1         216       0      0
2           0     184      0
3           0       0    491
```
- **`pd.crosstab(a, b)`** counts how often each pair of values appears together. It's the SQL `SELECT a, b, COUNT(*) ... GROUP BY a, b`, laid out as a grid.
- **Numbers only on the diagonal** mean that every `1` is always `First`, every `2` is always `Second`, and so on. The two columns are a perfect 1-to-1 match, so one of them is **redundant**: the same information, written differently.

### Cell 2: The other two pairs

```python
display(pd.crosstab(df_raw["survived"], df_raw["alive"]))
display(pd.crosstab(df_raw["embarked"], df_raw["embark_town"]))
```
```
alive      no  yes
survived          
0         549    0
1           0  342

embark_town  Cherbourg  Queenstown  Southampton
embarked                                       
C                  168           0            0
Q                    0          77            0
S                    0           0          644
```
Both are diagonal-only, so both are redundant pairs. ⚠️ **Why this matters in Phase 3:** `alive` *is* the answer (`survived`) written in words. If you left it in the inputs of a model that predicts `survived`, the model would score 100% by reading the answer. That mistake is called **data leakage**, and EDA is where you catch it.

### Cell 3: Derived columns (computed from other columns)

```python
print((df_raw["adult_male"] == (df_raw["who"] == "man")).all())
print((df_raw["alone"] == (df_raw["sibsp"] + df_raw["parch"] == 0)).all())
```
```
True
True
```
- `df_raw["who"] == "man"` gives a True/False column. Comparing it with `adult_male` gives True wherever the two agree.
- **`.all()`** is `True` only if **every** row is `True`. It's like PHP's "every item passes" check.
- So `adult_male` is just "who is man", and `alone` is just "no siblings, spouse, parents or children on board". They add no new information, but they're handy shortcuts, so **keep them**. They're different from the three pairs above, which are exact copies.

## Part 2: Duplicates

### Cell 4: How many?

```python
print("Duplicated rows:", df_raw.duplicated().sum())
print("Rows involved:  ", df_raw.duplicated(keep=False).sum())
```
```
Duplicated rows: 107
Rows involved:   160
```
- **`duplicated()`** marks each row that is an exact copy of an **earlier** row. The first copy isn't marked, so 107 is the number of "extra" copies.
- **`keep=False`** marks **every** copy, including the first. So 160 rows are involved, in **53 groups** of identical-looking rows.

### Cell 5: Look at the biggest groups

```python
cols = ["survived", "pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]
dups = df_raw[df_raw.duplicated(keep=False)]
dups[cols].value_counts(dropna=False).head(3)
```
```
survived  pclass  sex   age  sibsp  parch  fare    embarked
0         3       male  NaN  0      0      7.8958  S           13
                                           8.0500  S           12
                                           7.7500  Q            8
```
- `value_counts()` on several columns counts each **combination**. `dropna=False` is needed because `age` is `NaN` in these groups, and without it these rows would be dropped from the count.
- **The biggest group is 13 identical rows:** third-class men, no recorded age, travelling alone, standard fare £7.90 from Southampton, all died.

### Cell 6: What do the duplicates have in common?

```python
print(f"Age missing: {dups['age'].isna().mean():.1%}")
print(dups["pclass"].value_counts())
```
```
Age missing: 58.1%
pclass
3    125
2     31
1      4
```
**Decision: keep the duplicates.** This dataset has **no name or ticket number**, so nothing tells passengers apart. 13 men who all paid the standard third-class fare and have no recorded age *look* identical, but they were 13 different people. That's why 125 of the 160 rows are third class, and 58% have no age: with fewer details recorded, people are more likely to look alike. Deleting the "duplicates" would delete **real passengers** and change the survival rates.

**Laravel analogy:** two `users` rows with the same name, city and age aren't the same person. That's why tables have a primary key (`id`). Here the key is missing, so you can't prove these rows are duplicates.

> 💡 **Duplicates depend on which columns you compare.** With all 15 columns there are 107; with only the 8 columns in `cols` there are 111 (`df_raw[cols].duplicated().sum()`). Always say which columns you compared.

## Part 3: Odd values

### Cell 7: Fares of £0

```python
zero = df_raw[df_raw["fare"] == 0]
print(f"{len(zero)} passengers paid £0: "
      f"{(zero['sex'] == 'male').sum()} men, {zero['alone'].sum()} alone, "
      f"{(zero['embarked'] == 'S').sum()} from Southampton, {zero['survived'].sum()} survived")
print(zero["pclass"].value_counts().sort_index())
```
```
15 passengers paid £0: 15 men, 15 alone, 15 from Southampton, 1 survived
pclass
1    5
2    6
3    4
```
- Splitting a long f-string over several lines: Python joins string pieces that sit next to each other inside brackets.
- **This isn't random.** All 15 are men travelling alone who boarded at Southampton, across all three classes. That pattern fits complimentary tickets, such as staff travelling for work, much better than a typing mistake. **Keep them**, but remember that `£0` doesn't mean "the cheapest ticket". It will pull down fare averages slightly.

### Cell 8: The highest fares

```python
display(df_raw.nlargest(5, "fare")[["survived", "pclass", "sex", "age", "fare", "embarked"]])
print("99% of fares are below:", df_raw["fare"].quantile(0.99).round(2))
```
```
     survived  pclass     sex   age      fare embarked
258         1       1  female  35.0  512.3292        C
679         1       1    male  36.0  512.3292        C
737         1       1    male  35.0  512.3292        C
27          0       1    male  19.0  263.0000        S
88          1       1  female  23.0  263.0000        S
99% of fares are below: 249.01
```
- **Three passengers paid exactly 512.3292.** All three are first class, boarded at Cherbourg and survived. The same odd amount, three times, points to **one booking shared by a travelling party**, not a typo. In this dataset, `fare` is the price of the *ticket*, which can cover several people.
- **`quantile(0.99)`**: 99% of fares are below £249.01, so £512 is an **outlier**: far from the rest, but real.
- **An outlier isn't the same as an error.** Delete an error, like the `"five"` in Task 2. Keep a real outlier, and be aware that it skews averages (mean £32.20 vs median £14.45).

### Bonus: Odd ages

```python
print("Babies:", df_raw.loc[df_raw["age"] < 1, "age"].tolist())
print("Ages ending in .5 (over 1):", ((df_raw["age"] % 1 == 0.5) & (df_raw["age"] > 1)).sum())
```
```
Babies: [0.83, 0.92, 0.75, 0.75, 0.67, 0.42, 0.83]
Ages ending in .5 (over 1): 18
```
- Ages below 1 are babies, measured in fractions of a year (0.42 is about 5 months).
- In the original Titanic dataset's documentation, an age of the form `xx.5` means the age was **estimated**. Data often has conventions like this, and only the documentation explains them.
- `df.loc[rows, column]` selects rows by a mask *and* a column in one step. `% 1` gives the decimal part (28.5 % 1 = 0.5).

## Markdown answer cell

```markdown
## Exercise 3 answers
- **Redundant pairs** (crosstabs are diagonal-only): `pclass`/`class`, `survived`/`alive`, `embarked`/`embark_town`. Keep one of each. `alive` would be **data leakage** if it were used to predict `survived`.
- **Derived columns:** `adult_male` = "who is man"; `alone` = sibsp + parch == 0. Keep them as shortcuts.
- **Duplicates:** 107 (160 rows in 53 groups; the biggest is 13 third-class men with no age and the same £7.90 fare). **Keep them:** with no name or ticket ID, identical-looking rows are different people. Deleting them would remove real passengers.
- **£0 fares:** 15 passengers, all men, alone, from Southampton (likely complimentary tickets). Real, not errors.
- **Max fare £512.33:** 3 first-class passengers from Cherbourg on one shared booking. A real outlier; 99% of fares are below £249.
- **Outlier ≠ error:** delete errors, keep real outliers, and use the median when data is skewed.
```

Then **Restart → Run All**, commit, push, and ask Claude for **"Ex 4"** (clean: drop columns, fill missing ages by class).
