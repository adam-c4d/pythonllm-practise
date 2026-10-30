# Task 3: pandas basics (Phase 2)

**Goal:** redo the Task 2 sales report with pandas in a Jupyter notebook, then add charts. You'll see how much of your Task 2 code pandas replaces.

**Why the same data?** You already know every correct answer, so you can check pandas against your own Python version.

**Data:** the same file, [../01_python/data/sales.csv](../01_python/data/sales.csv). Don't copy it; read it with a relative path. It still has the 2 broken rows (`five` and the missing category).

```
02_data/
├── TASK_3.md
├── sales_pandas.ipynb    ← Exercises 1–4 (notebook)
├── report_pandas.py      ← Exercise 5 (script)
└── output/               ← charts (already git-ignored)
```

> **pandas 3 note:** you have pandas 3.1. Many tutorials online were written for pandas 1 or 2:
> - Text columns show as `str`. Older tutorials show `object`.
> - Don't use `inplace=True`. Assign the result instead: `df = df.dropna(...)`.

---

## Setup: your first notebook

1. In VS Code, create a new file `02_data/sales_pandas.ipynb`.
2. Top right: **Select Kernel** → **Python Environments** → **dsllm**.
3. In the first cell, type `import pandas as pd` and run it with **Shift+Enter**.

How notebooks work:
- A notebook is like `php artisan tinker` that remembers your variables and saves your code **and** its output in one file.
- The **last line** of a cell is displayed automatically. You don't need `print()`.
- Variables stay in memory until you restart the kernel. If things act strangely, click **Restart**, then **Run All**.
- Write your answers to the questions in **Markdown cells** (use the `+ Markdown` button).

> **If the kernel crashes when you draw a chart** (`Windows fatal exception: code 0xc06d007f`): the kernel isn't running inside the activated `dsllm` env, so it loads base Anaconda's maths library. Select the kernel again through **Python Environments → dsllm**. Don't use "Existing Jupyter Server".

---

## Exercise 1: Load and inspect

Load the CSV into a DataFrame called `df`, then look at it:

| Try | What it shows |
|---|---|
| `df.head()` | the first 5 rows |
| `df.shape` | `(rows, columns)` |
| `df.info()` | each column's type and how many values aren't missing |
| `df.isna().sum()` | how many values are missing in each column |

Answer these in a Markdown cell:
1. How many rows and columns are there?
2. `unit_price` is `float64`, but `quantity` is `str`. Why? (Look at the data.)
3. Which column has a missing value? What did pandas put in the empty cell?

✅ Expected: shape `(12, 5)`, and 1 missing value.

📚 Look up: `pd.read_csv`, `DataFrame.info`, `isna`, `NaN`.

## Exercise 2: Clean the data

In Task 2, `from_row` and `load_sales` handled this in about 30 lines. In pandas:

1. Convert `quantity` to numbers with `pd.to_numeric(..., errors="coerce")`. What happens to `"five"`?
2. **Before** you drop anything, display the bad rows: the rows where `quantity` **or** `category` is missing. Use a boolean mask with `|` (or), and put each condition in brackets.
3. Drop those rows with `dropna(subset=[...])`.
4. Look at `quantity`'s type now. Why is it `float64` and not a whole number? Convert it to `int`.
5. Convert `date` to a real date type.

✅ Expected:
- The bad rows have index `8` and `9`. In Task 2 they were lines 10 and 11. Why is the difference 2?
- 10 rows remain.
- `quantity` is `int64`, and `date` is `datetime64[us]`.

📚 Look up: `pd.to_numeric`, boolean indexing, `dropna`, `astype`, `pd.to_datetime`.

## Exercise 3: The report, pandas style

1. Add a `total` column: quantity × unit_price. **Don't write a loop.** pandas multiplies whole columns at once.
2. Add a `month` column like `"2026-01"`, made from `date`.
3. Reproduce every number from Task 2. Copy this table into a Markdown cell and fill in the right-hand column:

| Task 2 function | Your pandas code |
|---|---|
| `grand_total(sales)` | |
| `total_by_category(sales)` | |
| `total_by_month(sales)` | |
| `top_n(sales, 3)` | |
| `filter_category(sales, "Electronics")` | |

✅ Expected: the same numbers as in Task 2.
- Grand total: `4136.5`
- By category: Electronics `3065.0`, Furniture `815.0`, Stationery `256.5`
- By month: `2015.0`, `1047.5`, `414.0`, `660.0`
- Top 3: Laptop, Monitor, then Desk Chair **or** Filing Cabinet (both `360.0`)
- The Electronics filter returns 5 rows.

📚 Look up: column arithmetic, `.dt.strftime`, `.sum()`, `groupby`, `nlargest`, boolean indexing.

## Exercise 4: Charts

1. A **bar chart** of the total by category.
2. A **line chart** of the total by month.
3. Give each chart a title and axis labels.
4. Save both as PNG files in `02_data/output/`. Create the folder from code, like you did in Task 2.

✅ Expected: `output/sales_by_category.png` and `output/sales_by_month.png`

📚 Look up: `Series.plot(kind=...)`, `matplotlib.pyplot` (`plt.title`, `plt.xlabel`, `plt.ylabel`, `plt.savefig`), `bbox_inches="tight"`.

*Optional:* draw the bar chart a second time with seaborn (`sns.barplot`). Which version do you prefer, and why?

## Exercise 5: The short version (`report_pandas.py`)

Move the useful steps from your notebook into a normal script. It should print:
- the grand total
- the totals by category
- the totals by month
- the top 3 sales

Rules:
- The formatting doesn't have to match Task 2. Printing the pandas results as they are is fine.
- Aim for **10–15 lines**, not counting imports and blank lines.
- Build the CSV path from `Path(__file__)`, like you did in Task 2. The data is one folder up, in `01_python/data/`.

Then compare: your Task 2 version is 4 files and **170 lines** (`models.py`, `loader.py`, `analysis.py`, `sales_report.py`).

**Notebook or script?** A notebook is for exploring, like `tinker`. A script is for a job you run again and again, like an artisan command.

📚 Look up: `Path.parent`, `print(series)`, `Series.to_string()`.

---

## How to work
1. Do the exercises in order, and commit after each one.
2. Stuck for more than 20 minutes? Ask Claude for a **hint**.
3. When you're done, ask Claude to **"review ex1"** (or "review all").
