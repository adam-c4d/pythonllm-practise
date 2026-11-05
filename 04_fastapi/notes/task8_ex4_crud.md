# Task 8, Exercise 4: CRUD and error codes (worked example)

Continue in `04_fastapi/task8/main.py` (finished file: [examples/task8/ex4/](../examples/task8/ex4/)). The outputs below are real (run on 2026-11-05).

**The idea:** CRUD = Create, Read, Update, Delete. In Laravel, `Route::apiResource('diamonds', DiamondController::class)` gives you 5 routes: index, store, show, update, destroy. You already have index (`GET /diamonds`), show and store. This exercise adds update and destroy, and proper error codes.

| Laravel action | Method and path | Success code |
|---|---|---|
| index | `GET /diamonds` | 200 |
| show | `GET /diamonds/{id}` | 200, or **404** |
| store | `POST /diamonds` | **201** |
| update | `PATCH /diamonds/{id}` | 200, or 404 |
| destroy | `DELETE /diamonds/{id}` | **204**, or 404 |

**Change the `fastapi` import** to:
```python
from fastapi import FastAPI, HTTPException, Query
```

## Step 1: 404 instead of 500

Add this function under `app = FastAPI(...)`, and change `get_diamond` to use it:
```python
def find_diamond(diamond_id: int) -> dict:
    if diamond_id not in diamonds:
        raise HTTPException(status_code=404, detail=f"Diamond {diamond_id} not found")
    return diamonds[diamond_id]
```
```python
@app.get("/diamonds/{diamond_id}", response_model=DiamondOut)
def get_diamond(diamond_id: int) -> dict:
    return find_diamond(diamond_id)
```
```http
GET http://127.0.0.1:8001/diamonds/99
```
```
404 Not Found
{
  "detail": "Diamond 99 not found"
}
```
- **`raise HTTPException(status_code=404, detail=...)`** stops the request and sends this status with `{"detail": ...}`. It's Laravel's `abort(404, 'Diamond 99 not found')`.
- **`find_diamond` is your `findOrFail`:** it returns the diamond or raises. Every route that needs one diamond will call it, so the 404 is written once.
- **`raise`, not `return`:** an exception jumps straight out of every function, including the route that called `find_diamond`. That's why `get_diamond` needs no `if`.
- **No traceback in the terminal this time:** the log shows `"GET /diamonds/99 HTTP/1.1" 404 Not Found`. A 404 is an expected answer, not a crash.
- **Also change `max(diamonds) + 1` to `max(diamonds, default=0) + 1`** in `create_diamond`. Once deleting is possible, the dict can become empty, and `max()` of an empty dict raises `ValueError`. `default=0` makes the first id 1.

## Step 2: Update with PATCH

Add a model under `DiamondOut`:
```python
class DiamondPatch(BaseModel):
    carat: float | None = Field(default=None, gt=0, le=6)
    cut: Cut | None = None
    color: Color | None = None
    clarity: Clarity | None = None
    price: int | None = Field(default=None, gt=0, le=100_000)
    cost: int | None = Field(default=None, gt=0)
```
and a route at the end:
```python
@app.patch("/diamonds/{diamond_id}", response_model=DiamondOut)
def update_diamond(diamond_id: int, changes: DiamondPatch) -> dict:
    diamond = find_diamond(diamond_id)
    diamond.update(changes.model_dump(exclude_none=True))
    return diamond
```
In `/docs`, open **PATCH /diamonds/{diamond_id}** → Try it out, put `2` in `diamond_id`, and send:
```http
PATCH http://127.0.0.1:8001/diamonds/2
Content-Type: application/json

{"price": 2199}
```
```
200 OK
{
  "carat": 0.72,
  "cut": "Very Good",
  "color": "E",
  "clarity": "SI2",
  "price": 2199,
  "id": 2
}
```
Then `{"cut": "Premium", "price": null}`, and then `{"price": -5}`:
```http
PATCH http://127.0.0.1:8001/diamonds/2
Content-Type: application/json

{"cut": "Premium", "price": null}
```
```
200 OK
{
  "carat": 0.72,
  "cut": "Premium",
  "color": "E",
  "clarity": "SI2",
  "price": 2199,
  "id": 2
}
```
```http
PATCH http://127.0.0.1:8001/diamonds/2
Content-Type: application/json

{"price": -5}
```
```
422 Unprocessable Content
{
  "detail": [
    {
      "type": "greater_than",
      "loc": [
        "body",
        "price"
      ],
      "msg": "Input should be greater than 0",
      "input": -5,
      "ctx": {
        "gt": 0
      }
    }
  ]
}
```
- **PATCH = change some fields; PUT = replace the whole thing.** For PUT you'd take a full `DiamondIn`. PATCH is what most front ends need ("just change the price"), so every field in `DiamondPatch` is optional: `X | None = None`.
- **The rules still apply** to the fields you send: `-5` fails `gt=0`. Leaving a field out is allowed.
- **`model_dump(exclude_none=True)`** gives only the fields that have a value: `{"price": 2199}`. **`dict.update()`** writes them into the stored diamond (like `$diamond->fill($data)->save()`), so the other fields stay as they were.
- **Why `exclude_none`?** A field you leave out is `None`, and so is a field sent as `null`. Both are dropped, so `"price": null` keeps the old price instead of breaking it. (The FastAPI tutorial uses `exclude_unset=True`, which keeps an explicit `null`. Here that would store `price = None`, and the response model would then fail with a 500.)
- **`diamond` is the same dict object that lives in `diamonds`**, not a copy (Task 4: `=` never copies). Updating it updates the stock.

