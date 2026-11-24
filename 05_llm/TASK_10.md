# Task 10: LLM basics: calls, prompts and reliability (Phase 5)

**Goal:** call an LLM from Python: send messages, control the answer (system prompt, temperature, max_tokens), keep a conversation, stream the reply, compare prompts with a score, and handle failures properly in one reusable module, `llm.py`.

**Why it matters:** this is the daily work of the AI Engineer job you're aiming for. The capstone's `/ask` route is built from this task (calls and reliability), Task 11 (JSON output) and Task 12 (RAG).

**Before you start:** Ollama must be running with `qwen2.5:1.5b` ([SETUP.md](../SETUP.md) Steps 3–4). Check with `ollama list`. Everything runs on your PC: free, no API key.

**Laravel → LLM code for this task:**

| Laravel | Python |
|---|---|
| an SDK around `Http::post(...)` | `OpenAI(base_url=..., api_key=...)` + `client.chat.completions.create(...)` |
| middleware / config that applies to every request | the `system` message |
| the session, loaded on every request | the `history` list, sent on every call |
| `[$system, ...$history]`, `array_slice($h, -4)` | `[SYSTEM, *history]`, `history[-4:]` |
| `response()->stream(...)` | `stream=True` and a `for chunk in stream` loop |
| a Blade view with slots | a prompt template + `.format(...)` |
| a PHPUnit data provider | a list of `(message, expected)` test pairs |
| `config/services.php` + `.env` + a service class | `llm.py` (`load_dotenv`, `os.getenv`, `ask`, `chat`) |
| `Http::timeout(60)->retry(2)` | `OpenAI(..., timeout=60, max_retries=2)` |

```
05_llm/
├── TASK_10.md
├── task10/                      ← you make this folder and type your code here
│   ├── ex1_first_call.py
│   ├── ex2_roles_settings.py
│   ├── ex3_conversation.py
│   ├── ex4_streaming.py
│   ├── ex5_few_shot.py
│   ├── llm.py                   ← Exercise 6, reused in Tasks 11–12 and the capstone
│   └── ex6_reliability.py
├── notes/                       ← worked examples (task10_ex1_... to task10_ex6_...)
└── examples/task10/             ← the finished code
```

**How to run it:** in a `(dsllm)` terminal, `cd 05_llm/task10`, then for example `python ex1_first_call.py`. There's no web server in this task.

**About the expected outputs:** an LLM's wording isn't fully repeatable, even with `temperature=0, seed=42`, and your times will differ. ✅ below gives what must match (numbers, behaviour) and marks what may vary.

---

## Exercise 1: Your first call, and tokens

1. Make an `OpenAI` client for Ollama, and ask "In one sentence, what is a carat?" with `temperature=0, seed=42`. Print the answer and the seconds taken.
2. Print the model, `finish_reason` and token usage, then the whole response with `model_dump_json(indent=2, exclude_none=True)`.
3. Write `count_tokens(text)` (send the text with `max_tokens=1`, read `usage.prompt_tokens`). Subtract the overhead of an empty prompt and count the 7 texts in the notes, from "diamond" to the Hindi sentence.

✅ Expected: finish reason `stop`; 39 prompt tokens; an empty prompt is **29** tokens. `diamond` 1, `diamonds` 2, `unbelievably` 3, `HistGradientBoostingRegressor` 5, `$18,823` 7, the English sentence 17, the Hindi one 57. *Varies:* the sentence, its token count, and the time (the first call is slowest: 4.6 s, then about 1 s).

📚 Look up: Ollama "OpenAI compatibility"; Hugging Face LLM course "Tokenizers".

## Exercise 2: System prompts, temperature, max_tokens

1. Write `chat(messages, **settings)`.
2. Ask "Should I buy a diamond online?" with and without a shop-assistant system prompt. Compare the words and the seconds.
3. Ask for a shop name 3 times each with `temperature=0, seed=42`, `temperature=1`, and `temperature=1, seed=42`.
4. Ask "How are diamonds formed? Answer in 2 sentences." with `max_tokens` 15 and 200. Print `finish_reason`.

✅ Expected: the shop reply is much shorter and faster (about 35 vs 200 words, 2 s vs 11 s). Each seeded setting repeats the same name 3 times; `temperature=1` alone gives different names. `max_tokens=15` → `finish_reason='length'`; 200 → `'stop'`. *Varies:* the names and the wording.

