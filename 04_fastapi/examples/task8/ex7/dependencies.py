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
