import os
import sys
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock Django settings for standalone script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_ai_backend.settings')
import django
django.setup()

from travel_api.services.llama_service import LLaMAService

def test_cache():
    service = LLaMAService()
    
    test_query = "7 day honeymoon trip to Ella"
    
    print("\n--- TEST 1: Initial Request (Cache Miss expected) ---")
    start_time = time.time()
    itinerary1 = service.generate_itinerary(test_query)
    duration1 = time.time() - start_time
    print(f"Time taken: {duration1:.2f}s")
    
    print("\n--- TEST 2: Exact Same Request (Cache Hit expected) ---")
    start_time = time.time()
    itinerary2 = service.generate_itinerary(test_query)
    duration2 = time.time() - start_time
    print(f"Time taken: {duration2:.2f}s")
    
    if duration2 < duration1 / 10:
        print("\n✅ SUCCESS: Cache hit was significantly faster!")
    else:
        print("\n❌ FAILURE: Cache hit was not as fast as expected.")

    print("\n--- TEST 3: Similar Request (Semantic Hit expected) ---")
    similar_query = "a 7-day honeymoon in Ella"
    start_time = time.time()
    itinerary3 = service.generate_itinerary(similar_query)
    duration3 = time.time() - start_time
    print(f"Time taken: {duration3:.2f}s")

    if duration3 < duration1 / 10:
        print("\n✅ SUCCESS: Semantic match worked!")
    else:
        print("\n❌ FAILURE: Semantic match failed.")

if __name__ == "__main__":
    test_cache()
