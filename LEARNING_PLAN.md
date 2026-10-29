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
| **Task 2**: Python for data work ([spec](01_python/TASK_2.md)) | 🟡 In progress | |
| ├ Ex 1: `models.py` | ✅ Fixed 2026-10-29 | Category stripped; `from_row` checks all `FIELDS` (`None`/blank → `ValueError`). Optional: `frozen=True`, `Self` |
| ├ Ex 2: `loader.py` | ✅ Fixed 2026-10-29 | Short rows reported, no crash. Tested with `data/edge_cases.csv` (9 valid, 5 errors). Optional: `try/except/else` |
| ├ Ex 3: `analysis.py` | ✅ Reviewed 2026-10-28 | Correct. Optional: merge the two `total_by_*` functions |
| └ Ex 4: `sales_report.py` | ⬜ To do | File created but empty |
| Task 3: Phase 2, pandas & EDA | ⬜ Not started | |

## Next session: start here
1. ~~Fix the 2 bugs from the Ex 1–3 review~~ ✅ Done 2026-10-29.
2. Write Exercise 4 (`sales_report.py`). The expected output is in [01_python/TASK_2.md](01_python/TASK_2.md).
3. Ask Claude to **"review ex4"**.
4. Then ask for **Task 3** (pandas). You'll redo this whole report in about 10 lines.

## Habits
- Type the code yourself; don't copy-paste.
- Commit after each exercise.
- Stuck for more than 20 minutes? Ask for a **hint**, not the answer.
- Use `python -m pip install ...` inside the `(dsllm)` terminal.
- If a script seems frozen the first time it uses a new library, wait 1–2 minutes before pressing `Ctrl+C`.
