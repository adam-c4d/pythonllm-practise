# Task 9, Exercise 1: Load the model once: lifespan and `/health` (worked example)

Make a new folder `04_fastapi/task9/` and a file `main.py` in it (finished file: [examples/task9/ex1/main.py](../examples/task9/ex1/main.py)). The outputs below are real (run on 2026-11-23).

**You need the model file first:** `03_ml/models/diamond_price_model.joblib`, made by Task 6 Exercise 8. Check it's there:
```powershell
dir ..\..\03_ml\models
```
(run from inside `04_fastapi/task9/`). You should see `diamond_price_model.joblib`, about 566 KB.

**The idea:** loading a model is slow (reading a file, rebuilding Python objects), and predicting is fast. So you load it **once, when the server starts**, keep it in memory, and every request reuses it. Loading it inside the route would reload it for every request.

- **Laravel analogy:** a service provider's `register()` binding a **singleton**. It's built once at boot, then every controller gets the same object from the container.

## Step 1: `main.py`

```python
import time
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[2]  # the repo folder
MODEL_FILE = ROOT / "03_ml" / "models" / "diamond_price_model.joblib"

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.perf_counter()
    ml_models["price"] = joblib.load(MODEL_FILE)
    seconds = time.perf_counter() - start
    print(f"Loaded {MODEL_FILE.name} in {seconds:.2f} s")
    yield
    ml_models.clear()
    print("Model unloaded")


app = FastAPI(title="Diamond Price API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str | bool]:
    loaded = "price" in ml_models
    return {"status": "ok" if loaded else "no model", "model_loaded": loaded}
```

Start it, in an activated `(dsllm)` terminal:
```powershell
cd 04_fastapi/task9
fastapi dev main.py --port 8001
```
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [4580] using WatchFiles
INFO:     Started server process [17440]
INFO:     Waiting for application startup.
Loaded diamond_price_model.joblib in 1.18 s
INFO:     Application startup complete.
```
This log is put together from 2 runs: the `INFO` lines are from `fastapi dev`, and the `Loaded ...` line is from running the app with `TestClient` (Exercise 6). Where that line lands, your process numbers and the seconds will differ. **The very first start can take much longer** (17.32 s on my first run), because Windows Defender scans scikit-learn's files the first time they're loaded. It's 1–2 s after that.

```http
GET http://127.0.0.1:8001/health
```
```
200 OK
{
  "status": "ok",
  "model_loaded": true
}
```
Press **Ctrl+C** and the terminal prints `Model unloaded`.

## Why each part works

- **`Path(__file__).resolve().parents[2]`** finds the repo folder from this file's own location: `parents[0]` is `task9/`, `[1]` is `04_fastapi/`, `[2]` is the repo. So the path works whatever folder your terminal is in. It's Laravel's `base_path('03_ml/models/...')`. (The files in `examples/task9/exN/` sit 2 folders deeper, so they use `parents[4]`.)
- **`ROOT / "03_ml" / ...`**: `/` joins path parts on a `Path`, with the right separator for Windows.
- **`ml_models = {}`** is a module-level dict: one shared place for loaded models. A dict (rather than a plain variable) means the lifespan can fill it and the routes can read it, without the `global` keyword. Later you could hold several models: `ml_models["price"]`, `ml_models["survival"]`.
- **`lifespan`** is the start-up and shut-down hook:
  - Code **before `yield`** runs once when the server starts, before the first request.
  - **`yield`** is where the server runs and answers requests (for hours or days).
  - Code **after `yield`** runs once on shutdown (Ctrl+C). Here it frees the model. In a real app you'd close database connections there.
- **`@asynccontextmanager`** turns that one function with a `yield` into the "start / stop" object FastAPI expects. You don't need to understand `async` yet: copy this shape. FastAPI's docs use the same pattern.
- **`FastAPI(..., lifespan=lifespan)`** plugs the hook in.
- **`time.perf_counter()`** is a precise stopwatch (you used it in Task 2). The difference of 2 readings = seconds taken.
- **`/health`** is a standard endpoint for servers. Docker, Render and Kubernetes call it every few seconds to check the app is alive and ready. It returns `"model_loaded": false` if loading failed, which matters from Exercise 4 on.
- **`dict[str, str | bool]`**: the values are a string or a bool. FastAPI uses this return type to check and document the reply.

## What if the model file is missing?

In this version the server **doesn't start**. `joblib.load` raises an error inside the lifespan, and the log ends with:
```
FileNotFoundError: [Errno 2] No such file or directory: '...\\03_ml\\models\\diamond_price_model.joblib'
...
ERROR:    Application startup failed. Exiting.
```
Exercise 4 makes the server start anyway and answer **503** instead.

## Recap
- Load the model **once** in a `lifespan` function (before `yield`) ≈ a singleton bound in a service provider.
- Store it in a module-level dict (`ml_models`) that routes can read.
- `/health` tells servers (and you) whether the app is ready.
- Paths built from `Path(__file__)` work from any terminal folder.

📚 **Learn more:** [FastAPI: Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) · [`asynccontextmanager`](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager) · [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html) · [joblib model persistence](https://scikit-learn.org/stable/model_persistence.html)
