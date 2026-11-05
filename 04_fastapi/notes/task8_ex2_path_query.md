# Task 8, Exercise 2: Path and query parameters (worked example)

Continue in `04_fastapi/task8/main.py` (finished file: [examples/task8/ex2/](../examples/task8/ex2/)). Keep the server running: it reloads on every save. The outputs below are real (run on 2026-11-05).

**The idea:** in Laravel you read input with `$request->query('cut')` or a `{id}` in the route, and then validate it. In FastAPI you **declare the input as function parameters with type hints**. FastAPI reads them from the URL, converts them (`"2"` → `2`) and rejects bad values with a 422, before your function runs.

## Step 1: Grades as types, and the stock

Change `main.py` so it looks like this. New: the imports, the 3 grade types, the stock, and the body of `grades()`:
```python
from typing import Annotated, Literal, get_args

from fastapi import FastAPI, Query

Cut = Literal["Fair", "Good", "Very Good", "Premium", "Ideal"]
Color = Literal["J", "I", "H", "G", "F", "E", "D"]
Clarity = Literal["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]

# The shop's stock. `cost` is what the shop paid: customers must never see it.
diamonds = {
    1: {"id": 1, "carat": 0.23, "cut": "Ideal", "color": "E", "clarity": "SI2",
        "price": 326, "cost": 200},
    2: {"id": 2, "carat": 0.72, "cut": "Very Good", "color": "E", "clarity": "SI2",
        "price": 2376, "cost": 1450},
    3: {"id": 3, "carat": 0.91, "cut": "Good", "color": "D", "clarity": "SI1",
        "price": 3357, "cost": 2050},
    4: {"id": 4, "carat": 1.51, "cut": "Premium", "color": "E", "clarity": "SI1",
        "price": 12530, "cost": 7600},
    5: {"id": 5, "carat": 2.01, "cut": "Fair", "color": "G", "clarity": "I1",
        "price": 6315, "cost": 3900},
}

app = FastAPI(title="Diamond Shop")


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to Diamond Shop"}


@app.get("/grades")
def grades() -> dict[str, tuple[str, ...]]:
    return {
        "cut": get_args(Cut),
        "color": get_args(Color),
        "clarity": get_args(Clarity),
    }
```
```http
GET http://127.0.0.1:8001/grades
```
```
200 OK
{
  "cut": [
    "Fair",
    "Good",
    "Very Good",
    "Premium",
    "Ideal"
  ],
  "color": [
    "J",
    "I",
    "H",
    "G",
    "F",
    "E",
    "D"
  ],
  "clarity": [
    "I1",
    "SI2",
    "SI1",
    "VS2",
    "VS1",
    "VVS2",
    "VVS1",
    "IF"
  ]
}
```
- **`Literal["Fair", "Good", ...]`** is a type that allows **only these exact strings**. It's Laravel's `Rule::in(['Fair', 'Good', ...])`, written as a type. `Cut = Literal[...]` gives it a name, so every route can reuse it.
- **`get_args(Cut)`** reads the allowed values back out of the type, as a tuple. Now the grades are written **once**: change `Cut`, and both the validation and `/grades` follow. The reply is the same as in Exercise 1 (JSON has no tuples, so a tuple becomes a list).
- **`tuple[str, ...]`** means "a tuple of strings, any length". `tuple[str]` would mean exactly one string.
- **`diamonds` is a dict of dicts: id → diamond.** It plays the database for this task; Phase 5 and the capstone can swap in a real one. Each diamond is split over 2 lines to stay under 88 characters.
- **It lives in memory**, so every restart (and every reload) brings the original 5 back. Exercise 4 uses that.

## Step 2: A path parameter

