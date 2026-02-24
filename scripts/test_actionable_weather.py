import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'backend'))
from travel_api.services.trip_assistant import TripAssistantService

def test_actionable_advice():
    assistant = TripAssistantService()
    
    print("\n--- TEST: Rainy Weather + Beach Activity ---")
    bad_advice = assistant.get_advice(
        query="Should I go to the beach?",
        location_name="Galle",
        lat=6.0535,
        lon=80.2210,
        activity="Relax on Galle Fort Beach",
        description="Soak up the sun and enjoy the waves.",
        theme="Beach Relaxation"
    )
    # Note: Live weather might not be rainy in Galle right now, but we will see if the model evaluates it.
    print(f"Advice: {bad_advice}")

if __name__ == "__main__":
    test_actionable_advice()
