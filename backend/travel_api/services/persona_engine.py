PERSONAS = [
    {
        "key": "beach_lover",
        "name": "Beach Lover",
        "emoji": "🏖️",
        "color": "#0ea5e9",
        "themes": ["beach"],
        "desc": "Sun, sand, and sea define your journey. Sri Lanka's coastline is your paradise.",
        "traits": ["Coastal", "Relaxed", "Water Sports"],
    },
    {
        "key": "culture_seeker",
        "name": "Culture Seeker",
        "emoji": "🏛️",
        "color": "#f59e0b",
        "themes": ["cultural"],
        "desc": "Ancient temples, royal cities, and rich heritage shape every itinerary you choose.",
        "traits": ["History", "Architecture", "Traditions"],
    },
    {
        "key": "adventure_seeker",
        "name": "Adventure Seeker",
        "emoji": "🥾",
        "color": "#8b5cf6",
        "themes": ["adventure"],
        "desc": "Waterfalls, cliff trails, and off-road tracks are where you feel most alive.",
        "traits": ["Hiking", "Thrills", "Off-road"],
    },
    {
        "key": "nature_explorer",
        "name": "Nature Explorer",
        "emoji": "🌿",
        "color": "#10b981",
        "themes": ["nature"],
        "desc": "Rainforests, wildlife safaris, and misty mountains call your name every trip.",
        "traits": ["Wildlife", "Eco-Travel", "Rainforest"],
    },
    {
        "key": "foodie_traveler",
        "name": "Foodie Traveler",
        "emoji": "🍛",
        "color": "#f97316",
        "themes": ["foodie"],
        "desc": "Local spice routes, street food markets, and authentic cuisine are your compass.",
        "traits": ["Cuisine", "Markets", "Local Flavours"],
    },
]

DEFAULT_PERSONA = {
    "key": "explorer",
    "name": "Explorer",
    "emoji": "🗺️",
    "color": "#6366f1",
    "desc": "A versatile traveller who embraces every style. Generate more trips to discover your true persona!",
    "traits": ["Versatile", "Curious", "Open-minded"],
}


class PersonaEngine:
    def get_persona(self, user):
        """
        Analyse the user's saved trip themes and return their dominant travel persona.
        Returns a dict with name, emoji, color, desc, traits, trips_analyzed, top_theme.
        """
        try:
            from ..models import SavedTrip
            trips = list(SavedTrip.objects.filter(user=user))
        except Exception:
            return {**DEFAULT_PERSONA, "trips_analyzed": 0, "top_theme": None}

        if not trips:
            return {**DEFAULT_PERSONA, "trips_analyzed": 0, "top_theme": None}

        theme_counts: dict[str, int] = {}
        for trip in trips:
            theme = (trip.itinerary_json or {}).get("trip_theme", "")
            if theme:
                key = theme.lower().strip()
                theme_counts[key] = theme_counts.get(key, 0) + 1

        if not theme_counts:
            return {**DEFAULT_PERSONA, "trips_analyzed": len(trips), "top_theme": None}

        top_theme = max(theme_counts, key=theme_counts.get)

        for persona in PERSONAS:
            if any(t in top_theme for t in persona["themes"]):
                return {
                    **persona,
                    "trips_analyzed": len(trips),
                    "top_theme": top_theme,
                    "theme_breakdown": theme_counts,
                }

        return {**DEFAULT_PERSONA, "trips_analyzed": len(trips), "top_theme": top_theme}
