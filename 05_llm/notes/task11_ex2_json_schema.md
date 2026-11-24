# Task 11, Exercise 2: JSON Schema + Pydantic (worked example)

Make `ex2_json_schema.py` in `05_llm/task11/`, and add one function to your `llm.py` (finished files: [ex2_json_schema.py](../examples/task11/ex2_json_schema.py), [llm.py](../examples/task11/llm.py)). The outputs below are real (run on 2026-11-24, with `openai` 3.46.0 and Pydantic 2.14.1).

**The idea:** instead of asking nicely, send a **JSON Schema** with the request. Ollama then blocks every token that would break the schema, so a complete reply **has** to have your 5 keys, with numbers where you said numbers. This is called **structured output**. You don't write the schema by hand: a Pydantic class (Task 8) makes it, and the same class checks the reply.

- **Laravel analogy:** a Form Request for the *model's* answer. The rules go out with the request, and the reply is validated against them when it comes back.

## Step 1: A Pydantic class makes the schema

```python
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
```
```powershell
python ex2_json_schema.py
```
```
{
  "properties": {
    "carat": {
      "title": "Carat",
      "type": "number"
    },
    "cut": {
      "title": "Cut",
      "type": "string"
    },
    "color": {
      "title": "Color",
      "type": "string"
    },
    "clarity": {
      "title": "Clarity",
      "type": "string"
    },
    "price": {
      "title": "Price",
      "type": "number"
    }
  },
  "required": [
    "carat",
    "cut",
    "color",
    "clarity",
    "price"
  ],
  "title": "Diamond",
  "type": "object"
}
```
- **`model_json_schema()`** describes the class as a dict, in the JSON Schema standard. FastAPI uses the same thing for the request bodies in your `/docs` page (Task 8).
- **`float` → `"number"`, `str` → `"string"`.** A field without a default is listed in `"required"`.
- **`json.dumps(data, indent=2)`** is the opposite of `json.loads`: Python data → JSON text (`json_encode` with `JSON_PRETTY_PRINT`).

## Step 2: Send the schema with the request

Add:
```python
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
```
```
'{"carat": 2.01, "cut": "PREMIUM", "color": "J", "clarity": "SI2", "price": 14999}'
carat=2.01 cut='PREMIUM' color='J' clarity='SI2' price=14999.0
Price + 10%: $16,499
```

### Why each part works
- **No fence, and `14999` is a number.** The listing says `$14,999!`, but a JSON number can't contain `$` or a comma, so the model couldn't write them.
- **The prompt doesn't mention JSON at all.** The schema does that work.
- **`response_format`** carries the schema. `name` is a label that the API asks for.
- **`Diamond.model_validate_json(reply)`** parses the JSON text *and* validates it, in one step. The result is a `Diamond` object, so you write `diamond.price` (with autocompletion) instead of `row["price"]`.
- **`price=14999.0`:** Pydantic turned the whole number into the `float` you declared.

### The model doesn't see your schema
I sent the same messages 3 ways and looked at the prompt tokens:

| `response_format` | Prompt tokens | Reply |
|---|---|---|
| none | 50 | `The diamond is a 2.01 carat, J colour, SI2 clarity.` |
| `{"type": "json_object"}` | 50 | `{"cut":"Premium","carats":"2.01","colour":"J","clarity":"SI2"}` |
| `json_schema` | 50 | `{"carat": 2.01, "cut": "PREMIUM", "color": "J", "clarity": "SI2", "price": 14999}` |

- **50 tokens every time:** on Ollama the schema isn't added to the prompt. It only **limits what the model may write**. So explain the fields in the prompt when the key names alone aren't clear.
- **`json_object` ("JSON mode") is weaker:** the JSON is valid, but the model chose its own keys (`carats`, `colour`), left out the price and wrote the carat as text. Use `json_schema`.

## Step 3: What a validation error looks like

Add:
```python
try:
    Diamond.model_validate_json('{"carat": "heavy", "cut": "Ideal", "price": 900}')
except ValidationError as error:
    print(f"{error.error_count()} problems:")
    for problem in error.errors():
        print(f"  {problem['loc'][0]}: {problem['msg']}")
```
```
3 problems:
  carat: Input should be a valid number, unable to parse string as a number
  color: Field required
  clarity: Field required
```
- **All the problems are reported at once**, not only the first, like `$validator->errors()` in Laravel.
- **`loc`** is where the problem is (a tuple, because fields can be nested), and **`msg`** is what's wrong. FastAPI's 422 responses have the same `loc` and `msg`.
- **Why validate when the schema already limits the reply?** Not every server or model enforces schemas, a reply can be cut off, and your own Pydantic validators (Python code) can't be written in a schema. Treat LLM output like user input: **always validate it**.
- **Pydantic is a little forgiving:** `"price": "6500"` (text) is accepted and becomes `6500.0`, but `"$6,500"` is refused (I tested both).

