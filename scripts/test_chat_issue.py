import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from travel_api.services.llama_service import LLaMAService

def test_chat_generation():
    llama = LLaMAService()
    
    print("\n--- TEST: Text-based Natural Language Query ---")
    query_text = "7 days trip to Sri Lanka starting from Colombo (CMB Airport) for a Couple. Style: Beach. Start Date: 2026-02-22."
    
    try:
        itin1 = llama.generate_itinerary(query_text)
        print(f"\nResult Title: {itin1.get('title')}")
        if itin1.get("days"):
            num_days = len(itin1['days'])
            print(f"Number of Days Generated: {num_days}")
    except Exception as e:
        print(f"UNCAUGHT EXCEPTION: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_chat_generation()