## Step 3: Delete

```python
@app.delete("/diamonds/{diamond_id}", status_code=204)
def delete_diamond(diamond_id: int) -> None:
    find_diamond(diamond_id)
    del diamonds[diamond_id]
```
Delete diamond 5, then try again:
```http
DELETE http://127.0.0.1:8001/diamonds/5
```
```
204 No Content
(no body)
```
```http
DELETE http://127.0.0.1:8001/diamonds/5
```
```
404 Not Found
{
  "detail": "Diamond 5 not found"
}
```
- **204 = "done, and there's nothing to send back"**, like Laravel's `response()->noContent()`. The function returns `None` (`-> None`) and the reply has no body at all. In `/docs` you see **Code 204** and no response body.
- **`find_diamond(diamond_id)` here only checks** that the diamond exists (404 otherwise). Its return value isn't needed, so it isn't stored.
- **`del diamonds[diamond_id]`** removes the key from the dict.
- **The second DELETE is a 404**: the diamond is already gone.

## Step 4: Check, then restart

```http
GET http://127.0.0.1:8001/diamonds?max_price=7000
```
```
200 OK
[
  {
    "carat": 0.23,
    "cut": "Ideal",
    "color": "E",
    "clarity": "SI2",
    "price": 326,
    "id": 1
  },
  {
    "carat": 0.72,
    "cut": "Premium",
    "color": "E",
    "clarity": "SI2",
    "price": 2199,
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
Now stop the server (Ctrl+C), start it again, and ask for diamond 2:
```http
GET http://127.0.0.1:8001/diamonds/2
```
```
200 OK
{
  "carat": 0.72,
  "cut": "Very Good",
  "color": "E",
  "clarity": "SI2",
  "price": 2376,
  "id": 2
}
```
- **Before the restart:** diamond 2 is Premium at $2,199, and diamond 5 ($6,315) is gone from the list.
- **After the restart:** diamond 2 is back to Very Good at $2,376, and `GET /diamonds/5` works again. The stock is a Python dict in memory, rebuilt from the code at every start. Saving your file (auto-reload) resets it too.
- **That's why real APIs use a database.** For this task, memory is fine: you're learning routes, not storage. (Laravel's equivalent would be an array in a controller.)

## Recap
- `raise HTTPException(status_code=404, detail=...)` ≈ `abort(404)`. A `find_diamond()` helper ≈ `findOrFail`.
- `PATCH` with an all-optional model + `model_dump(exclude_none=True)` + `dict.update()` changes only what was sent.
- `DELETE` with `status_code=204` and `-> None` sends no body.
- Status codes so far: 200 OK, 201 Created, 204 No Content, 404 Not Found, 422 invalid input, 500 your bug.

📚 **Learn more:** [FastAPI: Handling Errors (`HTTPException`)](https://fastapi.tiangolo.com/tutorial/handling-errors/) · [Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/) · [Body - Updates (PUT and PATCH)](https://fastapi.tiangolo.com/tutorial/body-updates/) · [PATCH (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PATCH)

Then commit, push, and ask Claude for **"check, then ex 5"** (dependencies: pagination and an API key).
