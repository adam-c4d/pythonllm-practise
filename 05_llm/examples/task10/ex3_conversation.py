"""Task 10, Exercise 3: conversation memory (the API is stateless)."""

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
MODEL = "qwen2.5:1.5b"
SETTINGS = {"temperature": 0, "seed": 42, "max_tokens": 80}

intro = {"role": "user", "content": "Hi, my name is Adam. I want an engagement ring."}
name_question = {"role": "user", "content": "What is my name?"}

first = client.chat.completions.create(model=MODEL, messages=[intro], **SETTINGS)
print("Call 1:", first.choices[0].message.content)
second = client.chat.completions.create(
    model=MODEL, messages=[name_question], **SETTINGS
)
print("Call 2:", second.choices[0].message.content)

history = [
    intro,
    {"role": "assistant", "content": first.choices[0].message.content},
    name_question,
]
third = client.chat.completions.create(model=MODEL, messages=history, **SETTINGS)
print("With history:", third.choices[0].message.content)
print("Prompt tokens without and with history:",
      second.usage.prompt_tokens, "vs", third.usage.prompt_tokens)

SYSTEM = {"role": "system", "content": "You are a friendly diamond shop assistant. "
          "Answer in one short sentence."}
MAX_MESSAGES = 4  # keep the last 2 exchanges (user + assistant each)

chat_history: list[dict] = []
while True:
    text = input("You: ").strip()
    if text.lower() in {"", "quit", "exit"}:
        print("Bye!")
        break
    chat_history.append({"role": "user", "content": text})
    response = client.chat.completions.create(
        model=MODEL, messages=[SYSTEM, *chat_history], **SETTINGS
    )
    reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    chat_history = chat_history[-MAX_MESSAGES:]
    print(f"Bot: {reply}")
    print(f"     [{response.usage.prompt_tokens} prompt tokens, "
          f"{len(chat_history)} messages kept]")
