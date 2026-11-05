# Task 8, Exercise 3: Request bodies with Pydantic (worked example)

Continue in `04_fastapi/task8/main.py`, and make a new file `try_models.py` next to it (finished files: [examples/task8/ex3/](../examples/task8/ex3/)). The outputs below are real (run on 2026-11-05).

**The idea:** a **Pydantic model** is a class that lists the fields of some data, with their types and rules. Give it a dict and you get either a clean object or a list of every problem. It's a Laravel **FormRequest** (`rules()`) and a **DTO** in one. FastAPI uses models in two directions: **in** (validate the JSON body a client sends) and **out** (decide which fields the reply contains, like an **API Resource**).

**Add to the imports at the top of `main.py`** (then Shift+Alt+O to sort):
```python
from pydantic import BaseModel, Field
```

## Step 1: Three models

Put these under the `Cut` / `Color` / `Clarity` lines:
```python
class DiamondBase(BaseModel):
    carat: float = Field(gt=0, le=6)
    cut: Cut
    color: Color
    clarity: Clarity
    price: int = Field(gt=0, le=100_000, description="Selling price in US dollars")


class DiamondIn(DiamondBase):
    cost: int = Field(gt=0, description="What the shop paid. Never shown to customers.")


class DiamondOut(DiamondBase):
    id: int
```
Nothing to run yet; Step 2 tries the models out.