Add at the end:
```python
@app.get("/diamonds/{diamond_id}")
def get_diamond(diamond_id: int) -> dict:
    return diamonds[diamond_id]
```
```http
GET http://127.0.0.1:8001/diamonds/2
```
```
200 OK
{
  "id": 2,
  "carat": 0.72,
  "cut": "Very Good",
  "color": "E",
  "clarity": "SI2",
  "price": 2376,
  "cost": 1450
}
```
- **`{diamond_id}` in the path + a parameter with the same name** = a path parameter, like `Route::get('/diamonds/{id}', fn (int $id) => ...)`.
- **`diamond_id: int`** makes FastAPI convert the text `"2"` from the URL into the number `2`. Without it you'd get the string `"2"`, and `diamonds["2"]` would fail, because the keys are numbers.
- **The reply leaks `"cost": 1450`**, the shop's secret purchase price. Returning the raw dict returns *everything*. Exercise 3 fixes that with a response model, like an API Resource.

## Step 3: Wrong types and missing diamonds

```http
GET http://127.0.0.1:8001/diamonds/abc
```
```
422 Unprocessable Content
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": [
        "path",
        "diamond_id"
      ],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "abc"
    }
  ]
}
```
And a number that isn't in the stock:
```http
GET http://127.0.0.1:8001/diamonds/99
```
```
500 Internal Server Error
Internal Server Error
```
The server terminal shows the cause, at the end of a long traceback:
```
  File "C:\Users\phpde\OneDrive\Desktop\pythonllm-practise\04_fastapi\examples\task8\ex2\main.py", line 54, in get_diamond
    return diamonds[diamond_id]
           ~~~~~~~~^^^^^^^^^^^^
KeyError: 99
```
- **422 = "I understood your request, but the data is invalid."** Your function never ran. Laravel's FormRequest returns the same status code.
- **Each error says where (`loc`), what (`type`, `msg`) and what you sent (`input`).** `["path", "diamond_id"]` means "the `diamond_id` part of the URL path". Query errors say `"query"`, body errors `"body"`.
- **The 500 is a bug in *your* code:** `diamonds[99]` raises `KeyError`, nothing catches it, and FastAPI answers 500 with plain text (not JSON). It's Laravel's "Whoops" page with debug off. Exercise 4 turns this into a proper **404**.
- **Read the traceback from the bottom up** (Task 3): the last line is the error, and the line above it is your code.

## Step 4: Query parameters

Add:
```python
@app.get("/diamonds")
def list_diamonds(
    cut: Cut | None = None,
    max_price: int | None = None,
    sort_by: Literal["price", "carat"] = "price",
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[dict]:
    results = list(diamonds.values())
    if cut is not None:
        results = [d for d in results if d["cut"] == cut]
    if max_price is not None:
        results = [d for d in results if d["price"] <= max_price]
    results.sort(key=lambda d: d[sort_by])
    return results[:limit]
```
```http
GET http://127.0.0.1:8001/diamonds?max_price=3000
```
```
200 OK
[
  {
    "id": 1,
    "carat": 0.23,
    "cut": "Ideal",
    "color": "E",
    "clarity": "SI2",
    "price": 326,
    "cost": 200
  },
  {
    "id": 2,
    "carat": 0.72,
    "cut": "Very Good",
    "color": "E",
    "clarity": "SI2",
    "price": 2376,
    "cost": 1450
  }
]
```
And with a space in the value (the browser sends it as `%20`):
```http
GET http://127.0.0.1:8001/diamonds?cut=Very Good
```
```
200 OK
[
  {
    "id": 2,
    "carat": 0.72,
    "cut": "Very Good",
    "color": "E",
    "clarity": "SI2",
    "price": 2376,
    "cost": 1450
  }
]
```
- **A parameter that isn't in the path is a query parameter.** `?max_price=3000` fills `max_price`. There's no `$request` object to dig in.
- **`int | None = None`** means "a whole number, or nothing; nothing by default". So the filter is **optional**. A parameter without a default would be **required**, and leaving it out would give a 422.
- **`sort_by: Literal["price", "carat"] = "price"`** allows only 2 values, with a default. Try `?sort_by=carat`: diamonds 4 and 5 swap places (1.51 ct is lighter than 2.01 ct but costs more).
- **`Annotated[int, Query(ge=1, le=100)]`** adds rules to the type: at least 1, at most 100 (`ge` = greater or equal, `le` = less or equal). `Annotated` means "this type, plus extra information for FastAPI". The default `= 10` stays outside. This is the style the FastAPI docs recommend.
- **The function is plain Python:** list comprehensions filter, and `sort(key=lambda d: d[sort_by])` sorts by the chosen column. `lambda d: d[sort_by]` is a tiny one-line function, like PHP's `fn ($d) => $d[$sortBy]`.
- **Names must match exactly.** `?Cut=Ideal` (capital C) is an unknown parameter, and FastAPI **ignores** unknown parameters, so you get all 5 diamonds back without any error.

