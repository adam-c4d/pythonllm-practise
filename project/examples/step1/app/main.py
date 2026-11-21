"""Ask Your Data API: the capstone app."""

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile

from app.summary import summarise

app = FastAPI(title="Ask Your Data API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    """A quick "is it running?" check, like Laravel's /up route."""
    return {"status": "ok"}


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
