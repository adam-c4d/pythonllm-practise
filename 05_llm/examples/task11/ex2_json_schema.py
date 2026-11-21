"""Task 11, Exercise 2: a JSON Schema in response_format, checked by Pydantic."""

import json

from pydantic import BaseModel, ValidationError

import llm
from listings import LISTINGS


class Diamond(BaseModel):
    carat: float
    cut: str
    color: str
    clarity: str
    price: float


schema = Diamond.model_json_schema()
print(json.dumps(schema, indent=2))

SYSTEM = "Extract the diamond from the listing."
response = llm.client.chat.completions.create(
    model=llm.MODEL,
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": LISTINGS[2]}],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "diamond", "schema": schema},
    },
    temperature=0,
    seed=42,
)
reply = response.choices[0].message.content
print(repr(reply))
diamond = Diamond.model_validate_json(reply)
print(diamond)
print(f"Price + 10%: ${diamond.price * 1.1:,.0f}")

try:
    Diamond.model_validate_json('{"carat": "heavy", "cut": "Ideal", "price": 900}')
except ValidationError as error:
    print(f"{error.error_count()} problems:")
    for problem in error.errors():
        print(f"  {problem['loc'][0]}: {problem['msg']}")

for text in LISTINGS:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": text}]
    print(llm.parse(messages, Diamond))
