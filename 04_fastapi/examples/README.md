# Phase 4 examples: reference solutions

These folders hold the **finished code of every exercise** in Tasks 8 and 9. They are reference solutions: **type your own version first** in `04_fastapi/task8/` and `04_fastapi/task9/`, following the worked examples in [../notes/](../notes/). Open a file here only to compare, or when you're stuck.

Each `exN/` folder is complete on its own: it holds every file **as it is after that exercise**, so you can run any stage.

```
examples/
├── task8/              ← Task 8: diamond shop API (spec: ../TASK_8.md)
│   ├── ex1/  main.py                          first app, /grades
│   ├── ex2/  main.py                          path + query parameters
│   ├── ex3/  main.py, try_models.py           Pydantic bodies, response_model
│   ├── ex4/  main.py, try_models.py           PATCH, DELETE, 404
│   ├── ex5/  main.py, try_models.py           dependencies, API key
│   ├── ex6/  + test_main.py                   pytest (8 tests)
│   └── ex7/  main.py, config.py, schemas.py,  settings + APIRouter
│             dependencies.py, diamonds.py,
│             test_main.py, try_models.py
└── task9/              ← Task 9: serve the diamond price model (spec: ../TASK_9.md)
    ├── ex1/  main.py                          lifespan + /health
    ├── ex2/  main.py, schemas.py              POST /predict
    ├── ex3/  + time_batch.py                  POST /predict/batch, timing
    ├── ex4/  main.py, schemas.py, time_batch.py   422s, MODEL_PATH, 503
    ├── ex5/  main.py, schemas.py, time_batch.py   POST /summary (CSV upload)
    └── ex6/  + test_main.py                   pytest (7 tests)
```

## How to run one

Always in an activated **`(dsllm)`** terminal, from **inside** the exercise folder (the files import each other by bare name, `from schemas import ...`):
```powershell
cd 04_fastapi/examples/task8/ex5
fastapi dev main.py --port 8001
```
Open http://127.0.0.1:8001/docs. **Never use port 8000**: Laravel uses it. Stop with Ctrl+C. Run only one example server at a time (on Windows, a second server on the same port can start without an error, and then you can't tell which one answers).

| What | Where | Command (in that folder) |
|---|---|---|
| the API | any `exN/` | `fastapi dev main.py --port 8001` |
| Pydantic outside FastAPI | `task8/ex3`–`ex7` | `python try_models.py` |
| the tests | `task8/ex6`, `task8/ex7`, `task9/ex6` | `pytest -q` (no server needed) |
| batch vs single timing | `task9/ex3`–`ex6` | start the server first, then in a second terminal `python time_batch.py` |
| settings demo | `task8/ex7` | `$env:SHOP_NAME = "Mohali Diamonds"; $env:API_KEY = "some-long-key"`, then start the server |
| missing-model demo | `task9/ex4`–`ex6` | `$env:MODEL_PATH = "missing.joblib"`, then start the server; `Remove-Item Env:MODEL_PATH` afterwards |

Expected results: `pytest -q` prints `8 passed` (Task 8) and `7 passed` (Task 9).

## The only difference from your own files: paths in Task 9

Task 9 loads `03_ml/models/diamond_price_model.joblib` (and `time_batch.py` reads `03_ml/data/diamonds.csv`). The path is computed from the file's own location, so it works from any terminal folder:

| File | Line |
|---|---|
| your `04_fastapi/task9/main.py` and `time_batch.py` | `ROOT = Path(__file__).resolve().parents[2]  # the repo folder` |
| `examples/task9/exN/main.py` and `time_batch.py` | `ROOT = Path(__file__).resolve().parents[4]  # the repo folder` |

The examples sit 2 folders deeper (`examples/task9/exN/` instead of `task9/`), so they go up 4 folders instead of 2. Everything else is the same as in the notes.

**Task 9 needs the model file.** It's created by Task 6 Exercise 8 (`03_ml/diamond_prices.ipynb`). Without it, the ex1–ex3 servers stop at start-up with `FileNotFoundError`, and from ex4 on `/health` says `"model_loaded": false` and `/predict` answers **503**.

## Good to know
- **The data in Task 8 lives in memory.** Every restart (and every auto-reload after a save) brings back the original 5 diamonds.
- **Running Python creates `__pycache__/` folders** (and pytest a `.pytest_cache/`, which ignores itself). Your `.gitignore` is still switched off, so `git status` will list `__pycache__/`. Delete those folders before committing, or un-comment the `__pycache__/` line in `.gitignore`.
- **[../ruff.toml](../ruff.toml)** tells Ruff that `main`, `schemas`, `config`, `dependencies` and `diamonds` are your own modules, so Shift+Alt+O sorts them into their own import block.
- **Never put a real secret in these files or in a committed `.env`.** `dev-secret` is a placeholder for learning.
