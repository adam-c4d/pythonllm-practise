# Task 9, Exercise 6: Test the model API with pytest fixtures (worked example)

Continue in `04_fastapi/task9/`: add `test_main.py` (finished files: [examples/task9/ex6/](../examples/task9/ex6/)). `main.py` and `schemas.py` don't change. The outputs below are real (run on 2026-11-23).

**The idea:** the same `TestClient` and `pytest` as Task 8 Ex 6, with 2 new tools:
- a **fixture**, so every test gets a client **with the model loaded** (the lifespan has to run), and
- **`monkeypatch`**, to set `MODEL_PATH` for one test only and check the 503.

- **Laravel analogy:** a fixture is `setUp()` in a test class (or a `beforeEach` in Pest), but the test asks for it by name. `monkeypatch.setenv` is `config(['...' => ...])` inside one test, undone automatically afterwards.

## `test_main.py`

```python
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from main import app

SMALL = {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
         "depth": 61.5, "table": 56.0}
BIG = {"carat": 2.0, "cut": "Good", "color": "J", "clarity": "I1",
       "depth": 63.0, "table": 59.0}


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:  # `with` runs the lifespan: loads the model
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_predict_one(client):
    response = client.post("/predict", json=SMALL)
    assert response.status_code == 200
    assert response.json() == {"price": 1773}


def test_batch_matches_single(client):
    response = client.post("/predict/batch", json=[SMALL, BIG])
    assert response.json() == {"count": 2, "prices": [1773, 6713]}


def test_unknown_cut_is_422(client):
    response = client.post("/predict", json=SMALL | {"cut": "Excellent"})
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "cut"]
    assert error["type"] == "literal_error"


def test_summary_of_small_csv(client):
    csv_text = "carat,cut,price\n0.5,Ideal,1800\n1.0,,4600\n"
    files = {"file": ("small.csv", csv_text, "text/csv")}
    response = client.post("/summary", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 2
    assert body["missing_values"] == {"cut": 1}
    assert body["numeric_means"] == {"carat": 0.75, "price": 3200.0}


def test_summary_rejects_other_files(client):
    files = {"file": ("notes.txt", "hello", "text/plain")}
    response = client.post("/summary", files=files)
    assert response.status_code == 400


def test_missing_model_gives_503(monkeypatch):
    monkeypatch.setenv("MODEL_PATH", "no_such_file.joblib")
    with TestClient(app) as client:
        assert client.get("/health").json()["model_loaded"] is False
        assert client.post("/predict", json=SMALL).status_code == 503
```

Run it in a `(dsllm)` terminal, inside `04_fastapi/task9/`. **No server needed**:
```powershell
pytest -q
```
```
.......                                                                  [100%]
7 passed in 2.48s
```
List the tests without running them:
```powershell
pytest -q --co
```
```
test_main.py::test_health
test_main.py::test_predict_one
test_main.py::test_batch_matches_single
test_main.py::test_unknown_cut_is_422
test_main.py::test_summary_of_small_csv
test_main.py::test_summary_rejects_other_files
test_main.py::test_missing_model_gives_503

7 tests collected in 1.96s
```
pytest hides each test's `print` output while it passes. When a test fails, its report shows the lifespan's lines under `Captured stdout setup` (`Loaded diamond_price_model.joblib in 0.01 s`) and `Captured stdout teardown` (`Model unloaded`).

## Why each part works

