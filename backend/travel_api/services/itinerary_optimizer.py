"""
ItineraryOptimizer — weather-aware day re-ordering (Feature 3).
Swaps days only within the same geographic region cluster to preserve
the geographic progression logic already enforced by the LLM.
"""
from datetime import date, timedelta
from .weather_forecast import WeatherForecastService
from .activity_classifier import get_day_outdoor_ratio

REGION_CLUSTERS = {
    "west_coast":       {"Colombo", "Negombo", "Bentota", "Hikkaduwa", "Kalutara"},
    "south_coast":      {"Galle", "Unawatuna", "Mirissa", "Tangalle", "Weligama", "Matara"},
    "hill_country":     {"Kandy", "Ella", "Nuwara Eliya", "Haputale", "Bandarawela", "Hatton"},
    "cultural_triangle":{"Sigiriya", "Dambulla", "Anuradhapura", "Polonnaruwa", "Matale"},
    "east_coast":       {"Trincomalee", "Nilaveli", "Arugam Bay", "Batticaloa", "Ampara"},
    "north":            {"Jaffna", "Mannar", "Vavuniya"},
    "nature_south":     {"Yala", "Udawalawe", "Sinharaja"},
}


def _get_region(city: str) -> str:
    city_lower = city.lower()
    for region, cities in REGION_CLUSTERS.items():
        for c in cities:
            if c.lower() in city_lower or city_lower in c.lower():
                return region
    return "other"


class ItineraryOptimizer:
    def __init__(self):
        self.weather_svc = WeatherForecastService()

    def optimize(self, itinerary: dict, start_date: date | None = None) -> dict:
        """
        Re-order days within geographic clusters to align outdoor days with
        better weather. Returns the itinerary dict with an added
        'optimization_log' field and updated 'weather_forecast' on each day.
        """
        if start_date is None:
            start_date = date.today()

        days = itinerary.get("days", [])
        if len(days) < 2:
            itinerary["optimization_log"] = []
            return itinerary

        # 1. Attach metadata to each day
        for i, day in enumerate(days):
            city = day.get("location", "")
            day_date = start_date + timedelta(days=i)
            day["_date"] = day_date.isoformat()
            day["_region"] = _get_region(city)
            day["_outdoor_ratio"] = get_day_outdoor_ratio(day.get("activities", []))
            forecast = self.weather_svc.get_forecast_for_date(city, day["_date"])
            day["weather_forecast"] = forecast or {}

        # 2. Group indices by region
        from collections import defaultdict
        region_groups = defaultdict(list)
        for i, day in enumerate(days):
            region_groups[day["_region"]].append(i)

        log = []

        # 3. Within each region group, try swapping for better weather alignment
        for region, indices in region_groups.items():
            if len(indices) < 2:
                continue

            # Score alignment: high outdoor_ratio + high outdoor_score = good
            def alignment_score(idx):
                d = days[idx]
                outdoor_score = d.get("weather_forecast", {}).get("outdoor_score", 0.5)
                outdoor_ratio = d.get("_outdoor_ratio", 0.5)
                return outdoor_ratio * outdoor_score

            # Simple bubble sort within the region group — O(n²) fine for tiny groups
            changed = True
            while changed:
                changed = False
                for k in range(len(indices) - 1):
                    a, b = indices[k], indices[k + 1]
                    score_before = alignment_score(a) + alignment_score(b)

                    # Temporarily swap
                    days[a]["weather_forecast"], days[b]["weather_forecast"] = (
                        days[b]["weather_forecast"], days[a]["weather_forecast"]
                    )
                    days[a]["_date"], days[b]["_date"] = days[b]["_date"], days[a]["_date"]

                    score_after = alignment_score(a) + alignment_score(b)

                    if score_after > score_before + 0.05:  # only swap if meaningfully better
                        log.append({
                            "region": region,
                            "swapped_days": [days[a]["day"], days[b]["day"]],
                            "reason": (
                                f"Day {days[a]['day']} ({days[a]['location']}) outdoor ratio "
                                f"{days[a]['_outdoor_ratio']:.0%} aligned better with "
                                f"forecast score {days[a]['weather_forecast'].get('outdoor_score', 0):.2f}; "
                                f"Day {days[b]['day']} swapped accordingly."
                            ),
                        })
                        changed = True
                    else:
                        # Revert
                        days[a]["weather_forecast"], days[b]["weather_forecast"] = (
                            days[b]["weather_forecast"], days[a]["weather_forecast"]
                        )
                        days[a]["_date"], days[b]["_date"] = days[b]["_date"], days[a]["_date"]

        # 4. Clean up internal metadata keys
        for day in days:
            day.pop("_date", None)
            day.pop("_region", None)
            day.pop("_outdoor_ratio", None)

        itinerary["days"] = days
        itinerary["optimization_log"] = log
        itinerary["weather_optimized"] = len(log) > 0

        return itinerary
