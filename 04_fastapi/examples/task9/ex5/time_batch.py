import time
from pathlib import Path

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]  # the repo folder
URL = "http://127.0.0.1:8001"
FEATURES = ["carat", "cut", "color", "clarity", "depth", "table"]

df = pd.read_csv(ROOT / "03_ml" / "data" / "diamonds.csv")
diamonds = df[FEATURES].head(500).to_dict("records")

with httpx.Client(base_url=URL) as client:
    start = time.perf_counter()
    one_by_one = [client.post("/predict", json=d).json()["price"] for d in diamonds]
    single_seconds = time.perf_counter() - start

    start = time.perf_counter()
    batch = client.post("/predict/batch", json=diamonds).json()["prices"]
    batch_seconds = time.perf_counter() - start

print(f"{len(diamonds)} requests to /predict:   {single_seconds:.2f} s")
print(f"1 request to /predict/batch: {batch_seconds:.2f} s")
print(f"Batch is {single_seconds / batch_seconds:.0f}x faster")
print("Same prices:", one_by_one == batch)
