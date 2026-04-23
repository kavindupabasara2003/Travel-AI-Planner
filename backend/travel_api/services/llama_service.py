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
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_url = f"{ollama_host}/api/chat"
        self.embedding_url = f"{ollama_host}/api/embeddings"
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
             import re
             query_text = user_preferences
             text_lower = query_text.lower()
             
             # Fallback DEFAULTS so raw chat inputs do not crash the prompt variables
             # Extract duration dynamically using regex
             duration_match = re.search(r'(\d+)\s*days?', text_lower)
             duration = str(duration_match.group(1)) if duration_match else str(5)
             
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
                print("✅ Exact String Match Cache Hit! (PostgreSQL)")
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
                "narrative": "Write a full descriptive paragraph about the day's experiences.",
                "reasoning": "Explain in 1-2 sentences WHY this location was chosen: geographic progression from previous day, how it fits the {trip_type} style, and what makes it ideal for day 1."
            }},
            {{
                "day": 2,
                "location": "Next City",
                "theme": "Day theme",
                "activities": [
                    {{"time": "Morning", "activity": "Specific Activity Name", "description": "Details..."}}
                ],
                "suggested_restaurants": ["Restaurant 1"],
                "narrative": "Paragraph...",
                "reasoning": "WHY this city follows logically from day 1 and fits the trip style."
            }}
          ]
        }}

        IMPORTANT RULES:
        1. CRITICAL: Day 1 location MUST absolutely be "{start_loc}". Do not start the trip anywhere else.
        2. CRITICAL: You MUST generate EXACTLY {duration} objects in the "days" array (Day 1, Day 2, ..., Day {duration}). You must continue extending the array until you reach {duration} days!
        3. Replace ALL placeholder text with real, factual Sri Lankan locations, activities, and restaurant names relevant to a "{trip_type}" style trip.
        4. Maintain strict JSON formatting. DO NOT include code comments in the output JSON.
        5. CRITICAL: ENSURE GEOGRAPHIC PROGRESSION. You MUST NOT stay in the exact same city for more than 2 or 3 days. The user must travel to multiple distinct regions of Sri Lanka (e.g., South Coast, Cultural Triangle, Hill Country) as the itinerary progresses.
        6. For every day, include a "reasoning" field explaining the location choice.
        """

        # 3. LLaMA Generation
        payload = {
            "model": self.fallback_model, # Use the much smarter base model for stable JSON structure
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.4, "num_ctx": 8192, "num_predict": 4096} # Forced high generation output limit
        }
        
        try:
            print(f"🚀 Cache Miss. Generating with {payload['model']}...")
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            
            raw_content = response.json().get("message", {}).get("content", "")
            
            # Robust extraction using bracket counting to find the FIRST complete JSON object
            start_idx = raw_content.find('{')
            if start_idx != -1:
                open_braces = 0
                end_idx = -1
                for i in range(start_idx, len(raw_content)):
                    if raw_content[i] == '{':
                        open_braces += 1
                    elif raw_content[i] == '}':
                        open_braces -= 1
                        if open_braces == 0:
                            end_idx = i
                            break
                            
                if end_idx != -1:
                    content = raw_content[start_idx:end_idx+1]
                else:
                    content = raw_content
            else:
                content = raw_content
                
            content = content.replace("```json", "").replace("```", "").strip()
            
            if not content:
                raise ValueError("LLaMA returned an empty content string.")
                
            itinerary_data = json.loads(content)

            # 4. Post-processing: weather-adaptive re-ordering
            try:
                from .itinerary_optimizer import ItineraryOptimizer
                optimizer = ItineraryOptimizer()
                itinerary_data = optimizer.optimize(itinerary_data)
                print(f"✅ Weather optimizer applied. Swaps: {len(itinerary_data.get('optimization_log', []))}")
            except Exception as opt_err:
                print(f"⚠️  Weather optimizer skipped: {opt_err}")

            # 5. Post-processing: enrich reasoning traces with real data (XAI Feature 5)
            itinerary_data = self._enrich_reasoning_traces(itinerary_data)

            # 6. Save to Cache
            if query_embedding:
                print("💾 Saving new itinerary to Vector Bank...")
                self.store.save(query_text, query_embedding, itinerary_data)

            return itinerary_data
            
        except Exception as e:
            print(f"LLaMA Error: {e}")
            return {"error": str(e)}

    def generate_multi_itinerary(self, user_preferences):
        """
        Generate 3 itinerary variations simultaneously (Feature 1).
        Variation A: The Classic  — popular attractions, safe tourist route
        Variation B: Hidden Gems  — off-beaten-path, local favourites
        Variation C: Balanced Mix — highlights + hidden gems combined
        Each variation is cached independently using its own cache key suffix.
        """
        if isinstance(user_preferences, dict):
            duration = str(user_preferences.get('duration', '7'))
            start_loc = str(user_preferences.get('startLocation', 'Colombo')).strip()
            group = str(user_preferences.get('groupSize', 'Couple')).strip()
            trip_type = str(user_preferences.get('tripType', 'Beach')).strip()
            base_query = f"Duration: {duration} Days | Start Location: {start_loc} | Group: {group} | Style: {trip_type}"
        else:
            return {"error": "generate_multi_itinerary requires a dict of preferences"}

        variations = [
            {
                "key": "classic",
                "label": "The Classic",
                "emoji": "🏆",
                "cache_suffix": " | Variation: Classic",
                "persona_instruction": (
                    "Focus EXCLUSIVELY on Sri Lanka's most famous, iconic, and highly-rated tourist attractions. "
                    "Choose destinations every guidebook recommends: Sigiriya Rock, Temple of the Tooth, Galle Fort, "
                    "Yala National Park, Mirissa Beach, etc. This is the safe, proven, crowd-favourite route."
                ),
            },
            {
                "key": "hidden_gems",
                "label": "Hidden Gems",
                "emoji": "💎",
                "cache_suffix": " | Variation: Hidden Gems",
                "persona_instruction": (
                    "AVOID all mainstream tourist hotspots. Focus EXCLUSIVELY on lesser-known, off-the-beaten-path "
                    "Sri Lankan locations that most tourists miss: hidden waterfalls, local villages, secret beaches, "
                    "lesser-visited temples, local markets, and authentic experiences. "
                    "Do NOT include Sigiriya, Kandy Temple, Galle Fort, or Mirissa unless absolutely necessary."
                ),
            },
            {
                "key": "balanced",
                "label": "Balanced Mix",
                "emoji": "⚖️",
                "cache_suffix": " | Variation: Balanced",
                "persona_instruction": (
                    "Create a balanced itinerary combining 50% well-known highlights with 50% hidden gems and "
                    "local favourites. Each day should offer variety — pair a famous attraction with a local secret spot. "
                    "Optimise for maximum variety and authentic experience."
                ),
            },
        ]

        results = []
        for var in variations:
            cache_key = base_query + var["cache_suffix"]
            embedding = self.get_embedding(cache_key)

            # Check cache
            if embedding:
                cached = self.store.find_similar(cache_key, embedding)
                if cached:
                    print(f"✅ Cache hit for {var['label']}")
                    cached["variation_type"] = var["key"]
                    cached["variation_label"] = var["label"]
                    cached["variation_emoji"] = var["emoji"]
                    results.append(cached)
                    continue

            # Generate
            system_prompt = (
                f"You are an expert Sri Lanka Travel Agent. {var['persona_instruction']} "
                f"Generate a complete {duration}-day itinerary. DO NOT STOP EARLY."
            )
            user_message = f"""
