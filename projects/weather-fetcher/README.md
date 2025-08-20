# 🌦 Weather Data Fetcher

A minimal Python tool to fetch weather data using the [Meteomatics API](https://www.meteomatics.com/en/weather-api).  
Demonstrates **Logging**, **CLI (argparse)**, and **Config files** (.env, YAML).

---
## 🚀 Features
- Fetches live weather for any location
- Configurable api paths via ``config.yaml``
- API key management via ``.env``
- Logs info & errors for debugging

---
## ⚙️ Setup

### 📦 Install Requirements
```bash
pip install -r requirements.txt
```

### 🔑 Get access to API

Obtain API Credentials: Sign up for a free account at 
[Meteomatics](https://www.meteomatics.com/en/api/getting-started) to receive your 
API username and password.

Configure Credentials: Store your credentials in a ``.env`` file in the project directory:

```
METEOMATICS_USERNAME=your_username
METEOMATICS_PASSWORD=your_password
```

Alternatively, you can set these as environment variables:
```bash
export METEOMATICS_USERNAME=your_username
export METEOMATICS_PASSWORD=your_password
```

---
## 🌍 Usage

To fetch weather data for a specific location, run the script with 
the desired parameters:

```bash
python weather.py --latitude 52.5200 --longitude 13.4050 --units metric
```

| Parameter     | Description                                                      |
|---------------| ---------------------------------------------------------------- |
| `--latitude`  | Latitude of the location (e.g., 52.5200)                         |
| `--longitude` | Longitude of the location (e.g., 13.4050)                        |
| `--units`     | Output unit: `metric` (°C) or `imperial` (°F)                    |


This command retrieves the air temperature at 2 meters above ground level 
(in Celsius) for Berlin (latitude 52.5200, longitude 13.4050) at current time.

**Sample Output:**
```
{
    'latitude': 52.52, 
    'longitude': 13.405, 
    'date': '2025-08-20T19:47:46Z', 
    'temperature': 17.5
}
```

