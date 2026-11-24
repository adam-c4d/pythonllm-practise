# Task 11, Exercise 1: Asking for JSON in the prompt (worked example)

Make a new folder `05_llm/task11/` with 3 files: `llm.py`, `listings.py` and `ex1_json_by_prompt.py` (finished files: [listings.py](../examples/task11/listings.py), [ex1_json_by_prompt.py](../examples/task11/ex1_json_by_prompt.py)). Ollama must be running with `qwen2.5:1.5b`. The outputs below are real (run on 2026-11-24).

**The idea:** until now the LLM's answer was text for a person to read. A program needs **data**: numbers it can add up and fields it can save. The task here is **extraction**: a free-text listing goes in, and `carat`, `cut`, `color`, `clarity` and `price` come out. The obvious way is to ask for JSON in the prompt. This exercise shows how far that gets you, so you know why Exercise 2 is better.

- **Laravel analogy:** you call someone else's API that says "returns JSON" but has no contract. `$response->json()` is `null` one day, and `"price": "$14,999"` the next.

## Step 1: The files

Copy your Task 10 `llm.py` (in a `(dsllm)` terminal, inside `05_llm/task11/`):
```powershell
Copy-Item ..\task10\llm.py .
```

`listings.py`:
```python
"""Six free-text diamond listings, and what a perfect extraction would return."""

LISTINGS = [
    "Lovely 1.2 carat ideal cut stone, colour G, clarity VS1, asking $6,500",
    "Selling my 0.5ct diamond. Cut: very good. Color E, VVS2. Price 2100 USD.",
    "PREMIUM cut, 2.01 carats, J colour, SI2 clarity - yours for $14,999!",
    "Engagement ring stone: 0.9 carat, good cut, H, SI1. Asking 3.4k dollars.",
    "Fair-cut 1.5 carat diamond, I1 clarity and colour F, only $4,900 or best offer",
    "Flawless (IF) 0.31 carat D colour ideal cut gem, $1,850",
]

EXPECTED = [
    {"carat": 1.2, "cut": "Ideal", "color": "G", "clarity": "VS1",
     "asking_price": 6500},
    {"carat": 0.5, "cut": "Very Good", "color": "E", "clarity": "VVS2",
     "asking_price": 2100},
    {"carat": 2.01, "cut": "Premium", "color": "J", "clarity": "SI2",
     "asking_price": 14999},
    {"carat": 0.9, "cut": "Good", "color": "H", "clarity": "SI1",
     "asking_price": 3400},
    {"carat": 1.5, "cut": "Fair", "color": "F", "clarity": "I1",
     "asking_price": 4900},
    {"carat": 0.31, "cut": "Ideal", "color": "D", "clarity": "IF",
     "asking_price": 1850},
]
```
- **The listings are messy on purpose:** `0.5ct`, `3.4k dollars`, `PREMIUM`, `or best offer`, and the same facts in a different order. One regular expression for all 6 would be painful, and this is where an LLM helps.
- **`EXPECTED` isn't used in Exercises 1 and 2.** It's the answer key for scoring the extraction later. (It says `asking_price`; these two exercises use `price`.)

## Step 2: Ask for JSON

```python
"""Task 11, Exercise 1: asking for JSON in the prompt, and why it's fragile."""

import json

import llm
from listings import LISTINGS

ASK_JSON = ("Extract the diamond from the listing as JSON with the keys "
            "carat, cut, color, clarity and price.")

reply = llm.ask(LISTINGS[0], system=ASK_JSON, max_tokens=150)
print(repr(reply))
try:
    print(json.loads(reply))
except json.JSONDecodeError as error:
    print("json.loads failed:", error)
```
```powershell
python ex1_json_by_prompt.py
```
```
'```json\n{\n  "carat": "1.2 carat",\n  "cut": "ideal cut",\n  "color": "G",\n  "clarity": "VS1",\n  "price": "6500"\n}\n```'
json.loads failed: Expecting value: line 1 column 1 (char 0)
```

