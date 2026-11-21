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
