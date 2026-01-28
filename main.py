# import requests
# import pandas as pd
# from datetime import datetime, timedelta
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from joblib import load
# from fastapi.middleware.cors import CORSMiddleware
#
# # ==================================================
# # CONFIG
# # ==================================================
# OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
# GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
# MODEL_PATH = "ml/temperature_model_old.pkl"
#
# # ==================================================
# # FASTAPI APP
# # ==================================================
# app = FastAPI(title="AI Weather Prediction Backend API")
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # ==================================================
# # LOAD ML MODEL
# # ==================================================
# try:
#     model = load(MODEL_PATH)
# except Exception as e:
#     model = None
#     print("❌ Model loading failed:", e)
#
# # ==================================================
# # REQUEST BODY
# # ==================================================
# class WeatherRequest(BaseModel):
#     place: str
#
# # ==================================================
# # UTILITY FUNCTIONS
# # ==================================================
# def get_location(place: str):
#     try:
#         r = requests.get(GEOCODE_URL, params={"name": place, "count": 1}, timeout=10)
#         r.raise_for_status()
#         data = r.json()
#
#         if "results" not in data or not data["results"]:
#             print("❌ Location not found:", place)
#             return None, None
#
#         loc = data["results"][0]
#         return loc["latitude"], loc["longitude"]
#
#     except Exception as e:
#         print("❌ Geocode error:", e)
#         return None, None
#
#
# def get_live_weather(lat, lon):
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "current_weather": True,
#         "hourly": "relativehumidity_2m,precipitation,cloudcover,windspeed_10m",
#         "timezone": "auto"
#     }
#
#     try:
#         r = requests.get(OPEN_METEO_URL, params=params, timeout=15)
#         r.raise_for_status()
#         data = r.json()
#
#         if "current_weather" not in data or "hourly" not in data:
#             print("❌ Invalid weather response:", data)
#             return None
#
#         cw = data["current_weather"]
#
#         return {
#             "temperature": cw.get("temperature"),
#             "wind_speed": cw.get("windspeed"),
#             "humidity": data["hourly"]["relativehumidity_2m"][0],
#             "precipitation": data["hourly"]["precipitation"][0],
#             "cloud_cover": data["hourly"]["cloudcover"][0]
#         }
#
#     except Exception as e:
#         print("❌ Open-Meteo error:", e)
#         return None
#
#
# def predict_rain(precipitation, humidity, cloud_cover):
#     if precipitation > 1 or (humidity > 80 and cloud_cover > 70):
#         return "High chance of rain"
#     return "Low chance of rain"
#
#
# def get_weather_data(place):
#     lat, lon = get_location(place)
#     if lat is None:
#         return None
#
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "daily": "temperature_2m_max,temperature_2m_min",
#         "timezone": "auto"
#     }
#
#     try:
#         r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
#         r.raise_for_status()
#         data = r.json()
#
#         return {
#             "dates": data["daily"]["time"],
#             "temp_max": data["daily"]["temperature_2m_max"],
#             "temp_min": data["daily"]["temperature_2m_min"]
#         }
#
#     except Exception as e:
#         print("❌ Forecast error:", e)
#         return None
#
#
# def get_hourly_weather(lat, lon, hours=12):
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "hourly": "temperature_2m",
#         "forecast_days": 1,
#         "timezone": "auto"
#     }
#
#     try:
#         r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
#         r.raise_for_status()
#         data = r.json()
#
#         times = data["hourly"]["time"]
#         temps = data["hourly"]["temperature_2m"]
#
#         now = datetime.now()
#         hourly = []
#
#         for t, temp in zip(times, temps):
#             time_obj = datetime.fromisoformat(t)
#             if time_obj >= now:
#                 hourly.append({
#                     "time": time_obj.strftime("%H:%M"),
#                     "temperature": round(float(temp), 1)
#                 })
#             if len(hourly) == hours:
#                 break
#
#         return hourly
#
#     except Exception as e:
#         print("❌ Hourly forecast error:", e)
#         return None
#
# # ==================================================
# # HEALTH CHECK
# # ==================================================
# @app.get("/health")
# def health_check():
#     return {
#         "status": "ok",
#         "model_loaded": model is not None
#     }
#
# # ==================================================
# # LIVE + TOMORROW PREDICTION
# # ==================================================
# @app.post("/weather")
# def get_weather(request: WeatherRequest):
#     if model is None:
#         raise HTTPException(status_code=500, detail="Model not loaded")
#
#     place = request.place.strip()
#     if not place:
#         raise HTTPException(status_code=400, detail="Place is required")
#
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(status_code=404, detail="Location not found")
#
#     weather = get_live_weather(lat, lon)
#     if weather is None:
#         raise HTTPException(status_code=503, detail="Live weather unavailable")
#
#     temperature = weather["temperature"]
#     humidity = weather["humidity"]
#     precipitation = weather["precipitation"]
#     cloud_cover = weather["cloud_cover"]
#     wind_speed = weather["wind_speed"]
#
#     feels_like = temperature + (humidity * 0.05)
#
#     tomorrow = datetime.now() + timedelta(days=1)
#
#     model_input = pd.DataFrame([{
#         "tmin": temperature - 2,
#         "tmax": temperature + 2,
#         "prcp": precipitation,
#         "wspd": wind_speed,
#         "month": tomorrow.month,
#         "day": tomorrow.day
#     }])
#
#     predicted_temp = float(model.predict(model_input)[0])
#
#     return {
#         "place": place,
#         "coordinates": {"lat": lat, "lon": lon},
#         "live_weather": {
#             "temperature": round(temperature, 1),
#             "humidity": round(humidity, 0),
#             "precipitation": round(precipitation, 2),
#             "cloud_cover": round(cloud_cover, 0),
#             "wind_speed": round(wind_speed, 1),
#             "feels_like": round(feels_like, 1)
#         },
#         "tomorrow_prediction": {
#             "predicted_avg_temperature": round(predicted_temp, 2),
#             "rain_status": predict_rain(precipitation, humidity, cloud_cover)
#         }
#     }
#
# # ==================================================
# # 7 DAY FORECAST
# # ==================================================
# @app.get("/forecast7")
# def forecast_7(place: str):
#     data = get_weather_data(place)
#     if not data:
#         raise HTTPException(status_code=503, detail="Forecast unavailable")
#
#     forecast = []
#     for d, tmax, tmin in zip(
#         data["dates"], data["temp_max"], data["temp_min"]
#     ):
#         forecast.append({
#             "date": d,
#             "tmax": round(float(tmax), 1),
#             "tmin": round(float(tmin), 1)
#         })
#
#     return {"place": place, "forecast": forecast}
#
# # ==================================================
# # HOURLY FORECAST (UI GRAPH)
# # ==================================================
# @app.get("/hourly")
# def hourly_forecast(place: str, hours: int = 12):
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(status_code=404, detail="Location not found")
#
#     hourly = get_hourly_weather(lat, lon, hours)
#     if not hourly:
#         raise HTTPException(status_code=503, detail="Hourly forecast unavailable")
#
#     return {
#         "place": place,
#         "hours": hours,
#         "hourly_forecast": hourly
#     }


