import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_ai_backend.settings')
django.setup()

from travel_api.services.llama_service import LLaMAService
import json

svc = LLaMAService()
response = svc.generate_itinerary({
    "duration": 7,
    "startLocation": "Colombo (CMB Airport)",
    "groupSize": "Couple",
    "tripType": "Beach"
})

print("Generated Titles:")
for c in response.get("days", []):
    print(f"Day {c.get('day')}: {c.get('location')}")