### The fixture
- **Why not `client = TestClient(app)` at the top, as in Task 8?** Because then the **lifespan never runs**, and the model is never loaded. I checked: that client gets `{'status': 'no model', 'model_loaded': False}` from `/health` and **503** from `/predict`. Task 8 had no lifespan, so it didn't matter there.
- **`with TestClient(app) as test_client:`** runs the code before `yield` in your lifespan (load the model) when the `with` block starts, and the code after it (unload) when the block ends, just like starting and stopping the server.
- **`@pytest.fixture`** marks `client()` as a fixture. **A test asks for it by naming a parameter `client`**: pytest sees `def test_health(client)`, runs the fixture, and passes in what it `yield`s. That's dependency injection, the same idea as FastAPI's `Depends` and Laravel's container.
- **`yield test_client`**: everything before `yield` is setup, and everything after it (here, leaving the `with` block) is teardown. Same shape as the lifespan.
- **`Iterator[TestClient]`** is the type of a function that `yield`s a `TestClient`. Only for your editor.
- **One fixture run per test** (pytest's default "function" scope), so each test gets a fresh client and the model loads 6 times. After the first load the file is in Windows' cache, so each reload took about 0.01 s here. For a slower model you'd add `scope="module"` to load it once per file.

### The tests
- **`SMALL` and `BIG`** are the 2 diamonds from Exercises 2–3, written once and reused. Capital names = constants (PEP 8).
- **`test_predict_one` checks the exact price, 1773.** That pins down the model: if someone retrains it, this test fails and tells you the API's answers changed. That's useful, but it also means you update the number on purpose after retraining.
- **`SMALL | {"cut": "Excellent"}`** merges 2 dicts into a **new** one (the right side wins), leaving `SMALL` untouched. It's PHP's `array_merge($small, ['cut' => 'Excellent'])`.
- **`test_unknown_cut_is_422` checks `loc` and `type`**, not the message text. Messages can change between Pydantic versions; the codes are stable.
- **`files={"file": ("small.csv", csv_text, "text/csv")}`** uploads a file without a file on disk: (filename, content, content type). The key `"file"` matches the route's parameter name, like `-F "file=@..."` in curl.
- **`"1.0,,4600"`**: the empty value between the 2 commas is the gap that `missing_values == {"cut": 1}` checks for.

### The 503 test
- **`monkeypatch`** is a fixture built into pytest. You ask for it by name, like `client`.
- **`monkeypatch.setenv("MODEL_PATH", "no_such_file.joblib")`** sets the environment variable **for this test only**, and pytest removes it again afterwards. Other tests still get the real model. It's the test version of `$env:MODEL_PATH = ...` from Exercise 4.
- **This test makes its own `TestClient`** instead of using the `client` fixture, because the variable must be set **before** the lifespan runs.
- **`is False`, not `== False`:** compare with `True`, `False` and `None` using `is` (PEP 8; Ruff warns about `== False`).

## Try breaking it
Change `1773` to `1774` in `test_predict_one` and run `pytest -q` again. The end of the report:
```
>       assert response.json() == {"price": 1774}
E       AssertionError: assert {'price': 1773} == {'price': 1774}
E
E         Differing items:
E         {'price': 1773} != {'price': 1774}
...
FAILED test_main.py::test_predict_one - AssertionError: assert {'price': 1773...
1 failed, 6 passed in 2.50s
```
Then put it back.

## Recap
- Apps with a lifespan need `with TestClient(app)`, or the model is never loaded.
- A `@pytest.fixture` that `yield`s gives each test a ready client. A test asks for it by parameter name, like `Depends`.
- `monkeypatch.setenv` changes an environment variable for one test and undoes it afterwards.
- 7 tests cover health, single and batch predictions, a 422, the CSV summary, a 400 and the 503.

📚 **Learn more:** [FastAPI: Testing Events (lifespan)](https://fastapi.tiangolo.com/advanced/testing-events/) · [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) · [pytest: monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) · [HTTPX: multipart file uploads](https://www.python-httpx.org/quickstart/#sending-multipart-file-uploads) · [dict merge `|`](https://docs.python.org/3/library/stdtypes.html#dict)

## ✅ Task 9 done when
- [ ] `04_fastapi/task9/` has `main.py`, `schemas.py`, `time_batch.py` and `test_main.py`.
- [ ] `pytest -q` prints `7 passed`, and Ruff shows no problems in the folder.
- [ ] `/predict` gives 1773 for the 0.5 ct example, `time_batch.py` shows the batch is 100x+ faster, and `/summary` accepts `diamonds.csv`.
- [ ] With `$env:MODEL_PATH = "missing.joblib"` the server starts, `/health` says `"model_loaded": false` and `/predict` answers 503.

Then commit, push, and ask Claude to **"review all"**. That finishes Task 9 and Phase 4. Next is Phase 5: LLMs.
