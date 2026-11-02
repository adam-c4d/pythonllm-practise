# Task 4, Exercise 1: NumPy basics (worked example)

Create `02_data/numpy_basics.ipynb`, select the **dsllm** kernel, and type these cells. The outputs below are real (run on 2026-11-02).

**Why NumPy?** pandas stores its columns as NumPy arrays, and scikit-learn (Phase 3) takes NumPy arrays as input. The `np.float64(4136.5)` you saw in Task 3 was a NumPy number.

## Cell 1: Python lists can't do column maths

```python
import numpy as np

prices = [750.0, 15.5, 120.0]
quantities = [2, 10, 3]

prices * quantities
```
```
TypeError: can't multiply sequence by non-int of type 'list'
```
`quantities * 2` gives `[2, 10, 3, 2, 10, 3]`: it **repeats** the list. Lists are containers, not maths objects. That's why Task 2 needed loops.

## Cell 2: NumPy arrays can

```python
p = np.array(prices)
q = np.array(quantities)

p * q
```
```
array([1500.,  155.,  360.])
```
`q * 2` gives `array([ 4, 20,  6])`.
- `p * q` multiplies element by element (750×2, 15.5×10, 120×3).
- `q * 2` applies the 2 to every element. This is **broadcasting**, and it's why `df["quantity"] * df["unit_price"]` worked in Task 3.

## Cell 3: One type per array

```python
p.dtype, q.dtype, p.shape, p.ndim
```
```
(dtype('float64'), dtype('int64'), (3,), 1)
```
```python
np.array([1, 2.5, "x"])
```
```
array(['1', '2.5', 'x'], dtype='<U32')
```
- `dtype` is the type of every element, `shape` is the size along each dimension, and `ndim` is the number of dimensions.
- **One array, one type.** One piece of text makes everything text (`<U32` means Unicode text). It's the same reason `quantity` was `str` in Task 3, because of `"five"`.

## Cell 4: Summaries, masks and `np.where`

```python
t = p * q
t.sum(), t.mean(), t.max(), t.argmax()
```
```
(np.float64(2015.0), np.float64(671.6666666666666), np.float64(1500.0), np.int64(0))
```
```python
t[t > 300]
```
```
array([1500.,  360.])
```
```python
np.where(t > 300, "big", "small")
```
```
array(['big', 'small', 'big'], dtype='<U5')
```
- `argmax()` gives the **position** of the largest value (0 = Laptop).
- `t > 300` is a boolean mask, the same one pandas uses.
- `np.where(cond, a, b)` is PHP's `$x > 300 ? 'big' : 'small'` (or SQL `CASE WHEN`) applied to every element.

## Cell 5: 2D arrays and `axis`

```python
sales = np.array([[2, 750.0],
                  [10, 15.5],
                  [3, 120.0]])
sales.shape
```
```
(3, 2)
```
```python
sales[0]          # row 0
sales[:, 0]       # column 0
```
```
array([  2., 750.])
array([ 2., 10.,  3.])
```
```python
sales.sum(axis=0)
sales.sum(axis=1)
```
```
array([ 15. , 885.5])
array([752. ,  25.5, 123. ])
```
- `(3, 2)` means 3 rows and 2 columns. `[row, column]`, where `:` means "all".
- `axis=0` sums **down** the rows (one total per column). `axis=1` sums **across** (one total per row).
- 💡 **The axis you name disappears.** With `axis=0` the rows disappear, leaving one value per column.

## Cell 6: Speed

```python
nums = list(range(1_000_000))
arr = np.arange(1_000_000)

%timeit [n * 2 for n in nums]
%timeit arr * 2
```
Measured on the work PC: about **49 ms vs 2.7 ms, roughly 18× faster**. Your numbers will differ.
- `%timeit` is a notebook "magic" command that runs the line many times and averages. `1_000_000`: the underscores are only for readability.
- NumPy loops in compiled C code instead of Python. This matters with millions of rows, which is normal in ML.

## Cell 7: pandas → NumPy (what scikit-learn needs)

```python
import pandas as pd

df = pd.read_csv("data/titanic.csv")
X = df[["age", "fare"]].to_numpy()
X.shape
```
```
(891, 2)
```
```python
X[:3]
```
```
array([[22.    ,  7.25  ],
       [38.    , 71.2833],
       [26.    ,  7.925 ]])
```
- `.to_numpy()` drops the column names and the index, leaving a plain grid of numbers.
- `X` is the ML convention for the inputs: one row per sample (passenger) and one column per **feature**. In Phase 3 you'll give scikit-learn an `X` like this.

## Cell 8: Missing values: NumPy vs pandas

```python
ages = df["age"].to_numpy()
np.mean(ages), np.nanmean(ages), df["age"].mean()
```
```
(np.float64(nan), np.float64(29.69911764705882), np.float64(29.69911764705882))
```
- 177 ages are `NaN`. Any maths involving `NaN` gives `NaN`, so `np.mean` returns `nan`.
- `np.nanmean` skips the `NaN`s, and pandas skips them automatically.

## Cell 9: Random numbers you can repeat (seeds)

```python
rng = np.random.default_rng(42)
rng.integers(1, 7, size=10)
```
```
array([1, 5, 4, 3, 3, 6, 1, 5, 2, 1])
```
Run `np.random.default_rng(42)` again and you get exactly the same numbers.
- `integers(1, 7)` gives 1–6, because the upper limit is excluded, as with `range`.
- In Phase 3, a fixed seed means your random train/test split is the same every run, so results can be reproduced.

## Markdown answer cell

```markdown
## Exercise 1 answers
- Lists repeat (`*2`) or fail (`list * list`); arrays do element-by-element maths (vectorised).
- An array has one dtype; one piece of text turns everything into text.
- `axis=0` collapses rows (one result per column); `axis=1` collapses columns (one per row).
- NumPy was ~__× faster than a list comprehension on 1,000,000 numbers.
- `np.mean` returns `nan` if any value is missing; `np.nanmean` and pandas skip missing values.
- `X` = feature grid (rows = samples, columns = features), which is what scikit-learn takes.
- The same seed gives the same "random" numbers, so results can be reproduced.
```

Then **Restart → Run All**, commit, push, and ask Claude for **"Ex 2"**.