- **`class DiamondBase(BaseModel)`** makes a Pydantic model. Each line is a field: `name: type`. A field without a default is **required**.
- **`Field(gt=0, le=6)`** adds rules: carat greater than 0 and at most 6 (the biggest diamond in Task 6's data is 5.01). `gt`/`ge`/`lt`/`le` = greater than / greater or equal / less than / less or equal. In Laravel: `'carat' => 'required|numeric|gt:0|max:6'`.
- **`cut: Cut`** reuses the `Literal` from Exercise 2, so only the 5 real cuts pass. `100_000` is just `100000`; Python lets you put `_` in numbers to make them readable.
- **Inheritance, as in PHP's `extends`:** `DiamondIn` = the base fields + `cost` (what the shop sends **in**). `DiamondOut` = the base fields + `id` (what customers get **out**: no `cost`). The shared fields are written once.
- **`description=...`** appears in `/docs`. It's documentation for the people who use your API.

## Step 2: Try the models without FastAPI

`try_models.py`:
```python
from pydantic import ValidationError

from main import DiamondIn, DiamondOut

data = {"carat": "0.5", "cut": "Ideal", "color": "E", "clarity": "VS1",
        "price": 1800, "cost": 1100}
diamond = DiamondIn.model_validate(data)
print(diamond)
print(diamond.carat + 0.1, type(diamond.carat))
print(diamond.model_dump())

stored = {"id": 6, **diamond.model_dump()}
print(DiamondOut.model_validate(stored).model_dump())

bad = {"carat": -1, "cut": "Excellent", "color": "E", "price": 1800}
try:
    DiamondIn.model_validate(bad)
except ValidationError as error:
    print(error)
```
Run it in your second `(dsllm)` terminal, inside `task8/`:
```powershell
python try_models.py
```
```
carat=0.5 cut='Ideal' color='E' clarity='VS1' price=1800 cost=1100
0.6 <class 'float'>
{'carat': 0.5, 'cut': 'Ideal', 'color': 'E', 'clarity': 'VS1', 'price': 1800, 'cost': 1100}
{'carat': 0.5, 'cut': 'Ideal', 'color': 'E', 'clarity': 'VS1', 'price': 1800, 'id': 6}
4 validation errors for DiamondIn
carat
  Input should be greater than 0 [type=greater_than, input_value=-1, input_type=int]
    For further information visit https://errors.pydantic.dev/2.14/v/greater_than
cut
  Input should be 'Fair', 'Good', 'Very Good', 'Premium' or 'Ideal' [type=literal_error, input_value='Excellent', input_type=str]
    For further information visit https://errors.pydantic.dev/2.14/v/literal_error
clarity
  Field required [type=missing, input_value={'carat': -1, 'cut': 'Exc...or': 'E', 'price': 1800}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.14/v/missing
cost
  Field required [type=missing, input_value={'carat': -1, 'cut': 'Exc...or': 'E', 'price': 1800}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.14/v/missing
```
- **`from main import DiamondIn`:** `main.py` is a normal Python module, so another script can import from it (like Task 2's `from models import Sale`). Importing it creates `app` but doesn't start a server.
- **`model_validate(data)`** checks a dict and returns a `DiamondIn` object, like `Validator::make($data, $rules)->validated()`. **`"0.5"` (text) became the number `0.5`**: Pydantic converts when it's safe, so `diamond.carat + 0.1` is real maths.
- **`model_dump()`** turns the object back into a plain dict, the same as `$request->validated()`. `{"id": 6, **diamond.model_dump()}` builds a new dict: `id` first, then all the fields (`**` unpacks a dict, as in Task 2).
- **`DiamondOut.model_validate(stored)` dropped `cost`.** `DiamondOut` has no `cost` field, and Pydantic **ignores** extra keys by default. That's how the response model will hide it.
- **`ValidationError` lists every problem at once**, each with the field, the message and the input. FastAPI turns exactly this into the 422 reply. (Ruff knows `main` is your own module thanks to `04_fastapi/ruff.toml`, so Shift+Alt+O keeps it in its own import block.)

## Step 3: `POST /diamonds`

Add to `main.py`:
```python
@app.post("/diamonds", status_code=201, response_model=DiamondOut)
def create_diamond(diamond: DiamondIn) -> dict:
    new_id = max(diamonds) + 1
    diamonds[new_id] = {"id": new_id, **diamond.model_dump()}
    return diamonds[new_id]
```
In `/docs`, open the green **POST /diamonds** bar → **Try it out**, replace the example body with this, and click **Execute**:
```http
POST http://127.0.0.1:8001/diamonds
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
- **A parameter whose type is a Pydantic model is read from the JSON body.** That one line, `diamond: DiamondIn`, replaces a whole FormRequest class.
- **`status_code=201`** ("Created") is the right code for a new resource, like `response()->json($diamond, 201)`. Without it, FastAPI answers 200.
- **`response_model=DiamondOut`** = "whatever this function returns, send it in the shape of `DiamondOut`". The stored dict has `cost`, and the reply doesn't: this is your **API Resource**. The return type stays `-> dict`, because that's what the function really returns. (With `-> DiamondOut` and no `response_model`, your editor would complain that you return a dict.)
- **`max(diamonds) + 1`:** `max()` of a dict looks at the keys, so the next id is 6. A real database does this for you (auto-increment).
- **`/docs` shows the body and reply shapes.** Under **Request body** (marked *required*) the example is `{"carat": 1, "cut": "Fair", "color": "J", "clarity": "I1", "price": 1, "cost": 1}`: a valid made-up diamond built from your rules. The 201 example has `id` and no `cost`. Each model also appears under **Schemas** at the bottom of the page.

## Step 4: A bad body

```http
POST http://127.0.0.1:8001/diamonds
Content-Type: application/json

{"carat": 0, "cut": "Excellent", "color": "E", "clarity": "VS1", "price": "a lot"}
```
```
422 Unprocessable Content
{
  "detail": [
    {
      "type": "greater_than",
      "loc": [
        "body",
        "carat"
      ],
      "msg": "Input should be greater than 0",
      "input": 0,
      "ctx": {
        "gt": 0.0
      }
    },
    {
      "type": "literal_error",
      "loc": [
        "body",
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
        "body",
        "price"
      ],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "a lot"
    },
    {
      "type": "missing",
      "loc": [
        "body",
        "cost"
      ],
      "msg": "Field required",
      "input": {
        "carat": 0,
        "cut": "Excellent",
        "color": "E",
        "clarity": "VS1",
        "price": "a lot"
      }
    }
  ]
}
```
- **`"loc": ["body", "carat"]`:** the error is in the JSON body, field `carat`. Compare Exercise 2's `["query", "cut"]`.
- **4 problems, 1 reply**, and `create_diamond` never ran, so nothing was saved. You didn't write a single `if`.
- **`"gt": 0.0`** is the rule written as a decimal, because `carat` is a `float`. (`/docs` may show it as `0`; JavaScript doesn't print `.0`.)
- **Broken JSON** (for example a missing `}`) also gives a 422, with `"type": "json_invalid"` and `"msg": "JSON decode error"`.

## Step 5: Hide `cost` in the GET routes too

Add `response_model` to the 2 GET decorators from Exercise 2 (the functions stay the same):
```python
@app.get("/diamonds", response_model=list[DiamondOut])
```
```python
@app.get("/diamonds/{diamond_id}", response_model=DiamondOut)
```
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
- **The leak from Exercise 2 is fixed:** no `cost`. In Laravel you'd add `protected $hidden = ['cost'];` or return `new DiamondResource($diamond)`.
- **`list[DiamondOut]`** applies the model to every item in the list.
- **`id` now comes last**, because `DiamondOut` adds it after the inherited fields. The response model decides the order too. JSON clients look fields up by name, so order doesn't matter to them.
- **Rule of thumb:** every route that returns stored data gets a `response_model`, so a new secret field can never leak by accident.

## Recap
- A Pydantic model = fields with types and `Field(...)` rules. `model_validate(dict)` → object or `ValidationError`; `model_dump()` → dict.
- A route parameter typed with a model is the **JSON body**. Bad bodies get a 422 listing every error.
- `response_model=` shapes the reply (≈ API Resource / `$hidden`). In / out models via inheritance: `DiamondIn` has `cost`, `DiamondOut` has `id`.
- `status_code=201` for "created".

📚 **Learn more:** [FastAPI: Request Body](https://fastapi.tiangolo.com/tutorial/body/) · [Body - Fields](https://fastapi.tiangolo.com/tutorial/body-fields/) · [Response Model](https://fastapi.tiangolo.com/tutorial/response-model/) · [Extra Models (in / out)](https://fastapi.tiangolo.com/tutorial/extra-models/) · [Pydantic: Models](https://docs.pydantic.dev/latest/concepts/models/)

Then commit, push, and ask Claude for **"check, then ex 4"** (CRUD and error codes).
