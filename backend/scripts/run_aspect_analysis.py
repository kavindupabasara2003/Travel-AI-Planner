"""
Batch ABSA script — run from the backend/ directory:
  python manage.py shell < scripts/run_aspect_analysis.py
or:
  cd backend && python scripts/run_aspect_analysis.py
"""
import os
import sys
import csv
import django

# Allow running directly or via manage.py shell
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travel_ai_backend.settings")
    django.setup()

from travel_api.models import AttractionAspectScore
from travel_api.services.aspect_analyzer import AspectAnalyzer

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "SriLanka_Travel_Dataset_Final.csv"
)
MIN_REVIEW_LEN = 200


def main():
    analyzer = AspectAnalyzer()

    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    candidates = [
        r for r in rows
        if len(r.get("AI_Context", "")) > MIN_REVIEW_LEN
    ]
    print(f"Found {len(candidates)} attractions with reviews longer than {MIN_REVIEW_LEN} chars.")

    created = 0
    skipped = 0
    failed = 0

    for i, row in enumerate(candidates, 1):
        name = row["Location_Name"].strip()
        city = row["Located_City"].strip()
        loc_type = row["Location_Type"].strip()
        review = row["AI_Context"].strip()

        if AttractionAspectScore.objects.filter(attraction_name=name).exists():
            print(f"  [{i}/{len(candidates)}] SKIP (already exists): {name}")
            skipped += 1
            continue

        print(f"  [{i}/{len(candidates)}] Analyzing: {name} ({loc_type}, {city})")
        scores = analyzer.extract_scores(name, review)

        if scores is None:
            print(f"    FAILED — skipping.")
            failed += 1
            continue

        AttractionAspectScore.objects.create(
            attraction_name=name,
            location_type=loc_type,
            located_city=city,
            **scores,
        )
        print(f"    Saved. Scenery={scores['scenery']:.2f}, Crowd={scores['crowd_level']:.2f}")
        created += 1

    print(f"\nDone. Created: {created}, Skipped: {skipped}, Failed: {failed}")


if __name__ == "__main__":
    main()
