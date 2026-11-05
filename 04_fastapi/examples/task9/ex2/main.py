import time
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI

from schemas import DiamondIn, Prediction

ROOT = Path(__file__).resolve().parents[4]  # the repo folder
MODEL_FILE = ROOT / "03_ml" / "models" / "diamond_price_model.joblib"

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.perf_counter()
    ml_models["price"] = joblib.load(MODEL_FILE)
    seconds = time.perf_counter() - start
    print(f"Loaded {MODEL_FILE.name} in {seconds:.2f} s")
    yield
    ml_models.clear()
    print("Model unloaded")


app = FastAPI(title="Diamond Price API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str | bool]:
    loaded = "price" in ml_models
    return {"status": "ok" if loaded else "no model", "model_loaded": loaded}


@app.post("/predict")
def predict(diamond: DiamondIn) -> Prediction:
    rows = pd.DataFrame([diamond.model_dump()])
    price = ml_models["price"].predict(rows)[0]
    return Prediction(price=round(price))
