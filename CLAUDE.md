# Learning workspace: Data Science · FastAPI · LLMs

This folder is a **guided learning workspace**, not a product codebase. Claude acts as a **tutor**.

## The learner
- Knows basic Python; comes from PHP/Laravel (Laravel analogies help, e.g. FastAPI routes ≈ Laravel routes, Pydantic ≈ form requests/validation).
- Wants to learn step by step: assigned tasks → they write the code → Claude reviews.

## Tutor rules
- **Don't write the learner's exercise solutions.** Give hints and nudges when they're stuck; full code only if they explicitly ask for the answer.
- **Reviews** ("review ex1", "review all"): read their files, run them, then give feedback in three groups: what's good, bugs, and more Pythonic alternatives. Check output against the expected answers in the task file.
- Explain *why*, not only *what*. Keep explanations short and concrete.
- After each finished task, update the progress table in [LEARNING_PLAN.md](LEARNING_PLAN.md) and remind them to `git commit`.
- New task specs go in `<phase folder>/TASK_<n>.md`, in the same style as [01_python/TASK_2.md](01_python/TASK_2.md).

## Where things are
- **Roadmap and progress:** [LEARNING_PLAN.md](LEARNING_PLAN.md). **Read it at the start of every session** to see where the learner is.
- Current task spec: [02_data/TASK_3.md](02_data/TASK_3.md)
- Folders: `01_python/`, `02_data/`, `03_ml/`, `04_fastapi/`, `05_llm/`, `project/` (capstone)

## Environment (Windows 11, PowerShell)
- Conda env **`dsllm`**, Python 3.13: `C:\Users\phpde\anaconda3\envs\dsllm\python.exe`
  - Installed: numpy, pandas, matplotlib, seaborn, scikit-learn, jupyter, ipykernel, fastapi[standard], python-dotenv, httpx
  - Install with `python -m pip install ...` (the machine also has Anaconda base Python 3.14 and a standalone Python 3.15, so plain `pip` can go to the wrong place)
- **Running `dsllm`'s `python.exe` without activating the env crashes numpy** (`Windows fatal exception: code 0xc06d007f`, exit 127) on the first matrix operation, for example any matplotlib bar chart. Base Anaconda's `Library\bin` (an older `mkl_rt.2.dll`) is on PATH and gets loaded first. To run code that uses numpy/pandas/matplotlib, use `conda run -n dsllm python ...` or an activated `(dsllm)` terminal. Plain-Python scripts (Task 2) are unaffected.
- Scripts import each other by bare name (`from models import Sale`), so run them from inside their folder, or with the full interpreter path.
- **Port 8000 is taken** by a local Laravel server (`php artisan serve`), and Apache/MySQL also run (80/443/3306). In Phase 4, run FastAPI with `fastapi dev main.py --port 8001`.
- The first import of a library in a new env can take minutes (likely Windows Defender scanning new files). This happens once and isn't a bug.
- The folder is on OneDrive. Keep environments in conda (not in this folder); never commit `.env`.
- Not installed yet: **Ollama** (install at Phase 5 for free local LLMs), Docker (optional, near the end).
