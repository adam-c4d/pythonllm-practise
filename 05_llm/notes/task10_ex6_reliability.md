# Task 10, Exercise 6: Settings, timeouts, retries and clear errors (worked example)

Make 2 files in `05_llm/task10/`: `llm.py` and `ex6_reliability.py` (finished files: [examples/task10/llm.py](../examples/task10/llm.py), [ex6_reliability.py](../examples/task10/ex6_reliability.py)). The outputs below are real (run on 2026-11-24).

**The idea:** Exercises 1–5 each repeated the same client code, and crash with a long traceback if Ollama is closed. An LLM call is a network call: the server can be down, slow or busy, and the model name can be wrong. `llm.py` puts everything in one place: settings, the client, timeouts, retries and readable errors. Tasks 11 and 12 and the capstone reuse it.

- **Laravel analogy:** `config/services.php` + `.env` + a service class (`app/Services/LlmService.php`) + `Http::timeout(60)->retry(2)`.

## ⚠️ Before you make a `.env` file
The rules in this repo's `.gitignore` are switched off, so **Git would commit a `.env` file**. This exercise doesn't need one (every setting has a default). Before you ever create one, especially with a real API key in it:
1. In `.gitignore`, change the line `#-  .env` to `.env` (also worth doing for `__pycache__/`).
2. Check it: `git check-ignore .env` must print `.env`.

A key pushed to GitHub counts as stolen, even if you delete it later: it stays in the Git history. The only fix is to cancel it and make a new one.

## Step 1: `llm.py`

```python
"""LLM settings and helpers in one place (like a Laravel service + config file)."""

import os
from collections.abc import Iterator
from contextlib import contextmanager

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    NotFoundError,
    OpenAI,
)

load_dotenv()  # reads a .env file if there is one; real env vars win

BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
MODEL = os.getenv("LLM_MODEL", "qwen2.5:1.5b")
API_KEY = os.getenv("LLM_API_KEY", "ollama")
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))

client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT, max_retries=2)


class LLMError(Exception):
    """A problem with the LLM, with a message that says what to do next."""


@contextmanager
def friendly_errors() -> Iterator[None]:
    """Turn the SDK's many exceptions into one LLMError with a clear message."""
    try:
        yield
    except APITimeoutError as error:
        raise LLMError(f"No answer from {BASE_URL} in time. Try again, "
                       "or raise LLM_TIMEOUT.") from error
    except APIConnectionError as error:
        raise LLMError(f"Can't reach {BASE_URL}. Is Ollama running?") from error
    except NotFoundError as error:
        raise LLMError(f"Model {MODEL!r} not found. "
                       f"For Ollama, run: ollama pull {MODEL}") from error
    except APIStatusError as error:
        raise LLMError(f"The LLM server answered {error.status_code}: "
                       f"{error.message}") from error


def chat(messages: list[dict], **settings) -> str:
    """Send messages and return the reply text. Repeatable answers by default."""
    settings = {"temperature": 0, "seed": 42, "max_tokens": 300} | settings
    with friendly_errors():
        response = client.chat.completions.create(
            model=MODEL, messages=messages, **settings
        )
    return response.choices[0].message.content


def ask(question: str, system: str | None = None, **settings) -> str:
    """One question in, one answer out."""
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": question})
    return chat(messages, **settings)
```

