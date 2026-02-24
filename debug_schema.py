import requests
import json

def test_generation():
    url = "http://localhost:11434/api/chat"
    model = "srilanka-llama"
    
    # Strategy: Move instructions to USER message for higher attention
    # And use a simplified One-Shot example
    
    system_prompt = "You are a Travel Agent API. Output strictly valid JSON."
    
    user_query = "8 days trip to Sri Lanka starting from Galle for a Solo. Style: Beach. Start Date: 2026-01-11."
    
    user_message = f"""
    TASK: Create a 8-day itinerary for: "{user_query}"

    REQUIRED JSON FORMAT:
    {{
      "title": "My Trip",
      "summary": "Trip summary",
      "days": [
        {{
            "day": 1,
            "location": "City",
            "theme": "Theme",
            "activities": [
                {{"time": "Morning", "activity": "Activity Name"}},
                {{"time": "Afternoon", "activity": "Activity Name"}}
            ],
            "suggested_restaurants": ["Rest 1"],
            "narrative": "Day description"
        }}
      ]
    }}

    IMPORTANT:
    - You MUST generate "days" array with 8 items.
    - Do NOT output markdown.
    - Do NOT output the 'trip_id' schema.
    """

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0 # Strict
        }
    }
    
    print(f"Testing Prompt Strategy on {model}...")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result['message']['content']
        
        print("\n--- RAW OUTPUT ---")
        print(content)
        print("------------------\n")
        
        parsed = json.loads(content)
        if "days" in parsed and isinstance(parsed["days"], list):
            print(f"✅ Success! Generated {len(parsed['days'])} days.")
        else:
            print("❌ Failed. Key 'days' missing or invalid.")
            print(f"Keys found: {list(parsed.keys())}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generation()
