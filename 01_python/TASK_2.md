# Task 2: Python for data work (Phase 1)

**Goal:** build a small sales-report program using only plain Python: dataclasses, type hints, files, error handling, comprehensions, JSON and imports.

**Rule:** no pandas yet. Doing this by hand first shows you what pandas does for you in Phase 2.

**Data:** [data/sales.csv](data/sales.csv) has 12 rows. **2 of them are deliberately broken**:
- `Desk Lamp` has the quantity `five`.
- `Stapler` has no category.

```
01_python/
├── data/sales.csv        ← provided
├── models.py             ← Exercise 1
├── loader.py             ← Exercise 2
├── analysis.py           ← Exercise 3
└── sales_report.py       ← Exercise 4 (main script)
```

---

## Exercise 1: `models.py` (dataclasses and type hints)

Create a `Sale` dataclass with these fields: `date`, `product`, `category`, `quantity` (int) and `unit_price` (float). Give every field a type hint.

Add:
1. **A `total` property** that returns `quantity * unit_price`.
2. **A `month` property** that returns `"2026-01"` from the date `"2026-01-05"`. Use string slicing.
3. **A `from_row(cls, row: dict[str, str])` classmethod.** It turns one CSV row (where every value is a string) into a `Sale`:
   - Convert the quantity and price with `int()` and `float()`.
   - If the category is empty, `raise ValueError("missing category")`.

Test it under `if __name__ == "__main__":`.

📚 Look up: `@dataclass`, `@property`, `@classmethod`, and what `if __name__ == "__main__"` means.

## Exercise 2: `loader.py` (files and error handling)

```python
def load_sales(path: Path) -> tuple[list[Sale], list[str]]:
```
- Open the file with `csv.DictReader`.
- Build each row with `Sale.from_row`, inside `try/except ValueError`.
- Return the good sales and a list of error messages, for example `"Line 10: missing category"`. Use `enumerate(reader, start=2)` to get line numbers.

✅ Expected result: **10 sales and 2 errors**

📚 Look up: `pathlib.Path`, `csv.DictReader`, `with open(...)`, `try/except`, `enumerate`.

## Exercise 3: `analysis.py` (comprehensions and dicts)

| Function | Returns |
|---|---|
| `grand_total(sales)` | `float`: the total of all sales. Use `sum()` with a generator expression. |
| `total_by_category(sales)` | `dict[str, float]` |
| `total_by_month(sales)` | `dict[str, float]` |
| `top_n(sales, n=3)` | the `n` biggest sales, sorted by `total` |
| `filter_category(sales, category)` | a `list[Sale]` built with a **list comprehension** |

📚 Look up: list comprehensions, `dict.get(key, 0)` or `collections.defaultdict`, `sorted` with `key=`, `lambda`.

## Exercise 4: `sales_report.py` (put it together)

Load the sales, run the analysis, and print a report like this:

```
=== SALES REPORT ===
Valid rows: 10 | Skipped: 2
  ! Line 10: invalid literal for int() with base 10: 'five'
  ! Line 11: missing category

Grand total: £4,136.50

By category:
  Electronics   £3,065.00
  Furniture       £815.00
  Stationery      £256.50

By month:
  2026-01   £2,015.00
  2026-02   £1,047.50
  2026-03     £414.00
  2026-04     £660.00

Top 3 sales:
  1. Laptop          £1,500.00
  2. Monitor           £840.00
  3. Filing Cabinet    £360.00
```

(Desk Chair also totals £360, so either one at #3 is correct.)

Then **save the same data to `output/report.json`** with `json.dump(..., indent=2)`. Create the folder from code with `Path.mkdir(exist_ok=True)`.

📚 Look up: f-string formatting (`f"{value:,.2f}"`, `f"{name:<14}"`), `json.dump`.

---

## How to work
1. Do the exercises in order, and commit after each one.
2. Stuck for more than 20 minutes? Ask Claude for a **hint**.
3. When you're done, ask Claude to **"review ex1"** (or "review all").
