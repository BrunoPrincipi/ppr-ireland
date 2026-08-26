# ============================================
# PPR IRELAND - PRICE PREDICTION API
# ============================================
# FastAPI app that serves the XGBoost model
# as a REST API endpoint
# ============================================

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import os

# --- LOAD MODEL AND ENCODERS ---
# These were saved by train_model.py
# joblib loads them back into memory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, 'model.pkl'))
county_encoder = joblib.load(os.path.join(BASE_DIR, 'county_encoder.pkl'))
county_list = joblib.load(os.path.join(BASE_DIR, 'county_list.pkl'))

# --- CREATE FASTAPI APP ---
app = FastAPI(
    title="Irish Property Price Predictor",
    description="Predicts residential property prices in Ireland using XGBoost",
    version="1.0.0"
)

# --- DEFINE INPUT SCHEMA ---
# Pydantic BaseModel validates the incoming request
# If the user sends wrong data types it returns a clear error
class PropertyInput(BaseModel):
    county: str           # e.g. "Dublin"
    sale_year: int        # e.g. 2024
    sale_month: int       # e.g. 6
    is_new: int           # 1 for new build, 0 for second-hand
    vat_exclusive: int    # 1 if VAT exclusive, 0 if not

# --- DEFINE OUTPUT SCHEMA ---
class PredictionOutput(BaseModel):
    predicted_price: float
    county: str
    sale_year: int
    model_note: str

# --- HEALTH ENDPOINT ---
@app.get("/health")
def health_check():
    return {
        "status": "running",
        "model": "XGBoost Price Predictor",
        "counties_supported": len(county_list)
    }

# --- COUNTIES ENDPOINT ---
# Lists all valid counties so users know what to send
@app.get("/counties")
def get_counties():
    return {"counties": county_list}

# --- PREDICT ENDPOINT ---
@app.post("/predict", response_model=PredictionOutput)
def predict_price(data: PropertyInput):

    # Validate county
    if data.county not in county_list:
        return {
            "predicted_price": 0,
            "county": data.county,
            "sale_year": data.sale_year,
            "model_note": f"County '{data.county}' not recognised. Use /counties to see valid options."
        }

    # Encode county from string to number
    county_encoded = county_encoder.transform([data.county])[0]

    # Build feature array in same order as training
    features = np.array([[
        county_encoded,
        data.sale_year,
        data.sale_month,
        data.is_new,
        data.vat_exclusive
    ]])

    # Predict log price then convert back to euros
    log_price = model.predict(features)[0]
    predicted_price = float(np.exp(log_price))

    return {
        "predicted_price": round(predicted_price, 2),
        "county": data.county,
        "sale_year": data.sale_year,
        "model_note": "Prediction based on county, year and property type only. Actual prices vary significantly based on property size, condition and exact location."
    }