📚 Look up: Prompt Engineering Guide "LLM Settings"; `textwrap.shorten`.

## Exercise 3: A chatbot with memory

1. Tell the model your name in one call, and ask "What is my name?" in a second, separate call.
2. Ask again with a `history` list: user, assistant, user. Compare the prompt tokens.
3. Write a chat loop with `input()`, a system message in front of each request, and only the last `MAX_MESSAGES = 4` messages kept. Type: `Hi, I'm Adam.` / `What is my name?` / `What does VVS1 mean?` / `Do you sell platinum rings?` / `What is my name?` / `quit`.

✅ Expected: without history it doesn't know (it answered "I am Qwen, created by Alibaba Cloud."); with history "Your name is Adam."; prompt tokens **34 vs 118**. In the loop: the name is known at turn 2 and forgotten at turn 5. *Varies:* the wording, and the facts it invents (find at least one).

📚 Look up: Ollama "Context length"; Python "lists and slicing".

## Exercise 4: Streaming

1. Ask "Explain in 3 sentences what makes a diamond expensive." without streaming, and time it.
2. Ask again with `stream=True, stream_options={"include_usage": True}`. Print each piece as it arrives. Measure the time to the first token, the total time and the tokens per second.
3. Print the first 12 chunks, then join all the pieces.

✅ Expected: the first words show in well under a second, and the total time is about the same as without streaming (about 4.3 s, 20 tokens/s on the work PC). Chunks look like `'A', ' diamond', ' is', ...`; 88 tokens, 87 chunks with text. *Varies:* all times; the non-streaming call sometimes gives 80 tokens.

📚 Look up: the `openai` package's "Streaming responses"; `print(end=, flush=)`.

## Exercise 5: Zero-shot vs few-shot

1. Copy the 5 categories, 2 templates, 5 examples and 10 test messages from the notes.
2. Write `build_messages(template, message, examples)`: system prompt from `.format`, the examples as fake user/assistant turns, then the message. Print one result.
3. Write `classify(...)` (`temperature=0`, `max_tokens=10`, `.strip().lower()`) and `accuracy(...)`, which prints the misses.
4. Score 4 prompts: zero-shot, few-shot, zero-shot + definitions, few-shot + definitions.

✅ Expected: 70%, 80%, 90%, 90% (the same in 3 runs on the work PC). Be ready to explain why 80% vs 90% on 10 messages proves little, and why the examples must not appear in the tests.

📚 Look up: Prompt Engineering Guide "Few-shot Prompting"; `str.format`.

## Exercise 6: `llm.py`: settings, timeouts, retries, errors

1. Write `llm.py`: `load_dotenv()`, 4 settings from `os.getenv` (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`, `LLM_TIMEOUT`), a client with `timeout` and `max_retries=2`, an `LLMError` class, a `friendly_errors()` context manager, and `chat()` and `ask()`.
2. Write `ex6_reliability.py`: turn on `logging`, ask a question, then ask for a long essay with `timeout=2`.
3. Break it: `$env:LLM_MODEL = "qwen9"`, then `$env:LLM_BASE_URL = "http://127.0.0.1:9999/v1"`. Run `Remove-Item Env:...` after each.

⚠️ You don't need a `.env` file here. Before you ever make one, un-comment `.env` in `.gitignore` (it's switched off in this repo).

✅ Expected: the timeout gives 2 retries, then `LLM error: No answer from ... in time.` after about 7 s (3 × 2 s + the waits). Wrong model → `Model 'qwen9' not found. For Ollama, run: ollama pull qwen9`, with no retries. Wrong address → 2 retries, then `Can't reach http://127.0.0.1:9999/v1. Is Ollama running?`

📚 Look up: the `openai` package's "Handling errors", "Retries" and "Timeouts"; `contextlib.contextmanager`; python-dotenv.

---

## How to work
1. Make `05_llm/task10/` and do the exercises in order, one file each. Commit after each exercise.
2. The worked examples are in [notes/](notes/) (`task10_ex1_...` to `task10_ex6_...`). The finished code is in [examples/task10/](examples/task10/) if you get stuck. Your files and the examples are the same (no path differences this time).
3. When you're done, ask Claude to **"review all"**.
