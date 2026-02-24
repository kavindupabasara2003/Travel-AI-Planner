import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock Django settings for standalone script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_ai_backend.settings')
import django
django.setup()

from travel_api.services.trip_assistant import TripAssistantService

def test_live_context():
    assistant = TripAssistantService()
    
    print("\n--- TEST 1: Weather check in Colombo ---")
    # Coordinates for Colombo, Sri Lanka
    colombo_lat = 6.9271
    colombo_lon = 79.8612
    
    advice1 = assistant.get_advice(
        query="Should I go for a walk outside right now?", 
        location_name="Colombo", 
        lat=colombo_lat, 
        lon=colombo_lon
    )
    print(f"\nModel Advice:\n{advice1}")

    print("\n\n--- TEST 2: Crowd check in Kandy ---")
    advice2 = assistant.get_advice(
        query="Is it going to be crowded at the temple?", 
        location_name="Kandy", 
        lat=None, 
        lon=None
    )
    print(f"\nModel Advice:\n{advice2}")

if __name__ == "__main__":
    test_live_context()
