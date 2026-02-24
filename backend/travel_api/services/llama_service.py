import os
import json
import requests
from django.conf import settings

# Initialize Clients
# Note: In production these should be singletons or managed better

from .itinerary_store import ItineraryStore

class LLaMAService:
    def __init__(self):
        # Ollama Configuration
        self.ollama_url = "http://localhost:11434/api/chat"
        self.embedding_url = "http://localhost:11434/api/embeddings"
        self.model = "srilanka-llama" 
        self.fallback_model = "llama3.2"
        self.embedding_model = "nomic-embed-text"
        self.store = ItineraryStore()

    def get_embedding(self, text):
        """Generate embedding using Ollama."""
        payload = {
            "model": self.embedding_model,
            "prompt": text
        }
        try:
            response = requests.post(self.embedding_url, json=payload)
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Ollama Embedding Error: {e}")
            return None

    def generate_itinerary(self, user_preferences):
        """
        Generate itinerary with Semantic Cache (Vector Bank).
        """
        # 0. Parse Input
        if isinstance(user_preferences, dict):
             duration = str(user_preferences.get('duration', '7'))
             start_loc = str(user_preferences.get('startLocation', 'Colombo')).strip()
             group = str(user_preferences.get('groupSize', 'Couple')).strip()
             trip_type = str(user_preferences.get('tripType', 'Beach')).strip()
             
             # Create a highly explicit, unique string for the embedding model
             query_text = f"Duration: {duration} Days | Start Location: {start_loc} | Group: {group} | Style: {trip_type}"
        else:
             query_text = user_preferences
             text_lower = query_text.lower()
             
             # Fallback DEFAULTS so raw chat inputs do not crash the prompt variables
             duration = str(5)
             start_loc = "Sri Lanka"
             group = "Traveler"
             trip_type = "Sightseeing"
             
             # Improved heuristic: detection words for itineraries
             itinerary_keywords = ["plan", "trip", "itinerary", "day", "honeymoon", "vacation", "visit"]
             if not any(word in text_lower for word in itinerary_keywords):
                 return self.generate_chat_response(query_text)

        # 1. Semantic Cache Lookup
        print(f"🔍 Checking Vector Bank for: \"{query_text}\"")
        query_embedding = self.get_embedding(query_text)
        if query_embedding:
            cached_itinerary = self.store.find_similar(query_text, query_embedding)
            if cached_itinerary:
                return cached_itinerary

        # 2. Cache Miss - Prompt Construction
        system_prompt = f"You are an expert Sri Lanka Travel Agent. Generate a highly detailed, unique travel itinerary. You MUST generate the complete itinerary for the full {duration} days requested. DO NOT STOP EARLY."
        user_message = f"""
        TASK: Create a {duration}-Day itinerary for: "{query_text}"
        
        REQUIRED JSON FORMAT:
        {{
          "title": "Create a unique and catchy trip title here",
          "summary": "Write a compelling 1-sentence summary of the trip here",
          "trip_theme": "{trip_type}",
          "total_days": {duration},
          "days": [
            {{
                "day": 1,
                "location": "MUST BE {start_loc}",
                "theme": "Must relate to the overall {trip_type} style",
                "activities": [
                    {{"time": "Morning", "activity": "Specific Activity Name", "description": "Write a detailed description of what they will do"}},
                    {{"time": "Afternoon", "activity": "Specific Activity Name", "description": "Write a detailed description of what they will do"}}
                ],
                "suggested_restaurants": ["Name of a real restaurant in this city", "Another real restaurant"],
                "narrative": "Write a full descriptive paragraph about the day's experiences."
            }}
          ]
        }}
        
        IMPORTANT RULES:
        1. CRITICAL: Day 1 location MUST absolutely be "{start_loc}". Do not start the trip anywhere else.
        2. CRITICAL: You MUST generate EXACTLY {duration} objects in the "days" array (Day 1, Day 2, ..., Day {duration}). Do not stop early. Let the output be as long as necessary.
        3. Replace ALL placeholder text with real, factual Sri Lankan locations, activities, and restaurant names relevant to a "{trip_type}" style trip.
        4. Maintain strict JSON formatting. DO NOT include code comments in the output JSON.
        """

        # 3. LLaMA Generation
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.4, "num_ctx": 8192, "num_predict": -1} # Increased context and removed token limit
        }

        try:
            print(f"🚀 Cache Miss. Generating with {payload['model']}...")
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            
            content = response.json().get("message", {}).get("content", "").replace("```json", "").replace("```", "").strip()
            itinerary_data = json.loads(content)

            # 4. Save to Cache
            if query_embedding:
                print("💾 Saving new itinerary to Vector Bank...")
                self.store.save(query_text, query_embedding, itinerary_data)
                
            return itinerary_data
            
        except Exception as e:
            print(f"LLaMA Error: {e}")
            return {"error": str(e)}

    def generate_chat_response(self, user_text):
        """
        Handle natural language chat queries.
        """
        system_prompt = "You are a helpful Sri Lanka Travel Assistant. Keep answers concise."
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "stream": False
        }
        
        try:
            print(f"Sending CHAT request to Ollama ({payload['model']})...")
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")
            return {"chat_response": content}
        except Exception as e:
            return {"error": str(e)}
