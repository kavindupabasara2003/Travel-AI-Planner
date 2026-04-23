"""
Itinerary Quality Evaluation Framework (Feature 15).

Run from backend/:
  python scripts/evaluate_itinerary_quality.py [--batch 50]

Evaluates on 6 dimensions (each 0-100):
  1. Geographic Diversity
  2. Activity Variety
  3. Temporal Logic
  4. Restaurant Coverage
  5. Narrative Coherence
  6. Duration Compliance
"""
import os, sys, json, csv, argparse, random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travel_ai_backend.settings")

import django
django.setup()

from travel_api.services.llama_service import LLaMAService


class ItineraryEvaluator:
    def evaluate(self, itinerary: dict, requested_days: int) -> dict:
        days = itinerary.get("days", [])
        n = len(days)

        scores = {
            "geographic_diversity": self._geographic_diversity(days),
            "activity_variety": self._activity_variety(days),
            "temporal_logic": self._temporal_logic(days),
            "restaurant_coverage": self._restaurant_coverage(days),
            "narrative_coherence": self._narrative_coherence(days),
            "duration_compliance": self._duration_compliance(n, requested_days),
        }
        scores["overall"] = round(sum(scores.values()) / len(scores), 1)
        return scores

    def _geographic_diversity(self, days: list) -> float:
        if not days:
            return 0.0
        cities = set(d.get("location", "").split("(")[0].strip().lower() for d in days)
        ratio = len(cities) / len(days)
        return round(min(ratio * 100, 100), 1)

    def _activity_variety(self, days: list) -> float:
        all_acts = []
        for d in days:
            for a in d.get("activities", []):
                all_acts.append(a.get("activity", "").lower())
        if not all_acts:
            return 0.0
        unique = len(set(all_acts))
        return round(min((unique / len(all_acts)) * 100, 100), 1)

    def _temporal_logic(self, days: list) -> float:
        if not days:
            return 0.0
        day_nums = [d.get("day") for d in days]
        expected = list(range(1, len(days) + 1))
        correct = sum(1 for a, b in zip(day_nums, expected) if a == b)
        return round((correct / len(days)) * 100, 1)

    def _restaurant_coverage(self, days: list) -> float:
        if not days:
            return 0.0
        with_res = sum(1 for d in days if d.get("suggested_restaurants"))
        return round((with_res / len(days)) * 100, 1)

    def _narrative_coherence(self, days: list) -> float:
        if not days:
            return 0.0
        coherent = 0
        for d in days:
            narrative = (d.get("narrative") or "").lower()
            location = (d.get("location") or "").lower().split("(")[0].strip()
            # Check if any word from the location appears in the narrative
            if any(word in narrative for word in location.split() if len(word) > 3):
                coherent += 1
        return round((coherent / len(days)) * 100, 1)

    def _duration_compliance(self, actual: int, requested: int) -> float:
        if requested <= 0:
            return 100.0
        diff = abs(actual - requested)
        penalty = diff * 20
        return max(0.0, round(100.0 - penalty, 1))


def run_batch_evaluation(n_samples: int = 50):
    agent = LLaMAService()
    evaluator = ItineraryEvaluator()

    # Test parameter matrix
    durations = [3, 5, 7, 10]
    start_cities = ["Colombo", "Kandy", "Galle", "Negombo"]
    trip_types = ["Beach", "Cultural", "Adventure", "Foodie", "Honeymoon"]
    groups = ["Solo", "Couple", "Family"]

    results = []
    print(f"Running {n_samples} evaluations...\n")

    for i in range(n_samples):
        duration = random.choice(durations)
        prefs = {
            "duration": duration,
            "startLocation": random.choice(start_cities),
            "groupSize": random.choice(groups),
            "tripType": random.choice(trip_types),
        }

        print(f"[{i+1}/{n_samples}] {prefs}")

        try:
            itinerary = agent.generate_itinerary(prefs)
            if "error" in itinerary:
                print(f"  ERROR: {itinerary['error']}")
                continue

            scores = evaluator.evaluate(itinerary, duration)
            scores["prefs"] = json.dumps(prefs)
            results.append(scores)
            print(f"  Overall: {scores['overall']}/100")

        except Exception as e:
            print(f"  EXCEPTION: {e}")

    if not results:
        print("No results collected.")
        return

    # Print summary
    keys = ["geographic_diversity", "activity_variety", "temporal_logic",
            "restaurant_coverage", "narrative_coherence", "duration_compliance", "overall"]

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    for k in keys:
        vals = [r[k] for r in results if k in r]
        if vals:
            avg = sum(vals) / len(vals)
            print(f"  {k:<25}: {avg:.1f}/100")
    print(f"\n  Samples evaluated: {len(results)}/{n_samples}")

    # Save CSV
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys + ["prefs"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=50, help="Number of itineraries to evaluate")
    args = parser.parse_args()
    run_batch_evaluation(args.batch)