## Step 5: Bad query values

```http
GET http://127.0.0.1:8001/diamonds?cut=Excellent
```
```
422 Unprocessable Content
{
  "detail": [
    {
      "type": "literal_error",
      "loc": [
        "query",
        "cut"
      ],
      "msg": "Input should be 'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal'",
      "input": "Excellent",
      "ctx": {
        "expected": "'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal'"
      }
    }
  ]
}
```
Now 3 mistakes at once:
```http
GET http://127.0.0.1:8001/diamonds?cut=Excellent&limit=0&max_price=cheap
```
```
422 Unprocessable Content
{
  "detail": [
    {
      "type": "literal_error",
      "loc": [
        "query",
        "cut"
      ],
      "msg": "Input should be 'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal'",
      "input": "Excellent",
      "ctx": {
        "expected": "'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal'"
      }
    },
    {
      "type": "int_parsing",
      "loc": [
        "query",
        "max_price"
      ],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "cheap"
    },
    {
      "type": "greater_than_equal",
      "loc": [
        "query",
        "limit"
      ],
      "msg": "Input should be greater than or equal to 1",
      "input": "0",
      "ctx": {
        "ge": 1
      }
    }
  ]
}
```
- **The `Literal` type rejects `Excellent` and lists the allowed grades.** In Task 6, the model's encoder raised `ValueError: Found unknown categories ['Excellent']`. Here the API stops it at the door, with a clear message.
- **All errors come back together**, like Laravel's validator returning every message at once, so the client can fix everything in one go.
- **`ctx`** ("context") holds the rule that failed: `"ge": 1`.
- **Laravel's 422 looks different** (`{"message": ..., "errors": {"cut": [...]}}`), but it's the same idea. A front end can read `loc` to show each message next to the right field.
- **Open GET /diamonds in `/docs`:** `cut` is a drop-down ("Available values: Fair, Good, Very Good, Premium, Ideal", empty by default), `sort_by` is a drop-down set to `price`, and under `limit` it says `maximum: 100`, `minimum: 1`. The docs come from the same type hints. Under **Responses**, the example is just `[{"additionalProp1": {}}]`, because `list[dict]` says nothing about the fields. Exercise 3 improves that too.

## Recap
- Path parameter: `{diamond_id}` in the route + `diamond_id: int`. Query parameter: any other function parameter.
- The type hint does the work: conversion (`"2"` → `2`), validation, and the 422 error. `X | None = None` = optional; no default = required.
- `Literal[...]` ≈ `Rule::in([...])`; `Annotated[int, Query(ge=1, le=100)]` adds limits.
- Returning a raw dict leaks every field (`cost`), and an unknown id is still a 500. Exercises 3 and 4 fix both.

📚 **Learn more:** [FastAPI: Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/) · [Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/) · [Query Parameters and String Validations (`Annotated`, `Query`)](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/) · [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) · [`typing.get_args`](https://docs.python.org/3/library/typing.html#typing.get_args)

Then commit, push, and ask Claude for **"check, then ex 3"** (request bodies with Pydantic).
