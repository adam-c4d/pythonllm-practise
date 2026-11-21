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

prompt = [{"role": "user", "content": "Suggest a name for a new diamond shop. "
           "Reply with the name only."}]
for label, settings in [("temperature=0, seed=42", {"temperature": 0, "seed": 42}),
                        ("temperature=1", {"temperature": 1}),
                        ("temperature=1, seed=42", {"temperature": 1, "seed": 42})]:
    names = [chat(prompt, max_tokens=20, **settings) for _ in range(3)]
    print(f"{label:<23} {names}")

how = [{"role": "user", "content": "How are diamonds formed? Answer in 2 sentences."}]
for limit in [15, 200]:
    response = client.chat.completions.create(
        model=MODEL, messages=how, temperature=0, seed=42, max_tokens=limit
    )
    choice = response.choices[0]
    print(f"max_tokens={limit}: finish_reason={choice.finish_reason!r}, "
          f"{response.usage.completion_tokens} tokens")
    print(choice.message.content)
