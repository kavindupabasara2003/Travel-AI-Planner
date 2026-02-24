import os
import requests
import json
from datetime import datetime
from .llama_service import LLaMAService

class TripAssistantService:
    def __init__(self):
        self.llama_agent = LLaMAService()
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"
        
        # Determine current year and load correct holiday file
        current_year = datetime.now().year
        self.holidays_file = os.path.join(
            os.path.dirname(__file__), 
            f"srilanka_holidays/json/{current_year}.json"
        )
        self.holidays = self._load_holidays()

    def _load_holidays(self):
        """Load holiday data from the cloned srilanka-holidays repo."""
        if not os.path.exists(self.holidays_file):
            print(f"Warning: Holiday file not found at {self.holidays_file}. Using empty list.")
            return []
            
        try:
            with open(self.holidays_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading holiday data: {e}")
            return []

    def get_live_weather(self, lat, lon):
        """
        Fetch current weather from OpenMeteo (Free API).
        """
        if not lat or not lon:
            return None
            
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
            response = requests.get(self.weather_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return data.get("current", {})
        except Exception as e:
            print(f"Weather API Error: {e}")
            return None

    def interpret_weather_code(self, code):
        """Simple mapping for WMO Weather Codes"""
        if code is None: return "Unknown Condition"
        if code == 0: return "Clear sky"
        if code in [1, 2, 3]: return "Partly cloudy"
        if code in [45, 48]: return "Foggy"
        if code in [51, 53, 55, 61, 63, 65]: return "Rainy"
        if code in [80, 81, 82]: return "Heavy Rain Showers"
        if code >= 95: return "Thunderstorm"
        return "Overcast"
        
    def _check_if_holiday(self, date_str):
        """Checks if a given 'YYYY-MM-DD' string is a holiday and returns its summary."""
        for holiday in self.holidays:
            if holiday.get("start") == date_str:
                return holiday.get("summary")
        return None

    def get_advice(self, query, location_name, lat=None, lon=None, activity=None, description=None, theme=None):
        """
        Generate advice based on User Query + Real-time Context (Weather + Holidays) + Current Activity.
        """
        current_time = datetime.now()
        date_str = current_time.strftime("%Y-%m-%d")
        day_of_week = current_time.strftime("%A")
        time_str = current_time.strftime("%I:%M %p")
        
        # 1. Base Context
        context_str = f"Location: {location_name}\nDate: {date_str} ({day_of_week})\nTime: {time_str}\n"
        
        # 1.5 Activity Context
        if activity:
             context_str += f"Current Planned Activity: {activity}\n"
             if description: context_str += f"Activity Details: {description}\n"
             if theme: context_str += f"Overall Trip Theme: {theme}\n"
        
        # 2. Add Holiday Context
        holiday_name = self._check_if_holiday(date_str)
        if holiday_name:
             context_str += f"Holiday Status: TODAY IS A PUBLIC HOLIDAY ({holiday_name}). Expect heavy crowds at tourist spots and temples. Banks and mercantile sectors may be closed.\n"
        elif day_of_week in ["Saturday", "Sunday"]:
             context_str += "Holiday Status: Weekend. Expect moderate-to-high crowds at popular destinations.\n"
        else:
             context_str += "Holiday Status: Regular weekday. Crowds should be manageable.\n"

        # 3. Add Weather Context
        weather = self.get_live_weather(lat, lon)
        if weather:
            condition = self.interpret_weather_code(weather.get("weather_code"))
            temp = weather.get("temperature_2m", "N/A")
            precip = weather.get("precipitation", 0)
            context_str += f"Current Weather: {temp}°C, {condition}. Precipitation: {precip}mm.\n"
        else:
            context_str += "Current Weather: Data temporarily unavailable.\n"

        print(f"--- RAG Context Provided ---\n{context_str}\n---------------------------")

        # 4. Prompt LLaMA with Context
        system_prompt = f"""You are a Real-Time Travel Assistant for Sri Lanka providing live updates.
You MUST base your answer ENTIRELY on the following REAL-TIME CONTEXT. 

YOUR OBJECTIVE: Evaluate the "Current Weather" and "Holiday Status" against the user's "Current Planned Activity".
1. If the weather is BAD for the planned activity (e.g., raining during a beach trip, thunderstorms during a hike), you MUST explicitly tell the user the weather is bad for their plan and suggest an indoor/safe ALTERNATIVE that fits the "Overall Trip Theme".
2. If the weather is GOOD for the planned activity, you MUST explicitly validate their plan (e.g., "The weather is perfect for the beach right now.").
3. Warn them if the current holiday/weekend status will make their specific activity crowded.

CRITICAL: Keep your answer to 1-2 short, actionable sentences maximum. Do not list raw weather stats unless explaining your advice.

--- REAL-TIME CONTEXT ---
{context_str}
-------------------------
"""
        
        payload = {
            "model": self.llama_agent.fallback_model, # Use the base model which follows formatting instructions better
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "stream": False,
            "options": {
                "temperature": 0.3 # Keep it grounded in the context provided
            }
        }
        
        try:
            print(f"Sending RAG request to Ollama ({payload['model']})...")
            response = requests.post(self.llama_agent.ollama_url, json=payload)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")
            return content.strip()
        except Exception as e:
            return f"I couldn't check the live status right now. Please try again later. ({str(e)})"
