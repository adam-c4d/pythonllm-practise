# Task 10, Exercise 5: Prompt templates, zero-shot vs few-shot (worked example)

Make `ex5_few_shot.py` in `05_llm/task10/` (finished file: [examples/task10/ex5_few_shot.py](../examples/task10/ex5_few_shot.py)). The outputs below are real (run on 2026-11-24).

**The idea:** use the LLM as a **classifier**: a customer message goes in, one of 5 categories comes out. Then improve it **by changing the prompt only**, and **measure** each version on the same test messages, as you did with models in Phase 3. There are 2 ways to improve a prompt here:
- **definitions**: explain what each category means;
- **few-shot**: show a few solved examples. (**Zero-shot** = no examples.)

- **Laravel analogy:** the prompt template is a Blade view: fixed text with slots, filled in per request. The test list is a PHPUnit data provider.

**Why use this instead of scikit-learn?** A scikit-learn text classifier needs hundreds of labelled messages to train on. An LLM can do a fair job with none. The price: each call is slower and costs more.

## Step 1: The data

```python
"""Task 10, Exercise 5: prompt templates, zero-shot vs few-shot."""

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
MODEL = "qwen2.5:1.5b"

CATEGORIES = ["order_status", "pricing", "returns", "product_info", "complaint"]
PLAIN = (
    "Classify the customer message of a diamond shop into one of these "
    "categories: {categories}. Reply with the category only."
)
DEFINED = (
    "Classify the customer message of a diamond shop into one category:\n"
    "- order_status: where an order is, delivery, tracking, lost parcels\n"
    "- pricing: prices, discounts, payment\n"
    "- returns: refunds, exchanges, sending an item back\n"
    "- product_info: questions about stones, metals, grades and sizes\n"
    "- complaint: unhappy about quality, damage or service\n"
    "Reply with the category only."
)
EXAMPLES = [
    ("When will my necklace arrive?", "order_status"),
    ("What is the price of the heart-shaped pendant?", "pricing"),
    ("I want my money back, the colour is not what I expected.", "returns"),
    ("What does VVS1 clarity mean?", "product_info"),
    ("Your staff were rude to me on the phone.", "complaint"),
]
TESTS = [
    ("Where is my parcel? I ordered last Monday.", "order_status"),
    ("Do you give a discount if I buy two rings?", "pricing"),
    ("The ring doesn't fit, can I send it back for a refund?", "returns"),
    ("Is your 1 carat stone lab-grown or natural?", "product_info"),
    ("The stone fell out of the setting after a week. Very disappointed!",
     "complaint"),
    ("How much would a 0.5 carat VS1 diamond cost?", "pricing"),
    ("Can I exchange my earrings for a pendant?", "returns"),
    ("My order says delivered but nothing came.", "order_status"),
    ("Do you sell platinum wedding bands?", "product_info"),
    ("I waited 40 minutes in your shop and nobody helped me.", "complaint"),
]
```
- **`PLAIN` has a slot, `{categories}`.** It's a normal string, not an f-string: the slot is filled later with `.format(...)`.
- **`EXAMPLES` and `TESTS` share no messages.** Testing on messages shown in the prompt would be **data leakage** (Task 5 Ex 4): the model would just copy the answer.
- **5 examples, one per category.** A missing category would push the model towards the ones it has seen.

## Step 2: Build the messages

```python
def build_messages(template: str, message: str,
                   examples: list[tuple[str, str]]) -> list[dict]:
    """Fill the template, add the examples as earlier turns, then the message."""
    system = template.format(categories=", ".join(CATEGORIES))
    messages = [{"role": "system", "content": system}]
    for text, label in examples:
        messages.append({"role": "user", "content": text})
        messages.append({"role": "assistant", "content": label})
    messages.append({"role": "user", "content": message})
    return messages


for message in build_messages(PLAIN, "Do you sell gold chains?", EXAMPLES[:2]):
    print(f"{message['role']:>9}: {message['content']}")
```
```
   system: Classify the customer message of a diamond shop into one of these categories: order_status, pricing, returns, product_info, complaint. Reply with the category only.
     user: When will my necklace arrive?
assistant: order_status
     user: What is the price of the heart-shaped pendant?
assistant: pricing
     user: Do you sell gold chains?
```

### Why each part works
- **The examples are fake earlier turns.** As in Exercise 3, the model can't tell a real history from one you wrote. It sees 2 questions answered with a bare category name, so it continues the pattern.
- **`template.format(categories=...)`** fills the slot. `DEFINED` has no slot, and `.format` ignores names it doesn't need, so one function works for both templates.
- **Careful with `{}` in templates:** if your prompt contains JSON, `.format` reads its braces as slots. Write `{{` and `}}` for real braces (this comes up in Task 11).
- **Instructions go in `system`, the customer's text goes in `user`.** Keeping them apart makes it harder (not impossible) for a customer to write "ignore your instructions and..." That attack is called **prompt injection**.
- **`{message['role']:>9}`** right-aligns. Use single quotes inside the double-quoted f-string.

