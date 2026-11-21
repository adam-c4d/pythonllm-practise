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

print("The first 12 chunks:", pieces[:12])
answer = "".join(pieces)
print(f"Joined back together: {len(answer)} characters, {len(pieces)} chunks")
