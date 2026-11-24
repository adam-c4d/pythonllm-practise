# Task 10, Exercise 4: Streaming the answer (worked example)

Make `ex4_streaming.py` in `05_llm/task10/` (finished file: [examples/task10/ex4_streaming.py](../examples/task10/ex4_streaming.py)). The outputs below are real (run on 2026-11-24).

**The idea:** an LLM writes one token at a time. Without streaming, you wait until the last token and get everything at once. With `stream=True`, the server sends each piece **as soon as it's written**, and you print it as it arrives. The total time is the same, but the user starts reading almost immediately. ChatGPT and Claude both do this.

- **Laravel analogy:** `response()->stream(...)` (or `eventStream`) instead of building the whole response first. It's the same HTTP technique, server-sent events.

## Step 1: Without streaming

```python
"""Task 10, Exercise 4: streaming the answer token by token."""

import time

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
MODEL = "qwen2.5:1.5b"
messages = [{"role": "user", "content": "Explain in 3 sentences what makes a "
             "diamond expensive."}]

start = time.perf_counter()
response = client.chat.completions.create(
    model=MODEL, messages=messages, temperature=0, seed=42, max_tokens=150
)
print(f"Without streaming: nothing to show for {time.perf_counter() - start:.1f} s, "
      f"then {response.usage.completion_tokens} tokens at once")
```
```powershell
python ex4_streaming.py
```
```
Without streaming: nothing to show for 4.3 s, then 88 tokens at once
```

## Step 2: With streaming

```python
start = time.perf_counter()
first_token_at = None
pieces = []
stream = client.chat.completions.create(
    model=MODEL, messages=messages, temperature=0, seed=42, max_tokens=150,
    stream=True, stream_options={"include_usage": True},
)
for chunk in stream:
    if chunk.usage:
        usage = chunk.usage
    if not chunk.choices or not chunk.choices[0].delta.content:
        continue
    if first_token_at is None:
        first_token_at = time.perf_counter() - start
    piece = chunk.choices[0].delta.content
    pieces.append(piece)
    print(piece, end="", flush=True)
total = time.perf_counter() - start
print()
print(f"First token after {first_token_at:.2f} s, all {usage.completion_tokens} "
      f"tokens after {total:.1f} s ({usage.completion_tokens / total:.0f} tokens/s)")
```
The text appears word by word:
```
A diamond is expensive due to its rarity, the high quality of the material, and the labor-intensive process of cutting and polishing it. The scarcity of natural diamonds means that fewer diamonds are available, making them more valuable. Additionally, the process of creating a diamond involves a significant amount of energy and resources, which contributes to its high cost. Finally, the craftsmanship and skill required to cut and polish a diamond also contribute to its value.
First token after 0.07 s, all 88 tokens after 4.3 s (20 tokens/s)
```

### Why each part works
- **`stream=True`** changes what `create()` returns: instead of one response, an **iterator of chunks**. The `for` loop waits for each chunk and gets it as soon as it arrives.
- **`delta`, not `message`:** each chunk holds only the **new** piece (`chunk.choices[0].delta.content`).
- **Some chunks have no text.** The `if not ...: continue` line skips them. The last chunk, for example, carries the usage numbers and has an empty `choices` list, so `chunk.choices[0]` would crash on it.
- **`stream_options={"include_usage": True}`** asks for that usage chunk. Without it, Ollama sends no token counts when streaming (I checked).
- **`print(piece, end="", flush=True)`**: `end=""` stops `print` adding a new line after each piece, and `flush=True` shows it at once instead of waiting for a buffer to fill.
- **`first_token_at is None`** records the time once, at the first real piece. This measurement is called **time to first token** (TTFT), and it's the number users feel.
- **20 tokens/s** is this model's writing speed on the work PC. It's a handy number: an answer of 200 tokens takes about 10 s, streamed or not.

## Step 3: What the chunks look like

```python
print("The first 12 chunks:", pieces[:12])
answer = "".join(pieces)
print(f"Joined back together: {len(answer)} characters, {len(pieces)} chunks")
```
```
The first 12 chunks: ['A', ' diamond', ' is', ' expensive', ' due', ' to', ' its', ' rarity', ',', ' the', ' high', ' quality']
Joined back together: 480 characters, 87 chunks
```
- **One chunk ≈ one token.** You can see the tokens from Exercise 1: most words carry their leading space (`' diamond'`), and the comma is a token of its own.
- **87 chunks with text, 88 tokens:** the extra token is most likely the invisible "end of answer" marker. The skipped chunks aren't in `pieces`.
- **`"".join(pieces)`** glues the list into one string (PHP's `implode('', $pieces)`). Collect pieces in a list and join them at the end: you need the full text for the chat history, the database or the logs.
- **The model wrote 4 sentences, not 3** (count them). As in Exercise 2, counts are followed only roughly.

## Be careful with the 0.07 s
It's that low because Step 1 had **just sent the same prompt**, and Ollama keeps the last prompt's calculations in a cache. I measured new prompts separately:

| Prompt | Tokens | First token, new prompt | First token, same prompt again |
|---|---|---|---|
| short | 47 | 0.21 s | 0.07 s |
| long (59 lines of diamond data) | 1,233 | **5.68 s** | 0.07 s |

- **The model must read the whole prompt before it writes the first token.** On this PC, 1,233 tokens of reading took over 5 seconds, and streaming can't hide that part.
- That's why the course keeps prompts short, and why the capstone sends a **summary** of a CSV to the LLM, not the CSV itself.

**My runs:** I ran this script 4 times. Streaming gave 88 tokens every time. The non-streaming call gave 80 tokens twice and 88 twice: the "nearly repeatable" effect from Exercise 2.

## Recap
- `stream=True` returns chunks; read `chunk.choices[0].delta.content`, and skip chunks without text.
- Same total time, but the first words show at once. Measure **time to first token** and **tokens per second**.
- `print(piece, end="", flush=True)` shows pieces live; `"".join(pieces)` rebuilds the answer.
- A long new prompt delays the first token: reading input takes time too.

📚 **Learn more:** [`openai` Python package: streaming](https://github.com/openai/openai-python#streaming-responses) · [Ollama: OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) · [`print`](https://docs.python.org/3/library/functions.html#print) · [`str.join`](https://docs.python.org/3/library/stdtypes.html#str.join)
