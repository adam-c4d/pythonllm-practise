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
