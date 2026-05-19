# Skies — Weather Dashboard

A beautiful weather dashboard built with Python (Flask) + OpenWeatherMap API.

## Features

* Current weather with temperature, humidity, wind, visibility, pressure
* Air Quality Index (AQI)
* Sunrise / sunset with animated progress bar
* 5-day forecast with rain probability
* °C / °F toggle
* GPS "My Location" support
* Sky background that changes based on weather conditions

## Setup

### 1\. Get a free API key

Sign up at https://openweathermap.org/api → copy your API key.
The free tier includes: current weather, 5-day forecast, air quality, and geocoding.

### 2\. Install dependencies

```bash
pip install -r requirements.txt
```

### 3\. Set your API key (pick one method)

**Option A — Environment variable (recommended):**

```bash
# Mac/Linux
export OPENWEATHER\_API\_KEY=your\_key\_here

# Windows (Command Prompt)
set OPENWEATHER\_API\_KEY=your\_key\_here

# Windows (PowerShell)
$env:OPENWEATHER\_API\_KEY="your\_key\_here"
```

**Option B — Edit app.py directly:**

```python
API\_KEY = "your\_key\_here"   # line 9 in app.py
```

### 4\. Run the app

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Project structure

```
weather-dashboard/
├── app.py              # Flask backend — all API calls happen here
├── requirements.txt
└── templates/
    └── index.html      # Frontend (HTML + CSS + JS)
```

## How it works (great for learning!)

1. User types a city → browser calls `/api/weather?city=London`
2. Flask geocodes the city name → gets lat/lon
3. Flask calls OpenWeatherMap for current weather + forecast + AQI
4. Flask returns clean JSON to the browser
5. JavaScript renders the UI

The API key lives only in the backend — never exposed to the browser. This is the correct pattern for production apps.

## API endpoints used

|Endpoint|What it does|
|-|-|
|`geo/1.0/direct`|City name → lat/lon|
|`data/2.5/weather`|Current conditions|
|`data/2.5/forecast`|3-hour intervals, 5 days|
|`data/2.5/air\_pollution`|AQI + pollutant data|

## Next steps to extend this project

* \[ ] Add hourly forecast chart (use Chart.js)
* \[ ] Save favourite cities to localStorage
* \[ ] Add weather alerts
* \[ ] Deploy to Render or Railway (free hosting)
* \[ ] Add a map with Leaflet.js showing the city location

