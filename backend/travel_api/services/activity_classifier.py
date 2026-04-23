"""
ActivityClassifier — keyword-based outdoor/indoor/mixed classification (Feature 3).
"""

OUTDOOR_KEYWORDS = {
    "beach", "surf", "surfing", "snorkel", "snorkeling", "hike", "hiking", "trek",
    "trekking", "safari", "whale watching", "whale", "waterfall", "elephant", "national park",
    "boat", "river", "kayak", "kayaking", "zipline", "zip line", "tea plantation",
    "tea estate", "garden", "botanical", "fishing", "diving", "swim", "swimming",
    "rock", "fort", "ruins", "rock pool", "lagoon", "mangrove", "scenic", "viewpoint",
    "sunrise", "sunset", "mountain", "hill", "peak", "sightseeing", "cycling",
    "birdwatching", "bird watching", "nature walk", "jungle", "forest",
}

INDOOR_KEYWORDS = {
    "museum", "temple", "shrine", "stupa", "church", "mosque", "kovil", "dagoba",
    "gallery", "market", "mall", "shopping", "restaurant", "dining", "dinner",
    "lunch", "breakfast", "spa", "wellness", "ayurveda", "massage", "cooking class",
    "workshop", "hotel", "accommodation", "check in", "check-in", "arrival",
    "transit", "travel", "transfer", "flight", "train", "bus",
}


def classify_activity(activity_name: str, description: str = "") -> str:
    """Return 'outdoor', 'indoor', or 'mixed'."""
    combined = (activity_name + " " + description).lower()

    outdoor_hits = sum(1 for kw in OUTDOOR_KEYWORDS if kw in combined)
    indoor_hits = sum(1 for kw in INDOOR_KEYWORDS if kw in combined)

    if outdoor_hits == 0 and indoor_hits == 0:
        return "mixed"
    if outdoor_hits > indoor_hits:
        return "outdoor"
    if indoor_hits > outdoor_hits:
        return "indoor"
    return "mixed"


def get_day_outdoor_ratio(activities: list) -> float:
    """Return fraction of outdoor activities for a day (0.0–1.0)."""
    if not activities:
        return 0.5

    scores = []
    for act in activities:
        name = act.get("activity", "")
        desc = act.get("description", "")
        classification = classify_activity(name, desc)
        if classification == "outdoor":
            scores.append(1.0)
        elif classification == "indoor":
            scores.append(0.0)
        else:
            scores.append(0.5)

    return sum(scores) / len(scores)
