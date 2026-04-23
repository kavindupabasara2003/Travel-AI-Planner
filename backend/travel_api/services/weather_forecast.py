"""
WeatherForecastService — fetches 7-day forecasts from OpenMeteo (Feature 3 & UI-5).
Returns daily outdoor_score (0.0–1.0) based on WMO weather code.
"""
import requests

CITY_COORDS = {
    "Colombo": (6.9271, 79.8612),
    "Kandy": (7.2906, 80.6337),
    "Galle": (6.0535, 80.2210),
    "Ella": (6.8667, 81.0466),
    "Nuwara Eliya": (6.9497, 80.7891),
    "Sigiriya": (7.9570, 80.7603),
    "Mirissa": (5.9483, 80.4716),
    "Trincomalee": (8.5874, 81.2152),
    "Jaffna": (9.6615, 80.0255),
    "Anuradhapura": (8.3114, 80.4037),
    "Polonnaruwa": (7.9398, 81.0006),
    "Dambulla": (7.8731, 80.6517),
    "Hikkaduwa": (6.1395, 80.1060),
    "Bentota": (6.4248, 79.9966),
    "Negombo": (7.2008, 79.8380),
    "Haputale": (6.7667, 80.9667),
    "Arugam Bay": (6.8414, 81.8360),
    "Yala": (6.3728, 81.5167),
    "Udawalawe": (6.4738, 80.8994),
    "Tangalle": (6.0244, 80.7967),
    "Nilaveli": (8.7027, 81.2105),
    "Unawatuna": (6.0101, 80.2496),
    "Matale": (7.4675, 80.6234),
    "Ampara": (7.2982, 81.6724),
    "Batticaloa": (7.7167, 81.7000),
}

OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"


def _weather_code_to_outdoor_score(code: int) -> float:
    """Map WMO code to 0.0 (terrible outdoor) – 1.0 (perfect outdoor)."""
    if code == 0:
        return 1.0
    if code in (1, 2):
        return 0.85
    if code == 3:
        return 0.7
    if code in (45, 48):
        return 0.5
    if code in (51, 53, 55):
        return 0.4
    if code in (61, 63):
        return 0.3
    if code in (65, 80, 81, 82):
        return 0.15
    if code >= 95:
        return 0.05
    return 0.5


def _weather_emoji(code: int) -> str:
    if code == 0:
        return "☀️"
    if code in (1, 2, 3):
        return "🌤️"
    if code in (45, 48):
        return "🌫️"
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "🌧️"
    if code >= 95:
        return "⛈️"
    return "🌥️"


class WeatherForecastService:
    def get_coords(self, city: str) -> tuple | None:
        for known, coords in CITY_COORDS.items():
            if known.lower() in city.lower() or city.lower() in known.lower():
                return coords
        return None

    def get_forecast(self, city: str) -> list:
        """Returns list of daily forecast dicts (up to 7 days) or empty list."""
        coords = self.get_coords(city)
        if not coords:
            return []

        lat, lon = coords
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Asia/Colombo",
            "forecast_days": 7,
        }

        try:
            resp = requests.get(OPENMETEO_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("daily", {})
        except Exception as e:
            print(f"WeatherForecastService error for {city}: {e}")
            return []

        dates = data.get("time", [])
        codes = data.get("weather_code", [])
        max_temps = data.get("temperature_2m_max", [])
        precip = data.get("precipitation_sum", [])

        result = []
        for i, d in enumerate(dates):
            code = codes[i] if i < len(codes) else 0
            result.append({
                "date": d,
                "weather_code": code,
                "emoji": _weather_emoji(code),
                "max_temp": max_temps[i] if i < len(max_temps) else None,
                "precipitation": precip[i] if i < len(precip) else 0,
                "outdoor_score": _weather_code_to_outdoor_score(code),
            })

        return result

    def get_forecast_for_date(self, city: str, target_date: str) -> dict | None:
        """Return single-day forecast dict for a specific date, or None."""
        forecast = self.get_forecast(city)
        for day in forecast:
            if day["date"] == target_date:
                return day
        return None
