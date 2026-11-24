# Task 10, Exercise 2: System prompts, temperature and max_tokens (worked example)

Make `ex2_roles_settings.py` in `05_llm/task10/` (finished file: [examples/task10/ex2_roles_settings.py](../examples/task10/ex2_roles_settings.py)). The outputs below are real (run on 2026-11-24).

**The idea:** you control an LLM in 2 ways:
- **what you tell it**: above all the **system prompt**, your instructions for how to behave, separate from what the customer typed;
- **settings**: how random it is (`temperature`, `seed`) and how long it may answer (`max_tokens`).

- **Laravel analogy:** the system prompt is like middleware plus config: the developer sets it once, it applies to every request, and the visitor doesn't write it.

## Step 1: A helper function

```python
"""Task 10, Exercise 2: system prompts, temperature and max_tokens."""

import textwrap
import time

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
MODEL = "qwen2.5:1.5b"


def chat(messages: list[dict], **settings) -> str:
    """Send the messages and return the reply text."""
    response = client.chat.completions.create(
        model=MODEL, messages=messages, **settings
    )
    return response.choices[0].message.content
```
- **`**settings`** in the definition collects any extra named arguments into a dict (`chat(m, temperature=0)` → `{"temperature": 0}`). `**settings` in the call unpacks them again. So one helper accepts every API setting without listing them. You met `**` unpacking in Task 2.

## Step 2: With and without a system prompt

```python
question = {"role": "user", "content": "Should I buy a diamond online?"}
shop = {
    "role": "system",
    "content": "You are the assistant of a diamond shop in Mohali. Answer in at "
    "most 2 short sentences, then invite the customer to visit the shop.",
}
for label, messages in [("No system prompt", [question]),
                        ("Shop assistant", [shop, question])]:
    start = time.perf_counter()
    reply = chat(messages, temperature=0, seed=42, max_tokens=400)
    seconds = time.perf_counter() - start
    print(f"--- {label}: {len(reply.split())} words, {seconds:.1f} s ---")
    print(textwrap.shorten(reply, width=220, placeholder=" ..."))
```
```powershell
python ex2_roles_settings.py
```
```
--- No system prompt: 201 words, 11.2 s ---
As an AI language model, I cannot provide financial advice or make recommendations on specific products or services. However, I can provide some general information that may be helpful. Diamonds are a popular choice ...
--- Shop assistant: 36 words, 2.2 s ---
Yes, you can buy a diamond online, but it's important to ensure the quality and authenticity of the diamond. You can visit our shop in Mohali to see the diamonds in person and make a decision.
```

### Why each part works
- **The 3 roles:** `system` (the developer's instructions), `user` (the customer), `assistant` (the model's replies). The system message goes **first**.
- **The same question, a very different answer.** With no instructions the model gives a generic essay. With a role, a place and a length limit, it answers like a shop.
- **Shorter is faster:** 201 words took 11.2 s and 36 words took 2.2 s. The model writes one token at a time, so output length is most of the waiting time. "Answer in at most 2 short sentences" is also a speed setting.
- **Your system prompt replaces the default one** ("You are Qwen...", Exercise 1).
- **A system prompt is guidance, not a guarantee.** The model usually follows it, but a user can talk it out of its rules. Never put secrets in it, and never rely on it for security: check permissions in your own code.
- **`len(reply.split())`** counts words. **`textwrap.shorten`** cuts long text at a word boundary and adds `placeholder`, like Laravel's `Str::limit`.

## Step 3: Temperature and seed

```python
prompt = [{"role": "user", "content": "Suggest a name for a new diamond shop. "
           "Reply with the name only."}]
for label, settings in [("temperature=0, seed=42", {"temperature": 0, "seed": 42}),
                        ("temperature=1", {"temperature": 1}),
                        ("temperature=1, seed=42", {"temperature": 1, "seed": 42})]:
    names = [chat(prompt, max_tokens=20, **settings) for _ in range(3)]
    print(f"{label:<23} {names}")
```
```
temperature=0, seed=42  ['Radiant Sparkle Diamonds', 'Radiant Sparkle Diamonds', 'Radiant Sparkle Diamonds']
temperature=1           ['RadiantJewels', '"Radiant Sparkle Jewels"', 'Radiant Sparkle']
temperature=1, seed=42  ['"Radiant Eternity Diamond Emporium"', '"Radiant Eternity Diamond Emporium"', '"Radiant Eternity Diamond Emporium"']
```

