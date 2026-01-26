import requests

KERALA_COORDS = {
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Kollam": (8.8932, 76.6141),
    "Pathanamthitta": (9.2648, 76.7870),
    "Alappuzha": (9.4981, 76.3388),
    "Kottayam": (9.5916, 76.5222),
    "Idukki": (9.8492, 76.9770),
    "Ernakulam": (9.9816, 76.2999),
    "Thrissur": (10.5276, 76.2144),
    "Palakkad": (10.7867, 76.6548),
    "Malappuram": (11.0732, 76.0740),
    "Kozhikode": (11.2588, 75.7804),
    "Wayanad": (11.6854, 76.1320),
    "Kannur": (11.8745, 75.3704),
    "Kasaragod": (12.4996, 74.9869)
}


def get_location(place):
    if place in KERALA_COORDS:
        return KERALA_COORDS[place]

    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": place, "count": 1},
        timeout=10
    )

    data = response.json()
    if "results" not in data:
        return None, None

    result = data["results"][0]
    return result["latitude"], result["longitude"]


def get_live_weather(lat, lon):
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relativehumidity_2m",
                    "precipitation",
                    "cloudcover",
                    "windspeed_10m"
                ],
                "timezone": "auto"
            },
            timeout=10
        )
        response.raise_for_status()
        current = response.json()["current"]

        return {
            "temperature": current["temperature_2m"],
            "humidity": current["relativehumidity_2m"],
            "precipitation": current["precipitation"],
            "cloud_cover": current["cloudcover"],
            "wind_speed": current["windspeed_10m"]
        }

    except requests.RequestException:
        return None


def predict_rain(precipitation, humidity, cloud_cover):
    if precipitation > 0.1:
        return "Rain likely"
    if humidity > 75 and cloud_cover > 60:
        return "Possible rain"
    return "Low rain chance"


def get_weather_data(place):
    lat, lon = get_location(place)
    if lat is None:
        return None

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        },
        timeout=10
    )

    daily = response.json()["daily"]

    return {
        "dates": daily["time"],
        "temp_max": daily["temperature_2m_max"],
        "temp_min": daily["temperature_2m_min"]
    }
