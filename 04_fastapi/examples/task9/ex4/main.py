import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import Body, Depends, FastAPI, HTTPException
from sklearn.pipeline import Pipeline

from schemas import BatchPrediction, DiamondIn, Prediction

ROOT = Path(__file__).resolve().parents[4]  # the repo folder
MODEL_FILE = ROOT / "03_ml" / "models" / "diamond_price_model.joblib"

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = Path(os.getenv("MODEL_PATH", MODEL_FILE))
    start = time.perf_counter()
    try:
        ml_models["price"] = joblib.load(model_path)
    except FileNotFoundError:
        print(f"WARNING: no model at {model_path}. /predict will answer 503.")
    else:
        seconds = time.perf_counter() - start
        print(f"Loaded {model_path.name} in {seconds:.2f} s")
    yield
    ml_models.clear()
    print("Model unloaded")


app = FastAPI(title="Diamond Price API", lifespan=lifespan)


def get_model() -> Pipeline:
    if "price" not in ml_models:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run 03_ml/diamond_prices.ipynb (Exercise 8) "
            "to create it, then restart the server.",
        )
    return ml_models["price"]


Model = Annotated[Pipeline, Depends(get_model)]


@app.get("/health")
def health() -> dict[str, str | bool]:
    loaded = "price" in ml_models
    return {"status": "ok" if loaded else "no model", "model_loaded": loaded}


@app.post("/predict")
def predict(diamond: DiamondIn, model: Model) -> Prediction:
    rows = pd.DataFrame([diamond.model_dump()])
    price = model.predict(rows)[0]
    return Prediction(price=round(price))


@app.post("/predict/batch")
def predict_batch(
    diamonds: Annotated[list[DiamondIn], Body(min_length=1, max_length=1000)],
    model: Model,
) -> BatchPrediction:
    rows = pd.DataFrame([d.model_dump() for d in diamonds])
    prices = model.predict(rows)
    return BatchPrediction(count=len(prices), prices=[round(p) for p in prices])