### Why each part works
- **At each step the model has a probability for every possible next token.** `temperature` decides how it picks:
  - **0** = take the most likely token. Use it for facts, classification, extracting data and code.
  - **1** = pick at random according to the probabilities. Use it for ideas and creative text. The middle line changes on every run.
- **`seed=42`** starts the random choices from the same place, like `random_state=42` in scikit-learn. With a seed, even temperature 1 repeats.
- **Some names arrive with quotes and some without,** though the prompt said "the name only". Model output needs cleaning (`.strip('"')`) before your code uses it. Task 11 makes output strict with JSON schemas.
- **`for _ in range(3)`**: `_` is the usual name for a loop variable you don't use.

### `temperature=0` is nearly repeatable, not exactly
I ran this script 3 times. The shop-name lines for the 2 seeded settings were identical each time, but the shop assistant's reply wasn't: 36 words in the first run, and in the other two 31 words ("...ensure the seller is reputable and the product is genuine. Visit our shop in Mohali for a genuine diamond experience."). The likely reason is tiny rounding differences in the calculation, for example depending on how much of the prompt was already processed. They can flip a close choice between 2 tokens, and the answer then goes another way. I didn't prove that cause here.

**So never write a test that expects an exact LLM sentence.** Check properties instead: is it short enough, does it contain the right word, is it valid JSON? January's evals block is about exactly this.

## Step 4: max_tokens

```python
how = [{"role": "user", "content": "How are diamonds formed? Answer in 2 sentences."}]
for limit in [15, 200]:
    response = client.chat.completions.create(
        model=MODEL, messages=how, temperature=0, seed=42, max_tokens=limit
    )
    choice = response.choices[0]
    print(f"max_tokens={limit}: finish_reason={choice.finish_reason!r}, "
          f"{response.usage.completion_tokens} tokens")
    print(choice.message.content)
```
```
max_tokens=15: finish_reason='length', 15 tokens
Diamonds are formed deep within the Earth's mantle under extreme heat and pressure
max_tokens=200: finish_reason='stop', 23 tokens
Diamonds are formed deep within the Earth's mantle under extreme heat and pressure, typically over billions of years.
```

### Why each part works
- **`max_tokens` is a hard cut, not a request.** The model doesn't know the limit and doesn't plan for it. At 15 tokens the text just stops, with `finish_reason='length'`.
- **The cut answer looks complete.** "...under extreme heat and pressure" reads like a finished sentence apart from the full stop. Only `finish_reason` tells you for sure.
- **Use both controls:** ask for a short answer in the prompt, and set `max_tokens` as a safety limit, so one strange request can't run for minutes or cost a lot.
- **The model wrote 1 sentence, not 2.** Small models follow counts only roughly. If the exact number matters, check it in code.
- **`{...!r}`** prints the `repr`, with the quotes, so you can see it's a string.

## Recap
- `system` = the developer's instructions, `user` = the customer, `assistant` = the model.
- A clear system prompt makes answers shorter, faster and on-brand, but it isn't security.
- `temperature=0` for facts, higher for ideas; `seed` makes random choices repeat. Neither promises word-for-word identical answers.
- `max_tokens` cuts the answer off; check `finish_reason`.

📚 **Learn more:** [LLM settings (Prompt Engineering Guide)](https://www.promptingguide.ai/introduction/settings) · [Chat completions reference](https://platform.openai.com/docs/api-reference/chat/create) · [`textwrap.shorten`](https://docs.python.org/3/library/textwrap.html#textwrap.shorten) · [`**` unpacking](https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists)
