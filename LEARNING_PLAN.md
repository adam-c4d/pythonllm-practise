# Learning Plan: Data Science · FastAPI · LLMs

## Roadmap

| Phase | Folder | Topic | Time | What you'll be able to do |
|---|---|---|---|---|
| 0 | — | Setup | 1 day | Clean environment, Git, folder structure |
| 1 | `01_python/` | Python level-up | 1 week | Type hints, dataclasses, comprehensions, file/JSON handling, errors, modules |
| 2 | `02_data/` | Data analysis | 2 weeks | NumPy, pandas, matplotlib/seaborn charts, exploring a real dataset in Jupyter |
| 3 | `03_ml/` | Machine learning basics | 1–2 weeks | scikit-learn: train/test split, regression & classification, saving models |
| 4 | `04_fastapi/` | FastAPI | 1 week | Routes, Pydantic validation, serving your ML model as an API |
| 5 | `05_llm/` | LLMs | 2 weeks | Calling an LLM, prompts, structured output, RAG basics |
| 🏁 | `project/` | **Capstone** | 2 weeks | **"Ask Your Data" API** (below) |

### Capstone: "Ask Your Data" API
A FastAPI app where you upload a CSV file and get:
- `/summary`: statistics and charts made with pandas
- `/predict`: predictions from a scikit-learn model you trained
- `/ask`: plain-English questions about the data, answered by an LLM

It uses every phase, so each skill you learn goes into one portfolio project.

## Target dates
Set 2026-11-03 for full-time study (6–8 h a day, 5–6 days a week). **Goal: start applying for AI Engineer / LLM developer jobs in late January 2027.**

| Dates | Target |
|---|---|
| Wed 4 Nov | Finish Task 4 (Ex 5–7) → **Phase 2 done** |
| 5–13 Nov | Phase 3: ML basics (scikit-learn) |
| 16–20 Nov | Phase 4: FastAPI (your Laravel experience helps most here) |
| 23 Nov – 4 Dec | Phase 5: LLMs |
| 7–18 Dec | Capstone: "Ask Your Data" API |
| 21 Dec – 1 Jan | Break / catch-up buffer |
| 4–22 Jan | Job-ready: pytest, Docker, deployment, tool calling, LLM evals, GitHub and CV polish |
| from ~25 Jan | Apply |

**Daily rhythm:** about 3–4 exercises a day (for example, Task 4 Ex 1–4 on 3 Nov). If one phase overruns, move the dates after it back and let the December buffer absorb it.

## Progress

