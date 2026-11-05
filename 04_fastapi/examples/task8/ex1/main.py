from fastapi import FastAPI

app = FastAPI(title="Diamond Shop")


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to Diamond Shop"}


@app.get("/grades")
def grades() -> dict[str, list[str]]:
    return {
        "cut": ["Fair", "Good", "Very Good", "Premium", "Ideal"],
        "color": ["J", "I", "H", "G", "F", "E", "D"],
        "clarity": ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"],
    }
