import json
import logging
import os
from contextlib import asynccontextmanager
from math import exp
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

logger = logging.getLogger("loan-api")


def load_model() -> dict:
    """Read the model from MODEL_PATH (configurable, so the image needs no local files)."""
    path = os.getenv("MODEL_PATH", "model/model.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()  # fail fast if the model is missing
    yield


app = FastAPI(title="Loan Prediction API", version="1.0.0", lifespan=lifespan)


class PredictionRequest(BaseModel):
    amount_usd: int = Field(..., ge=100, le=5000, examples=[1500])
    term_months: Literal[3, 6, 12, 18, 24] = Field(..., examples=[12])
    monthly_income_usd: float = Field(..., gt=0, le=100000, examples=[400])


class PredictionResponse(BaseModel):
    default_probability: float = Field(..., ge=0, le=1, examples=[0.3])
    risk_band: Literal["low", "medium", "high"]
    model_version: str


def log_prediction(req: PredictionRequest, probability: float, band: str) -> None:
    """Store the prediction if DATABASE_URL is set; never break the prediction itself."""
    url = os.getenv("DATABASE_URL")
    if not url:
        return
    try:
        import psycopg

        with psycopg.connect(url, connect_timeout=3) as conn:
            conn.execute(
                "INSERT INTO predictions (amount_usd, term_months, monthly_income_usd, "
                "default_probability, risk_band) VALUES (%s, %s, %s, %s, %s)",
                (req.amount_usd, req.term_months, req.monthly_income_usd, probability, band),
            )
    except Exception:
        logger.warning("Could not log prediction to the database", exc_info=True)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_version": app.state.model["version"],
        "git_sha": os.getenv("GIT_SHA", "unknown"),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    model = app.state.model
    c = model["coefficients"]
    z = (
        model["intercept"]
        + c["amount_usd"] * req.amount_usd
        + c["term_months"] * req.term_months
        + c["monthly_income_usd"] * req.monthly_income_usd
    )
    probability = round(1 / (1 + exp(-z)), 4)
    bands = model["bands"]
    band = "low" if probability < bands["low_below"] else (
        "medium" if probability < bands["high_from"] else "high")
    log_prediction(req, probability, band)
    return PredictionResponse(default_probability=probability, risk_band=band,
                              model_version=model["version"])
