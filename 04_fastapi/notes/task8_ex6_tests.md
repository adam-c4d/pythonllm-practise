# Task 8, Exercise 6: Tests with pytest and TestClient (worked example)

Make a new file `04_fastapi/task8/test_main.py` (finished file: [examples/task8/ex6/](../examples/task8/ex6/)). `main.py` doesn't change. The outputs below are real (run on 2026-11-05).

**The idea:** so far you've tested by clicking in `/docs`. That's slow, and you have to remember what to check. A **test** is a function that sends a request and **asserts** what must come back. **pytest** finds and runs all of them in a second. It's `php artisan test` with feature tests: `$this->getJson('/api/diamonds/3')->assertStatus(200)` becomes `client.get("/diamonds/3")` + `assert response.status_code == 200`.

**pytest** is installed in `dsllm` (check with `python -m pip show pytest`). If it's missing on your other computer: `python -m pip install pytest`.

## Step 1: The test file

```python
from fastapi.testclient import TestClient

from main import API_KEY, app

client = TestClient(app)
AUTH = {"X-API-Key": API_KEY}
NEW_DIAMOND = {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
               "price": 1800, "cost": 1100}


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Diamond Shop"}


def test_list_filters_by_max_price():
    response = client.get("/diamonds", params={"max_price": 3000})
    assert response.status_code == 200
    prices = [d["price"] for d in response.json()]
    assert prices == [326, 2376]


def test_get_one_hides_cost():
    response = client.get("/diamonds/3")
    assert response.status_code == 200
    body = response.json()
    assert body["cut"] == "Good"
    assert "cost" not in body


def test_missing_diamond_is_404():
    response = client.get("/diamonds/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Diamond 999 not found"}


def test_unknown_cut_is_422():
    response = client.get("/diamonds", params={"cut": "Excellent"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "cut"]


def test_create_needs_api_key():
    response = client.post("/diamonds", json=NEW_DIAMOND)
    assert response.status_code == 401


def test_create_rejects_bad_data():
    bad = NEW_DIAMOND | {"carat": -1}
    response = client.post("/diamonds", json=bad, headers=AUTH)
    assert response.status_code == 422


def test_create_update_delete():
    created = client.post("/diamonds", json=NEW_DIAMOND, headers=AUTH)
    assert created.status_code == 201
    new_id = created.json()["id"]

    updated = client.patch(f"/diamonds/{new_id}", json={"price": 1750}, headers=AUTH)
    assert updated.status_code == 200
    assert updated.json()["price"] == 1750

    deleted = client.delete(f"/diamonds/{new_id}", headers=AUTH)
    assert deleted.status_code == 204
    assert client.get(f"/diamonds/{new_id}").status_code == 404
```
Nothing runs yet; Step 2 runs the tests.

- **`TestClient(app)`** sends requests **straight into your app object**, with no server and no network. It has the same methods as an HTTP client: `get`, `post`, `patch`, `delete`. It's Laravel's built-in test client (`$this->getJson`, `$this->postJson`).
- **`json=...`** sends a JSON body; **`params=...`** builds the query string (`?max_price=3000`); **`headers=...`** adds headers. **`response.json()`** turns the reply back into a dict or list.
- **`assert <something true>`** is the whole assertion library. `assert a == b` replaces `assertSame`/`assertEquals`, `assert "cost" not in body` replaces `assertArrayNotHasKey`. If it's false, the test fails.
- **pytest finds tests by name:** files called `test_*.py`, functions called `test_*`. No classes and no `extends TestCase` needed.
- **`NEW_DIAMOND | {"carat": -1}`** makes a copy of the dict with one value changed (the `|` operator merges dicts). The original stays valid for the other tests.
- **Every test checks one behaviour, and its name says which one.** When `test_create_needs_api_key` fails, you know what broke without reading the code.

## Step 2: Run them

Stop nothing: the tests don't need the server. In your second `(dsllm)` terminal, inside `task8/`:
```powershell
pytest -q
```
```
........                                                                 [100%]
8 passed in 0.43s
```
- **Each dot is a passing test.** `-q` (quiet) keeps the output short; `pytest -v` prints one line per test name instead.
- **Under half a second for 8 requests**, because nothing goes over the network. (The very first run after an install can take a few seconds longer.)
- **Run a single test** with `pytest -q test_main.py::test_get_one_hides_cost` (it prints `1 passed`). Useful while you fix one thing.
- **pytest makes a `.pytest_cache/` folder.** It has its own `.gitignore` inside, so Git ignores it.

## Step 3: Make one fail on purpose

Change the expected message in `test_home` to `"Welcome to the Diamond Shop"`, run `pytest -q` again, read the report, then change it back:
```
F.......                                                                 [100%]
================================== FAILURES ===================================
__________________________________ test_home __________________________________

    def test_home():
        response = client.get("/")
        assert response.status_code == 200
>       assert response.json() == {"message": "Welcome to the Diamond Shop"}
E       AssertionError: assert {'message': '...Diamond Shop'} == {'message': '...Diamond Shop'}
E         
E         Differing items:
E         {'message': 'Welcome to Diamond Shop'} != {'message': 'Welcome to the Diamond Shop'}
E         Use -v to get more diff

test_main.py:14: AssertionError
=========================== short test summary info ===========================
FAILED test_main.py::test_home - AssertionError: assert {'message': '...Diamo...
1 failed, 7 passed in 0.47s
```
- **`F` = failed.** The other 7 tests still ran: one failure doesn't stop the rest.
- **`>` points at the line that failed**, and the `E` lines explain why: **"Differing items"** shows what came back (left) and what you expected (right). pytest rewrites plain `assert` statements to produce this, so you don't need special assert functions.
- **`test_main.py:14`** is the file and line number. The summary at the end lists every failed test, useful when there are many.
- **Always see a test fail once.** A test that can't fail (wrong file name, a typo in `assert`) gives you false confidence.

## Step 4: Why the tests don't trip over each other

- **The stock is shared** by all tests in one run (one `app`, one `diamonds` dict). If one test deleted diamond 3, `test_get_one_hides_cost` could fail, depending on the order.
- **So the write test makes its own diamond:** `test_create_update_delete` creates a new one, changes it and deletes it. The 5 starting diamonds are never changed, and the read tests can rely on them.
- **`new_id = created.json()["id"]`** reads the id from the reply instead of guessing it (6? 7?), so the test works in any order. Laravel solves the same problem with `RefreshDatabase` and factories; with a real database you'd do that here too (Task 9 shows pytest **fixtures**).
- **Laravel names:** this file is your `tests/Feature/DiamondTest.php`; `pytest -q` is `php artisan test`.

## Recap
- `client = TestClient(app)`, then `client.get/post/patch/delete(...)` with `json=`, `params=` and `headers=`. No server needed.
- Plain `assert` statements; pytest finds `test_*.py` files and `test_*` functions and shows a clear diff when one fails.
- Test the unhappy paths too: 401, 404, 422. They're where APIs break.
- Keep tests independent: create what you change instead of changing shared data.

📚 **Learn more:** [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/) · [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html) · [pytest: assertions](https://docs.pytest.org/en/stable/how-to/assert.html) · [HTTPX quickstart (the client TestClient is built on)](https://www.python-httpx.org/quickstart/)

Then commit, push, and ask Claude for **"check, then ex 7"** (settings and routers).