TASK: Create a {duration}-Day {var['label']} itinerary for: "{base_query}"

REQUIRED JSON FORMAT:
{{
  "title": "Unique catchy title reflecting the {var['label']} style",
  "summary": "One compelling sentence summarising this variation",
  "trip_theme": "{trip_type}",
  "variation_type": "{var['key']}",
  "variation_label": "{var['label']}",
  "variation_emoji": "{var['emoji']}",
  "total_days": {duration},
  "days": [
    {{
      "day": 1,
      "location": "MUST BE {start_loc}",
      "theme": "Day theme",
      "activities": [
        {{"time": "Morning", "activity": "Activity Name", "description": "Detailed description"}},
        {{"time": "Afternoon", "activity": "Activity Name", "description": "Detailed description"}}
      ],
      "suggested_restaurants": ["Restaurant 1", "Restaurant 2"],
      "narrative": "Full descriptive paragraph about the day.",
      "reasoning": "WHY this location fits the {var['label']} style."
    }}
  ]
}}

RULES:
1. Day 1 MUST start at {start_loc}.
2. Generate EXACTLY {duration} days.
3. Use real Sri Lankan locations, restaurants, and activities.
4. {var['persona_instruction']}
5. Ensure geographic progression across Sri Lanka.
"""
            payload = {
                "model": self.fallback_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.5, "num_ctx": 8192, "num_predict": 4096},
            }

            try:
                print(f"🚀 Generating {var['label']} variation...")
                resp = requests.post(self.ollama_url, json=payload)
                resp.raise_for_status()
                raw = resp.json().get("message", {}).get("content", "")

                # Extract JSON
                start = raw.find('{')
                if start != -1:
                    depth = 0
                    end = -1
                    for i in range(start, len(raw)):
                        if raw[i] == '{': depth += 1
                        elif raw[i] == '}':
                            depth -= 1
                            if depth == 0:
                                end = i
                                break
                    content = raw[start:end+1] if end != -1 else raw
                else:
                    content = raw

                content = content.replace("```json", "").replace("```", "").strip()
                itinerary = json.loads(content)
                itinerary["variation_type"] = var["key"]
                itinerary["variation_label"] = var["label"]
                itinerary["variation_emoji"] = var["emoji"]

                # Post-process: weather optimizer + XAI
                try:
                    from .itinerary_optimizer import ItineraryOptimizer
                    itinerary = ItineraryOptimizer().optimize(itinerary)
                except Exception:
                    pass
                itinerary = self._enrich_reasoning_traces(itinerary)

                # Cache
                if embedding:
                    self.store.save(cache_key, embedding, itinerary)

                results.append(itinerary)

            except Exception as e:
                print(f"Error generating {var['label']}: {e}")
                results.append({"error": str(e), "variation_type": var["key"],
                                "variation_label": var["label"], "variation_emoji": var["emoji"]})

        return results

    def _enrich_reasoning_traces(self, itinerary: dict) -> dict:
        """
        Enrich each day's LLM 'reasoning' with real data:
        weather forecast, crowd prediction, and ABSA scores where available.
        Produces a structured 'reasoning_trace' dict on each day.
        """
        from datetime import date as date_cls
        try:
            from .crowd_predictor import CrowdPredictor
            crowd_predictor = CrowdPredictor()
        except Exception:
            crowd_predictor = None

        days = itinerary.get("days", [])
        start_date = date_cls.today()

        for i, day in enumerate(days):
            day_date = (start_date + __import__("datetime").timedelta(days=i)).isoformat()
            location = day.get("location", "")
            llm_reasoning = day.get("reasoning", "")

            trace = {"location_choice": llm_reasoning}

            # Weather
            wf = day.get("weather_forecast", {})
            if wf:
                trace["weather_alignment"] = (
                    f"{wf.get('emoji','')}{wf.get('max_temp','')}°C, "
                    f"outdoor score {wf.get('outdoor_score', 0):.0%}"
                )
            else:
                trace["weather_alignment"] = "Weather data unavailable."

            # Crowd prediction
            if crowd_predictor:
                try:
                    crowd = crowd_predictor.predict(day_date)
                    trace["crowd_prediction"] = (
                        f"{crowd['label']} ({crowd['level']}/5) — "
                        f"{'Public holiday — expect high crowds' if crowd['is_poya'] else ''}"
                        f"{'Weekend — moderate-high crowds' if crowd['is_weekend'] and not crowd['is_poya'] else ''}"
                        f"{'Weekday — manageable crowds' if not crowd['is_weekend'] and not crowd['is_poya'] else ''}"
                    ).strip(" —")
                except Exception:
                    trace["crowd_prediction"] = "Crowd data unavailable."
            else:
                trace["crowd_prediction"] = "Crowd model not ready."

            # ABSA aspect highlights
            try:
                from travel_api.models import AttractionAspectScore
                aspects = AttractionAspectScore.objects.filter(
                    located_city__icontains=location.split("(")[0].strip()
                ).first()
                if aspects:
                    top = sorted({
                        "Scenery": aspects.scenery,
                        "Cleanliness": aspects.cleanliness,
                        "Safety": aspects.safety,
                        "Cultural Significance": aspects.cultural_significance,
                    }.items(), key=lambda x: x[1], reverse=True)[:2]
                    trace["aspect_highlights"] = ", ".join(f"{k}: {v:.0%}" for k, v in top)
                else:
                    trace["aspect_highlights"] = "No aspect data for this location yet."
            except Exception:
                trace["aspect_highlights"] = "Aspect data unavailable."

            day["reasoning_trace"] = trace

        itinerary["days"] = days
        return itinerary

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
