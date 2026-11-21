"""Request and response shapes (like Laravel FormRequests and API Resources)."""

from typing import Literal

from pydantic import BaseModel, Field

Cut = Literal["Fair", "Good", "Very Good", "Premium", "Ideal"]
Color = Literal["J", "I", "H", "G", "F", "E", "D"]
Clarity = Literal["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]


class DiamondIn(BaseModel):
    """One diamond to price. Pydantic checks every field before our code runs."""

    carat: float = Field(gt=0, le=6, examples=[1.0])
    cut: Cut
    color: Color
    clarity: Clarity
    depth: float = Field(ge=40, le=80, examples=[62.0])
    table: float = Field(ge=40, le=100, examples=[58.0])


class PriceOut(BaseModel):
    """The predicted price, in US dollars."""

    price: float
