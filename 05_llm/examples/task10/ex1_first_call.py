"""Task 10, Exercise 1: your first LLM call."""

import time

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
MODEL = "qwen2.5:1.5b"

start = time.perf_counter()
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "In one sentence, what is a carat?"}],
    temperature=0,
    seed=42,
)
seconds = time.perf_counter() - start
print(response.choices[0].message.content)
print(f"Took {seconds:.1f} s")

print("Model:", response.model)
print("Finish reason:", response.choices[0].finish_reason)
usage = response.usage
print(f"Tokens: {usage.prompt_tokens} in + {usage.completion_tokens} out "
      f"= {usage.total_tokens}")
print(response.model_dump_json(indent=2, exclude_none=True))


def count_tokens(text: str) -> int:
    """Send a text, ask for 1 token back, and read how many tokens went in."""
    reply = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": text}],
        max_tokens=1,
    )
    return reply.usage.prompt_tokens


overhead = count_tokens("")
print("Tokens in an empty prompt:", overhead)
texts = [
    "diamond",
    "diamonds",
    "unbelievably",
    "HistGradientBoostingRegressor",
    "$18,823",
    "The price of a diamond depends on its carat, cut, colour and clarity.",
    "हीरे की कीमत उसके कैरेट, कट, रंग और स्पष्टता पर निर्भर करती है।",
]
for text in texts:
    tokens = count_tokens(text) - overhead
    print(f"{tokens:>3} tokens {len(text):>3} characters  {text}")
