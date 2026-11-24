# Task 10, Exercise 3: A chatbot with memory (the API is stateless) (worked example)

Make `ex3_conversation.py` in `05_llm/task10/` (finished file: [examples/task10/ex3_conversation.py](../examples/task10/ex3_conversation.py)). The outputs below are real (run on 2026-11-24).

**The idea:** the model **remembers nothing** between calls. Each request starts from zero. A chatbot seems to remember because **your code sends the whole conversation again every time**.

- **Laravel analogy:** HTTP is stateless too. Laravel "remembers" a visitor by loading the session on every request. Here the session is a Python list called `history`.

## Step 1: Prove that it forgets

```python
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
```
```powershell
python ex3_conversation.py
```
```
Call 1: Hello Adam! It's great to meet you. I'm here to help you find the perfect engagement ring. Before we begin, could you tell me a little bit more about what you're looking for in a ring? What materials do you prefer? Do you have any specific designs or styles in mind?
Call 2: I am Qwen, created by Alibaba Cloud.
```
Call 2 has no idea who Adam is. It even answered with **its own** name, from the default system prompt ("You are Qwen, created by Alibaba Cloud", Exercise 1). That was the only name in its input.

## Step 2: Send the history

```python
history = [
    intro,
    {"role": "assistant", "content": first.choices[0].message.content},
    name_question,
]
third = client.chat.completions.create(model=MODEL, messages=history, **SETTINGS)
print("With history:", third.choices[0].message.content)
print("Prompt tokens without and with history:",
      second.usage.prompt_tokens, "vs", third.usage.prompt_tokens)
```
```
With history: Your name is Adam.
Prompt tokens without and with history: 34 vs 118
```

### Why each part works
- **`history` is the conversation in order:** user, assistant, user. The model's own earlier reply goes back in with the role `"assistant"`.
- **Memory costs tokens:** 34 → 118. Every turn makes the next request longer, so a long chat gets slower and more expensive with each message.
- **There's also a hard limit**, the **context window**. `ollama show qwen2.5:1.5b` says this model supports 32,768 tokens, but Ollama may be set to use less (see the link at the bottom). When a conversation doesn't fit, something has to be dropped, so you should decide what.

## Step 3: A chat loop that keeps the last few messages

```python
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
```
Type these 5 messages, then `quit` (I fed them in with a small script; the replies are the model's real ones):
```
You: Hi, I'm Adam.
Bot: Hello Adam! Welcome to the diamond shop. How can I assist you today?
     [33 prompt tokens, 2 messages kept]
You: What is my name?
Bot: Your name is Adam.
     [64 prompt tokens, 4 messages kept]
You: What does VVS1 mean?
Bot: VVS1 is the highest level of clarity in diamond grading, indicating the finest level of internal and external clarity.
     [86 prompt tokens, 4 messages kept]
You: Do you sell platinum rings?
Bot: I'm sorry, but I don't sell any jewelry. I'm here to assist with information and help you find the perfect diamond.
     [93 prompt tokens, 4 messages kept]
You: What is my name?
Bot: I'm sorry, but I don't have the ability to know your name.
     [115 prompt tokens, 4 messages kept]
You: quit
Bye!
```
Turn 2 knows the name. By turn 5, both messages that mention Adam have fallen out of the last 4, so it's gone. A second run gave slightly different wording, but the name was remembered and forgotten at the same turns.

### Why each part works
- **`input("You: ")`** waits for you to type a line. **`.strip()`** removes spaces around it.
- **`text.lower() in {"", "quit", "exit"}`**: a **set** is a quick way to test against several values. An empty line also quits.
- **`[SYSTEM, *chat_history]`**: `*` unpacks the list into a new list, like PHP's `[$system, ...$history]`. **The system prompt is added to every request, outside the history**, so trimming can never drop the bot's instructions.
- **`chat_history[-MAX_MESSAGES:]`** keeps the last 4 items (Python slicing; PHP's `array_slice($h, -4)`). It's called a **sliding window**.
- **Why an even number?** It keeps whole user + assistant pairs. An odd number would start the history with an answer to a question the model can't see.
- **The window limits messages, not tokens**, so a long reply still makes the next prompt longer (86 → 93 → 115). It stops growth without end, though.
- **Forgetting isn't always visible.** In another run I asked "What was my first question?" twice. The second time, the question had left the window, but the bot's own earlier reply *quoting* it was still there, so it answered correctly.

### The model makes things up
Look at the replies as a shop owner would:
- **"VVS1 is the highest level of clarity"** is false. FL (Flawless) and IF are higher; VVS1 is third.
- **"I don't sell any jewelry"** is invented, and in another run the bot said "Yes, we do! We offer a variety of lab-created diamonds". Nobody told it what the shop sells.

This is **hallucination**: the model writes *likely* text, whether or not it's true. The fix is to give it the facts to answer from: that's RAG (Task 12). Until then, don't let a bot promise anything about stock, prices or returns.

**What real chatbots do for memory:** keep the last N messages (this exercise), summarise older messages with the LLM and keep the summary, or save facts such as the name in a database and put them in the system prompt.

## Recap
- The API is stateless: your code sends the whole conversation on every call.
- `history` = a list of `user` and `assistant` messages in order; the `system` message goes in front each time.
- More history = more tokens = slower and more expensive. A sliding window (`[-4:]`) limits it, and the bot forgets what falls out.
- A fluent answer isn't necessarily true. Check facts, or provide them.

📚 **Learn more:** [Ollama: context length](https://docs.ollama.com/context-length) · [Chat completions reference](https://platform.openai.com/docs/api-reference/chat/create) · [`input`](https://docs.python.org/3/library/functions.html#input) · [Python tutorial: lists and slicing](https://docs.python.org/3/tutorial/introduction.html#lists)
