import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from travel_api.services.llama_service import LLaMAService

def test_cache_and_prompt():
    llama = LLaMAService()
    
    print("\n--- TEST: Enforcing Duration Generation ---")
    req1 = {
        "duration": 4,  # Change duration to bypass cache
        "startLocation": "Colombo",
        "groupSize": "Couple",
        "tripType": "Culture"
    }
    itin1 = llama.generate_itinerary(req1)
    
    print(f"\nResult 1 Title: {itin1.get('title')}")
    if itin1.get("days"):
        num_days = len(itin1['days'])
        print(f"Number of Days Generated: {num_days} / 4")
        for i, day in enumerate(itin1['days']):
            print(f"  Day {i+1} Location: {day.get('location')}")

if __name__ == "__main__":
    test_cache_and_prompt()