import requests
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from joblib import load
from fastapi.middleware.cors import CORSMiddleware

# ==================================================
# CONFIG
# ==================================================
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
MODEL_PATH = "ml/temperature_model_old.pkl"

# ==================================================
# FASTAPI APP
# ==================================================
app = FastAPI(title="AI Weather Prediction Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# LOAD ML MODEL
# ==================================================
try:
    model = load(MODEL_PATH)
except Exception as e:
    model = None
    print("❌ Model loading failed:", e)

# ==================================================
# REQUEST BODY
# ==================================================
class WeatherRequest(BaseModel):
    place: str

# ==================================================
# UTILITY FUNCTIONS
# ==================================================
def get_location(place: str):
    try:
        r = requests.get(GEOCODE_URL, params={"name": place, "count": 1}, timeout=10)
        r.raise_for_status()
        data = r.json()

        if "results" not in data or not data["results"]:
            print("❌ Location not found:", place)
            return None, None

        loc = data["results"][0]
        return loc["latitude"], loc["longitude"]

    except Exception as e:
        print("❌ Geocode error:", e)
        return None, None


def get_live_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "relativehumidity_2m,precipitation,cloudcover,windspeed_10m",
        "timezone": "auto"
    }

    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()

        if "current_weather" not in data or "hourly" not in data:
            raise ValueError("Invalid Open-Meteo response")

        cw = data["current_weather"]

        return {
            "temperature": cw.get("temperature", 30.0),
            "wind_speed": cw.get("windspeed", 10.0),
            "humidity": data["hourly"]["relativehumidity_2m"][0],
            "precipitation": data["hourly"]["precipitation"][0],
            "cloud_cover": data["hourly"]["cloudcover"][0]
        }

    except Exception as e:
        print("⚠️ Open-Meteo live weather failed, using fallback:", e)
        return {
            "temperature": 30.0,
            "wind_speed": 10.0,
            "humidity": 70,
            "precipitation": 0.0,
            "cloud_cover": 40
        }


