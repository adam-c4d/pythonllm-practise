# Task 8: FastAPI basics: a diamond shop API (Phase 4)

**Goal:** build a small JSON API for a diamond shop: list and filter the stock, show one diamond, add, change and delete diamonds, protect the write routes with an API key, and test it all with pytest. You already know how to do this in Laravel; this task shows the same ideas in FastAPI.

**Why it matters:** almost every AI Engineer job is "an LLM or a model behind an API". FastAPI is the usual way to build that in Python. Task 9 puts your Task 6 model behind this kind of API, and the capstone adds `/summary` and `/ask`.

**Laravel → FastAPI, in one table:**

| Laravel | FastAPI |
|---|---|
| `php artisan serve` | `fastapi dev main.py --port 8001` |
| `routes/api.php`: `Route::get('/diamonds/{id}', ...)` | `@app.get("/diamonds/{diamond_id}")` above a function |
| `$request->query('cut')` | a function parameter `cut: str \| None = None` |
| FormRequest `rules()` + 422 JSON errors | a Pydantic `BaseModel` + automatic 422 |
| API Resource (`toArray`, `$hidden`) | `response_model=DiamondOut` |
| `abort(404)` / `findOrFail` | `raise HTTPException(status_code=404)` |
| `Route::apiResource` (index/store/show/update/destroy) | 5 functions with `@app.get/post/patch/delete` |
| service container, middleware | `Depends(...)` |
| route model binding | a dependency that finds the diamond or raises 404 |
| `$this->getJson(...)->assertStatus(200)` | `client.get(...)`, `assert response.status_code == 200` |
| `Route::prefix('diamonds')->group(...)` | `APIRouter(prefix="/diamonds")` |
| `.env` + `config('app.name')` | `BaseSettings` + `settings.shop_name` |
| Scribe / L5-Swagger docs | `/docs`: automatic, nothing to install |

```
04_fastapi/
├── TASK_8.md
├── ruff.toml          ← tells Ruff that main, schemas, ... are your own modules
├── task8/             ← you make this folder and type your code here
│   ├── main.py        ← Exercises 1–7
│   ├── try_models.py  ← Exercise 3
│   ├── test_main.py   ← Exercise 6
│   └── config.py, schemas.py, dependencies.py, diamonds.py  ← Exercise 7
├── notes/             ← worked examples (task8_ex1_... to task8_ex7_...)
└── examples/task8/    ← the finished code after each exercise (ex1/ to ex7/)
```

**How to run it (every exercise):** open a terminal in VS Code and make sure it shows `(dsllm)`. Then:
```powershell
cd 04_fastapi/task8
fastapi dev main.py --port 8001
```
Open http://127.0.0.1:8001/docs. **Always use port 8001**: your Laravel server already uses 8000. Stop the server with **Ctrl+C**. Tests (from Exercise 6): `pytest -q` in a second `(dsllm)` terminal, inside `04_fastapi/task8`.

**The shop's stock** (5 real diamonds from Task 6's data; `cost` is made up and is secret):

| id | carat | cut | color | clarity | price | cost |
|---|---|---|---|---|---|---|
| 1 | 0.23 | Ideal | E | SI2 | 326 | 200 |
| 2 | 0.72 | Very Good | E | SI2 | 2,376 | 1,450 |
| 3 | 0.91 | Good | D | SI1 | 3,357 | 2,050 |
| 4 | 1.51 | Premium | E | SI1 | 12,530 | 7,600 |
| 5 | 2.01 | Fair | G | I1 | 6,315 | 3,900 |

**Words you'll meet:**

| Word | Meaning |
|---|---|
| **endpoint / route** | one URL + HTTP method, such as `GET /diamonds`. FastAPI calls it a *path operation* |
| **path parameter** | a value inside the URL: the `2` in `/diamonds/2` |
| **query parameter** | a value after `?`: `/diamonds?cut=Ideal&limit=5` |
| **request body** | the JSON a client sends with POST or PATCH |
| **Pydantic model** | a class that describes and validates data (like a FormRequest plus a DTO) |
| **status code** | the number in the reply: 200 OK, 201 Created, 204 No Content, 401, 404, 422, 500 |
| **dependency** | a function FastAPI runs before your route and whose result it passes in |
| **OpenAPI** | a standard JSON description of an API. FastAPI writes it for you at `/openapi.json`, and `/docs` draws it |

