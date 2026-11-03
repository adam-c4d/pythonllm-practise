# Task 4, Exercise 5: Ask questions (worked example)

Continue in `02_data/titanic_eda.ipynb`, below the Exercise 4 answers. Add a Markdown cell `## Exercise 5: Ask questions`, then type these cells. The outputs are real (run on 2026-11-03).

Every question has the same shape: **split passengers into groups → survival rate per group.** You'll write that once, as a function, and reuse it.

## Cell 1: A helper function, then sex

```python
def survival_by(groups):
    """Number of passengers and survival rate (%) for each group."""
    table = df.groupby(groups, observed=True)["survived"].agg(["count", "mean"])
    table["mean"] = (table["mean"] * 100).round(1)
    return table.rename(columns={"count": "passengers", "mean": "survival_%"})


survival_by("sex")
```
```
        passengers  survival_%
sex                           
female         314        74.2
male           577        18.9
```
- **The mean of a 0/1 column is the share of 1s** (from Exercise 2), so `mean` of `survived` per group **is** that group's survival rate.
- **`.agg(["count", "mean"])`** computes two things per group at once, giving two columns. It's like `SELECT COUNT(*), AVG(survived) ... GROUP BY sex`.
- **`rename(columns={old: new})`** gives the columns readable names.
- **Why show `passengers` next to the rate?** A rate from 6 people means much less than a rate from 577. You'll see why it matters in Cell 6.
- **Why a function?** You'll ask the same question 5 times. It's like a reusable Eloquent scope or a helper in Laravel: write it once, call it everywhere. `groups` can be a column name (`"sex"`) or a whole Series (Cell 4).
- **`observed=True`** is explained in Cell 4.

**Answer:** yes. **74.2% of women survived vs 18.9% of men**, almost four times as likely. "Women and children first" was really applied.

## Cell 2: Class

```python
survival_by("pclass")
```
```
        passengers  survival_%
pclass                        
1              216        63.0
2              184        47.3
3              491        24.2
```
**Answer:** yes. Each step down in class lowers the rate: **63.0% → 47.3% → 24.2%**. A first-class passenger was about 2.6 times as likely to survive as a third-class one.

## Cell 3: Sex and class together (`pivot_table`)

```python
rates = df.pivot_table(index="sex", columns="pclass", values="survived",
                       aggfunc="mean", margins=True)
(rates * 100).round(1)
```
```
pclass     1     2     3   All
sex                           
female  96.8  92.1  50.0  74.2
male    36.9  15.7  13.5  18.9
All     63.0  47.3  24.2  38.4
```
- **`pivot_table`** is an Excel pivot table: `index=` gives the rows, `columns=` gives the columns, and `values=` + `aggfunc=` is what goes in each cell. Each cell is the survival rate of *that* sex in *that* class.
- **`margins=True`** adds the `All` row and column. Those are exactly your answers from Cells 1 and 2, and the corner is the overall 38.4%. It's a good self-check.
- The same table without `pivot_table`: `df.groupby(["sex", "pclass"])["survived"].mean().unstack()`. **`unstack()`** turns the inner group level into columns.
- Change `aggfunc="mean"` to `"count"` to see the group sizes. The smallest group is 76 (second-class women), so every cell here is based on enough people.

**What this table shows that Cells 1 and 2 couldn't:**
- **Almost all first- and second-class women survived** (96.8%, 92.1%), but only **half of third-class women** did (50.0%).
- **Sex mattered more than class:** a third-class woman (50.0%) had better odds than a first-class man (36.9%).
- **Third-class men had the worst odds: 13.5%.**

## Cell 4: Age groups with `pd.cut`

```python
bins = [0, 12, 18, 35, 60, 120]
labels = ["child", "teen", "young adult", "adult", "senior"]
age_group = pd.cut(df_raw["age"], bins=bins, labels=labels)
print(age_group.head(6))
survival_by(age_group)
```
```
0    young adult
1          adult
2    young adult
3    young adult
4    young adult
5            NaN
Name: age, dtype: category
Categories (5, str): ['child' < 'teen' < 'young adult' < 'adult' < 'senior']
             passengers  survival_%
age                                
child                69        58.0
teen                 70        42.9
young adult         358        38.3
adult               195        40.0
senior               22        22.7
```
- **`pd.cut`** puts numbers into ranges ("bins"). The bins `[0, 12, 18, 35, 60, 120]` make 5 ranges, and each range **includes its right edge**: `(0, 12]` is child (so 12 counts as a child and 12.5 as a teen), `(12, 18]` is teen, and so on. Five ranges need **one more edge than labels** (6 edges, 5 labels).
- It's PHP's `match (true) { $age <= 12 => 'child', $age <= 18 => 'teen', ... }`, but for all 891 rows at once.
- **The result is a `category` column**, ordered `child < teen < ...`. Groups come out in *age* order, not alphabetical order (`adult, child, senior, ...`).
- **Row 5 is `NaN`** because `df_raw` has no age for that passenger. `groupby` leaves `NaN` out, so the table counts only the **714 real ages**.
- **`survival_by(age_group)` works with a Series** because `df` and `df_raw` have the same row labels (0–890), so pandas lines them up.
- **`observed=True`** means "show only the groups that have rows". With `observed=False`, a category with no passengers would still appear, with a count of 0. `True` is the default in pandas 3, but writing it makes the code clear and avoids a warning in pandas 2.

