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

**Tutorials and function docs for each phase:** see [Learning resources](#learning-resources) at the bottom.

## Target dates
Set 2026-11-03 for full-time study (6–8 h a day, 5–6 days a week). **Goal: start applying for AI Engineer / LLM developer jobs in late January 2027.**

| Dates | Target |
|---|---|
| Wed 4 Nov | Finish Task 4 (Ex 5–7) → **Phase 2 done** ✅ (on time) |
| 5–13 Nov | Phase 3: ML basics (scikit-learn) |
| 16–20 Nov | Phase 4: FastAPI (your Laravel experience helps most here) |
| 23 Nov – 4 Dec | Phase 5: LLMs |
| 7–18 Dec | Capstone: "Ask Your Data" API |
| 21 Dec – 1 Jan | Break / catch-up buffer |
| 4–22 Jan | Job-ready: pytest, Docker, deployment ([notes](project/notes/deployment_overview.md)), tool calling, LLM evals, GitHub and CV polish |
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
| **Task 4**: EDA + NumPy ([spec](02_data/TASK_4.md)) | ✅ Done (2026-11-04) → **Phase 2 done** | Titanic dataset (891 rows) in `02_data/data/titanic.csv`. Review all: every expected answer matches; a fresh run from scratch reproduces all 38 cell outputs exactly. Last tidy-ups are in "Next session" |
| ├ Ex 1: NumPy basics | ✅ Done 2026-11-03 | NumPy ~26× faster. Fixed: Cell 1 now shows lists failing vs arrays working; multi-result cells use `print()` (a notebook shows only a cell's **last line**). Explored `min`/`argmin`/`std`/`var` unprompted. Committed `594b707`. Clean Run All done 2026-11-04 |
| ├ Ex 2: first look | ✅ Done 2026-11-03 | All numbers match; Run All 1–8 clean. Committed `632b8d0`. Learned: `info()` prints and returns `None` (so don't put it in an f-string); use `display(df)` for tables, not `print(df)`. Tidy: fix the `info` cell, stale `'object'` comment, empty last cell |
| ├ Ex 3: spot the problems | ✅ Done 2026-11-03 | All outputs match; fresh Run All clean; `display()` used correctly. Worked example in [notes](02_data/notes/task4_ex3_problems.md): `crosstab`, `.all()`, data leakage (`alive`), `duplicated(keep=False)`, multi-column `value_counts`, keep duplicates (no ID), £0 fares, outlier ≠ error, `quantile`, `.loc`. Learned: gaps in execution numbers mean cells ran out of order, so Restart → Run All before committing. Ex 2 fixes done. Committed `6cb462d` |
| ├ Ex 4: clean | ✅ Done 2026-11-03 | All outputs match: `(891, 11)`, 0 missing, medians 37 / 29 / 24, port `S`; Run All 1–24 in order. Answers cell notes the side effect (age std 14.53 → 13.24). Worked example in [notes](02_data/notes/task4_ex4_clean.md): `drop(columns=)` returns new, `=` never copies (`.copy()`), `groupby().transform("median")` vs `.median()` (window function vs GROUP BY), `fillna` aligns by index, pandas 3 `inplace` trap, `mode()[0]`. Committed `d2f4731` |
| ├ Ex 5: ask questions | ✅ Done 2026-11-03 | All outputs match the spec. Committed `a30ecff`. Style: 2 blank lines after a function (PEP 8, Ruff E305); heading missing "Ask questions"; run number 27 skipped (re-ran a cell). Worked example in [notes](02_data/notes/task4_ex5_questions.md): helper function `survival_by()`, `.agg(["count", "mean"])`, `pivot_table(margins=True)`, `pd.cut(bins=, labels=)` (right edge included; `category` dtype), `observed=True`, `join(suffixes=)`, why real ages (`df_raw`) for age questions, `family_size` (feature engineering), small groups give noisy rates |
| ├ Ex 6: charts | ✅ Done 2026-11-04 | All 4 charts correct and saved; correlations match (−0.54 / −0.34 / +0.26). Histogram fixed to `df_raw["age"]` with `savefig`. Worked example in [notes](02_data/notes/task4_ex6_charts.md): `histplot(bins=)`, `barplot(hue=, palette={dict})` (mean of 0/1 = rate; 95% CI lines), `PercentFormatter`, box plot anatomy, `fill=False`, `astype(int)`, `corr()`, `heatmap(mask=, vmin=, vmax=)`, `.iloc`, `np.triu`, diverging colours; correlation only sees straight lines and isn't causation |
| └ Ex 7: write-up | ✅ Done 2026-11-04 | Numbers cell output matches; 5 findings + 1 limitation. Worked example in [notes](02_data/notes/task4_ex7_writeup.md): writing findings for a manager (so-what first, number + comparison, round, no column names, no causal claims), headline numbers pulled from code (`.loc`, `:.0f` vs `:.0%`), 1 limitation. Review fixes done (`savefig`, duplicate heading, import order, Run All in both notebooks). Committed `c43b0c5` |
| **Task 5**: first ML model ([spec](03_ml/TASK_5.md)) | 🟡 In progress (started 2026-11-04) | Predict Titanic survival with scikit-learn in `03_ml/titanic_model.ipynb`: split → baseline → model → metrics → leakage → pipeline → trees → cross-validation → save |
| ├ Ex 1: X, y, split, baseline | ✅ Done 2026-11-04 | All outputs match (712 / 179, 38.3% / 38.5%, 41.3% without `stratify`, baseline 61.5%); Run All 1–5 in order. Worked example in [notes](03_ml/notes/task5_ex1_split_baseline.md): ML = learning rules from examples; `fit` / `predict` / `score` (one contract for every model); `train_test_split(stratify=)`; `DummyClassifier` |
| ├ Ex 2: logistic regression | 🟡 Explained 2026-11-04 | [notes](03_ml/notes/task5_ex2_logistic_regression.md): `simple_features()` for both sets, `fit`, `predict_proba[:, 1]`, `coef_` / `intercept_`, weighted sum + sigmoid. To do: type in, commit |
| ├ Ex 3: confusion matrix, precision, recall | 🟡 Explained 2026-11-04 | [notes](03_ml/notes/task5_ex3_confusion_matrix.md): `confusion_matrix`, `classification_report`, `ConfusionMatrixDisplay`, the 0.5 cut-off trade-off |
| ├ Ex 4: data leakage | 🟡 Explained 2026-11-04 | [notes](03_ml/notes/task5_ex4_leakage.md): `alive` → fake 100%; fitting on all rows (median 28.0 vs 28.5) |
| ├ Ex 5: pipelines | 🟡 Explained 2026-11-04 | [notes](03_ml/notes/task5_ex5_pipelines.md): `Pipeline`, `ColumnTransformer`, `SimpleImputer`, `StandardScaler`, `OneHotEncoder(handle_unknown=)`, `named_steps`, learned attributes end in `_` |
| ├ Ex 6: trees, forests, overfitting | 🟡 Explained 2026-11-04 | [notes](03_ml/notes/task5_ex6_trees.md): `make_model()` + `clone`, overfitting (98% vs 82%), `max_depth`, `plot_tree`, random forest, `feature_importances_` caveat |
| ├ Ex 7: cross-validation, tuning | 🟡 Explained 2026-11-04 | [notes](03_ml/notes/task5_ex7_cross_validation.md): 5-fold `cross_val_score`, `GridSearchCV` (`model__` names), `cv_results_`, test set once at the end |
| └ Ex 8: save and load the model | 🟡 Explained 2026-11-04 | [notes](03_ml/notes/task5_ex8_save_model.md): `joblib.dump` / `load` (trust + version warnings), predict from a list of dicts, `/predict` preview |

## Next session: start here
1. `git pull` first (you may have worked on the other computer).
2. **Task 5 Ex 2–8:** all worked examples are ready in [03_ml/notes/](03_ml/notes/) (`task5_ex2_...` to `task5_ex8_...`). Type them into `03_ml/titanic_model.ipynb` in order, Restart → Run All, and commit after each exercise.
3. Ask Claude to **"check"** after any exercise, and **"review all"** at the end. Then Task 6 (regression). Phase 3 target: 5–13 Nov. Learning style: worked examples with explanations.
4. **Plan change (agreed 2026-11-04):** add **PyTorch and TensorFlow** (deep learning) to the roadmap. Local AI-agency jobs ask for them, e.g. BeeSolver Technology (Mohali): "AI/ML Engineer, Python/PyTorch, 3+ yrs". Decide with Claude where it fits (likely a short block after Phase 3) and how long it takes.
4. Optional: format `report_pandas.py` with Ruff (`Shift+Alt+F`); rename `## Exercise 5:` to `## Exercise 5: Ask questions` in `titanic_eda.ipynb`.

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

## Learning resources
Use **W3Schools** for a quick first read of a topic: short pages with a "Try it Yourself" button. Use the **official docs** when you need every parameter of a function. They are the source of truth, like laravel.com/docs. Under each subject, "Used in this project" links go straight to the official page for each function you have typed so far. All links were checked on 2026-11-04.

**Reading an official API page:** the signature is at the top, then Parameters (with defaults), Returns, and Examples at the bottom. Scroll to Examples first.

**Where each type of project is deployed:** each subject ends with a **Deployed** line. The full explanation, with Laravel comparisons, is in [project/notes/deployment_overview.md](project/notes/deployment_overview.md).

### Python (Phase 1)
- **W3Schools:** [Python tutorial](https://www.w3schools.com/python/default.asp) · [Classes](https://www.w3schools.com/python/python_classes.asp) · [List comprehension](https://www.w3schools.com/python/python_lists_comprehension.asp) · [Try/except](https://www.w3schools.com/python/python_try_except.asp) · [JSON](https://www.w3schools.com/python/python_json.asp) · [Modules](https://www.w3schools.com/python/python_modules.asp) · [Built-in functions](https://www.w3schools.com/python/python_ref_functions.asp)
- **Go deeper:** [Official Python tutorial](https://docs.python.org/3/tutorial/) · [Real Python](https://realpython.com/) (long, clear articles, one topic each) · [Standard library reference](https://docs.python.org/3/library/)
- **Used in this project:** [`@dataclass`, `asdict`](https://docs.python.org/3/library/dataclasses.html) · [`csv.DictReader`](https://docs.python.org/3/library/csv.html#csv.DictReader) · [`json.dump`](https://docs.python.org/3/library/json.html#json.dump) · [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html) · [`typing.Self`](https://docs.python.org/3/library/typing.html#typing.Self) · [`Callable`](https://docs.python.org/3/library/collections.abc.html) · [format specs (`:,.2f`, `<14`)](https://docs.python.org/3/library/string.html#format-specification-mini-language)
- **Deployed:** as scripts that run on a schedule (cron, Cloud Run Jobs, Airflow for multi-step pipelines), ≈ Laravel's scheduler. [Details](project/notes/deployment_overview.md#4-plain-python-scripts-and-data-jobs)

### Data analysis (Phase 2: NumPy, pandas, matplotlib, seaborn)
- **W3Schools:** [NumPy](https://www.w3schools.com/python/numpy/default.asp) · [pandas](https://www.w3schools.com/python/pandas/default.asp) · [pandas cleaning](https://www.w3schools.com/python/pandas/pandas_cleaning.asp) · [DataFrame reference](https://www.w3schools.com/python/pandas/pandas_ref_dataframe.asp) (every DataFrame method on one page) · [Matplotlib](https://www.w3schools.com/python/matplotlib_intro.asp) · [Data Science](https://www.w3schools.com/datascience/default.asp) · [Statistics](https://www.w3schools.com/statistics/index.php)
- **Go deeper (pick 1–2):**
  - [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) and the [pandas getting-started tutorials](https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html) (official)
  - Kaggle Learn: [Pandas](https://www.kaggle.com/learn/pandas), [Data Cleaning](https://www.kaggle.com/learn/data-cleaning), [Data Visualization](https://www.kaggle.com/learn/data-visualization). Free, short, exercises in the browser, certificate at the end
  - [Python for Data Analysis, 3rd ed.](https://wesmckinney.com/book/): free online book by Wes McKinney, who created pandas
  - [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/): free online book covering NumPy, pandas, matplotlib and scikit-learn
  - [seaborn tutorial](https://seaborn.pydata.org/tutorial.html) (official)
- **Used in this project:**
  - NumPy: [`array`](https://numpy.org/doc/stable/reference/generated/numpy.array.html) · [`mean`](https://numpy.org/doc/stable/reference/generated/numpy.mean.html) · [`nanmean`](https://numpy.org/doc/stable/reference/generated/numpy.nanmean.html) · [`std`](https://numpy.org/doc/stable/reference/generated/numpy.std.html) · [`argmin`](https://numpy.org/doc/stable/reference/generated/numpy.argmin.html) · [`where`](https://numpy.org/doc/stable/reference/generated/numpy.where.html) · [`exp`](https://numpy.org/doc/stable/reference/generated/numpy.exp.html) · [`arange`](https://numpy.org/doc/stable/reference/generated/numpy.arange.html) · [`triu`](https://numpy.org/doc/stable/reference/generated/numpy.triu.html) · [`ones_like`](https://numpy.org/doc/stable/reference/generated/numpy.ones_like.html)
  - pandas, load and inspect: [`read_csv`](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) · [`head`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.head.html) · [`info`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.info.html) · [`describe`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html) · [`shape`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.shape.html) · [`dtypes`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dtypes.html) · [`isna`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.isna.html) · [`value_counts`](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)
  - pandas, clean: [`to_numeric`](https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html) · [`to_datetime`](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html) · [`str.strip`](https://pandas.pydata.org/docs/reference/api/pandas.Series.str.strip.html) · [`dropna`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html) · [`fillna`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.fillna.html) · [`astype`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.astype.html) · [`drop`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html) · [`duplicated`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.duplicated.html) · [`copy`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.copy.html) · [`mode`](https://pandas.pydata.org/docs/reference/api/pandas.Series.mode.html)
  - pandas, select: [`loc`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html) · [`iloc`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iloc.html) · [boolean masks](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing)
  - pandas, summarise: [`groupby`](https://pandas.pydata.org/docs/user_guide/groupby.html) (guide, includes `agg` and `transform`) · [`agg`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html) · [`pivot_table`](https://pandas.pydata.org/docs/reference/api/pandas.pivot_table.html) · [`crosstab`](https://pandas.pydata.org/docs/reference/api/pandas.crosstab.html) · [`cut`](https://pandas.pydata.org/docs/reference/api/pandas.cut.html) · [`join`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html) · [`nlargest`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.nlargest.html) · [`sort_values`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html) · [`reset_index`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html) · [`quantile`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.quantile.html) · [`corr`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html) · [`dt.strftime`](https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.strftime.html)
  - matplotlib: [`figure`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.figure.html) · [`title`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.title.html) · [`xlabel`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xlabel.html) · [`ylabel`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ylabel.html) · [`savefig`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html) · [`show`](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html) · [`PercentFormatter`](https://matplotlib.org/stable/api/ticker_api.html#matplotlib.ticker.PercentFormatter)
  - seaborn: [`histplot`](https://seaborn.pydata.org/generated/seaborn.histplot.html) · [`barplot`](https://seaborn.pydata.org/generated/seaborn.barplot.html) · [`boxplot`](https://seaborn.pydata.org/generated/seaborn.boxplot.html) · [`heatmap`](https://seaborn.pydata.org/generated/seaborn.heatmap.html) · [`blend_palette`](https://seaborn.pydata.org/generated/seaborn.blend_palette.html)
- **Also common (not used yet):** [`merge`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) (≈ SQL `JOIN` on columns) · [`concat`](https://pandas.pydata.org/docs/reference/api/pandas.concat.html) · [`apply`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html) · [`map`](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html) · [`query`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html) · [`melt`](https://pandas.pydata.org/docs/reference/api/pandas.melt.html) · [`rolling`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html) · [`resample`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html) · [`to_csv`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html) · [`read_sql`](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html) · [`scatterplot`](https://seaborn.pydata.org/generated/seaborn.scatterplot.html) · [`pairplot`](https://seaborn.pydata.org/generated/seaborn.pairplot.html)
- **Other tools you'll hear about:** [Polars](https://docs.pola.rs/) (a faster pandas alternative) · [Plotly](https://plotly.com/python/) (interactive charts) · [DuckDB](https://duckdb.org/docs/) (SQL queries straight on CSV files and DataFrames)
- **Deployed:** notebooks are not deployed. The code moves into `.py` scripts that run on a schedule (as you did in Task 3 Ex 5), or into a Streamlit dashboard. [Details](project/notes/deployment_overview.md#5-notebooks-dashboards-and-demos)

### Machine learning (Phase 3: scikit-learn)
- **W3Schools:** [ML getting started](https://www.w3schools.com/python/python_ml_getting_started.asp) · [Train/test](https://www.w3schools.com/python/python_ml_train_test.asp) · [Linear regression](https://www.w3schools.com/python/python_ml_linear_regression.asp) · [Logistic regression](https://www.w3schools.com/python/python_ml_logistic_regression.asp) · [Confusion matrix](https://www.w3schools.com/python/python_ml_confusion_matrix.asp) · [Decision tree](https://www.w3schools.com/python/python_ml_decision_tree.asp) · [Bagging](https://www.w3schools.com/python/python_ml_bagging.asp) · [Cross-validation](https://www.w3schools.com/python/python_ml_cross_validation.asp) · [Grid search](https://www.w3schools.com/python/python_ml_grid_search.asp) · [Categorical data](https://www.w3schools.com/python/python_ml_preprocessing.asp) · [Scaling](https://www.w3schools.com/python/python_ml_scale.asp) · [AUC-ROC](https://www.w3schools.com/python/python_ml_auc_roc.asp)
- **Go deeper (pick 1–2):**
  - [scikit-learn MOOC](https://inria.github.io/scikit-learn-mooc/): free course by the scikit-learn team. Pipelines, cross-validation and tuning, the same path as Task 5
  - Kaggle Learn: [Intro to ML](https://www.kaggle.com/learn/intro-to-machine-learning), then [Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning) (missing values, pipelines, leakage, XGBoost)
  - [Google ML Crash Course](https://developers.google.com/machine-learning/crash-course): concepts with interactive visuals
  - [StatQuest on YouTube](https://www.youtube.com/@statquest): short videos on the maths behind each model
  - [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html) (official; long, so read only the section you need)
- **Used in this project:** [`train_test_split`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html) · [`DummyClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html) · [`LogisticRegression`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) · [`confusion_matrix`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html) · [`ConfusionMatrixDisplay`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ConfusionMatrixDisplay.html) · [`classification_report`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html) · [`precision_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html) · [`recall_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html) · [`Pipeline`](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html) · [`ColumnTransformer`](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html) · [`SimpleImputer`](https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html) · [`StandardScaler`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html) · [`OneHotEncoder`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html) · [`clone`](https://scikit-learn.org/stable/modules/generated/sklearn.base.clone.html) · [`DecisionTreeClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html) · [`plot_tree`](https://scikit-learn.org/stable/modules/generated/sklearn.tree.plot_tree.html) · [`RandomForestClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html) · [`cross_val_score`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_score.html) · [`GridSearchCV`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html) · [`joblib.dump` / `load`](https://scikit-learn.org/stable/model_persistence.html)
- **Coming next and also common:** [`LinearRegression`](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html) · [`mean_absolute_error`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html) · [`root_mean_squared_error`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.root_mean_squared_error.html) · [`r2_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html) (Task 6, regression) · [`roc_auc_score`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html) · [`StratifiedKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html) · [`RandomizedSearchCV`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html) · [`HistGradientBoostingClassifier`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html) · [`KMeans`](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
- **Other tools you'll hear about:** [XGBoost](https://xgboost.readthedocs.io/) and [LightGBM](https://lightgbm.readthedocs.io/) (gradient boosting, often the strongest models on tables) · [PyTorch](https://docs.pytorch.org/tutorials/) (deep learning, neural networks)
- **Deployed:** in two halves. Training runs offline and saves a `.joblib` file. Serving then loads it inside FastAPI (`/predict`, the most common way for scikit-learn), runs as a nightly batch job that writes predictions to a table, or uses a managed endpoint (AWS SageMaker, Google Vertex AI). [Details](project/notes/deployment_overview.md#2-machine-learning-models-scikit-learn)

### FastAPI (Phase 4)
- **W3Schools:** has **no FastAPI tutorial** (checked 2026-11-04). Related pages: [Python JSON](https://www.w3schools.com/python/python_json.asp) · [Python classes](https://www.w3schools.com/python/python_classes.asp) (Pydantic models are classes) · [requests module](https://www.w3schools.com/python/module_requests.asp) (calling an API from Python)
- **Go deeper:**
  - [FastAPI official tutorial](https://fastapi.tiangolo.com/tutorial/): the best FastAPI course there is. Short pages, runnable code. Use it as your main course for Phase 4
  - [Pydantic docs: models](https://pydantic.dev/docs/validation/latest/concepts/models/): validation (≈ Laravel Form Requests)
  - [Real Python: FastAPI](https://realpython.com/fastapi-python-web-apis/): one long article that walks through a working FastAPI app
  - [TestDriven.io FastAPI articles](https://testdriven.io/blog/topics/fastapi/): testing, Docker and deployment (useful in January)
- **What we'll use** (official tutorial pages): [first steps](https://fastapi.tiangolo.com/tutorial/first-steps/) · [path parameters](https://fastapi.tiangolo.com/tutorial/path-params/) (≈ `Route::get('/users/{id}')`) · [query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) · [request body](https://fastapi.tiangolo.com/tutorial/body/) · [response model](https://fastapi.tiangolo.com/tutorial/response-model/) (≈ API Resources) · [`HTTPException`](https://fastapi.tiangolo.com/tutorial/handling-errors/) (≈ `abort(404)`) · [`UploadFile`](https://fastapi.tiangolo.com/tutorial/request-files/) (the capstone's CSV upload) · [`Depends`](https://fastapi.tiangolo.com/tutorial/dependencies/) (≈ service container injection) · [`APIRouter`](https://fastapi.tiangolo.com/tutorial/bigger-applications/) (≈ route groups) · [`TestClient`](https://fastapi.tiangolo.com/tutorial/testing/) (≈ Laravel feature tests) · [settings from env vars](https://fastapi.tiangolo.com/advanced/settings/) (≈ `.env` + `config()`) · [CORS](https://fastapi.tiangolo.com/tutorial/cors/) · [HTTPX](https://www.python-httpx.org/) (≈ Laravel's `Http::` client)
- **Other tools you'll hear about:** [Flask](https://flask.palletsprojects.com/) (smaller and older) · [Django REST framework](https://www.django-rest-framework.org/) (closest to full Laravel) · [Litestar](https://docs.litestar.dev/latest/). FastAPI is the usual choice for AI and ML APIs
- **Deployed:** as a Docker image that uvicorn runs, usually on serverless containers (Google Cloud Run, AWS ECS Fargate, Azure Container Apps), or on Render / Railway for small projects (≈ Forge). [Details](project/notes/deployment_overview.md#1-fastapi-apis)

### LLMs (Phase 5)
- **W3Schools:** [Generative AI](https://www.w3schools.com/gen_ai/index.php) · [Prompt engineering intro](https://www.w3schools.com/gen_ai/gen_ai_prompt_intro.php) · [Text-to-text prompts](https://www.w3schools.com/gen_ai/gen_ai_prompt_text-to-text_intro.php). These are short and about using chat apps, with no Python API code. Good for the vocabulary only
- **Go deeper (pick 1–2):**
  - [Claude docs](https://platform.claude.com/docs/en/home) (official): API, prompting, tool use, structured output, evals
  - [Anthropic courses on GitHub](https://github.com/anthropics/courses): free Jupyter notebooks on API basics, prompt engineering, real-world prompting, prompt evaluations and tool use
  - [DeepLearning.AI courses](https://www.deeplearning.ai/courses/): filter by "Short Courses" for free 1–2 hour video courses on RAG, agents, function calling and evals
  - [Hugging Face LLM course](https://huggingface.co/learn/llm-course/chapter1/1): how transformers work, open-source models
  - [Prompt Engineering Guide](https://www.promptingguide.ai/): a catalogue of prompting techniques
- **What we'll use:** [get started](https://platform.claude.com/docs/en/get-started) · [Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) · [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) · [streaming](https://platform.claude.com/docs/en/build-with-claude/streaming) · [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) (JSON that fits a schema) · [tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) (function calling) · [embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) (the base of RAG) · [evals](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) · [Ollama](https://docs.ollama.com/) (free local models)
- **Other tools you'll hear about:** [OpenAI API](https://developers.openai.com/api/docs) (another provider, same ideas) · [LangChain](https://docs.langchain.com/) and [LlamaIndex](https://developers.llamaindex.ai/python/framework/) (frameworks for RAG and agents) · [Pydantic AI](https://pydantic.dev/docs/ai/overview/) (agents with Pydantic models) · [Chroma](https://docs.trychroma.com/docs/overview/introduction) and [pgvector](https://github.com/pgvector/pgvector) (vector databases; pgvector stores embeddings inside Postgres)
- **Deployed:** as a FastAPI app that calls a hosted model's API (Anthropic or OpenAI directly, or through AWS Bedrock, Azure or Google Vertex AI), plus a vector database, a queue for slow jobs and tracing. Companies rarely host the model themselves; when they do, it runs on GPU servers with vLLM. [Details](project/notes/deployment_overview.md#3-llm-apps-the-ai-engineer-job-youre-aiming-for)

### Deployment (January: job-ready)
- **W3Schools:** has **no Docker tutorial** (checked 2026-11-04). Related: [Git](https://www.w3schools.com/git/default.asp) · [AWS Cloud Practitioner](https://www.w3schools.com/aws/index.php) (cloud vocabulary)
- **Go deeper:**
  - [FastAPI deployment guide](https://fastapi.tiangolo.com/deployment/) and [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/) (official)
  - [Docker: get started](https://docs.docker.com/get-started/), then [Docker's Python guide](https://docs.docker.com/guides/python/)
  - [GitHub Actions: build and test Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python): CI that runs Ruff and pytest on every push
  - [pytest: get started](https://docs.pytest.org/en/stable/getting-started.html) (≈ PHPUnit)
- **Where to put the capstone:** [Render: deploy FastAPI](https://render.com/docs/deploy-fastapi) (easiest) · [Google Cloud Run quickstart](https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) (how companies do it; the example uses Flask, the steps are the same) · [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces) with [Streamlit](https://docs.streamlit.io/) or [Gradio](https://www.gradio.app/guides/quickstart) (a free demo page a recruiter can click) · [MLflow](https://mlflow.org/docs/latest/) (model registry, for later)
