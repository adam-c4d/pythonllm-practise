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
