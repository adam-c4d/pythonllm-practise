# Task 8, Exercise 5: Dependencies: pagination and an API key (worked example)

Continue in `04_fastapi/task8/main.py` (finished file: [examples/task8/ex5/](../examples/task8/ex5/)). The outputs below are real (run on 2026-11-05).

**The idea:** a **dependency** is a function that FastAPI runs *before* your route. You write `Depends(some_function)`; FastAPI calls it (filling its parameters from the request, like a route), then passes the result in. If the dependency raises an `HTTPException`, the route never runs. One mechanism covers 3 Laravel features:

| You want | Laravel | FastAPI |
|---|---|---|
| shared input (pagination) | a trait or a base FormRequest | a dependency that returns values |
| a guard (API key) | route middleware `->middleware('auth')` | `dependencies=[Depends(require_api_key)]` |
| "find it or 404" | route model binding `fn (Diamond $diamond)` | a dependency that returns the diamond |

And like Laravel's **service container**, you never call these functions yourself: you declare what you need in the signature, and the framework provides it.

**Change the `fastapi` import** to:
```python
from fastapi import Depends, FastAPI, Header, HTTPException, Query
```

## Step 1: Pagination as a dependency

Add under `app = FastAPI(...)`:
```python
# --- Dependencies ---------------------------------------------------------------
def pagination(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict[str, int]:
    return {"skip": skip, "limit": limit}


Pagination = Annotated[dict[str, int], Depends(pagination)]
```
(Also put a matching `# --- Routes ---...` comment line above `@app.get("/")`, so the file reads in 2 parts.) Then, in `list_diamonds`, replace the `limit` parameter with `page: Pagination` (as the **first** parameter) and change the last line:
```python
@app.get("/diamonds", response_model=list[DiamondOut])
def list_diamonds(
    page: Pagination,
    cut: Cut | None = None,
    max_price: int | None = None,
    sort_by: Literal["price", "carat"] = "price",
) -> list[dict]:
    results = list(diamonds.values())
    if cut is not None:
        results = [d for d in results if d["cut"] == cut]
    if max_price is not None:
        results = [d for d in results if d["price"] <= max_price]
    results.sort(key=lambda d: d[sort_by])
    return results[page["skip"] : page["skip"] + page["limit"]]
```
```http
GET http://127.0.0.1:8001/diamonds?skip=1&limit=2
```
```
200 OK
[
  {
    "carat": 0.72,
    "cut": "Very Good",
    "color": "E",
    "clarity": "SI2",
    "price": 2376,
    "id": 2
  },
  {
    "carat": 0.91,
    "cut": "Good",
    "color": "D",
    "clarity": "SI1",
    "price": 3357,
    "id": 3
  }
]
```
```http
GET http://127.0.0.1:8001/diamonds?skip=-1
```
```
422 Unprocessable Content
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": [
        "query",
        "skip"
      ],
      "msg": "Input should be greater than or equal to 0",
      "input": "-1",
      "ctx": {
        "ge": 0
      }
    }
  ]
}
```
- **`pagination` looks like a route without a decorator.** Its parameters are query parameters, with the same rules as before. FastAPI reads `?skip=1&limit=2`, validates them, calls `pagination(skip=1, limit=2)` and passes the dict in as `page`.
- **`Pagination = Annotated[dict[str, int], Depends(pagination)]`** is a reusable type: "a `dict[str, int]` that comes from `pagination()`". Any future list route (orders, customers) just adds `page: Pagination`. Change the limits once, and every list follows.
- **`page` goes first** because Python doesn't allow a parameter without a default (`page`) after parameters with defaults.
- **`results[skip : skip + limit]`** is a slice: skip 1, take 2 → items 2 and 3. It's SQL's `OFFSET 1 LIMIT 2`, or Laravel's `->skip(1)->take(2)`. (Ruff's formatter puts spaces around `:` when the slice has maths in it.)
- **`/docs` still shows `skip` and `limit`** on GET /diamonds: FastAPI looks inside dependencies to build the docs.

## Step 2: An API key guard (≈ middleware)

