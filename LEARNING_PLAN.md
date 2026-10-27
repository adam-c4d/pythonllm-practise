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
| ├ Ex 1: `models.py` | ✅ Written, output correct | Not reviewed yet |
| ├ Ex 2: `loader.py` | ✅ Written, output correct | 10 sales / 2 errors. Not reviewed yet |
| ├ Ex 3: `analysis.py` | ✅ Written, output correct | All totals match. Not reviewed yet |
| └ Ex 4: `sales_report.py` | ⬜ To do | File created but empty |
| Task 3: Phase 2, pandas & EDA | ⬜ Not started | |

## Next session: start here
1. Commit Exercises 1–3 (they aren't committed yet):
   `git add . ; git commit -m "Ex1-3: Sale model, loader, analysis"`
2. Ask Claude: **"review ex1-3"** to get feedback on what you've written.
3. Write Exercise 4 (`sales_report.py`). The expected output is in [01_python/TASK_2.md](01_python/TASK_2.md).
4. Then ask for **Task 3** (pandas). You'll redo this whole report in about 10 lines.

## Habits
- Type the code yourself; don't copy-paste.
- Commit after each exercise.
- Stuck for more than 20 minutes? Ask for a **hint**, not the answer.
- Use `python -m pip install ...` inside the `(dsllm)` terminal.
- If a script seems frozen the first time it uses a new library, wait 1–2 minutes before pressing `Ctrl+C`.