### Why each part works
- **`llm.ask(text, system=...)`** is your Task 10 helper: rules in the system message, data in the user message.
- **`repr(reply)`** shows the string as Python sees it, with `\n` and the quotes visible (PHP's `var_export`). Use it whenever text looks right but doesn't parse.
- **`json.loads(text)`** turns JSON text into Python data, like `json_decode($text, true)`. Unlike PHP's default, it **raises an exception** on bad JSON instead of returning `null`.
- **Why it failed:** the reply starts with a Markdown fence (three backticks + `json`). Models often write JSON that way because it displays nicely in a chat. Character 0 is a backtick, which isn't JSON.
- **Look at the values too:** `"1.2 carat"` and `"6500"` are strings.

## Step 3: Ask more firmly, and clean up

Add:
```python
JSON_ONLY = ("Extract the diamond from the listing. Reply with JSON only, with "
             "the keys carat, cut, color, clarity and price.")


def strip_fences(text: str) -> str:
    """Remove the ```json ... ``` Markdown fence that models like to add."""
    return text.strip().removeprefix("```json").removesuffix("```").strip()


replies = [llm.ask(text, system=JSON_ONLY, max_tokens=150) for text in LISTINGS]
plain_ok = 0
rows = []
for reply in replies:
    try:
        json.loads(reply)
        plain_ok += 1
    except json.JSONDecodeError:
        pass
    try:
        rows.append(json.loads(strip_fences(reply)))
    except json.JSONDecodeError as error:
        print("Still not JSON:", error)
print(f"json.loads worked on {plain_ok} of {len(replies)} replies as they were")
print(f"After strip_fences: {len(rows)} of {len(replies)}")
```
```
json.loads worked on 3 of 6 replies as they were
After strip_fences: 6 of 6
```

### Why each part works
- **"Reply with JSON only" isn't enough:** half of the replies still came with a fence. A prompt is a request, not a rule.
- **`removeprefix` / `removesuffix`** cut the text off only if it's there, so clean replies pass through unchanged (Laravel's `Str::chopStart` / `Str::chopEnd`).
- **The list comprehension makes 6 calls**, one per listing, one after another.
- **All 6 parse now.** It's tempting to stop here. Don't.

## Step 4: JSON isn't the same as correct data

Add:
```python
CUTS = {"Fair", "Good", "Very Good", "Premium", "Ideal"}
usable = 0
for row in rows:
    problems = []
    for key in ["carat", "price"]:
        if not isinstance(row.get(key), int | float):
            problems.append(f"{key}={row.get(key)!r} is not a number")
    if row.get("cut") not in CUTS:
        problems.append(f"cut={row.get('cut')!r} is not a grade")
    usable += not problems
    print(f"{row.get('carat')!s:>5} carat: {'; '.join(problems) or 'OK'}")
print(f"Usable without more cleaning: {usable} of {len(rows)}")
```
```
  1.2 carat: carat='1.2' is not a number; price='6500' is not a number; cut='ideal' is not a grade
  0.5 carat: cut='very good' is not a grade
 2.01 carat: cut='PREMIUM' is not a grade
  0.9 carat: cut='good' is not a grade
  1.5 carat: price='$4,900 or best offer' is not a number
 0.31 carat: carat='0.31' is not a number; price='$1,850' is not a number; cut='ideal' is not a grade
Usable without more cleaning: 0 of 6
```

### Why each part works
- **`isinstance(value, int | float)`** asks: is it a number? JSON `6500` becomes an `int`, `1.2` a `float`, and `"6500"` a `str`, which fails.
- **`row.get(key)`** returns `None` for a missing key instead of crashing (PHP's `$row['key'] ?? null`).
- **`!r`** in an f-string means `repr(...)`. The quotes in `'1.2'` show that it's text, not a number. **`!s:>5`** means `str(...)`, right-aligned in 5 characters.
- **`usable += not problems`**: an empty list is falsy, so `not problems` is `True`, which counts as 1.
- **`'; '.join(problems) or 'OK'`**: an empty string is falsy too, so you get `'OK'` (PHP's `?:`).

### What to notice
- **0 of 6 rows can be used as they are.** In the diamonds data the grades are `Ideal` and `Very Good`, so `df["cut"] == "Ideal"` would miss `"ideal"`, without any error.
- **The same key has different types in different rows:** `carat` is sometimes a number and sometimes a string.
- **This check is only about form.** It doesn't look at `color` or `clarity`, and it can't tell whether a number is the *right* number.

**My runs:** I ran the script 3 times. Runs 2 and 3 gave the output above. Run 1 was different: only **1 of 6** replies parsed as they were, and prices came back as `'$14,999'` and `'4,900'`. All 3 runs ended with 6 of 6 after `strip_fences` and **0 of 6 usable**. So even with the same prompt, your cleaning code has to handle formats it hasn't seen yet.

## Recap
- `json.loads` raises `json.JSONDecodeError` on bad JSON. `repr()` shows what's really in the string.
- Models like to add Markdown fences, and "JSON only" in the prompt doesn't reliably stop it.
- **Valid JSON ≠ valid data.** Check the types and the allowed values as well.
- Every new cleaning rule handles one more format. Exercise 2 fixes the cause: the model is *only allowed* to write what your schema permits.

📚 **Learn more:** [`json.loads`](https://docs.python.org/3/library/json.html#json.loads) · [`str.removeprefix`](https://docs.python.org/3/library/stdtypes.html#str.removeprefix) · [`isinstance`](https://docs.python.org/3/library/functions.html#isinstance)
