"""Ask Your Data API: the capstone app."""

from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile

from app.config import MODEL_PATH
from app.schemas import DiamondIn, PriceOut
from app.summary import summarise

models: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the price model once, when the server starts (like a provider's boot())."""
    if MODEL_PATH.exists():
        models["price"] = joblib.load(MODEL_PATH)
    yield
    models.clear()


app = FastAPI(title="Ask Your Data API", version="0.2.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    """A quick "is it running?" check, like Laravel's /up route."""
    return {"status": "ok", "price_model_loaded": "price" in models}


@app.post("/summary")
def summary(file: UploadFile) -> dict:
    """Upload a CSV file and get a summary of its contents."""
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")
    try:
        df = pd.read_csv(file.file)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as err:
        message = f"Can't read this CSV: {err}"
        raise HTTPException(status_code=400, detail=message) from err
    return {"filename": file.filename, **summarise(df)}


@app.post("/predict")
def predict(diamond: DiamondIn) -> PriceOut:
    """Predict the price of one diamond with the Task 6 model."""
    model = models.get("price")
    if model is None:
        message = f"No price model at {MODEL_PATH}. Run Task 6 Exercise 8 first."
        raise HTTPException(status_code=503, detail=message)
    row = pd.DataFrame([diamond.model_dump()])
    return PriceOut(price=round(float(model.predict(row)[0]), 2))
