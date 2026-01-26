import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from joblib import load
from fastapi.middleware.cors import CORSMiddleware

from api.weather_api import (
    get_location,
    get_live_weather,
    predict_rain,
    get_weather_data
)

# ✅ FIRST create app
app = FastAPI(title="AI Weather Prediction Backend API")

# ✅ THEN add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you will change to vercel url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------
# Load ML Model (Only once)
# ------------------------------------
MODEL_PATH = "ml/temperature_model_old.pkl"

try:
    model = load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"❌ Error loading model: {e}")


# ------------------------------------
# Request Body
# ------------------------------------
class WeatherRequest(BaseModel):
    place: str


# ------------------------------------
# Health Check API
# ------------------------------------
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None
    }


# ------------------------------------
# Weather Prediction API (POST)
# ------------------------------------
@app.post("/weather")
def get_weather(request: WeatherRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    place = request.place.strip()
    if not place:
        raise HTTPException(status_code=400, detail="Place is required")

    # 1) Get location
    try:
        lat, lon = get_location(place)
    except Exception:
        raise HTTPException(status_code=503, detail="Location service unavailable")

    if lat is None or lon is None:
        raise HTTPException(status_code=404, detail="Location not found")

    # 2) Get live weather
    try:
        weather = get_live_weather(lat, lon)
    except Exception:
        raise HTTPException(status_code=503, detail="Live weather service unavailable")

    if weather is None:
        raise HTTPException(status_code=503, detail="Live weather not available")

    # Extract
    temperature = weather.get("temperature", 0)
    humidity = weather.get("humidity", 0)
    precipitation = weather.get("precipitation", 0)
    cloud_cover = weather.get("cloud_cover", 0)
    wind_speed = weather.get("wind_speed", 0)

    feels_like = temperature + (humidity * 0.05)

    # 3) Tomorrow Prediction (ML)
    tomorrow = datetime.now() + timedelta(days=1)

    model_input = pd.DataFrame([{
        "tmin": temperature - 2,
        "tmax": temperature + 2,
        "prcp": precipitation,
        "wspd": wind_speed,
        "month": tomorrow.month,
        "day": tomorrow.day
    }])

    try:
        predicted_temp = float(model.predict(model_input)[0])
    except Exception:
        raise HTTPException(status_code=500, detail="Prediction failed")

    # 4) Rain Prediction (Rule-based)
    rain_status = predict_rain(
        precipitation=precipitation,
        humidity=humidity,
        cloud_cover=cloud_cover
    )

    # Response
    return {
        "place": place,
        "coordinates": {"lat": lat, "lon": lon},
        "live_weather": {
            "temperature": round(float(temperature), 1),
            "humidity": round(float(humidity), 0),
            "precipitation": round(float(precipitation), 2),
            "cloud_cover": round(float(cloud_cover), 0),
            "wind_speed": round(float(wind_speed), 1),
            "feels_like": round(float(feels_like), 1)
        },
        "tomorrow_prediction": {
            "predicted_avg_temperature": round(predicted_temp, 2),
            "rain_status": rain_status
        }
    }


# ------------------------------------
# 7-Day Forecast API (GET)
# ------------------------------------
@app.get("/forecast7")
def get_7day_forecast(place: str):
    place = place.strip()
    if not place:
        raise HTTPException(status_code=400, detail="Place is required")

    try:
        weekly_data = get_weather_data(place)
    except Exception:
        raise HTTPException(status_code=503, detail="Forecast service unavailable")

    if not weekly_data:
        raise HTTPException(status_code=503, detail="7-day forecast not available")

    forecast_list = []
    for d, tmax, tmin in zip(
        weekly_data["dates"],
        weekly_data["temp_max"],
        weekly_data["temp_min"]
    ):
        forecast_list.append({
            "date": d,
            "tmax": round(float(tmax), 1),
            "tmin": round(float(tmin), 1)
        })

    return {
        "place": place,
        "forecast": forecast_list
    }
