# import requests
# from datetime import datetime, timedelta
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
#
# # ================= CONFIG =================
# OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
# GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
#
# # ================= APP =================
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# class PlaceRequest(BaseModel):
#     place: str
#
# # ================= LOCATION =================
# def get_location(place):
#     r = requests.get(GEOCODE, params={"name": place, "count": 1}).json()
#
#     if "results" not in r:
#         return None, None
#
#     loc = r["results"][0]
#     return loc["latitude"], loc["longitude"]
#
# # ================= FETCH WEATHER DATA =================
# def fetch_data(lat, lon):
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "hourly": ",".join([
#             "temperature_2m",
#             "apparent_temperature",
#             "relativehumidity_2m",
#             "precipitation",
#             "cloudcover",
#             "windspeed_10m"
#         ]),
#         "daily": "temperature_2m_max",
#         "forecast_days": 7,
#         "timezone": "auto"
#     }
#
#     return requests.get(OPEN_METEO, params=params).json()
#
# # =====================================================
# # 1️⃣ CURRENT WEATHER
# # =====================================================
# @app.post("/current-weather")
# def current_weather(req: PlaceRequest):
#     lat, lon = get_location(req.place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     data = fetch_data(lat, lon)
#     h = data["hourly"]
#
#     return {
#         "temperature": h["temperature_2m"][0],
#         "feels_like": h["apparent_temperature"][0],
#         "humidity": h["relativehumidity_2m"][0],
#         "wind": h["windspeed_10m"][0],
#         "cloud": h["cloudcover"][0],
#         "rain": "Yes" if h["precipitation"][0] > 0 else "No"
#     }
#
# # =====================================================
# # 2️⃣ 7 DAY FORECAST
# # =====================================================
# @app.get("/forecast7")
# def forecast7(place: str):
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "daily": "temperature_2m_max",
#         "forecast_days": 7,
#         "timezone": "auto"
#     }
#
#     data = requests.get(OPEN_METEO, params=params).json()
#     d = data["daily"]
#
#     result = []
#     for i, date in enumerate(d["time"]):
#         result.append({
#             "day": datetime.fromisoformat(date).strftime("%a"),
#             "temp": round(d["temperature_2m_max"][i])
#         })
#
#     return result
#
# # =====================================================
# # 3️⃣ HOURLY FORECAST (GRAPH)
# # =====================================================
# @app.get("/hourly")
# def hourly(place: str, day_index: int = 0):
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     data = fetch_data(lat, lon)
#     h = data["hourly"]
#
#     target_date = datetime.now().date() + timedelta(days=day_index)
#
#     result = []
#     for i, t in enumerate(h["time"]):
#         dt = datetime.fromisoformat(t)
#
#         if dt.date() != target_date:
#             continue
#
#         result.append({
#             "time": dt.strftime("%H:%M"),
#             "temp": h["temperature_2m"][i]
#         })
#
#     return result
#
# # =====================================================
# # 4️⃣ DAY DETAILS (CARD INFO)
# # =====================================================
# @app.get("/day-details")
# def day_details(place: str, day_index: int = 0):
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     data = fetch_data(lat, lon)
#     h = data["hourly"]
#
#     target_date = datetime.now().date() + timedelta(days=day_index)
#
#     feels, hum, wind, cloud, rain = [], [], [], [], []
#
#     for i, t in enumerate(h["time"]):
#         dt = datetime.fromisoformat(t)
#
#         if dt.date() != target_date:
#             continue
#
#         feels.append(h["apparent_temperature"][i])
#         hum.append(h["relativehumidity_2m"][i])
#         wind.append(h["windspeed_10m"][i])
#         cloud.append(h["cloudcover"][i])
#         rain.append(h["precipitation"][i])
#
#     return {
#         "feels_like": max(feels) if feels else 0,
#         "humidity": sum(hum)/len(hum) if hum else 0,
#         "wind": max(wind) if wind else 0,
#         "cloud": sum(cloud)/len(cloud) if cloud else 0,
#         "rain": "Yes" if sum(rain) > 0 else "No"
#     }
#
# # =====================================================
# # 5️⃣ HEALTH CHECK
# # =====================================================
# @app.get("/health")
# def health():
#     return {"status": "ok"}
#

# import requests
# from datetime import datetime, timedelta
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
#
# # ================= CONFIG =================
# OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
# GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
#
# # ================= APP =================
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# class PlaceRequest(BaseModel):
#     place: str
#
# # ================= LOCATION =================
# def get_location(place):
#     r = requests.get(GEOCODE, params={"name": place, "count": 1}).json()
#     if "results" not in r:
#         return None, None
#     loc = r["results"][0]
#     return loc["latitude"], loc["longitude"]
#
# # ================= FETCH WEATHER DATA =================
# def fetch_data(lat, lon):
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "hourly": ",".join([
#             "temperature_2m",
#             "apparent_temperature",
#             "relativehumidity_2m",
#             "precipitation",
#             "cloudcover",
#             "windspeed_10m"
#         ]),
#         "daily": "temperature_2m_max",
#         "forecast_days": 7,
#         "timezone": "auto"
#     }
#     return requests.get(OPEN_METEO, params=params).json()
#
# # =====================================================
# # 1️⃣ POST /weather → CURRENT WEATHER
# # =====================================================
# @app.post("/weather")
# def current_weather(req: PlaceRequest):
#     lat, lon = get_location(req.place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     data = fetch_data(lat, lon)
#     h = data["hourly"]
#
#     return {
#         "temperature": h["temperature_2m"][0],
#         "feels_like": h["apparent_temperature"][0],
#         "humidity": h["relativehumidity_2m"][0],
#         "wind": h["windspeed_10m"][0],
#         "cloud": h["cloudcover"][0],
#         "rain": "Yes" if h["precipitation"][0] > 0 else "No"
#     }
#
# # =====================================================
# # 2️⃣ GET /forecast7 → 7 DAY FORECAST
# # =====================================================
# @app.get("/forecast7")
# def forecast7(place: str):
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     params = {
#         "latitude": lat,
#         "longitude": lon,
#         "daily": "temperature_2m_max",
#         "forecast_days": 7,
#         "timezone": "auto"
#     }
#
#     data = requests.get(OPEN_METEO, params=params).json()
#     d = data["daily"]
#
#     result = []
#     for i, date in enumerate(d["time"]):
#         result.append({
#             "day": datetime.fromisoformat(date).strftime("%a"),
#             "temp": round(d["temperature_2m_max"][i])
#         })
#
#     return result
#
# # =====================================================
# # 3️⃣ GET /weather → HOURLY FORECAST
# # =====================================================
# @app.get("/weather")
# def hourly_weather(place: str, hours: int = 12):
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     data = fetch_data(lat, lon)
#     h = data["hourly"]
#
#     result = []
#     for i in range(min(hours, len(h["time"]))):
#         result.append({
#             "time": datetime.fromisoformat(h["time"][i]).strftime("%H:%M"),
#             "temp": h["temperature_2m"][i]
#         })
#
#     return result
#
# # =====================================================
# # 4️⃣ DAY DETAILS (UNCHANGED ✅)
# # =====================================================
# @app.get("/day-details")
# def day_details(place: str, day_index: int = 0):
#     lat, lon = get_location(place)
#     if lat is None:
#         raise HTTPException(404, "Place not found")
#
#     data = fetch_data(lat, lon)
#     h = data["hourly"]
#
#     target_date = datetime.now().date() + timedelta(days=day_index)
#
#     feels, hum, wind, cloud, rain = [], [], [], [], []
#
#     for i, t in enumerate(h["time"]):
#         dt = datetime.fromisoformat(t)
#         if dt.date() != target_date:
#             continue
#
#         feels.append(h["apparent_temperature"][i])
#         hum.append(h["relativehumidity_2m"][i])
#         wind.append(h["windspeed_10m"][i])
#         cloud.append(h["cloudcover"][i])
#         rain.append(h["precipitation"][i])
#
#     return {
#         "feels_like": max(feels) if feels else 0,
#         "humidity": sum(hum)/len(hum) if hum else 0,
#         "wind": max(wind) if wind else 0,
#         "cloud": sum(cloud)/len(cloud) if cloud else 0,
#         "rain": "Yes" if sum(rain) > 0 else "No"
#     }
#
# # =====================================================
# # 5️⃣ HEALTH CHECK
# # =====================================================
# @app.get("/health")
# def health():
#     return {"status": "ok"}


import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ================= CONFIG =================
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"

# ================= APP =================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlaceRequest(BaseModel):
    place: str

# ================= LOCATION =================
def get_location(place):
    r = requests.get(GEOCODE, params={"name": place, "count": 1}).json()

    if "results" not in r:
        return None, None

    loc = r["results"][0]
    return loc["latitude"], loc["longitude"]

# ================= FETCH WEATHER DATA =================
def fetch_data(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "relativehumidity_2m",
            "precipitation",
            "cloudcover",
            "windspeed_10m"
        ]),
        "daily": "temperature_2m_max,temperature_2m_min",
        "forecast_days": 7,
        "timezone": "auto"
    }

    return requests.get(OPEN_METEO, params=params).json()

# ================= PREDICT RAIN =================
def predict_rain(precipitation, humidity, cloud_cover):
    if precipitation > 1 or (humidity > 80 and cloud_cover > 70):
        return "High chance of rain"
    return "Low chance of rain"

# =====================================================
# 1️⃣ CURRENT WEATHER + TOMORROW PREDICTION
# =====================================================
@app.post("/weather")
def current_weather(req: PlaceRequest):
    lat, lon = get_location(req.place)
    if lat is None:
        raise HTTPException(404, "Place not found")

    data = fetch_data(lat, lon)
    h = data["hourly"]

    temperature = h["temperature_2m"][0]
    humidity = h["relativehumidity_2m"][0]
    precipitation = h["precipitation"][0]
    cloud_cover = h["cloudcover"][0]
    wind_speed = h["windspeed_10m"][0]
    feels_like = h["apparent_temperature"][0]

    # Dummy tomorrow prediction using simple logic
    predicted_avg_temperature = round(temperature + 0.8, 1)
    rain_status = predict_rain(precipitation, humidity, cloud_cover)

    return {
        "place": req.place,
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
            "predicted_avg_temperature": predicted_avg_temperature,
            "rain_status": rain_status
        }
    }

# =====================================================
# 2️⃣ 7 DAY FORECAST
# =====================================================
@app.get("/forecast7")
def forecast7(place: str):
    lat, lon = get_location(place)
    if lat is None:
        raise HTTPException(404, "Place not found")

    data = fetch_data(lat, lon)
    d = data["daily"]

    forecast = []
    for date, tmax, tmin in zip(d["time"], d["temperature_2m_max"], d["temperature_2m_min"]):
        forecast.append({
            "date": date,
            "tmax": round(tmax, 1),
            "tmin": round(tmin, 1)
        })

    return {
        "place": place,
        "forecast": forecast
    }

# =====================================================
# 3️⃣ HOURLY FORECAST
# =====================================================
@app.get("/hourly")
def hourly(place: str, hours: int = 12):
    lat, lon = get_location(place)
    if lat is None:
        raise HTTPException(404, "Place not found")

    data = fetch_data(lat, lon)
    h = data["hourly"]

    now = datetime.now()
    hourly_forecast = []

    for t, temp in zip(h["time"], h["temperature_2m"]):
        dt = datetime.fromisoformat(t)
        if dt >= now:
            hourly_forecast.append({
                "time": dt.strftime("%H:%M"),
                "temperature": round(temp, 1)
            })
        if len(hourly_forecast) == hours:
            break

    return {
        "place": place,
        "hours": hours,
        "hourly_forecast": hourly_forecast
    }

# =====================================================
# 4️⃣ DAY DETAILS (CARD INFO) — keep unchanged
# =====================================================
@app.get("/day-details")
def day_details(place: str, day_index: int = 0):
    lat, lon = get_location(place)
    if lat is None:
        raise HTTPException(404, "Place not found")

    data = fetch_data(lat, lon)
    h = data["hourly"]

    target_date = datetime.now().date() + timedelta(days=day_index)

    feels, hum, wind, cloud, rain = [], [], [], [], []

    for i, t in enumerate(h["time"]):
        dt = datetime.fromisoformat(t)
        if dt.date() != target_date:
            continue

        feels.append(h["apparent_temperature"][i])
        hum.append(h["relativehumidity_2m"][i])
        wind.append(h["windspeed_10m"][i])
        cloud.append(h["cloudcover"][i])
        rain.append(h["precipitation"][i])

    return {
        "feels_like": max(feels) if feels else 0,
        "humidity": sum(hum)/len(hum) if hum else 0,
        "wind": max(wind) if wind else 0,
        "cloud": sum(cloud)/len(cloud) if cloud else 0,
        "rain": "Yes" if sum(rain) > 0 else "No"
    }

# =====================================================
# 5️⃣ HEALTH CHECK
# =====================================================
@app.get("/health")
def health():
    return {"status": "ok"}