| Task | Status | Notes |
|---|---|---|
| **Task 1**: Environment setup | ✅ Done (2026-10-27) | Conda env `dsllm` (Python 3.13), VS Code extensions, Git, folders, first commit |
| **Task 2**: Python for data work ([spec](01_python/TASK_2.md)) | ✅ Done (2026-10-29) | Optional improvements done 2026-10-30 (`frozen`, `Self`, `try/else`, `total_by`) |
| ├ Ex 1: `models.py` | ✅ Fixed 2026-10-29 | Category stripped; `from_row` checks all `FIELDS` (`None`/blank → `ValueError`). Optional: `frozen=True`, `Self` |
| ├ Ex 2: `loader.py` | ✅ Fixed 2026-10-29 | Short rows reported, no crash. Tested with `data/edge_cases.csv` (9 valid, 5 errors). Optional: `try/except/else` |
| ├ Ex 3: `analysis.py` | ✅ Reviewed 2026-10-28 | Correct. Optional: merge the two `total_by_*` functions |
| └ Ex 4: `sales_report.py` | ✅ Done 2026-10-29 | Output matches spec exactly. Learned: format specs (`:,.2f`, `<14`, `>9`), `main()` pattern, `asdict` + `**` unpacking. JSON should store raw numbers, not `"£..."` strings |
| **Task 3**: pandas basics ([spec](02_data/TASK_3.md)) | ✅ Done (2026-11-02) | Same sales data as Task 2, in a notebook |
| ├ Ex 1: load and inspect | ✅ Done 2026-10-30 | `read_csv`, DataFrame vs Series, index, `shape`, `info`, dtypes, `NaN`, `isna().sum()` |
| ├ Ex 2: clean | ✅ Done 2026-11-02 | `to_numeric(errors="coerce")`, `.str.strip()`, boolean masks (`\|` `&` `~`), `dropna(subset=)`, `astype`, `to_datetime`. Notebook tidied, Run All works, committed (`d5c448f`) |
| ├ Ex 3: report, pandas style | ✅ Done 2026-11-02 | Column maths (vectorised), `.dt.strftime`, `groupby().sum()` (sorts groups), `nlargest`, `[[...]]` vs `[...]`, `.agg`. Fixed a `KeyError` (`price` → `unit_price`); learned to read tracebacks bottom-up. Committed `7eb09fd` |
| ├ Ex 4: charts | ✅ Done 2026-11-02 | Bar + line + seaborn charts correct; both PNGs saved. Heading and preference answer tidied; Run All 1–36 clean. Committed `a646ff1` |
| └ Ex 5: `report_pandas.py` | ✅ Done 2026-11-02 | Correct from any folder; added `to_string(float_format=...)` unprompted. Ruff: `f` on strings without `{}` (F541), lines > 88 (E501), trailing whitespace. Committed `47e33ab` |
| **Task 4**: EDA + NumPy ([spec](02_data/TASK_4.md)) | 🟡 In progress | Titanic dataset (891 rows) in `02_data/data/titanic.csv` |
| ├ Ex 1: NumPy basics | ✅ Done 2026-11-03 | NumPy ~26× faster. Fixed: Cell 1 now shows lists failing vs arrays working; multi-result cells use `print()` (a notebook shows only a cell's **last line**). Explored `min`/`argmin`/`std`/`var` unprompted. Committed `594b707`. To do: Restart → Run All once (Cell 1 has no saved output) |
| ├ Ex 2: first look | ✅ Done 2026-11-03 | All numbers match; Run All 1–8 clean. Committed `632b8d0`. Learned: `info()` prints and returns `None` (so don't put it in an f-string); use `display(df)` for tables, not `print(df)`. Tidy: fix the `info` cell, stale `'object'` comment, empty last cell |
| ├ Ex 3: spot the problems | ✅ Done 2026-11-03 | All outputs match; fresh Run All clean; `display()` used correctly. Worked example in [notes](02_data/notes/task4_ex3_problems.md): `crosstab`, `.all()`, data leakage (`alive`), `duplicated(keep=False)`, multi-column `value_counts`, keep duplicates (no ID), £0 fares, outlier ≠ error, `quantile`, `.loc`. Learned: gaps in execution numbers mean cells ran out of order, so Restart → Run All before committing. Ex 2 fixes done. Committed `6cb462d` |
| ├ Ex 4: clean | ✅ Done 2026-11-03 | All outputs match: `(891, 11)`, 0 missing, medians 37 / 29 / 24, port `S`; Run All 1–24 in order. Answers cell notes the side effect (age std 14.53 → 13.24). Worked example in [notes](02_data/notes/task4_ex4_clean.md): `drop(columns=)` returns new, `=` never copies (`.copy()`), `groupby().transform("median")` vs `.median()` (window function vs GROUP BY), `fillna` aligns by index, pandas 3 `inplace` trap, `mode()[0]`. Committed `d2f4731` |
| ├ Ex 5: ask questions | 🟡 Explained 2026-11-03 | Worked example in [notes](02_data/notes/task4_ex5_questions.md): helper function `survival_by()`, `.agg(["count", "mean"])`, `pivot_table(margins=True)`, `pd.cut(bins=, labels=)` (right edge included; `category` dtype), `observed=True`, `join(suffixes=)`, why real ages (`df_raw`) for age questions, `family_size` (feature engineering), small groups give noisy rates. To do: type in, commit |
| ├ Ex 6: charts | ⬜ To do | |
| └ Ex 7: write-up | ⬜ To do | |

## Next session: start here
1. `git pull` first (you may have worked on the other computer).
2. Finish **Task 4 Ex 5**: in `02_data/titanic_eda.ipynb`, type the cells from [02_data/notes/task4_ex5_questions.md](02_data/notes/task4_ex5_questions.md). Restart → Run All, commit, push. Learning style: worked examples with explanations.
3. Then **Ex 6** (charts) and **Ex 7** (write-up), then **"review all"**. That finishes Task 4 and Phase 2 (target: Wed 4 Nov).
4. Optional: format `report_pandas.py` with Ruff (`Shift+Alt+F`); Restart → Run All in `numpy_basics.ipynb`.

## Working on two computers
**Every session:** `git pull` at the start, then `git add .`, `git commit` and `git push` at the end. GitHub is the only sync. If you forget to push, the other computer won't have your work.

**First-time setup on a new computer:**
1. Install [Anaconda](https://www.anaconda.com/download) (or Miniconda), [Git](https://git-scm.com/download/win) and VS Code with the extensions from Task 1 (Python, Jupyter, Ruff, Data Wrangler, Rainbow CSV, Error Lens).
2. Tell Git who you are, using the same name and email as on the work PC (check there with `git config user.name` and `git config user.email`):
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```
3. Clone into a folder **outside OneDrive**, for example `C:\dev`. Don't use OneDrive and Git to sync the same folder at the same time, because they can clash and corrupt the `.git` folder.
   ```powershell
   mkdir C:\dev; cd C:\dev
   git clone https://github.com/adam-c4d/pythonllm-practise.git
   cd pythonllm-practise
   ```
   Sign in to GitHub in the browser window that opens. The repository is private.
4. Rebuild the Python environment from [environment.yml](environment.yml). It takes a few minutes.
   ```powershell
   conda init powershell        # once, then reopen the terminal
   conda env create -f environment.yml
   conda activate dsllm
   python 01_python/check_setup.py
   ```
   ✅ It should print Python 3.13 and the numpy / pandas / sklearn / fastapi versions.
5. In VS Code, open the folder, then go to **Python: Select Interpreter → dsllm**. In notebooks, use **Select Kernel → Python Environments → dsllm**.
6. Start Claude in the folder and say **"let's continue"**. It reads `CLAUDE.md` and this plan.

## Habits
- Type the code yourself; don't copy-paste.
- Commit after each exercise, and push before you leave.
- Stuck? Ask Claude for an **explanation or a worked example**.
- Use `python -m pip install ...` inside the `(dsllm)` terminal.
- If a script seems frozen the first time it uses a new library, wait 1–2 minutes before pressing `Ctrl+C`.
