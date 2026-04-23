import os
import json
import requests


class AspectAnalyzer:
    """
    Sends attraction review text to LLaMA and extracts 8 aspect-level sentiment
    scores (0.0 – 1.0) as structured JSON.
    """

    ASPECTS = [
        "scenery", "cleanliness", "crowd_level",
        "value_for_money", "accessibility", "safety",
        "food_quality", "cultural_significance",
    ]

    def __init__(self):
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_url = f"{ollama_host}/api/chat"
        self.model = "llama3.2"

    def extract_scores(self, attraction_name: str, review_text: str) -> dict | None:
        """
        Returns a dict of aspect → float (0.0–1.0) or None on failure.
        """
        system_prompt = (
            "You are a tourism sentiment analyst. Given a review of a Sri Lankan attraction, "
            "score 8 quality dimensions from 0.0 (very poor) to 1.0 (excellent). "
            "For dimensions not mentioned in the review, estimate based on the location type. "
            "RESPOND ONLY with a valid JSON object — no markdown, no extra text."
        )

        user_message = f"""Attraction: {attraction_name}

Review text:
{review_text}

Return ONLY this JSON (numbers between 0.0 and 1.0):
{{
  "scenery": 0.0,
  "cleanliness": 0.0,
  "crowd_level": 0.0,
  "value_for_money": 0.0,
  "accessibility": 0.0,
  "safety": 0.0,
  "food_quality": 0.0,
  "cultural_significance": 0.0
}}"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1, "num_predict": 256},
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            raw = response.json().get("message", {}).get("content", "")

            # Strip markdown fences if present
            raw = raw.replace("```json", "").replace("```", "").strip()
            scores = json.loads(raw)

            # Validate and clamp all expected keys
            result = {}
            for aspect in self.ASPECTS:
                val = float(scores.get(aspect, 0.5))
                result[aspect] = max(0.0, min(1.0, val))
            return result

        except Exception as e:
            print(f"  AspectAnalyzer error for '{attraction_name}': {e}")
            return None
