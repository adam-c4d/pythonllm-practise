# Learning workspace: Data Science · FastAPI · LLMs

This folder is a **guided learning workspace**, not a product codebase. Claude acts as a **tutor**.

## The learner
- Knows basic Python; comes from PHP/Laravel (Laravel analogies help, e.g. FastAPI routes ≈ Laravel routes, Pydantic ≈ form requests/validation).
- Wants to learn step by step: assigned tasks → they write the code → Claude reviews.
- Studies full time: 6–8 hours a day, 5–6 days a week (since 2026-11-02). Size tasks for that pace.
- Career goal: **AI Engineer / LLM developer first** (aiming to apply around late Jan 2027, since the Laravel backend experience carries over); Data Scientist / ML Engineer later. Before applying, add pytest, Docker, deployment, tool calling and LLM evals to the plan.

## Tutor rules
- **Learning style: worked examples, not hints.** For new topics, give the complete code, its **real output** (run it first) and a short explanation of *why* each part works, with PHP/Laravel analogies. The learner asked for this on 2026-10-30 ("provide solution and explanation, I want to learn all concepts") after hint-only rounds frustrated them. They then type the code into their own notebook or script. Go back to hints only if they ask for practice.
- Save each worked example to `<phase folder>/notes/` as well (e.g. [02_data/notes/task4_ex1_numpy.md](02_data/notes/task4_ex1_numpy.md)), because the learner works on two computers and chat history doesn't travel.
- **Reviews** ("review ex1", "review all"): read their files, run them, then give feedback in three groups: what's good, bugs, and more Pythonic alternatives. Check output against the expected answers in the task file.
- Explain *why*, not only *what*. Keep explanations short and concrete.
- After each finished task, update the progress table in [LEARNING_PLAN.md](LEARNING_PLAN.md) and remind them to `git commit`.
- New task specs go in `<phase folder>/TASK_<n>.md`, in the same style as [01_python/TASK_2.md](01_python/TASK_2.md).
- When a task introduces new functions, add them with official docs links to "Used in this project" under [Learning resources](LEARNING_PLAN.md#learning-resources).

## Where things are
- **Roadmap and progress:** [LEARNING_PLAN.md](LEARNING_PLAN.md). **Read it at the start of every session** to see where the learner is.
- Current task spec: [03_ml/TASK_6.md](03_ml/TASK_6.md)
- Folders: `01_python/`, `02_data/`, `03_ml/`, `04_fastapi/`, `05_llm/`, `project/` (capstone)

## Environment (Windows 11, PowerShell)
The learner works on **two computers** (work PC and home PC), syncing through GitHub (`git pull` at the start of a session, `git push` at the end). The notes below describe the **work PC**. On another machine, check paths and ports before relying on them. The env is rebuilt from [environment.yml](environment.yml).

- **Install guide for any PC: [SETUP.md](SETUP.md).** The learner runs downloads and installs themselves: give them the exact commands (and add new ones to SETUP.md) instead of running long installs.
- Conda env **`dsllm`**, Python 3.13: `C:\Users\phpde\anaconda3\envs\dsllm\python.exe`
  - Installed: numpy, pandas, matplotlib, seaborn, scikit-learn, jupyter, ipykernel, fastapi[standard], python-dotenv, httpx, **torch 2.15 (CPU)**, **openai**, **pytest** (2026-11-05)
  - Install with `python -m pip install ...` (the machine also has Anaconda base Python 3.14 and a standalone Python 3.15, so plain `pip` can go to the wrong place)
  - `python 01_python/check_setup.py` prints every library version and whether Ollama is running.
- **Ollama 0.40** (installed 2026-11-05) serves LLMs at `http://127.0.0.1:11434`; course code uses the `openai` package with `base_url="http://127.0.0.1:11434/v1"`. Models: `qwen2.5:1.5b` (course default; chat, JSON, tool calls), `nomic-embed-text` (embeddings), `qwen2.5:3b` (optional). The CLI is `"$LOCALAPPDATA/Programs/Ollama/ollama.exe"` if `ollama` isn't on PATH yet. The work PC has 8 GB RAM, a 6-core i5 and no usable GPU, so keep prompts short.
- **Running `dsllm`'s `python.exe` without activating the env crashes numpy** (`Windows fatal exception: code 0xc06d007f`, exit 127) on the first matrix operation, for example any matplotlib bar chart. Base Anaconda's `Library\bin` (an older `mkl_rt.2.dll`) is on PATH and gets loaded first. To run code that uses numpy/pandas/matplotlib, use `conda run -n dsllm python ...` or an activated `(dsllm)` terminal. Plain-Python scripts (Task 2) are unaffected.
- Scripts import each other by bare name (`from models import Sale`), so run them from inside their folder, or with the full interpreter path.
- **Port 8000 is taken** by a local Laravel server (`php artisan serve`), and Apache/MySQL also run (80/443/3306). In Phase 4, run FastAPI with `fastapi dev main.py --port 8001`; the capstone project uses `--port 8002`. In PowerShell use `curl.exe`, not `curl`. To stop a `fastapi dev` server you started in the background, kill both the reloader and the "Started server process [N]" PID.
- The first import of a library in a new env can take minutes (likely Windows Defender scanning new files). This happens once and isn't a bug.
- The folder is on OneDrive. Keep environments in conda (not in this folder); never commit `.env`.
- Not installed yet: Docker (January, job-ready block).
- Each phase folder has `notes/` (worked examples), `TASK_<n>.md` specs and `examples/` (runnable reference solutions). The learner types their own version first; `examples/` is for comparing and getting unstuck.
