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
