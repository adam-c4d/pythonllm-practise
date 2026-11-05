# Task 8, Exercise 7: Organise it like a real project: settings and routers (worked example)

Still in `04_fastapi/task8/`. This exercise **moves** code from `main.py` into 4 new files and adds settings (finished files: [examples/task8/ex7/](../examples/task8/ex7/)). The outputs below are real (run on 2026-11-05).

**The idea:** `main.py` now has about 150 lines doing 5 jobs. A Laravel project spreads the same jobs over folders: `config/` + `.env`, `app/Http/Requests`, middleware, controllers, and `routes/api.php`. The FastAPI equivalent:

| File | Job | Laravel |
|---|---|---|
| `config.py` | settings from environment variables | `config/app.php` + `.env` |
| `schemas.py` | grade types and Pydantic models | FormRequests + API Resources |
| `dependencies.py` | pagination and the API key check | middleware, shared traits |
| `diamonds.py` | the stock and the 5 diamond routes, on an `APIRouter` | a controller + its route group |
| `main.py` | creates the app, plugs in the router, `/` and `/grades` | `bootstrap/app.php` + `routes/api.php` |

The tests from Exercise 6 are your safety net: if they still pass after the move, the API still works.

## Step 1: `config.py`: settings from the environment

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    shop_name: str = "Diamond Shop"
    api_key: str = "dev-secret"


settings = Settings()
```
Check it from the second terminal, inside `task8/`:
```powershell
python -c "from config import settings; print(settings)"
```
```
shop_name='Diamond Shop' api_key='dev-secret'
```
- **`BaseSettings` is a Pydantic model that fills itself from environment variables.** The field `shop_name` reads `SHOP_NAME` (upper or lower case both work); `api_key` reads `API_KEY`. If a variable isn't set, the default is used. It's Laravel's `env('SHOP_NAME', 'Diamond Shop')`, with type checking: `port: int` would reject `PORT=abc` at start-up.
- **`settings = Settings()`** reads the environment **once**, when the module is imported. Other files do `from config import settings` and use `settings.api_key`, like `config('app.key')`.
- **`env_file=".env"`** also reads a `.env` file in the folder you start from, if there is one. A real environment variable beats the `.env` file, which beats the default (I checked all 3). Same order as Laravel.
- **`pydantic_settings`** comes with `fastapi[standard]`, so there's nothing to install.
- **`python -c "..."`** runs one line of Python without making a file. Handy for quick checks.

## Step 2: `schemas.py`: the types and models

Move the 3 grade types and the 4 models out of `main.py` into a new file:
```python
from typing import Literal

from pydantic import BaseModel, Field

