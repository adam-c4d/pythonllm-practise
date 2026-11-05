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
