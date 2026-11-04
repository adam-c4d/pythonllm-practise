# Task 4, Exercise 7: Write up your findings (worked example)

The last exercise of Task 4. Continue at the bottom of `02_data/titanic_eda.ipynb`, and add a Markdown cell `## Exercise 7: Findings`. The output is real (run on 2026-11-03).

**The job:** turn your analysis into **5 findings and 1 limitation** for a manager who will never read your code. This is a real AI Engineer / Data Scientist skill. The analysis only counts if someone can act on it.

## How to write a finding

| ❌ Analyst notes | ✅ Finding for a manager |
|---|---|
| `groupby("sex")["survived"].mean()` gives 0.742 and 0.189 | Women were almost **four times** as likely to survive as men (74% vs 19%). |
| `pclass` has correlation −0.34 with `survived` | **63%** of first-class passengers survived, compared with **24%** in third class. |
| `family_size` 2–4 survival_% = 57.9 | Small families did best: **58%** survived, nearly twice the rate of people travelling alone (30%). |

The rules behind the right-hand column:
1. **Lead with the "so what", not the method.** The reader doesn't care that you used `groupby`. It's like a Laravel release note for a client: "Customers can now pay by card", not "Added a `PaymentController@store` route".
2. **Every finding has a number, and a comparison.** "74% survived" means little on its own; "74% vs 19%" tells a story.
3. **Round for humans.** Use 74%, not 74.2% or 0.742. Use "almost four times", not 3.93×.
4. **Plain words, no column names.** Write "third class", not `pclass == 3`; write "travelling alone", not `family_size == 1`. Translate correlations into rates.
5. **Most important first.** Sex was the biggest factor, so it goes first.
6. **Don't claim causes.** Write "were more likely to survive" or "had better odds". Avoid "being a woman *caused* survival": your data shows patterns, not reasons (remember `fare` vs `pclass` in Exercise 6).
7. **Be honest about the data.** The limitation tells the reader how far to trust the findings.

## Cell 1: Pull the headline numbers from your analysis

Every number in a write-up should come from code, not from memory or copying. If the data changes, you re-run and update.

```python
by_sex = survival_by("sex")["survival_%"]
by_class = survival_by("pclass")["survival_%"]
by_age = survival_by(age_group)["survival_%"]
by_family = survival_by(family_type)["survival_%"]

print(f"1. Women vs men:        {by_sex['female']:.0f}% vs {by_sex['male']:.0f}% "
      f"({by_sex['female'] / by_sex['male']:.1f}x)")
print(f"2. 1st vs 3rd class:    {by_class.loc[1]:.0f}% vs {by_class.loc[3]:.0f}% "
      f"({by_class.loc[1] / by_class.loc[3]:.1f}x)")
print(f"3. 3rd-class women {rates.loc['female', 3]:.0%}, 1st-class men "
      f"{rates.loc['male', 1]:.0%}, 3rd-class men {rates.loc['male', 3]:.0%}")
print(f"4. Children vs young adults: {by_age['child']:.0f}% vs {by_age['young adult']:.0f}%")
print(f"5. Alone / small / large family: {by_family['alone']:.0f}% / "
      f"{by_family['small (2-4)']:.0f}% / {by_family['large (5+)']:.0f}%")
print(f"Limitation: {df_raw['age'].isna().mean():.0%} of ages missing "
      f"({df_raw['age'].isna().sum()} of {len(df_raw)})")
```
```
1. Women vs men:        74% vs 19% (3.9x)
2. 1st vs 3rd class:    63% vs 24% (2.6x)
3. 3rd-class women 50%, 1st-class men 37%, 3rd-class men 14%
4. Children vs young adults: 58% vs 38%
5. Alone / small / large family: 30% / 58% / 16%
Limitation: 20% of ages missing (177 of 891)
```
- **It reuses your work.** `survival_by`, `age_group` and `family_type` come from Exercise 5, and `rates` is the `pivot_table` from Exercise 5 Cell 3. That's another reason the notebook must run top to bottom.
- **`["survival_%"]`** keeps just the rate column, so `by_sex['female']` is a single number (74.2).
- **`.loc[1]`** looks up class **1 by label**. With a number index, `.loc` makes it clear you mean "the row called 1", not "position 1".
- **`rates.loc['female', 3]`** takes the row and column labels together, like a cell reference (row "female", column 3) in a spreadsheet.
- **`:.0f`** rounds a number to 0 decimals (74.2 → `74`). **`:.0%`** does the same for a share and adds `%` (0.5 → `50%`). `rates` holds shares (0.5), but `survival_by` already made percentages (74.2), so they need different formats.
- **Long f-strings over two lines:** inside brackets, Python joins the pieces, as in Exercise 3.

## Cell 2: The write-up (Markdown)

This cell has no heading of its own, because the `## Exercise 7: Findings` heading cell is already above Cell 1.

```markdown
**Who survived the Titanic?** An analysis of 891 passengers.

1. **Sex was the biggest factor:** women were almost four times as likely to survive as men (74% vs 19%).
2. **Class mattered too:** 63% of first-class passengers survived, compared with 24% in third class.
3. **Sex outweighed class:** a third-class woman had better odds (50%) than a first-class man (37%), and third-class men had the worst odds of all (14%).
4. **Children were more likely to be saved:** 58% of children aged 12 and under survived, against 38% of young adults (19–35).
5. **Small families did best:** 58% of people in families of 2–4 survived, nearly twice the rate of people travelling alone (30%), while large families of 5 or more did worst (16%).

**Limitation:** 1 in 5 passengers (177 of 891) has no recorded age, and most of them travelled third class. So the age finding rests on the 714 known ages, and it may not hold for everyone on board.
```

Why these 5, in this order:
- **Biggest effect first** (sex), then the second biggest (class), then the one that **combines them** and tells you something new: sex mattered *more* than class.
- Findings 4 and 5 show patterns that a simple average would hide: children (with real ages only), and the up-then-down family pattern that correlation missed in Exercise 6.
- **Every finding is one sentence with a comparison.** Read each one aloud to check it. If you have to explain it, rewrite it.

**Other limitations you could choose instead** (the spec asks for one):
- The data covers 891 of roughly 1,300 passengers, and **no crew**, so it's a sample, not the full ship.
- There are **no names or ticket numbers**, so the 107 identical-looking rows can't be checked (Exercise 3).
- **Small groups give noisy rates:** for example, the 72% for families of 4 comes from only 29 people (Exercise 5).
- **Patterns aren't causes:** first-class passengers paid more *and* survived more, but the data can't show why (Exercise 6).

## ✅ Done when
- [ ] The headline numbers cell runs and matches the output above.
- [ ] 5 findings, each **one sentence with a number and a comparison**, with no code or column names.
- [ ] 1 limitation that says how it affects the findings.
- [ ] **Restart → Run All** runs top to bottom with no errors.

Then commit, push, and ask Claude to **"review all"**. That finishes Task 4 and Phase 2. 🎉
