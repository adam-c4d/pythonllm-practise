# Task 9: Serve the diamond price model (Phase 4)

**Goal:** put your Task 6 model behind a FastAPI app: load it once at start-up, predict one diamond or a batch, return honest errors (422 for bad input, 503 when the model is missing), summarise an uploaded CSV, and test it all with pytest.

**Why it matters:** "a model behind an API" is the core of most AI Engineer jobs. The capstone ("Ask Your Data" API) starts from this code: `/summary` is built here, and `/ask` (an LLM) comes in Phase 5.

**Before you start:** you need `03_ml/models/diamond_price_model.joblib`, made by Task 6 Exercise 8 (`03_ml/diamond_prices.ipynb`).

**Laravel → FastAPI for this task:**

| Laravel | FastAPI |
|---|---|
| a singleton bound in a service provider's `register()` | load the model in a `lifespan` function (before `yield`) |
| `base_path('03_ml/...')` | `Path(__file__).resolve().parents[2] / "03_ml" / ...` |
| `Product::insert([...])` instead of many `create()` calls | `POST /predict/batch` with a `list[DiamondIn]` body |
| `'items' => 'array\|min:1\|max:1000'` | `Body(min_length=1, max_length=1000)` |
| `php artisan down` → 503 | a `get_model` dependency that raises `HTTPException(503)` |
| `env('MODEL_PATH', ...)` | `os.getenv("MODEL_PATH", default)` |
| `$request->file('file')` + `mimes:csv` | `file: UploadFile` + a `.csv` check |
| `Http::post(...)` | `httpx.Client().post(...)` |
| `setUp()` / Pest `beforeEach` | a `@pytest.fixture` |
| `config([...])` inside one test | `monkeypatch.setenv(...)` |

```
04_fastapi/
├── TASK_9.md
├── task9/              ← you make this folder and type your code here
│   ├── main.py         ← Exercises 1–5
│   ├── schemas.py      ← Exercises 2–5
│   ├── time_batch.py   ← Exercise 3
│   └── test_main.py    ← Exercise 6
├── notes/              ← worked examples (task9_ex1_... to task9_ex6_...)
└── examples/task9/     ← the finished code after each exercise (ex1/ to ex6/)
```

**How to run it:** in a `(dsllm)` terminal, `cd 04_fastapi/task9`, then `fastapi dev main.py --port 8001` and open http://127.0.0.1:8001/docs. Port 8001, as in Task 8 (Laravel uses 8000).

**The model's 6 inputs:** `carat`, `cut`, `color`, `clarity`, `depth`, `table`. The 2 test diamonds used throughout:

| Name | carat | cut | color | clarity | depth | table | predicted price |
|---|---|---|---|---|---|---|---|
| small | 0.5 | Ideal | E | VS1 | 61.5 | 56.0 | $1,773 |
| big | 2.0 | Good | J | I1 | 63.0 | 59.0 | $6,713 |

---

## Exercise 1: Load the model once (lifespan) and `/health`

1. In `task9/main.py`, build the model path from `Path(__file__)`, and make a module-level dict `ml_models = {}`.
2. Write a `lifespan` function (`@asynccontextmanager`) that loads the model with `joblib.load` before `yield`, prints how long it took, and clears the dict after `yield`. Pass it to `FastAPI(title="Diamond Price API", lifespan=lifespan)`.
3. Add `GET /health`, which says whether the model is loaded.
4. Start the server, call `/health`, then stop it with Ctrl+C.

✅ Expected: the log shows `Loaded diamond_price_model.joblib in 1.18 s` (your time will differ; the very first start can take 15+ s), and `/health` → `{"status": "ok", "model_loaded": true}`. Ctrl+C prints `Model unloaded`.

📚 Look up: FastAPI "Lifespan Events", `contextlib.asynccontextmanager`.

## Exercise 2: `POST /predict`

1. In `schemas.py`, write `DiamondIn` (the 6 inputs, with `Literal` grades and `Field` limits: carat 0–6, depth 40–80, table 40–100) with an example in `json_schema_extra`, and `Prediction` (`price: int`).
2. `POST /predict`: `model_dump()` → one-row DataFrame → `predict(...)[0]` → `Prediction(price=round(price))`.
3. Try both test diamonds in `/docs`.

✅ Expected: small → `{"price": 1773}`, big → `{"price": 6713}`: the same as Task 6 Ex 8.

