"""Check the learning environment: Python, the libraries, and the Ollama server.

Run it in an activated (dsllm) terminal:  python 01_python/check_setup.py
"""

import importlib
import json
import sys
import urllib.request

LIBRARIES = ["numpy", "pandas", "sklearn", "matplotlib", "seaborn", "fastapi",
             "torch", "openai", "pytest"]

print("Python:", sys.version.split()[0])
print("Interpreter:", sys.executable)
for name in LIBRARIES:
    try:
        lib = importlib.import_module(name)
        print(f"{name:10} {lib.__version__}")
    except ImportError:
        print(f"{name:10} MISSING (see SETUP.md)")

try:
    with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as reply:
        models = [model["name"] for model in json.load(reply)["models"]]
    print("Ollama     running, models:", ", ".join(models) or "none yet")
except OSError:
    print("Ollama     not running or not installed (see SETUP.md)")