### Why each part works
- **`load_dotenv()`** reads a `.env` file, if there is one, into environment variables. It looks in `llm.py`'s folder and then in the folders above it (I tested both). **A real environment variable beats `.env`** (tested too: `$env:LLM_MODEL` won).
- **`os.getenv(name, default)`**: as in Task 9 Ex 4, like Laravel's `env()`. Changing provider becomes a settings change: a new `LLM_BASE_URL`, `LLM_MODEL` and `LLM_API_KEY`.
- **`float(os.getenv("LLM_TIMEOUT", "60"))`**: environment variables are always **strings**, so convert numbers yourself. The default is a string too, for the same reason.
- **`timeout=TIMEOUT`**: give up on an attempt after 60 s. The package's own default is 10 minutes, which is far too long for a user to wait.
- **`max_retries=2`**: try up to 2 more times, waiting a little longer each time (**exponential backoff**). It retries problems that may go away: no connection, timeouts, 429 (too many requests) and 5xx server errors. It doesn't retry a 404, because asking again can't help.
- **`class LLMError(Exception)`**: your own exception type. The rest of your code catches **one** type and doesn't need to know that `openai` exists.
- **`@contextmanager` + `yield`**: the non-async sibling of the `@asynccontextmanager` from Task 9. The code inside `with friendly_errors():` runs at the `yield`, so an exception raised there lands in these `except` blocks. Any function that calls the LLM can reuse it, with one `with` line.
- **The order of the `except` blocks matters: specific first.** `APITimeoutError` is a child of `APIConnectionError`, and `NotFoundError` is a child of `APIStatusError`. Python uses the first block that matches, so with the parent first, the child's message would never appear.
- **`raise ... from error`** keeps the original exception attached for debugging (Task 9 Ex 5).
- **`{...defaults...} | settings`**: the right side wins (Task 9 Ex 6), so `ask(..., max_tokens=500)` overrides the default 300.
- **`[...] if system else []`**: a system message only if you gave one.

## Step 2: `ex6_reliability.py`

```python
"""Task 10, Exercise 6: settings, timeouts, retries and clear errors."""

import logging
import time

import llm

logging.basicConfig(level=logging.INFO, format="  [%(name)s] %(message)s")

print(f"Model {llm.MODEL} at {llm.BASE_URL}, timeout {llm.TIMEOUT:.0f} s")
start = time.perf_counter()
try:
    print(llm.ask("In one sentence, what is clarity in a diamond?"))
except llm.LLMError as error:
    raise SystemExit(f"LLM error: {error}") from None
print(f"Took {time.perf_counter() - start:.1f} s")

start = time.perf_counter()
try:
    llm.ask("Write a long essay about diamonds.", max_tokens=500, timeout=2)
except llm.LLMError as error:
    print("LLM error:", error)
print(f"Gave up after {time.perf_counter() - start:.1f} s")
```
```powershell
python ex6_reliability.py
```
```
Model qwen2.5:1.5b at http://127.0.0.1:11434/v1, timeout 60 s
  [httpx2] HTTP Request: POST http://127.0.0.1:11434/v1/chat/completions "HTTP/1.1 200 OK"
Clarity in a diamond refers to the absence of internal and external flaws.
Took 0.9 s
  [openai._base_client] Retrying request in 0.418639 seconds (retry 1 of 2)
  [openai._base_client] Retrying request in 0.802045 seconds (retry 2 of 2)
LLM error: No answer from http://127.0.0.1:11434/v1 in time. Try again, or raise LLM_TIMEOUT.
Gave up after 7.2 s
```
The wording, the waiting times and the seconds differ a little each run.

### Why each part works
- **`import llm`** runs `llm.py` once. `llm.ask`, `llm.MODEL` and `llm.LLMError` then show where each name comes from. It works because both files are in the same folder, and you run the script from inside it.
- **`logging.basicConfig(level=logging.INFO)`** shows what libraries are doing. That's where the request and retry lines come from; the `openai` package uses Python's standard `logging`. (`httpx2` is the HTTP library that openai 3.46 uses.) `%(name)s` is which library spoke. It's Laravel's `storage/logs`, sent to the terminal.
- **`raise SystemExit(message)`** prints the message and stops the script with exit code 1, so other programs can see that it failed. `from None` hides the original traceback from the user.
- **`timeout=2` in one call** overrides the client's 60 s for that call only.
- **The arithmetic: 3 attempts × 2 s + 0.4 s + 0.8 s of waiting = 7.2 s.** So `timeout` is **per attempt**. With `timeout=60` and 2 retries, the worst case is over 3 minutes. Remember that when you choose a timeout for a web page.

