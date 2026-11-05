from typing import Literal

from pydantic import BaseModel, Field

Cut = Literal["Fair", "Good", "Very Good", "Premium", "Ideal"]
Color = Literal["J", "I", "H", "G", "F", "E", "D"]
Clarity = Literal["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]


class DiamondIn(BaseModel):
    carat: float = Field(gt=0, le=6, description="Weight (1 carat = 0.2 g)")
    cut: Cut
    color: Color
    clarity: Clarity
    depth: float = Field(ge=40, le=80, description="Total depth in %")
    table: float = Field(ge=40, le=100, description="Width of the top in %")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
                 "depth": 61.5, "table": 56.0}
            ]
        }
    }


class Prediction(BaseModel):
    price: int = Field(description="Predicted price in US dollars")