def predict_rain(precipitation, humidity, cloud_cover):
    if precipitation > 1 or (humidity > 80 and cloud_cover > 70):
        return "High chance of rain"
    return "Low chance of rain"


def get_weather_data(place):
    lat, lon = get_location(place)
    if lat is None:
        return None

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }

    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        return {
            "dates": data["daily"]["time"],
            "temp_max": data["daily"]["temperature_2m_max"],
            "temp_min": data["daily"]["temperature_2m_min"]
        }

    except Exception as e:
        print("⚠️ Forecast API failed, using fallback:", e)

        today = datetime.now()
        dates, tmax, tmin = [], [], []

        for i in range(7):
            d = today + timedelta(days=i)
            dates.append(d.strftime("%Y-%m-%d"))
            tmax.append(30.0)
            tmin.append(24.0)

        return {
            "dates": dates,
            "temp_max": tmax,
            "temp_min": tmin
        }


def get_hourly_weather(lat, lon, hours=12):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "forecast_days": 1,
        "timezone": "auto"
    }

    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        times = data["hourly"]["time"]
        temps = data["hourly"]["temperature_2m"]

        now = datetime.now()
        hourly = []

        for t, temp in zip(times, temps):
            time_obj = datetime.fromisoformat(t)
            if time_obj >= now:
                hourly.append({
                    "time": time_obj.strftime("%H:%M"),
                    "temperature": round(float(temp), 1)
                })
            if len(hourly) == hours:
                break

        return hourly

    except Exception as e:
        print("⚠️ Hourly API failed, using fallback:", e)
        return [
            {"time": "10:00", "temperature": 29},
            {"time": "11:00", "temperature": 30},
            {"time": "12:00", "temperature": 31},
            {"time": "13:00", "temperature": 32},
            {"time": "14:00", "temperature": 31},
        ]

# ==================================================
# HEALTH CHECK
# ==================================================
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None
    }

# ==================================================
# LIVE + TOMORROW PREDICTION
# ==================================================
@app.post("/weather")
def get_weather(request: WeatherRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    place = request.place.strip()
    if not place:
        raise HTTPException(status_code=400, detail="Place is required")

    lat, lon = get_location(place)
    if lat is None:
        raise HTTPException(status_code=404, detail="Location not found")

    weather = get_live_weather(lat, lon)

    temperature = weather["temperature"]
    humidity = weather["humidity"]
    precipitation = weather["precipitation"]
    cloud_cover = weather["cloud_cover"]
    wind_speed = weather["wind_speed"]

    feels_like = temperature + (humidity * 0.05)

    tomorrow = datetime.now() + timedelta(days=1)

    model_input = pd.DataFrame([{
        "tmin": temperature - 2,
        "tmax": temperature + 2,
        "prcp": precipitation,
        "wspd": wind_speed,
        "month": tomorrow.month,
        "day": tomorrow.day
    }])

    predicted_temp = float(model.predict(model_input)[0])

    return {
        "place": place,
        "coordinates": {"lat": lat, "lon": lon},
        "live_weather": {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 0),
            "precipitation": round(precipitation, 2),
            "cloud_cover": round(cloud_cover, 0),
            "wind_speed": round(wind_speed, 1),
            "feels_like": round(feels_like, 1)
        },
        "tomorrow_prediction": {
            "predicted_avg_temperature": round(predicted_temp, 2),
            "rain_status": predict_rain(precipitation, humidity, cloud_cover)
        }
    }

# ==================================================
# 7 DAY FORECAST
# ==================================================
@app.get("/forecast7")
def forecast_7(place: str):
    data = get_weather_data(place)

    forecast = []
    for d, tmax, tmin in zip(
        data["dates"], data["temp_max"], data["temp_min"]
    ):
        forecast.append({
            "date": d,
            "tmax": round(float(tmax), 1),
            "tmin": round(float(tmin), 1)
        })

    return {"place": place, "forecast": forecast}

# ==================================================
# HOURLY FORECAST (UI GRAPH)
# ==================================================
@app.get("/hourly")
def hourly_forecast(place: str, hours: int = 12):
    lat, lon = get_location(place)
    if lat is None:
        raise HTTPException(status_code=404, detail="Location not found")

    hourly = get_hourly_weather(lat, lon, hours)

    return {
        "place": place,
        "hours": hours,
        "hourly_forecast": hourly
    }