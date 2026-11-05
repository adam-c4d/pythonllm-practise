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
