# Task 10, Exercise 1: Your first LLM call and tokens (worked example)

Make a new folder `05_llm/task10/` and a file `ex1_first_call.py` in it (finished file: [examples/task10/ex1_first_call.py](../examples/task10/ex1_first_call.py)). The outputs below are real (run on 2026-11-24).

**You need Ollama running, with the course model.** Check it:
```powershell
ollama list
```
You should see `qwen2.5:1.5b`. If not, follow [SETUP.md](../../SETUP.md) Steps 3–4.

**The idea:** an LLM is a program that takes text in and predicts the text that comes next. You don't load it in your script, as you did with the diamond model. It runs in a **server** (Ollama, on your own PC, port 11434), and your Python code sends it HTTP requests. The `openai` package builds those requests for you. Ollama understands the same format as OpenAI's API, so the same code works with a paid provider later: only the address, key and model name change.

- **Laravel analogy:** `Http::withToken(...)->post('https://api.example.com/...')` wrapped in an SDK, as the Stripe package does for Stripe.

## Step 1: Ask one question

```python
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
```
Run it in a `(dsllm)` terminal, inside `05_llm/task10/`:
```powershell
python ex1_first_call.py
```
```
A carat is a unit of weight used to measure gemstones and some types of jewelry.
Took 4.6 s
```
- **The first call is the slow one** (4.6 s), because Ollama has to load the model from disk into memory. Later runs took 0.9 s and 1.1 s.
- **Your sentence may differ a little from mine.** One of my runs said "...used for measuring gemstones and precious metals." Exercise 2 explains why.

### Why each part works
- **`OpenAI(base_url=..., api_key=...)`** makes a client. `base_url` sends the requests to Ollama instead of OpenAI. **The `/v1` at the end is required.** The package insists on an API key, but Ollama ignores it, so any text works (`"ollama"`).
- **`client.chat.completions.create(...)`** sends one `POST /v1/chat/completions` and waits for the whole answer.
- **`messages`** is a list of dicts, one per message, each with a `role` (who is speaking) and `content` (what they said). Here there's one message, from the `user`.
- **`temperature=0, seed=42`** ask for repeatable answers (Exercise 2).
- **`response.choices[0].message.content`** is the answer text. `choices` is a list because the API can return several alternative answers. You'll nearly always use the first.

## Step 2: Look inside the response

Add:
```python
print("Model:", response.model)
print("Finish reason:", response.choices[0].finish_reason)
usage = response.usage
print(f"Tokens: {usage.prompt_tokens} in + {usage.completion_tokens} out "
      f"= {usage.total_tokens}")
print(response.model_dump_json(indent=2, exclude_none=True))
```
```
Model: qwen2.5:1.5b
Finish reason: stop
Tokens: 39 in + 20 out = 59
{
  "id": "chatcmpl-845",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "A carat is a unit of weight used to measure gemstones and some types of jewelry.",
        "role": "assistant"
      }
    }
  ],
  "created": 1795500070,
  "model": "qwen2.5:1.5b",
  "object": "chat.completion",
  "system_fingerprint": "fp_ollama",
  "usage": {
    "completion_tokens": 20,
    "prompt_tokens": 39,
    "total_tokens": 59,
    "prompt_tokens_details": {
      "cached_tokens": 0
    }
  }
}
```

### Why each part works
- **The response is a Pydantic model**, like the ones you wrote in Task 8. So you read it with dots (`response.usage`) and it has `model_dump_json()`. `exclude_none=True` hides the many empty fields, as in your PATCH route.
- **`finish_reason`** says why the model stopped. `"stop"` = it finished. `"length"` = it was cut off by a limit (Exercise 2). Check it whenever a cut-off answer would hurt.
- **The reply's role is `"assistant"`**: that's the model's own role. You'll need it in Exercise 3.
- **`usage`** counts **tokens**, the pieces of text the model works in. Paid providers charge per token, usually more for output than for input. On your own PC, more tokens = more seconds.

## Step 3: What is a token?

Add:
```python
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
```
```
Tokens in an empty prompt: 29
  1 tokens   7 characters  diamond
  2 tokens   8 characters  diamonds
  3 tokens  12 characters  unbelievably
  5 tokens  29 characters  HistGradientBoostingRegressor
  7 tokens   7 characters  $18,823
 17 tokens  69 characters  The price of a diamond depends on its carat, cut, colour and clarity.
 57 tokens  63 characters  हीरे की कीमत उसके कैरेट, कट, रंग और स्पष्टता पर निर्भर करती है।
```
These counts were the same in every run.

### What to notice
- **A token is a piece of a word.** Common words are 1 token (`diamond`); rarer ones are split (`unbelievably` = 3).
- **English: about 4 characters per token** (69 characters → 17 tokens). That's a useful rule of thumb for estimating cost.
- **Numbers are expensive:** `$18,823` is 7 tokens for 7 characters. A CSV full of numbers uses far more tokens than you'd guess, which matters for the capstone.
- **Hindi: 57 tokens for the same sentence that takes 17 in English**, over 3 times as many. Most likely the model's vocabulary was built mainly from other languages, so Hindi gets split into small pieces. The same question costs more and runs slower in Hindi.
- **An empty prompt is 29 tokens**, not 0. Two things are added around your text: markers that say where each message starts and ends, and a **default system prompt** stored in the model. See it with `ollama show qwen2.5:1.5b`:
  ```
    System
      You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
  ```
- **`max_tokens=1`** keeps the counting fast: the model reads the whole text but writes only 1 token.
- **`overhead` is subtracted** so that each line counts only its own text.
- **`{tokens:>3}`** right-aligns in 3 characters (Task 2 format specs).

**If the Hindi line crashes with `UnicodeEncodeError`,** your terminal isn't using UTF-8. Run `$env:PYTHONUTF8 = "1"` in that terminal and try again.

## Recap
- An LLM runs in a server; the `openai` client sends it HTTP requests. `base_url` picks the server.
- `messages` is a list of `{"role": ..., "content": ...}` dicts; the answer is `response.choices[0].message.content`.
- `finish_reason` tells you whether the answer is complete. `usage` counts tokens (= cost and time).
- A token is a piece of a word: about 4 characters in English, and far more tokens for numbers and Hindi.

📚 **Learn more:** [Ollama: OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) · [`openai` Python package](https://github.com/openai/openai-python) · [Chat completions reference](https://platform.openai.com/docs/api-reference/chat/create) · [Hugging Face LLM course: tokenizers](https://huggingface.co/learn/llm-course/chapter2/4)
