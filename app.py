from flask import Flask, render_template, jsonify, request
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "http://api.openweathermap.org/geo/1.0"


def kelvin_to_celsius(k):
    return round(k - 273.15, 1)


def kelvin_to_fahrenheit(k):
    return round((k - 273.15) * 9/5 + 32, 1)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def get_weather():
    city = request.args.get("city", "")
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    units = request.args.get("units", "metric")  # metric or imperial

    if not city and not (lat and lon):
        return jsonify({"error": "Please provide a city name or coordinates"}), 400

    try:
        # If city name given, geocode it first
        if city:
            geo_resp = requests.get(
                f"{GEO_URL}/direct",
                params={"q": city, "limit": 1, "appid": API_KEY},
                timeout=5
            )
            geo_data = geo_resp.json()
            if not geo_data:
                return jsonify({"error": f"City '{city}' not found"}), 404
            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]
            city_name = geo_data[0]["name"]
            country = geo_data[0].get("country", "")
        else:
            city_name = "Your Location"
            country = ""

        # Current weather
        current_resp = requests.get(
            f"{BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": units},
            timeout=5
        )
        current = current_resp.json()

        if current.get("cod") != 200:
            return jsonify({"error": current.get("message", "API error")}), 400

        # 5-day forecast (3-hour intervals)
        forecast_resp = requests.get(
            f"{BASE_URL}/forecast",
            params={"lat": lat, "lon": lon, "appid": API_KEY, "units": units},
            timeout=5
        )
        forecast_data = forecast_resp.json()

        # Air quality
        aqi_resp = requests.get(
            f"{BASE_URL}/air_pollution",
            params={"lat": lat, "lon": lon, "appid": API_KEY},
            timeout=5
        )
        aqi_data = aqi_resp.json()

        # Process daily forecast (pick one reading per day at noon)
        daily = {}
        for item in forecast_data.get("list", []):
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            hour = datetime.fromtimestamp(item["dt"]).hour
            if date not in daily or abs(hour - 12) < abs(
                datetime.fromtimestamp(daily[date]["dt"]).hour - 12
            ):
                daily[date] = item

        forecast_daily = list(daily.values())[:5]

        # AQI label
        aqi_index = aqi_data["list"][0]["main"]["aqi"] if aqi_data.get("list") else None
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

        unit_symbol = "°C" if units == "metric" else "°F"
        speed_unit = "m/s" if units == "metric" else "mph"

        return jsonify({
            "city": city_name,
            "country": country,
            "lat": lat,
            "lon": lon,
            "current": {
                "temp": round(current["main"]["temp"]),
                "feels_like": round(current["main"]["feels_like"]),
                "temp_min": round(current["main"]["temp_min"]),
                "temp_max": round(current["main"]["temp_max"]),
                "humidity": current["main"]["humidity"],
                "pressure": current["main"]["pressure"],
                "wind_speed": current["wind"]["speed"],
                "wind_deg": current["wind"].get("deg", 0),
                "visibility": current.get("visibility", 0) // 1000,
                "description": current["weather"][0]["description"].title(),
                "icon": current["weather"][0]["icon"],
                "main": current["weather"][0]["main"],
                "sunrise": datetime.fromtimestamp(current["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(current["sys"]["sunset"]).strftime("%H:%M"),
                "clouds": current["clouds"]["alc"] if "alc" in current.get("clouds", {}) else current["clouds"].get("all", 0),
            },
            "forecast": [
                {
                    "date": datetime.fromtimestamp(d["dt"]).strftime("%a %d %b"),
                    "temp_max": round(d["main"]["temp_max"]),
                    "temp_min": round(d["main"]["temp_min"]),
                    "description": d["weather"][0]["description"].title(),
                    "icon": d["weather"][0]["icon"],
                    "main": d["weather"][0]["main"],
                    "humidity": d["main"]["humidity"],
                    "wind": d["wind"]["speed"],
                    "pop": round(d.get("pop", 0) * 100),
                }
                for d in forecast_daily
            ],
            "aqi": {
                "index": aqi_index,
                "label": aqi_labels.get(aqi_index, "Unknown") if aqi_index else "Unknown",
                "components": aqi_data["list"][0]["components"] if aqi_data.get("list") else {}
            },
            "unit_symbol": unit_symbol,
            "speed_unit": speed_unit,
        })

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to weather service"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Weather service timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