Cut = Literal["Fair", "Good", "Very Good", "Premium", "Ideal"]
Color = Literal["J", "I", "H", "G", "F", "E", "D"]
Clarity = Literal["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]


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


class DiamondPatch(BaseModel):
    carat: float | None = Field(default=None, gt=0, le=6)
    cut: Cut | None = None
    color: Color | None = None
    clarity: Clarity | None = None
    price: int | None = Field(default=None, gt=0, le=100_000)
    cost: int | None = Field(default=None, gt=0)
```
Nothing new here: it's the same code, in its own file.

- **"Schemas" is the usual FastAPI name for the Pydantic models**, to tell them apart from database models (Eloquent models would live in `models.py`).
- **This file imports nothing of yours**, so any other file can import it without circular imports.

## Step 3: `dependencies.py`: the shared checks

```python
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query

from config import settings


def pagination(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict[str, int]:
    return {"skip": skip, "limit": limit}


Pagination = Annotated[dict[str, int], Depends(pagination)]


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Missing or wrong API key")
```
- **The only change: `settings.api_key` instead of `API_KEY`.** The key is no longer written in the code. Delete the `API_KEY = "dev-secret"` line from `main.py`.
- **The 2 import blocks:** third-party (`fastapi`), then your own modules (`config`). `04_fastapi/ruff.toml` tells Ruff which names are yours, so **Shift+Alt+O** keeps them apart.

## Step 4: `diamonds.py`: a router for the 5 diamond routes

```python
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException

from dependencies import Pagination, require_api_key
from schemas import Cut, DiamondIn, DiamondOut, DiamondPatch

router = APIRouter(prefix="/diamonds", tags=["diamonds"])

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


def find_diamond(diamond_id: int) -> dict:
    if diamond_id not in diamonds:
        raise HTTPException(status_code=404, detail=f"Diamond {diamond_id} not found")
    return diamonds[diamond_id]


FoundDiamond = Annotated[dict, Depends(find_diamond)]


@router.get("", response_model=list[DiamondOut])
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


@router.get("/{diamond_id}", response_model=DiamondOut)
def get_diamond(diamond: FoundDiamond) -> dict:
    return diamond


@router.post(
    "",
    status_code=201,
    response_model=DiamondOut,
    dependencies=[Depends(require_api_key)],
)
def create_diamond(diamond: DiamondIn) -> dict:
    new_id = max(diamonds, default=0) + 1
    diamonds[new_id] = {"id": new_id, **diamond.model_dump()}
    return diamonds[new_id]


@router.patch(
    "/{diamond_id}",
    response_model=DiamondOut,
    dependencies=[Depends(require_api_key)],
)
def update_diamond(diamond: FoundDiamond, changes: DiamondPatch) -> dict:
    diamond.update(changes.model_dump(exclude_none=True))
    return diamond


@router.delete(
    "/{diamond_id}",
    status_code=204,
    dependencies=[Depends(require_api_key)],
)
def delete_diamond(diamond: FoundDiamond) -> None:
    del diamonds[diamond["id"]]
```
- **`APIRouter` is a mini app**: it collects routes, and `main.py` plugs it in. It's `Route::prefix('diamonds')->group(...)`, in its own file, like a controller.
- **`prefix="/diamonds"`** is added in front of every route here: `@router.get("/{diamond_id}")` becomes `GET /diamonds/{diamond_id}`. **`""`** means the prefix itself, `/diamonds`. (`"/"` would make it `/diamonds/`, with a trailing slash.)
- **`tags=["diamonds"]`** groups these routes in `/docs`.
- **`@app.` became `@router.`**, and the paths lost their `/diamonds` start. The function bodies didn't change at all.
- **The stock moved here too**, next to the only code that uses it. Later, a database would replace this dict, and only this file would change.

## Step 5: `main.py`, now short

Replace all of `main.py` with:
```python
from typing import get_args

from fastapi import FastAPI

import diamonds
from config import settings
from schemas import Clarity, Color, Cut

app = FastAPI(title=settings.shop_name)
app.include_router(diamonds.router)


@app.get("/")
def home() -> dict[str, str]:
    return {"message": f"Welcome to {settings.shop_name}"}


@app.get("/grades")
def grades() -> dict[str, tuple[str, ...]]:
    return {
        "cut": get_args(Cut),
        "color": get_args(Color),
        "clarity": get_args(Clarity),
    }
```
Start the server as usual and open `/docs`. At the top there are now 2 sections: **diamonds** with the 5 bars (GET, POST, GET, PATCH, DELETE) and **default** with `GET /` and `GET /grades`. **Schemas** at the bottom lists `DiamondIn`, `DiamondOut`, `DiamondPatch` and the 2 validation-error models.

- **`app.include_router(diamonds.router)`** registers every route of the router, like Laravel loading `routes/api.php`. A bigger app has one router per topic (`orders.router`, `customers.router`) and one `include_router` line each.
- **`import diamonds`** imports the module; `diamonds.router` is its `router` object. (In `diamonds.py`, the name `diamonds` is the dict; here it's the module. Each file has its own names.)
- **The title and welcome message come from the settings**, so another shop could run the same code under its own name.

## Step 6: Fix the imports in the tests, and run them

In `test_main.py`, the top now starts like this (2 changed lines: the `config` import and `AUTH`):
```python
from fastapi.testclient import TestClient

from config import settings
from main import app

client = TestClient(app)
AUTH = {"X-API-Key": settings.api_key}
```
and the last line of `test_home` becomes:
```python
    assert response.json() == {"message": f"Welcome to {settings.shop_name}"}
```
In `try_models.py`, change `from main import DiamondIn, DiamondOut` to `from schemas import DiamondIn, DiamondOut`. Then:
```powershell
pytest -q
```
```
........                                                                 [100%]
8 passed in 0.44s
```
- **8 passed: the refactor changed nothing on the outside.** This is why you wrote the tests first. Moving 150 lines between files without tests is guesswork.
- **The tests read the key and the shop name from `settings`**, so they pass whatever the environment says. Before this change, `$env:SHOP_NAME = "..."` would have broken `test_home`.
- **`from main import app` still works**: `main.py` builds the full app, routers included.

## Step 7: Change the settings without touching the code

Make a real random key (yours will be different):
```powershell
python -c "import secrets; print(secrets.token_urlsafe(24))"
```
```
AXD928FktGUyVJH5svjQJsA8qpGiD6YS
```
Stop the server (Ctrl+C), set 2 environment variables **in the same terminal**, and start it again:
```powershell
$env:SHOP_NAME = "Mohali Diamonds"
$env:API_KEY = "AXD928FktGUyVJH5svjQJsA8qpGiD6YS"
fastapi dev main.py --port 8001
```
```http
GET http://127.0.0.1:8001/
```
```
200 OK
{
  "message": "Welcome to Mohali Diamonds"
}
```
The old key is now wrong, and the new one works:
```http
POST http://127.0.0.1:8001/diamonds
X-API-Key: dev-secret
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
X-API-Key: AXD928FktGUyVJH5svjQJsA8qpGiD6YS
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
- **`secrets.token_urlsafe(24)`** makes 24 random bytes, written as 32 URL-safe characters. Use the `secrets` module for keys and passwords, never `random`.
- **`$env:NAME = "value"`** sets an environment variable in this PowerShell window only, until you close it. `Remove-Item Env:API_KEY` removes it again. The server reads them at start-up, so set them **before** `fastapi dev`.
- **Same code, different behaviour:** that's the point of settings. Your laptop uses the defaults, and the production server sets real values (Render, Docker and Cloud Run all have a place to type environment variables).
- **A `.env` file works too** (one `NAME=value` per line, in `task8/`). But your `.gitignore` is still switched off, so **Git would commit your secret**. Before you ever make a `.env` file, un-comment the `.env` line in `.gitignore` (you'll need it for the LLM API keys in Phase 5). Commit a `.env.example` with fake values instead, like Laravel does.

## Recap
- `BaseSettings` reads typed settings from environment variables (and `.env`), with defaults ≈ `config()` + `env()`. Secrets never go in the code.
- `APIRouter(prefix=..., tags=[...])` groups routes in their own file ≈ a controller with `Route::prefix()->group()`; `app.include_router(...)` plugs it in.
- Split by job: `config.py`, `schemas.py`, `dependencies.py`, one router per topic, and a short `main.py`.
- Refactor with the tests running: 8 passed before and after.

📚 **Learn more:** [FastAPI: Bigger Applications (`APIRouter`)](https://fastapi.tiangolo.com/tutorial/bigger-applications/) · [FastAPI: Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/) · [Pydantic: Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) · [`secrets`](https://docs.python.org/3/library/secrets.html)

## ✅ Task 8 done when
- [ ] `04_fastapi/task8/` has `main.py`, `config.py`, `schemas.py`, `dependencies.py`, `diamonds.py`, `test_main.py` and `try_models.py`.
- [ ] `pytest -q` prints `8 passed`, and Ruff shows no problems in the folder.
- [ ] You can do every request of Exercises 2–5 in `/docs`.

Then commit, push, and ask Claude to **"review all"**. That finishes Task 8. Next is Task 9: serving your diamond price model.
