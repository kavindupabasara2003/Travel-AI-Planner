from celery import shared_task


VARIATIONS_CONFIG = [
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
            "local favourites. Each day should offer variety — pair a famous attraction with a local secret spot."
        ),
    },
]


@shared_task(bind=True, name='travel_api.tasks.generate_single_task', max_retries=0, time_limit=600)
def generate_single_task(self, preferences):
    """Async single-variation itinerary generation with progress updates."""
    from travel_api.services.llama_service import LLaMAService
    service = LLaMAService()

    self.update_state(state='PROGRESS', meta={'progress': 10, 'message': '🔍 Checking cache...'})
    result = service.generate_itinerary(preferences)
    return result


@shared_task(bind=True, name='travel_api.tasks.generate_multi_task', max_retries=0, time_limit=900)
def generate_multi_task(self, preferences):
    """Async 3-variation itinerary generation with per-variation progress updates."""
    from travel_api.services.llama_service import LLaMAService
    service = LLaMAService()

    if not isinstance(preferences, dict):
        raise ValueError("preferences must be a dict")

    duration = str(preferences.get('duration', '7'))
    start_loc = str(preferences.get('startLocation', 'Colombo')).strip()
    group = str(preferences.get('groupSize', 'Couple')).strip()
    trip_type = str(preferences.get('tripType', 'Beach')).strip()
    base_query = f"Duration: {duration} Days | Start Location: {start_loc} | Group: {group} | Style: {trip_type}"

    results = []
    total = len(VARIATIONS_CONFIG)

    for i, var in enumerate(VARIATIONS_CONFIG):
        self.update_state(state='PROGRESS', meta={
            'progress': 5 + int((i / total) * 85),
            'message': f'✨ Generating {var["label"]} ({i + 1}/{total})...',
        })
        result = service._generate_single_variation(var, base_query, duration, start_loc, trip_type)
        results.append(result)

    self.update_state(state='PROGRESS', meta={'progress': 95, 'message': '✅ Finalising your itineraries...'})
    return {'variations': results}