**Answer:** yes. **Children had the best odds (58.0%), and seniors the worst (22.7%).** Teens, young adults and adults are all close (38–43%). Note that the senior group has only 22 people.

## Cell 5: Why `df_raw["age"]` and not your filled ages?

```python
real = survival_by(age_group)
filled = survival_by(pd.cut(df["age"], bins=bins, labels=labels))
display(real.join(filled, suffixes=("", "_filled")))
no_age = df_raw.loc[df_raw["age"].isna(), "survived"].mean()
print(f"Survival rate of the 177 passengers with no age: {no_age:.1%}")
```
```
             passengers  survival_%  passengers_filled  survival_%_filled
age                                                                      
child                69        58.0                 69               58.0
teen                 70        42.9                 70               42.9
young adult         358        38.3                505               34.7
adult               195        40.0                225               40.9
senior               22        22.7                 22               22.7
Survival rate of the 177 passengers with no age: 29.4%
```
- **`real.join(filled)`** puts two tables side by side, matched on their index (the age group). It's a SQL `JOIN ... ON` the group name. **`suffixes=("", "_filled")`** renames the clashing columns from the second table. (`rsuffix=` also works, but pandas 3.1 marks it as deprecated.)
- **The guesses all land in 2 groups.** The fill values were 24 and 29 (147 people) and 37 (30 people), so "young adult" grows from **358 to 505**, and "adult" from 195 to 225.
- **They change the answer, too.** The passengers with no age survived at only 29.4%, because most were in third class. Adding them drags "young adult" down from 38.3% to **34.7%**. That drop comes from *our guess*, not from history.
- **The rule:** filled values are fine as model inputs, but when the question is **about** the column you filled, use the real values.

## Cell 6: Family size

```python
df["family_size"] = df["sibsp"] + df["parch"] + 1
survival_by("family_size")
```
```
             passengers  survival_%
family_size                        
1                   537        30.4
2                   161        55.3
3                   102        57.8
4                    29        72.4
5                    15        20.0
6                    22        13.6
7                    12        33.3
8                     6         0.0
11                    7         0.0
```
- **`+ 1` counts the passenger themselves**: siblings/spouses + parents/children + you.
- Creating a new column from existing ones is called **feature engineering**, and you'll do a lot of it in Phase 3. `df` is now `(891, 12)`.
- ⚠️ **Watch the group sizes.** 72.4% for a family of 4 comes from only 29 people, and 0% for 11 comes from **7 people who all paid the same £69.55, so they're one single family**. In a group of 6, one person moves the rate by about 17 points. Small groups give noisy rates, which is why `survival_by` shows `passengers`.

## Cell 7: Group the family sizes (`pd.cut` again)

```python
family_type = pd.cut(df["family_size"], bins=[0, 1, 4, 11],
                     labels=["alone", "small (2-4)", "large (5+)"])
survival_by(family_type)
```
```
             passengers  survival_%
family_size                        
alone               537        30.4
small (2-4)         292        57.9
large (5+)           62        16.1
```
Grouping the tiny groups gives rates you can trust more. The bins `[0, 1, 4, 11]` make the ranges `(0, 1]` alone, `(1, 4]` small and `(4, 11]` large.

**Answer:** people travelling **alone did worse (30.4%)** than small families of 2–4 (**57.9%**), but **large families of 5+ did worst (16.1%)**. A likely reason: **54 of the 62 people in large families were in third class** (`df.loc[df["family_size"] >= 5, "pclass"].value_counts()`), and it was hard to get a big family to the lifeboats together.

## Markdown answer cell

```markdown
## Exercise 5 answers
1. **Sex:** women 74.2% vs men 18.9%, so women were almost 4 times as likely to survive.
2. **Class:** 1st 63.0%, 2nd 47.3%, 3rd 24.2%. Each class down lowered the odds.
3. **Sex × class:** first-class women 96.8%, third-class women 50.0%, third-class men 13.5%. Sex mattered more than class: a third-class woman (50.0%) did better than a first-class man (36.9%).
4. **Age (real ages only):** children 58.0%, seniors 22.7%; teens, young adults and adults all 38–43%. **Why `df_raw["age"]`:** the 177 filled ages all land on 24, 29 or 37, so "young adult" grows from 358 to 505, and its rate drops from 38.3% to 34.7% because the passengers with no age had only a 29.4% survival rate. Filled values are a guess, so don't use them to answer questions about that column.
5. **Family size:** alone 30.4%, small families (2–4) 57.9%, large families (5+) 16.1%. A family of 4 had the best rate (72.4%), but small groups (29 people or fewer) give noisy rates.
```

Then **Restart → Run All**, commit, push, and ask Claude for **"Ex 6"** (charts saved to `output/`).
