import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeatherRequest(BaseModel):
    place: str

# ================= LOCATION =================
def get_location(place):
    r = requests.get(GEOCODE, params={"name": place, "count": 1}).json()
    if "results" not in r:
        return None, None
    loc = r["results"][0]
    return loc["latitude"], loc["longitude"]

# ================= FETCH ALL DATA =================
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
        "daily": "temperature_2m_max",
        "forecast_days": 7,
        "timezone": "auto"
    }

    return requests.get(OPEN_METEO, params=params).json()

# ================= DAY SUMMARY =================
def summarize_day(data, day_index):
    h = data["hourly"]
    target_date = datetime.now().date() + timedelta(days=day_index)

    temps=[]
    feels=[]
    hum=[]
    rain=[]
    cloud=[]
    wind=[]
    hourly_graph=[]

    for i,t in enumerate(h["time"]):
        dt=datetime.fromisoformat(t)

        if dt.date()!=target_date:
            continue

        temps.append(h["temperature_2m"][i])
        feels.append(h["apparent_temperature"][i])
        hum.append(h["relativehumidity_2m"][i])
        rain.append(h["precipitation"][i])
        cloud.append(h["cloudcover"][i])
        wind.append(h["windspeed_10m"][i])

        hourly_graph.append({
            "time":dt.strftime("%H:%M"),
            "temp":h["temperature_2m"][i]
        })

    return {
        "feels_like": round(max(feels),1),
        "humidity": round(sum(hum)/len(hum)),
        "wind": round(max(wind),1),
        "cloud": round(sum(cloud)/len(cloud)),
        "rain": "Yes" if sum(rain)>0 else "No",
        "hourly": hourly_graph
    }

# ================= MAIN LOAD =================
@app.post("/weather")
def weather(req: WeatherRequest):
    lat,lon=get_location(req.place)
    if lat is None:
        raise HTTPException(404,"Place not found")

    data=fetch_data(lat,lon)

    daily_cards=[]
    for i,d in enumerate(data["daily"]["time"]):
        day=datetime.fromisoformat(d).strftime("%a")
        daily_cards.append({
            "day":day,
            "temp":round(data["daily"]["temperature_2m_max"][i])
        })

    today_details=summarize_day(data,0)

    return {
        "place":req.place,
        "today_temp":daily_cards[0]["temp"],
        "daily_cards":daily_cards,
        "details":today_details
    }

# ================= DAY CLICK =================
@app.get("/day-details")
def day_details(place:str,day_index:int=0):
    lat,lon=get_location(place)
    if lat is None:
        raise HTTPException(404,"Place not found")

    data=fetch_data(lat,lon)
    return summarize_day(data,day_index)

# ================= HEALTH =================
@app.get("/health")
def health():
    return {"status":"ok"}
