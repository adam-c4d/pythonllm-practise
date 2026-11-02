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

## Progress

| Task | Status | Notes |
|---|---|---|
| **Task 1**: Environment setup | ✅ Done (2026-10-27) | Conda env `dsllm` (Python 3.13), VS Code extensions, Git, folders, first commit |
| **Task 2**: Python for data work ([spec](01_python/TASK_2.md)) | ✅ Done (2026-10-29) | Optional improvements done 2026-10-30 (`frozen`, `Self`, `try/else`, `total_by`) |
| ├ Ex 1: `models.py` | ✅ Fixed 2026-10-29 | Category stripped; `from_row` checks all `FIELDS` (`None`/blank → `ValueError`). Optional: `frozen=True`, `Self` |
| ├ Ex 2: `loader.py` | ✅ Fixed 2026-10-29 | Short rows reported, no crash. Tested with `data/edge_cases.csv` (9 valid, 5 errors). Optional: `try/except/else` |
| ├ Ex 3: `analysis.py` | ✅ Reviewed 2026-10-28 | Correct. Optional: merge the two `total_by_*` functions |
| └ Ex 4: `sales_report.py` | ✅ Done 2026-10-29 | Output matches spec exactly. Learned: format specs (`:,.2f`, `<14`, `>9`), `main()` pattern, `asdict` + `**` unpacking. JSON should store raw numbers, not `"£..."` strings |
| **Task 3**: pandas basics ([spec](02_data/TASK_3.md)) | 🟡 In progress | Same sales data as Task 2, in a notebook |
| ├ Ex 1: load and inspect | ✅ Done 2026-10-30 | `read_csv`, DataFrame vs Series, index, `shape`, `info`, dtypes, `NaN`, `isna().sum()` |
| ├ Ex 2: clean | ✅ Done 2026-11-02 | `to_numeric(errors="coerce")`, `.str.strip()`, boolean masks (`\|` `&` `~`), `dropna(subset=)`, `astype`, `to_datetime`. Run All works (checked 2026-11-02). Tidy-up: delete the 5 duplicate cells |
| ├ Ex 3: report, pandas style | ⬜ To do | |
| ├ Ex 4: charts | ⬜ To do | |
| └ Ex 5: `report_pandas.py` | ⬜ To do | |
| Task 4: explore a real dataset (EDA) + NumPy basics | ⬜ Not started | |

## Next session: start here
1. Tidy the notebook (see the Ex 2 note), then **Restart → Run All** to check it runs top to bottom.
2. Ask Claude for **"Ex 3"** (the report, pandas style). Learning style: worked examples with explanations.
3. Then Ex 4 (charts) and Ex 5 (`report_pandas.py`). Commit after each one.

## Habits
- Type the code yourself; don't copy-paste.
- Commit after each exercise.
- Stuck for more than 20 minutes? Ask for a **hint**, not the answer.
- Use `python -m pip install ...` inside the `(dsllm)` terminal.
- If a script seems frozen the first time it uses a new library, wait 1–2 minutes before pressing `Ctrl+C`.
