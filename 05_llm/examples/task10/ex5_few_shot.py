"""Task 10, Exercise 5: prompt templates, zero-shot vs few-shot."""

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
MODEL = "qwen2.5:1.5b"

CATEGORIES = ["order_status", "pricing", "returns", "product_info", "complaint"]
PLAIN = (
    "Classify the customer message of a diamond shop into one of these "
    "categories: {categories}. Reply with the category only."
)
DEFINED = (
    "Classify the customer message of a diamond shop into one category:\n"
    "- order_status: where an order is, delivery, tracking, lost parcels\n"
    "- pricing: prices, discounts, payment\n"
    "- returns: refunds, exchanges, sending an item back\n"
    "- product_info: questions about stones, metals, grades and sizes\n"
    "- complaint: unhappy about quality, damage or service\n"
    "Reply with the category only."
)
EXAMPLES = [
    ("When will my necklace arrive?", "order_status"),
    ("What is the price of the heart-shaped pendant?", "pricing"),
    ("I want my money back, the colour is not what I expected.", "returns"),
    ("What does VVS1 clarity mean?", "product_info"),
    ("Your staff were rude to me on the phone.", "complaint"),
]
TESTS = [
    ("Where is my parcel? I ordered last Monday.", "order_status"),
    ("Do you give a discount if I buy two rings?", "pricing"),
    ("The ring doesn't fit, can I send it back for a refund?", "returns"),
    ("Is your 1 carat stone lab-grown or natural?", "product_info"),
    ("The stone fell out of the setting after a week. Very disappointed!",
     "complaint"),
    ("How much would a 0.5 carat VS1 diamond cost?", "pricing"),
    ("Can I exchange my earrings for a pendant?", "returns"),
    ("My order says delivered but nothing came.", "order_status"),
    ("Do you sell platinum wedding bands?", "product_info"),
    ("I waited 40 minutes in your shop and nobody helped me.", "complaint"),
]


def build_messages(template: str, message: str,
                   examples: list[tuple[str, str]]) -> list[dict]:
    """Fill the template, add the examples as earlier turns, then the message."""
    system = template.format(categories=", ".join(CATEGORIES))
    messages = [{"role": "system", "content": system}]
    for text, label in examples:
        messages.append({"role": "user", "content": text})
        messages.append({"role": "assistant", "content": label})
    messages.append({"role": "user", "content": message})
    return messages


for message in build_messages(PLAIN, "Do you sell gold chains?", EXAMPLES[:2]):
    print(f"{message['role']:>9}: {message['content']}")


def classify(template: str, message: str, examples: list[tuple[str, str]]) -> str:
    """Return the model's category for one message, tidied up."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=build_messages(template, message, examples),
        temperature=0,
        seed=42,
        max_tokens=10,
    )
    return response.choices[0].message.content.strip().lower()


def accuracy(template: str, examples: list[tuple[str, str]]) -> float:
    """Classify every test message; print the misses; return the share correct."""
    correct = 0
    for message, expected in TESTS:
        answer = classify(template, message, examples)
        if answer == expected:
            correct += 1
        else:
            print(f"    miss: {message!r} -> {answer!r} (expected {expected!r})")
    return correct / len(TESTS)


print(f"Zero-shot: {accuracy(PLAIN, []):.0%}")

for name, template, examples in [
    ("few-shot", PLAIN, EXAMPLES),
    ("zero-shot + definitions", DEFINED, []),
    ("few-shot + definitions", DEFINED, EXAMPLES),
]:
    print(f"{name}: {accuracy(template, examples):.0%}")
