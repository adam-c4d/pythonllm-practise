# Setup: everything to install for this course

Follow this on **any computer** (for example your home PC) to get the same setup as the work PC. Every step was done on the work PC on 2026-11-05 with the versions shown. Run the commands in **PowerShell**, in the repo folder, unless a step says otherwise.

| What | Why | Needed from | Download size |
|---|---|---|---|
| Git, VS Code, Anaconda | the basics (Task 1) | now | — |
| The `dsllm` conda env | Python 3.13 + all libraries | now | about 1.5 GB |
| PyTorch (CPU) | deep learning (Task 7) | Phase 3 | about 200 MB (inside the env) |
| `openai`, `pytest` | LLM client (Phase 5), tests (Task 8) | Phase 4 | small (inside the env) |
| Ollama | runs LLMs on your own PC, free | Phase 5 + project `/ask` | about 1.2 GB |
| `qwen2.5:1.5b` | the course's chat model | Phase 5 | 986 MB |
| `nomic-embed-text` | embeddings for RAG (Task 12) | Phase 5 | 274 MB |
| `qwen2.5:3b` (optional) | better answers, about 2× slower | Phase 5 | 1.9 GB |
| Docker Desktop | containers (January) | January | later |

**Hardware:** 8 GB of RAM is enough for `qwen2.5:1.5b`. No graphics card is needed: everything runs on the CPU. Keep about 10 GB of disk free.

---

## Step 1: Get the latest code
```powershell
cd C:\dev\pythonllm-practise     # or wherever you cloned it
git pull
```
First time on this computer? Follow **"First-time setup on a new computer"** in [LEARNING_PLAN.md](LEARNING_PLAN.md#working-on-two-computers) first (Anaconda, Git, VS Code, `git clone`).

## Step 2: Create or update the Python environment
[environment.yml](environment.yml) lists every library, including PyTorch (CPU build), `openai` and `pytest`.

**If `dsllm` doesn't exist yet on this computer:**
```powershell
conda env create -f environment.yml
```
**If `dsllm` already exists** (you made it earlier in the course), add the new libraries:
```powershell
conda env update -n dsllm -f environment.yml
```
It takes a few minutes. PyTorch is the big one (about 200 MB).

**If conda's update fails**, install the 3 new libraries with pip instead, in an activated terminal:
```powershell
conda activate dsllm
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install openai pytest
```
- Always use `python -m pip`, not plain `pip`, so the libraries go into `dsllm` and not into another Python on the PC.
- `--index-url .../whl/cpu` gets the **CPU-only** PyTorch build. The default download can include GPU (CUDA) files you don't need, several GB of them.

## Step 3: Install Ollama
Ollama runs LLMs locally: no API key, no cost, and your data stays on your PC. It also offers an **OpenAI-compatible API** at `http://127.0.0.1:11434/v1`, so the course code uses the standard `openai` package, and switching to a paid provider later is a config change.

```powershell
winget install --id Ollama.Ollama -e
```
If `winget` isn't available, download the installer from [ollama.com/download/windows](https://ollama.com/download/windows) and run it.

- After installing, **close and reopen the terminal** so the `ollama` command is found.
- Ollama starts by itself with Windows (a llama icon in the system tray) and runs a small server on port **11434**. To free RAM when you're not using it, right-click the tray icon → **Quit Ollama**. Start it again from the Start menu.

Check it:
```powershell
ollama --version
curl.exe http://127.0.0.1:11434/api/version
```
✅ Expected (work PC): `ollama version is 0.40.14` and `{"version":"0.40.14"}`. A newer version is fine.

In PowerShell, use `curl.exe` and not `curl`: in Windows PowerShell 5.1, `curl` is a different command (`Invoke-WebRequest`).

## Step 4: Download the models
```powershell
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
ollama pull qwen2.5:3b        # optional: better answers, slower, needs more RAM
ollama list
```
- **`qwen2.5:1.5b`** is the course's chat model: a small LLM (1.5 billion parameters) that handles chat, JSON output and tool calling. On the work PC (6-core i5, 8 GB RAM) a short answer takes a few seconds.
- **`nomic-embed-text`** turns text into vectors for search (RAG, Task 12). It can't chat.
- Models are stored outside the repo (in `C:\Users\<you>\.ollama\models`), so they're **never committed to Git**.

Try a model in the terminal (type `/bye` to leave):
```powershell
ollama run qwen2.5:1.5b "Explain a random forest in one sentence."
```

## Step 5: Check everything
In an activated terminal, from the repo folder:
```powershell
conda activate dsllm
python 01_python/check_setup.py
```
✅ Expected (work PC, 2026-11-05):
```
Python: 3.13.17
Interpreter: C:\Users\phpde\anaconda3\envs\dsllm\python.exe
numpy      2.5.4
pandas     3.1.0
sklearn    1.9.1
matplotlib 3.11.2
seaborn    0.13.2
fastapi    0.162.0
torch      2.15.0+cpu
openai     3.46.0
pytest     9.2.0
Ollama     running, models: qwen2.5:1.5b
```
Once you've downloaded all the models, the last line lists them all. Slightly newer version numbers are fine. A `MISSING` line means Step 2 didn't finish, and `Ollama not running` means Ollama is closed or not installed (Step 3).

## Ports used by the course
| Port | What |
|---|---|
| 8000 | your Laravel app (`php artisan serve`), so the course never uses it |
| 8001 | practice APIs in Phase 4 (`fastapi dev main.py --port 8001`) |
| 8002 | the capstone project API (`fastapi dev app/main.py --port 8002`) |
| 11434 | Ollama |

## Later: Docker (January, not yet)
Docker Desktop is needed only for the January "job-ready" block (packaging the project for deployment). Don't install it yet; that step will have its own instructions.

## Troubleshooting
- **`ollama` is not recognized:** close and reopen the terminal (or VS Code) after installing.
- **Python crashes with `Windows fatal exception: code 0xc06d007f`:** you ran the env's `python.exe` without activating it. Use `conda activate dsllm` first (see CLAUDE.md).
- **`Connection refused` on port 11434:** Ollama isn't running. Start it from the Start menu.
- **Answers are very slow, or the PC freezes:** close other heavy programs, or stay with `qwen2.5:1.5b` instead of `3b`.
- **`conda env update` is very slow:** use the pip commands in Step 2 instead.