Add a constant under the `Clarity` line:
```python
API_KEY = "dev-secret"  # Exercise 7 moves this into an environment variable
```
then this function under `Pagination`, and the `dependencies=[...]` argument on the 3 write routes:
```python
def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Missing or wrong API key")
```
```python
@app.post(
    "/diamonds",
    status_code=201,
    response_model=DiamondOut,
    dependencies=[Depends(require_api_key)],
)
```
Do the same for `@app.patch(...)` and `@app.delete(...)`: put each argument on its own line and add `dependencies=[Depends(require_api_key)],`. Now send the Exercise 3 body 3 times: with no header, with `X-API-Key: guess`, and with the right key:
```http
POST http://127.0.0.1:8001/diamonds
Content-Type: application/json

{"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1", "price": 1800, "cost": 1100}
```
```
401 Unauthorized
{
  "detail": "Missing or wrong API key"
}
```
```http
POST http://127.0.0.1:8001/diamonds
X-API-Key: guess
Content-Type: application/json

{"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1", "price": 1800, "cost": 1100}
```
```
401 Unauthorized
{
  "detail": "Missing or wrong API key"
}
```
```http
POST http://127.0.0.1:8001/diamonds
X-API-Key: dev-secret
Content-Type: application/json

{"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1", "price": 1800, "cost": 1100}
```
```
201 Created
{
  "carat": 0.5,
  "cut": "Ideal",
  "color": "E",
  "clarity": "VS1",
  "price": 1800,
  "id": 6
}
```
- **`Header()`** reads a request header instead of a query parameter. FastAPI turns the Python name `x_api_key` into the header name `x-api-key` (`_` → `-`). Header names ignore case, so `X-API-Key` and `x-api-key` both work.
- **`str | None = None`:** a missing header is `None`, which isn't equal to `API_KEY`, so it gets the same 401 as a wrong key. You don't tell an attacker which part was wrong.
- **`dependencies=[Depends(require_api_key)]`** in the decorator runs the check without passing anything to the function, because the guard returns nothing (`-> None`). It's `Route::post(...)->middleware('auth.apikey')`. GET routes stay public.
- **401 Unauthorized** = "who are you? Send valid credentials." (403 Forbidden would mean "I know who you are, and you may not do this.")
- **In `/docs`**, the 3 write routes now have an **x-api-key** text box (marked *header*) next to their other parameters. Type `dev-secret` there before you click Execute.
- **This is a teaching version.** A real key is long and random, lives in an environment variable (Exercise 7), and is compared with `secrets.compare_digest(a, b)`, which takes the same time whatever the input, so attackers can't guess it character by character from response times.

## Step 3: "Find it or 404" as a dependency (≈ route model binding)

Add one line under `find_diamond`, then let the 3 single-diamond routes ask for the diamond itself:
```python
FoundDiamond = Annotated[dict, Depends(find_diamond)]
```
```python
@app.get("/diamonds/{diamond_id}", response_model=DiamondOut)
def get_diamond(diamond: FoundDiamond) -> dict:
    return diamond
```
```python
def update_diamond(diamond: FoundDiamond, changes: DiamondPatch) -> dict:
    diamond.update(changes.model_dump(exclude_none=True))
    return diamond
```
```python
def delete_diamond(diamond: FoundDiamond) -> None:
    del diamonds[diamond["id"]]
```
(Only the `def` lines and bodies change; keep the decorators from Step 2.) Then:
```http
GET http://127.0.0.1:8001/diamonds/3
```
```
200 OK
{
  "carat": 0.91,
  "cut": "Good",
  "color": "D",
  "clarity": "SI1",
  "price": 3357,
  "id": 3
}
```
Delete a diamond that doesn't exist, first without the key, then with it:
```http
DELETE http://127.0.0.1:8001/diamonds/99
```
```
401 Unauthorized
{
  "detail": "Missing or wrong API key"
}
```
```http
DELETE http://127.0.0.1:8001/diamonds/99
X-API-Key: dev-secret
```
```
404 Not Found
{
  "detail": "Diamond 99 not found"
}
```
- **`find_diamond(diamond_id: int)` is now a dependency.** FastAPI sees its `diamond_id` parameter, fills it from the path `{diamond_id}`, and hands the found dict to the route as `diamond`. That's Laravel's route model binding: `Route::get('/diamonds/{diamond}', fn (Diamond $diamond) => $diamond)`.
- **The routes got shorter**: no `find_diamond(...)` call, no `diamond_id` parameter. The 404 is still there, inside the dependency.
- **`del diamonds[diamond["id"]]`:** the route no longer has `diamond_id`, but the diamond dict knows its own `id`.
- **The key is checked before the diamond is looked up** (401, not 404), because decorator dependencies run first. Good: a stranger can't even find out which ids exist.

## Recap
- `Depends(fn)`: FastAPI calls `fn` with values from the request and injects the result (≈ service container). `Annotated[type, Depends(fn)]` makes a reusable parameter type.
- Shared parameters (`Pagination`), guards (`dependencies=[Depends(require_api_key)]` ≈ middleware) and lookups (`FoundDiamond` ≈ route model binding) are all just dependencies.
- `Header()` reads headers (`x_api_key` → `x-api-key`). Missing or wrong key → 401.

📚 **Learn more:** [FastAPI: Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) · [Dependencies in path operation decorators](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/) · [Header Parameters](https://fastapi.tiangolo.com/tutorial/header-params/) · [`secrets.compare_digest`](https://docs.python.org/3/library/secrets.html)

Then commit, push, and ask Claude for **"check, then ex 6"** (tests with pytest and TestClient).