📚 Look up: FastAPI "Declare Request Example Data"; scikit-learn `Pipeline.predict`.

## Exercise 3: `POST /predict/batch` and timing

1. Add `BatchPrediction` (`count`, `prices`). Write `POST /predict/batch` taking `Annotated[list[DiamondIn], Body(min_length=1, max_length=1000)]`, with one DataFrame and one `predict` call.
2. Send both test diamonds, then an empty list.
3. Write `time_batch.py`: read the first 500 diamonds from `03_ml/data/diamonds.csv`, send them one by one to `/predict` and all at once to `/predict/batch` with `httpx.Client`, and compare the times. Run it in a second terminal while the server runs.

✅ Expected: `{"count": 2, "prices": [1773, 6713]}`. `[]` → **422** `too_short`; 1,001 items → **422** `too_long`. Timing: about `1.98 s` vs `0.01 s`, the batch **100x+ faster**, and `Same prices: True`.

📚 Look up: FastAPI "Body - Nested Models"; HTTPX "Quickstart"; `DataFrame.to_dict("records")`.

## Exercise 4: Errors: 422 and 503

1. Send the small diamond with one problem at a time: `cut: "Excellent"`, `carat: 0`, no `depth`, `carat: "big"`, and extra fields. Read each `loc` and `type`.
2. Read the model path from `os.getenv("MODEL_PATH", MODEL_FILE)`. Load it inside `try / except FileNotFoundError / else`, so the server starts without a model.
3. Write a `get_model()` dependency that returns the model or raises **503**, and use `model: Model` in both prediction routes.
4. Restart with `$env:MODEL_PATH = "missing.joblib"`, test, then `Remove-Item Env:MODEL_PATH`.

✅ Expected: 422s with `literal_error`, `greater_than`, `missing`, `float_parsing`; in a batch, `"loc": ["body", 1, "cut"]`; extra fields are ignored (200). Without the model: the log says `WARNING: no model at missing.joblib. /predict will answer 503.`, `/health` → `{"status": "no model", "model_loaded": false}`, and `/predict` → **503** (even for a bad cut).

📚 Look up: FastAPI "Handling Errors", "Dependencies"; `os.getenv`; MDN "503".

## Exercise 5: `POST /summary` (CSV upload)

1. Add `Summary` (`filename`, `rows`, `columns`, `missing_values`, `numeric_means`).
2. `POST /summary` with `file: UploadFile`: reject non-`.csv` names with **400**, read with `pd.read_csv(file.file)`, turn the 3 CSV read errors into **400**, and return the summary.
3. Upload `03_ml/data/diamonds.csv` from `/docs` and with `curl.exe -F`, then a small CSV with a gap, a `.txt`, and an empty `.csv`.

✅ Expected: diamonds.csv → 53,940 rows, 10 columns, `"missing_values": {}`, mean price `3932.8`. The small CSV → `"missing_values": {"cut": 1}`, `"numeric_means": {"carat": 0.75, "price": 3200.0}`. `.txt` → **400** `Please upload a .csv file`; empty → **400** `Bad CSV: No columns to parse from file`.

📚 Look up: FastAPI "Request Files"; `pandas.read_csv`, `DataFrame.mean`.

## Exercise 6: Tests with a fixture and monkeypatch

1. In `test_main.py`, write a `client` fixture that `yield`s a client from `with TestClient(app)` (so the lifespan runs).
2. Write 7 tests: health, one prediction, batch, unknown cut (422 `loc` and `type`), CSV summary, non-CSV (400), and missing model (503) using `monkeypatch.setenv("MODEL_PATH", ...)`.
3. Run `pytest -q`. Break one expectation and read the report.

✅ Expected: `7 passed` without a running server. Changing 1773 to 1774 gives `1 failed, 6 passed` with `Differing items`.

📚 Look up: FastAPI "Testing Events"; pytest "fixtures", "monkeypatch".

---

## How to work
1. Make `04_fastapi/task9/` and do the exercises in order, in the same files. Commit after each exercise.
2. The worked examples are in [notes/](notes/) (`task9_ex1_...` to `task9_ex6_...`). The finished code of every exercise is in [examples/task9/](examples/task9/) if you get stuck ([README](examples/README.md)). Your files use `parents[2]` for the repo folder, and the examples use `parents[4]`.
3. When you're done, ask Claude to **"review all"**.