---

## Exercise 1: Your first API

1. Make the folder `04_fastapi/task8/` and a file `main.py` with `app = FastAPI(title="Diamond Shop")` and one route, `GET /`, that returns `{"message": "Welcome to Diamond Shop"}`.
2. Start it with `fastapi dev main.py --port 8001` and open http://127.0.0.1:8001/ in the browser. Call it from a second terminal with `curl.exe -s -i`.
3. Open `/docs` and `/openapi.json`. Try `GET /` with **Try it out → Execute**. Try a URL that doesn't exist.
4. Add `GET /grades`, which returns the 3 lists of grades (worst → best). Save, and watch the server reload.

✅ Expected: `{"message":"Welcome to Diamond Shop"}` with `HTTP/1.1 200 OK` and `content-type: application/json`. A wrong URL gives **404** `{"detail":"Not Found"}`. `/openapi.json` starts with `{"openapi":"3.1.0","info":{"title":"Diamond Shop"...`. `/grades` returns 5 cuts, 7 colours and 8 clarities.

📚 Look up: FastAPI "First Steps", `fastapi dev` vs `fastapi run`.

## Exercise 2: Path and query parameters

1. Define the grades once as `Literal` types (`Cut`, `Color`, `Clarity`) and rewrite `/grades` with `get_args`. Add the stock as a dict of dicts (table above).
2. `GET /diamonds/{diamond_id}` with `diamond_id: int`. Try `/diamonds/2`, `/diamonds/abc` and `/diamonds/99`.
3. `GET /diamonds` with the filters `cut: Cut | None = None`, `max_price: int | None = None`, `sort_by: Literal["price", "carat"] = "price"`, and `limit: Annotated[int, Query(ge=1, le=100)] = 10`.
4. Send bad values: `?cut=Excellent`, then `?cut=Excellent&limit=0&max_price=cheap`.

✅ Expected: `/diamonds/2` shows the 0.72 carat Very Good diamond **including `"cost": 1450`** (a leak, fixed in Exercise 3). `/diamonds/abc` → **422** `int_parsing`. `/diamonds/99` → **500 Internal Server Error** (`KeyError: 99` in the terminal; fixed in Exercise 4). `?max_price=3000` → diamonds 1 and 2. `?cut=Excellent` → **422** `Input should be 'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal'`. The 3 bad values give **3 errors in one reply**.

📚 Look up: FastAPI "Path Parameters", "Query Parameters", "Query Parameters and String Validations", `typing.Literal`, `typing.Annotated`.

## Exercise 3: Request bodies with Pydantic

1. Write 3 models: `DiamondBase` (carat `Field(gt=0, le=6)`, cut, color, clarity, price `Field(gt=0, le=100_000)`), `DiamondIn(DiamondBase)` adding `cost`, and `DiamondOut(DiamondBase)` adding `id`.
2. In `try_models.py`, validate a dict with `DiamondIn.model_validate`, print `model_dump()`, and catch a `ValidationError`.
3. `POST /diamonds` with `status_code=201` and `response_model=DiamondOut`. The new id is `max(diamonds) + 1`.
4. Add `response_model=DiamondOut` (and `list[DiamondOut]`) to both GET routes.

✅ Expected: `"carat": "0.5"` (a string) becomes the float `0.5`. A dict with 4 problems gives `4 validation errors for DiamondIn`. POST → **201** with `"id": 6` and **no `cost`**. A bad body → **422** listing `carat`, `cut`, `price` and the missing `cost`. `GET /diamonds/2` no longer shows `cost`, and `id` now comes last.

📚 Look up: FastAPI "Request Body", "Body - Fields", "Response Model", "Extra Models"; Pydantic "Models".

## Exercise 4: CRUD and error codes

