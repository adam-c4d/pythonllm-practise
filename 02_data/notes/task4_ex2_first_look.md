# Task 4, Exercise 2: First look at the Titanic data (worked example)

Create `02_data/titanic_eda.ipynb` (you'll use it for Exercises 2–7) and select the **dsllm** kernel. Add a Markdown cell `## Exercise 2: First look`, then type these cells. The outputs are real (run on 2026-11-03).

> 💡 Remember: a notebook shows only the **last line** of a cell. Each cell below has one result you want to see. When you want several, use `print()`.

## Cell 1: Imports (always at the top)

```python
import pandas as pd
```
Later exercises add `matplotlib` and `seaborn` here, so every dependency is in one place, like `use` statements at the top of a PHP file.

## Cell 2: Load and check the size

```python
df_raw = pd.read_csv("data/titanic.csv")
df_raw.shape
```
```
(891, 15)
```
- **891 passengers (rows) and 15 columns.**
- **Why `df_raw`?** In Exercise 4 you'll make a cleaned copy called `df`. Keeping the original untouched means you can always compare with it, or start the cleaning again. It's like keeping the original uploaded file in Laravel instead of overwriting it.

## Cell 3: Look at the first rows

```python
df_raw.head()
```
```
   survived  pclass     sex   age  sibsp  parch     fare embarked  class    who  adult_male deck  embark_town alive  alone
0         0       3    male  22.0      1      0   7.2500        S  Third    man        True  NaN  Southampton    no  False
1         1       1  female  38.0      1      0  71.2833        C  First  woman       False    C    Cherbourg   yes  False
2         1       3  female  26.0      0      0   7.9250        S  Third  woman       False  NaN  Southampton   yes   True
3         1       1  female  35.0      1      0  53.1000        S  First  woman       False    C  Southampton   yes  False
4         0       3    male  35.0      0      0   8.0500        S  Third    man        True  NaN  Southampton    no   True
```
Already you can spot `NaN` in `deck`, and pairs that look like the same information twice: `pclass`/`class` (3 = Third), `survived`/`alive` (0 = no), `embarked`/`embark_town` (S = Southampton). You'll prove that in Exercise 3.

## Cell 4: Column types and missing values

```python
df_raw.info()
```
```
<class 'pandas.DataFrame'>
RangeIndex: 891 entries, 0 to 890
Data columns (total 15 columns):
 #   Column       Non-Null Count  Dtype  
---  ------       --------------  -----  
 0   survived     891 non-null    int64  
 1   pclass       891 non-null    int64  
 2   sex          891 non-null    str    
 3   age          714 non-null    float64
 4   sibsp        891 non-null    int64  
 5   parch        891 non-null    int64  
 6   fare         891 non-null    float64
 7   embarked     889 non-null    str    
 8   class        891 non-null    str    
 9   who          891 non-null    str    
 10  adult_male   891 non-null    bool   
 11  deck         203 non-null    str    
 12  embark_town  889 non-null    str    
 13  alive        891 non-null    str    
 14  alone        891 non-null    bool   
dtypes: bool(2), float64(2), int64(4), str(7)
memory usage: 92.4 KB
```
- **Non-Null Count** is how many values are **present**. Anything below 891 has gaps: `age` 714, `deck` only 203, and `embarked`/`embark_town` 889.
- **`age` is `float64`, not `int64`.** That's partly because babies have fractional ages (0.42 years), and partly because `NaN` is a float, as you saw with `quantity` in Task 3.
- **`bool`** columns hold `True`/`False`. You'll see shortly that they behave like 1/0.

## Cell 5: Summary of the number columns

```python
df_raw.describe().round(2)
```
```
       survived  pclass     age   sibsp   parch    fare
count    891.00  891.00  714.00  891.00  891.00  891.00
mean       0.38    2.31   29.70    0.52    0.38   32.20
std        0.49    0.84   14.53    1.10    0.81   49.69
min        0.00    1.00    0.42    0.00    0.00    0.00
25%        0.00    2.00   20.12    0.00    0.00    7.91
50%        0.00    3.00   28.00    0.00    0.00   14.45
75%        1.00    3.00   38.00    1.00    0.00   31.00
max        1.00    3.00   80.00    8.00    6.00  512.33
```
How to read it: `count` is the values present; `mean` is the average; `std` is the spread (how far values usually are from the mean); `min`/`max` are the extremes; `25%`/`50%`/`75%` are **percentiles**, where `50%` is the **median**, the middle value. `.round(2)` only makes it easier to read.

What a data scientist notices:
- **`survived` mean = 0.38:** the average of a 0/1 column is the **share of 1s**, so 38% survived.
- **`fare` mean (32.20) is more than twice the median (14.45).** A few very expensive tickets (max **512.33**) pull the average up, so the data is **skewed**. For skewed data, the median describes a "typical" passenger better.
- **`age` min 0.42** is a baby of about 5 months. It's real, not an error.
- **`pclass` mean 2.31 means nothing.** Class is a *category* stored as a number. "Average class 2.31" makes as much sense as an "average postcode". Always ask whether a number column is really a quantity.
- **`parch` 75% = 0:** at least three quarters of passengers had no parents or children on board.

## Cell 6: Summary of the text columns

```python
df_raw.describe(include="str")
```
```
         sex embarked  class  who deck  embark_town alive
count    891      889    891  891  203          889   891
unique     2        3      3    3    7            3     2
top     male        S  Third  man    C  Southampton    no
freq     577      644    491  537   59          644   549
```
For text, `describe` shows how many values there are (`count`), how many **different** values (`unique`), the most common one (`top`) and how often it appears (`freq`). So: 577 of 891 passengers were male, most were in Third class (491), and most boarded at Southampton (644).

## Cell 7: Percentage missing per column

```python
missing_pct = (df_raw.isna().mean() * 100).round(1).sort_values(ascending=False)
missing_pct[missing_pct > 0]
```
```
deck           77.2
age            19.9
embarked        0.2
embark_town     0.2
```
Read the chain left to right:
1. **`df_raw.isna()`** gives a True/False table of the same size, where `True` means missing.
2. **`.mean()`** averages each column. **`True` counts as 1 and `False` as 0,** so the mean is the **share** of missing values. For example, `pd.Series([True, False, True, True]).mean()` is `0.75`.
3. **`* 100`** turns the share into a percentage, and **`.round(1)`** keeps 1 decimal.
4. **`.sort_values(ascending=False)`** puts the worst columns first.
5. **`missing_pct[missing_pct > 0]`** is a boolean mask that keeps only the columns with gaps.

**Why percentages, not counts?** "688 missing" means nothing until you know the total. **77.2%** tells you at once that `deck` is mostly empty, which is why you'll drop it in Exercise 4. **19.9%** for `age` is worth filling in, and **0.2%** (2 rows) is trivial.

## Cell 8: Survival rate

```python
rate = df_raw["survived"].mean()
print(f"Survival rate: {rate:.1%}")
print(df_raw["survived"].value_counts())
```
```
Survival rate: 38.4%
survived
0    549
1    342
Name: count, dtype: int64
```
- `.mean()` gives `0.3838...`, the share of 1s, as in Cell 5.
- **`:.1%`** in an f-string multiplies by 100, keeps 1 decimal and adds `%`. It's tidier than `* 100`.
- **`value_counts()`** counts each value: 549 died and 342 survived. That's 891 in total, and 342/891 is 38.4%.
- `value_counts(normalize=True)` gives shares instead of counts: `0.616` and `0.384`.

## Cell 9: Passengers per class and per port

```python
print(df_raw["class"].value_counts())
print(df_raw["embarked"].value_counts(dropna=False))
```
```
class
Third     491
First     216
Second    184
Name: count, dtype: int64
embarked
S      644
C      168
Q       77
NaN      2
Name: count, dtype: int64
```
- More than half of the passengers (491) travelled Third class.
- ⚠️ **`dropna=False` matters.** Without it, `value_counts` **silently leaves out** the 2 missing ports, and the counts add up to 889 instead of 891. It's like SQL's `COUNT(column)`, which skips `NULL`s. When you're exploring data, always look at the missing values too.

## Markdown answer cell

```markdown
## Exercise 2 answers
- **Size:** 891 passengers, 15 columns.
- **Missing:** `deck` 77.2%, `age` 19.9%, `embarked` / `embark_town` 0.2% (2 rows). Everything else is complete.
- **Survival rate:** 38.4% (342 of 891).
- **Class:** Third 491, First 216, Second 184. **Port:** Southampton 644, Cherbourg 168, Queenstown 77, unknown 2.
- **Fare is skewed:** mean £32.20 vs median £14.45 (max £512.33), so a few very expensive tickets pull the average up.
- `pclass` is a category stored as a number, so its mean (2.31) is meaningless.
- The mean of a True/False or 0/1 column is the share of `True`/1, which is how `isna().mean()` gives the share missing.
```

Then **Restart → Run All**, commit, push, and ask Claude for **"Ex 3"** (spot the problems).