## Step 4: `parse()`, both steps in one function

Add this import to your `llm.py`, after the `openai` import:
```python
from pydantic import BaseModel
```
And this function at the end:
```python
def parse[T: BaseModel](messages: list[dict], schema: type[T], **settings) -> T:
    """Send messages and return the reply as a validated `schema` object."""
    settings = {"temperature": 0, "seed": 42, "max_tokens": 300} | settings
    with friendly_errors():
        response = client.chat.completions.parse(
            model=MODEL, messages=messages, response_format=schema, **settings
        )
    return response.choices[0].message.parsed
```
Then, at the end of `ex2_json_schema.py`:
```python
for text in LISTINGS:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": text}]
    print(llm.parse(messages, Diamond))
```
```
carat=1.2 cut='ideal' color='G' clarity='VS1' price=6500.0
carat=0.5 cut='very good' color='E' clarity='VVS2' price=2100.0
carat=2.01 cut='PREMIUM' color='J' clarity='SI2' price=14999.0
carat=0.9 cut='good' color='H' clarity='SI1' price=3400.0
carat=1.5 cut='Fair' color='F' clarity='I1' price=4900.0
carat=0.31 cut='ideal' color='D' clarity='flawless (IF)' price=1850.0
```

### Why each part works
- **`client.chat.completions.parse(..., response_format=Diamond)`** takes the **class** itself. The package makes the schema, sends it, and validates the reply. It also adds `"additionalProperties": false` (no extra keys allowed).
- **`message.parsed`** is the finished `Diamond` object (`message.content` still has the raw text).
- **`def parse[T: BaseModel](..., schema: type[T]) -> T`** is a **generic** function (Python 3.12+). Read it as: "give me any Pydantic class, and I return an object of *that* class". So your editor knows that `parse(messages, Diamond)` returns a `Diamond`. PHP has this only in comments: `@template T of Model`, `@param class-string<T>`, `@return T`.
- **`type[T]`** means the class itself, not an object of it (like passing `Diamond::class`).

### What to notice
- **Every carat and price is correct,** even `3.4k dollars` → `3400.0`. With JSON asked for in the prompt, 0 of 6 rows were usable.
- **The text fields are still loose:** `'ideal'`, `'PREMIUM'`, `'flawless (IF)'`. They're allowed, because the schema says only `"string"`. The fix is to list the permitted values in the class (Python's `Literal`), so the model can't write anything else.

## ⚠️ What a schema doesn't protect you from

**1. Invented values.** Every field is required, so the model must write *something*. I tried 2 listings with missing facts (3 times each, always the same result):

| Listing | Result |
|---|---|
| `Plain gold wedding band, size 7, no stones, $300` | `carat=0.0 cut='round' color='yellow' clarity='SI1' price=300.0` |
| `Beautiful 1 carat diamond, great sparkle. Call me!` | `carat=1.0 cut='great sparkle' color='not specified' clarity='not specified' price=0.0` |

There's no diamond in the first one, but it got a clarity of `SI1`. Both passed validation. **A schema checks the form, not the truth.** A good start is to let a field be empty, with `price: float | None` (Laravel's `nullable`).

**2. Cut-off JSON.** With `max_tokens=10` the reply was `{"carat": 2.01,` with `finish_reason='length'`. `llm.parse` then raises `openai.LengthFinishReasonError`. That's a child of `OpenAIError`, but not one of the types `friendly_errors` looks for, so **you see the long traceback** instead of an `LLMError`. Give JSON replies enough `max_tokens` (300 is plenty here).

**3. Impossible values.** `cut="banana"` and `price=-5` pass validation (I tested it), because `str` and `float` allow them. You know the tool for the price from Task 8: `Field(gt=0)`.

**My runs:** I ran the script 3 times. In Step 4, all 3 runs gave the same 6 lines. In Step 2, run 1 wrote `"Premium"` and the others `"PREMIUM"`: the "nearly repeatable" effect from Task 10. The token table and the tests in this section came from a separate script.

## Recap
- `response_format` with a JSON Schema **forces** the form of the reply; a prompt only asks for it.
- One Pydantic class does both jobs: it makes the schema (`model_json_schema`) and checks the reply (`model_validate_json`). `client.chat.completions.parse` does both in one call.
- `json_object` asks only for valid JSON. `json_schema` fixes your keys and types too.
- A schema can't stop invented facts, cut-off replies or values that your types allow. Validate, and give fields a way to be empty.

📚 **Learn more:** [Ollama: structured outputs](https://docs.ollama.com/capabilities/structured-outputs) · [`openai` package: `parse` helpers](https://github.com/openai/openai-python/blob/main/helpers.md) · [Pydantic: JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/) · [Pydantic: models](https://docs.pydantic.dev/latest/concepts/models/) · [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/) · [Generic functions](https://docs.python.org/3/reference/compound_stmts.html#generic-functions)
