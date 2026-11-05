from pydantic import ValidationError

from schemas import DiamondIn, DiamondOut

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