## Step 3: Classify and score

```python
def classify(template: str, message: str, examples: list[tuple[str, str]]) -> str:
    """Return the model's category for one message, tidied up."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=build_messages(template, message, examples),
        temperature=0,
        seed=42,
        max_tokens=10,
    )
    return response.choices[0].message.content.strip().lower()


def accuracy(template: str, examples: list[tuple[str, str]]) -> float:
    """Classify every test message; print the misses; return the share correct."""
    correct = 0
    for message, expected in TESTS:
        answer = classify(template, message, examples)
        if answer == expected:
            correct += 1
        else:
            print(f"    miss: {message!r} -> {answer!r} (expected {expected!r})")
    return correct / len(TESTS)


print(f"Zero-shot: {accuracy(PLAIN, []):.0%}")
```
```
    miss: 'Where is my parcel? I ordered last Monday.' -> 'returns' (expected 'order_status')
    miss: 'The stone fell out of the setting after a week. Very disappointed!' -> 'returns' (expected 'complaint')
    miss: 'My order says delivered but nothing came.' -> 'returns' (expected 'order_status')
Zero-shot: 70%
```
- **`temperature=0`**: for classification you want the most likely answer, not a creative one.
- **`max_tokens=10`** is enough for a category name, and stops the model from explaining itself.
- **`.strip().lower()`** forgives small differences (`" Pricing"`). Anything else that isn't a category counts as a miss, which is the safe choice.
- **All 3 misses are `returns`.** The model seems to think anything gone wrong with an order is a return. Reading the misses tells you what to fix; the 70% alone doesn't.

## Step 4: Compare the prompts

```python
for name, template, examples in [
    ("few-shot", PLAIN, EXAMPLES),
    ("zero-shot + definitions", DEFINED, []),
    ("few-shot + definitions", DEFINED, EXAMPLES),
]:
    print(f"{name}: {accuracy(template, examples):.0%}")
```
```
    miss: 'The stone fell out of the setting after a week. Very disappointed!' -> 'returns' (expected 'complaint')
    miss: 'My order says delivered but nothing came.' -> 'returns' (expected 'order_status')
few-shot: 80%
    miss: 'I waited 40 minutes in your shop and nobody helped me.' -> 'order_status' (expected 'complaint')
zero-shot + definitions: 90%
    miss: 'The stone fell out of the setting after a week. Very disappointed!' -> 'returns' (expected 'complaint')
few-shot + definitions: 90%
```

| Prompt | Accuracy | Misses |
|---|---|---|
| zero-shot | 70% | parcel, stone fell out, nothing came |
| few-shot | 80% | stone fell out, nothing came |
| zero-shot + definitions | 90% | waited 40 minutes |
| few-shot + definitions | 90% | stone fell out |

I ran the script 3 times and got the same 4 scores each time.

### How to read these numbers
- **The model never changed, only the text around the message.** Both techniques helped.
- **The definitions helped most here**, and they're short. Examples make every call longer: 10 more messages (5 pairs) each time.
- **10 test messages is too few to trust.** Each message is worth 10%, so 80% vs 90% is **one** message. It's the same small-group noise you saw in Task 4 Ex 5. A real test set needs 50–200 messages, and more for rare categories.
- **Don't tune on the test set.** If you read the misses, rewrite the prompt to fix them and test on the same 10 messages, the score looks better than it really is (Task 5 Ex 7: the test set is for once, at the end). Use one set for improving and another for the final score.
- **"The stone fell out... Very disappointed!" is arguable.** Complaint or return? If 2 people would label it differently, fix the **definition** first (for example "returns: only if the customer asks for a refund or exchange").
- **This is a small eval**: fixed inputs, expected outputs, a score per prompt. It's what AI Engineers do before changing a prompt or model in production, and you'll build on it in January.

## Recap
- A prompt template is fixed text with slots (`.format`). Instructions go in `system`, customer text in `user`.
- Few-shot = fake earlier turns (`user` message, `assistant` answer). Zero-shot = none.
- Measure every prompt on the same test messages, and read the misses: 70 → 80 → 90 → 90%.
- 10 messages can't separate 80% from 90%, and tuning on the test set cheats.

📚 **Learn more:** [Few-shot prompting (Prompt Engineering Guide)](https://www.promptingguide.ai/techniques/fewshot) · [Claude docs: examples in prompts](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/multishot-prompting) · [`str.format`](https://docs.python.org/3/library/stdtypes.html#str.format)
