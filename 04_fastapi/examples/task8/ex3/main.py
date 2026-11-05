from typing import Annotated, Literal, get_args

from fastapi import FastAPI, Query
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


@app.get("/diamonds", response_model=list[DiamondOut])
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


@app.get("/diamonds/{diamond_id}", response_model=DiamondOut)
def get_diamond(diamond_id: int) -> dict:
    return diamonds[diamond_id]


@app.post("/diamonds", status_code=201, response_model=DiamondOut)
def create_diamond(diamond: DiamondIn) -> dict:
    new_id = max(diamonds) + 1
    diamonds[new_id] = {"id": new_id, **diamond.model_dump()}
    return diamonds[new_id]
