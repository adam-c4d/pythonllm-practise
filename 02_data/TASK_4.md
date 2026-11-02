# Task 4: Explore a real dataset (EDA) + NumPy basics (Phase 2)

**Goal:** learn NumPy, the library underneath pandas and scikit-learn. Then do a full **exploratory data analysis (EDA)** on a real dataset: look at it, find its problems, clean it, ask questions, chart the answers and write up what you found.

**Why EDA matters:** before you train a model (Phase 3) or let an LLM answer questions about data (the capstone), you need to know what's in the data and what's wrong with it. A data scientist's day is mostly this.

**Data:** [data/titanic.csv](data/titanic.csv) has 891 Titanic passengers and 15 columns, including whether each one survived. It's a classic first dataset, so most online tutorials use it too, and help is easy to find.

```
02_data/
├── TASK_4.md
├── data/titanic.csv       ← provided
├── numpy_basics.ipynb     ← Exercise 1
├── titanic_eda.ipynb      ← Exercises 2–7
└── output/                ← charts (git-ignored)
```

| Column | Meaning |
|---|---|
| `survived` | 1 = survived, 0 = died |
| `pclass` / `class` | ticket class: 1 = First, 2 = Second, 3 = Third |
| `sex`, `age` | passenger's sex and age in years |
| `sibsp` | number of siblings/spouses on board |
| `parch` | number of parents/children on board |
| `fare` | ticket price (in 1912 pounds) |
| `embarked` / `embark_town` | port: C = Cherbourg, Q = Queenstown, S = Southampton |
| `who`, `adult_male`, `alone` | derived columns (man/woman/child, etc.) |
| `deck` | cabin deck letter |
| `alive` | "yes"/"no" |

---

## Exercise 1: NumPy basics (`numpy_basics.ipynb`)

1. Multiply two Python lists element by element. What happens? Then do it with NumPy arrays.
2. Check an array's `dtype`, `shape` and `ndim`. What happens when you mix numbers and text in one array?
3. Use `sum`, `mean`, `max` and `argmax`, a boolean mask, and `np.where`.
4. Make a 2D array (rows × columns). Select a row and a column, and sum with `axis=0` and `axis=1`.
5. Time a list comprehension against NumPy on 1,000,000 numbers (`%timeit`).
6. Turn Titanic's `age` and `fare` columns into a NumPy array with `.to_numpy()`. Compare `np.mean` with `np.nanmean`.
7. Make random numbers with a **seed** (`np.random.default_rng(42)`) and show that the same seed gives the same numbers.

✅ Expected: `[750.0, 15.5, 120.0] * [2, 10, 3]` gives `array([1500., 155., 360.])`; the 2D array `X` has shape `(891, 2)`; `np.mean` of `age` gives `nan` but `np.nanmean` gives `29.699...`

📚 Look up: `np.array`, `dtype`, `shape`, `axis`, boolean indexing, `np.where`, `np.nanmean`, `np.random.default_rng`.

## Exercise 2: First look

Load the CSV into `df_raw`. Find:
1. The shape, the column types (`info`) and a summary (`describe`).
2. **The percentage of missing values** in each column, sorted from most to least missing.
3. The overall survival rate. Hint: the `mean` of a 0/1 column is the share of 1s.
4. How many passengers there are in each class and from each port (`value_counts`).

✅ Expected: shape `(891, 15)`; missing: `deck` **77.2%**, `age` **19.9%**, `embarked` and `embark_town` **0.2%** (2 rows); survival rate **38.4%** (342 of 891).

📚 Look up: `isna().mean()`, `sort_values`, `value_counts(dropna=False)`.

## Exercise 3: Spot the problems

1. **Redundant columns.** Three pairs of columns contain the same information in different forms. Prove it with `pd.crosstab` (a count table of one column against another).
2. **Duplicates.** Count fully duplicated rows with `df_raw.duplicated().sum()`. Should you drop them? Think about what's missing from this dataset that would tell people apart.
3. **Odd values.** How many passengers paid a fare of `0`? What's the highest fare, and is it a typo?

✅ Expected:
- The pairs are `pclass`/`class`, `survived`/`alive` and `embarked`/`embark_town`. Each crosstab has numbers only on its diagonal.
- **107 duplicated rows.** **Don't drop them.** There's no name or ticket ID column, so two different passengers with the same class, sex, age and fare look identical.
- **15** passengers have a fare of `0`, and the maximum fare is `512.33`. That's not a typo: some first-class suites really cost this much.

📚 Look up: `pd.crosstab`, `duplicated`.

## Exercise 4: Clean

Make a cleaned copy `df` and **keep `df_raw` unchanged**:
1. Drop `class`, `alive` and `embark_town` (they're redundant) and `deck` (77% missing).
2. Fill the missing `age` values with the **median age of that passenger's class**, not one median for everyone. First-class passengers were older.
3. Fill the 2 missing `embarked` values with the most common port.

✅ Expected: shape `(891, 11)` and **0** missing values. The median ages by class are 37 / 29 / 24, and the most common port is `S`.

📚 Look up: `drop(columns=)`, `groupby().transform("median")`, `fillna`, `mode()`.

## Exercise 5: Ask questions

Answer each one with code and write the answer in a Markdown cell:
1. Did women survive more than men?
2. Did class matter?
3. Sex **and** class together: make a table with sex as rows and class as columns (`pivot_table`).
4. Did children survive more? Group ages into `child` (0–12), `teen` (13–18), `young adult` (19–35), `adult` (36–60) and `senior` (61+) with `pd.cut`. **Use `df_raw["age"]`, not your filled-in ages.** Why does that matter?
5. Add `family_size` = `sibsp + parch + 1`. Did people travelling alone do better or worse?

✅ Expected:
- Women **74.2%**, men **18.9%**
- Class 1 **63.0%**, class 2 **47.3%**, class 3 **24.2%**
- First-class women **96.8%**, third-class women **50.0%**, third-class men **13.5%**
- Children **58.0%** and seniors **22.7%**. With the filled ages, "young adult" grows from 358 to **505** people, because all the guessed ages land there.
- Alone (`family_size` 1): **30.4%**. A family of 4: **72.4%**. Families of 5 or more: 0–33%.

📚 Look up: `pivot_table`, `pd.cut(bins=, labels=)`, `groupby(observed=True)`.

## Exercise 6: Charts

Save each one to `output/`:
1. `age_histogram.png`: the spread of ages (`sns.histplot`).
2. `survival_by_class_sex.png`: survival rate by class, with one bar per sex (`sns.barplot` with `hue=`). This time seaborn's default of averaging is exactly what you want. Why?
3. `fare_by_class.png`: fares by class as a box plot (`sns.boxplot`).
4. `correlation_heatmap.png`: correlations between the number columns (`sns.heatmap` of `df.corr()`). Add `is_male` (1/0) first so sex is included.

✅ Expected: in the heatmap, the strongest link to `survived` is `is_male` (**−0.54**), then `pclass` (**−0.34**), then `fare` (**+0.26**).

📚 Look up: `sns.histplot`, `sns.barplot(hue=)`, `sns.boxplot`, `sns.heatmap(annot=True)`, `DataFrame.corr`.

## Exercise 7: Write up your findings

In a final Markdown cell, write **5 findings**, each one sentence with a number, as if for a manager who won't read your code. Also include **1 limitation** of the data.

Example finding: *"Women were almost four times as likely to survive as men (74% vs 19%)."*

---

## How to work
1. Do the exercises in order, and commit after each one.
2. If you're stuck, ask Claude for an explanation or a worked example.
3. When you're done, ask Claude to **"review ex1"** (or "review all").