1. Write `find_diamond(diamond_id)`, which raises `HTTPException(status_code=404, detail=...)` when the id is unknown, and use it in `GET /diamonds/{diamond_id}`.
2. `PATCH /diamonds/{diamond_id}` with a `DiamondPatch` model (every field optional). Update only the fields that were sent: `model_dump(exclude_none=True)`.
3. `DELETE /diamonds/{diamond_id}` with `status_code=204`, returning nothing.
4. Restart the server and check the data again.

✅ Expected: `/diamonds/99` → **404** `{"detail": "Diamond 99 not found"}`. `PATCH /diamonds/2` with `{"price": 2199}` → **200**, only the price changes. `{"cut": "Premium", "price": null}` changes the cut and keeps the price. `{"price": -5}` → **422**. `DELETE /diamonds/5` → **204** with no body; deleting it again → **404**. After a restart, diamond 2 costs $2,376 again and diamond 5 is back.

📚 Look up: FastAPI "Handling Errors", "Response Status Code", "Body - Updates".

## Exercise 5: Dependencies: pagination and an API key

1. Write a `pagination(skip, limit)` dependency and use it in `GET /diamonds` as `page: Pagination`, where `Pagination = Annotated[dict[str, int], Depends(pagination)]`.
2. Write `require_api_key(x_api_key: Annotated[str | None, Header()] = None)`, which raises **401** unless the header equals `API_KEY = "dev-secret"`. Add `dependencies=[Depends(require_api_key)]` to POST, PATCH and DELETE.
3. Turn `find_diamond` into a dependency, `FoundDiamond = Annotated[dict, Depends(find_diamond)]`, and use it in GET, PATCH and DELETE.

✅ Expected: `?skip=1&limit=2` → diamonds 2 and 3. `?skip=-1` → **422**. POST without the header or with a wrong key → **401** `{"detail": "Missing or wrong API key"}`; with `X-API-Key: dev-secret` → **201**. `DELETE /diamonds/99` without a key → **401** (the key is checked first); with the key → **404**. `GET /diamonds/3` still works.

📚 Look up: FastAPI "Dependencies", "Dependencies in path operation decorators", "Header Parameters".

## Exercise 6: Tests with pytest and TestClient

1. Make `test_main.py` with `client = TestClient(app)` and 8 tests: home, filter by price, `cost` is hidden, 404, 422, 401, a bad POST, and create → update → delete in one test.
2. Run `pytest -q`. Then break one test on purpose and read pytest's report.

✅ Expected: `8 passed` in under 2 seconds, **without** a running server. A broken expectation shows `1 failed, 7 passed` with a `Differing items:` diff.

📚 Look up: FastAPI "Testing", pytest "Get started", pytest "assert".

## Exercise 7: Organise it like a real project: settings and routers

1. `config.py`: a `Settings(BaseSettings)` class with `shop_name: str = "Diamond Shop"` and `api_key: str = "dev-secret"`, read from environment variables (and a `.env` file).
2. Split `main.py`: models → `schemas.py`, dependencies → `dependencies.py`, the stock and the 5 diamond routes → `diamonds.py` with `router = APIRouter(prefix="/diamonds", tags=["diamonds"])`. `main.py` keeps `/` and `/grades` and calls `app.include_router(diamonds.router)`.
3. Update the 2 imports in `test_main.py` (and `try_models.py`) and run `pytest -q`.
4. Start the server with `$env:SHOP_NAME` and `$env:API_KEY` set.

✅ Expected: still `8 passed` (the refactor changed nothing on the outside). `/docs` groups the 5 routes under **diamonds**. With `$env:SHOP_NAME = "Mohali Diamonds"`, `GET /` says `Welcome to Mohali Diamonds`, and the old key `dev-secret` gets **401**.

📚 Look up: FastAPI "Bigger Applications", "Settings and Environment Variables"; Pydantic "Settings Management".

---

## How to work
1. Make `04_fastapi/task8/` and do the exercises in order, in the same files. Commit after each exercise.
2. The worked examples are in [notes/](notes/) (`task8_ex1_...` to `task8_ex7_...`). The finished code of every exercise is in [examples/task8/](examples/task8/) if you get stuck ([README](examples/README.md)).
3. When you're done, ask Claude to **"review all"**.