## Step 3: Break it on purpose

**A model that isn't installed:**
```powershell
$env:LLM_MODEL = "qwen9"
python ex6_reliability.py
Remove-Item Env:LLM_MODEL
```
```
Model qwen9 at http://127.0.0.1:11434/v1, timeout 60 s
  [httpx2] HTTP Request: POST http://127.0.0.1:11434/v1/chat/completions "HTTP/1.1 404 Not Found"
LLM error: Model 'qwen9' not found. For Ollama, run: ollama pull qwen9
```
One request and no retries: a 404 won't fix itself.

**Nothing listening at the address** (the same as Ollama being closed):
```powershell
$env:LLM_BASE_URL = "http://127.0.0.1:9999/v1"
python ex6_reliability.py
Remove-Item Env:LLM_BASE_URL
```
```
Model qwen2.5:1.5b at http://127.0.0.1:9999/v1, timeout 60 s
  [openai._base_client] Retrying request in 0.377758 seconds (retry 1 of 2)
  [openai._base_client] Retrying request in 0.855550 seconds (retry 2 of 2)
LLM error: Can't reach http://127.0.0.1:9999/v1. Is Ollama running?
```

**A misleading one: the `/v1` forgotten.** With `$env:LLM_BASE_URL = "http://127.0.0.1:11434"`:
```
Model qwen2.5:1.5b at http://127.0.0.1:11434, timeout 60 s
  [httpx2] HTTP Request: POST http://127.0.0.1:11434/chat/completions "HTTP/1.1 404 Not Found"
LLM error: Model 'qwen2.5:1.5b' not found. For Ollama, run: ollama pull qwen2.5:1.5b
```
The model **is** installed. The wrong **URL** also gives a 404, and `friendly_errors` guesses "model". The log line shows the truth: the path has no `/v1`. A friendly message is still a guess, so keep the log.

**A bigger model, without changing any code** (if you pulled the optional `qwen2.5:3b`):
```powershell
$env:LLM_MODEL = "qwen2.5:3b"
python ex6_reliability.py
Remove-Item Env:LLM_MODEL
```
```
Model qwen2.5:3b at http://127.0.0.1:11434/v1, timeout 60 s
  [httpx2] HTTP Request: POST http://127.0.0.1:11434/v1/chat/completions "HTTP/1.1 200 OK"
Clarity in a diamond refers to the absence of imperfections or inclusions within the stone, which affects its appearance and value.
Took 15.5 s
```
Those 15.5 s include loading the model into memory. (The timeout part after it printed the same kind of lines as before.)

**Always run the `Remove-Item` line afterwards**, or the setting stays for the rest of that terminal session.

## Recap
- One module (`llm.py`) holds the settings, the client and the helpers. Everything else calls `ask` or `chat`.
- Settings come from environment variables, then `.env`, then defaults. **Ignore `.env` in Git before you create one.**
- `timeout` is per attempt; retries multiply it. Temporary problems are retried, a 404 isn't.
- Catch specific exceptions before their parents, and turn them into one `LLMError` that says what to do next.

📚 **Learn more:** [`openai` Python package: errors, retries, timeouts](https://github.com/openai/openai-python#handling-errors) · [python-dotenv](https://pypi.org/project/python-dotenv/) · [`contextmanager`](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager) · [`logging.basicConfig`](https://docs.python.org/3/library/logging.html#logging.basicConfig) · [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit)

## ✅ Task 10 done when
- [ ] `05_llm/task10/` has `llm.py` and `ex1_...` to `ex6_...`, and each one runs.
- [ ] The chatbot in Exercise 3 remembers your name at turn 2 and has forgotten it by turn 5.
- [ ] Exercise 5 prints 4 scores, and you can say why 80% vs 90% proves little.
- [ ] Exercise 6 shows a clear message for a wrong model, a wrong address and a timeout.
- [ ] Ruff shows no problems in the folder.

Then commit, push, and ask Claude to **"review all"**. Next is Task 11: structured output (JSON).
