"""
Crowd Density Prediction — ML-based (Feature 4).
Trains a GradientBoostingClassifier on synthetic Sri Lankan tourism data.
The model is cached as a pickle after first training.
"""
import os
import pickle
import csv
import random
from datetime import datetime, date
from zoneinfo import ZoneInfo

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crowd_model.pkl")

HOLIDAY_FILE_TPL = os.path.join(
    os.path.dirname(__file__),
    "srilanka_holidays/json/{year}.json",
)

LABELS = {1: "Very Low", 2: "Low", 3: "Moderate", 4: "High", 5: "Very High"}


def _load_holidays(year: int) -> set:
    import json
    path = HOLIDAY_FILE_TPL.format(year=year)
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        data = json.load(f)
    return {h["start"] for h in data}


def _is_poya(date_str: str, holidays: set) -> bool:
    return date_str in holidays


def _date_to_features(d: date, holidays: set) -> list:
    date_str = d.isoformat()
    day_of_week = d.weekday()       # 0=Mon … 6=Sun
    month = d.month
    is_poya = int(_is_poya(date_str, holidays))
    is_weekend = int(day_of_week >= 5)
    # Peak season Dec-Mar=1, Jul-Aug=0.7, others=0
    if month in (12, 1, 2, 3):
        season_score = 1.0
    elif month in (7, 8):
        season_score = 0.7
    else:
        season_score = 0.0
    # School holidays Apr and Aug in Sri Lanka
    is_school_holiday = int(month in (4, 8))
    return [day_of_week, month, is_poya, is_weekend, season_score, is_school_holiday]


def _generate_training_data(n=5000) -> tuple:
    """Generate synthetic crowd samples based on known Sri Lankan tourism patterns."""
    random.seed(42)
    X, y = [], []
    start = date(2022, 1, 1)
    holidays_2022 = _load_holidays(2022)
    holidays_2023 = _load_holidays(2023)
    holidays_2024 = _load_holidays(2024)
    holidays_2025 = _load_holidays(2025)

    all_holidays = holidays_2022 | holidays_2023 | holidays_2024 | holidays_2025

    for _ in range(n):
        delta = random.randint(0, 1460)
        d = date(2022, 1, 1)
        import datetime as dt_mod
        d = start + dt_mod.timedelta(days=delta)
        feats = _date_to_features(d, all_holidays)

        is_poya, is_weekend, season, school = feats[2], feats[3], feats[4], feats[5]

        base = 2.0
        if is_poya:
            base += 2.2
        if is_weekend:
            base += 0.9
        base += season * 0.7
        if school:
            base += 0.5

        noise = random.gauss(0, 0.5)
        level = max(1, min(5, round(base + noise)))

        X.append(feats)
        y.append(level)

    return X, y


class CrowdPredictor:
    def __init__(self):
        self._model = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                self._model = pickle.load(f)
            print("CrowdPredictor: loaded model from cache.")
        else:
            self._train()

    def _train(self):
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import cross_val_score
            import numpy as np
        except ImportError:
            print("WARNING: sklearn not available. CrowdPredictor will use rule-based fallback.")
            self._model = None
            return

        print("CrowdPredictor: training on synthetic data...")
        X, y = _generate_training_data(5000)
        clf = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
        clf.fit(X, y)

        scores = cross_val_score(clf, X, y, cv=5)
        print(f"CrowdPredictor: CV accuracy = {scores.mean():.2%} ± {scores.std():.2%}")

        with open(MODEL_PATH, "wb") as f:
            pickle.dump(clf, f)
        self._model = clf
        print(f"CrowdPredictor: model saved to {MODEL_PATH}")

    def predict(self, date_str: str) -> dict:
        """Return crowd prediction for a given 'YYYY-MM-DD' date string."""
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            d = date.today()

        holidays = _load_holidays(d.year)
        feats = _date_to_features(d, holidays)

        if self._model is not None:
            try:
                level = int(self._model.predict([feats])[0])
                proba = self._model.predict_proba([feats])[0]
                confidence = round(float(max(proba)) * 100, 1)
            except Exception:
                level, confidence = self._rule_based(feats)
        else:
            level, confidence = self._rule_based(feats)

        level = max(1, min(5, level))
        return {
            "date": date_str,
            "level": level,
            "label": LABELS[level],
            "confidence": confidence,
            "is_poya": bool(feats[2]),
            "is_weekend": bool(feats[3]),
        }

    def _rule_based(self, feats: list) -> tuple:
        _, month, is_poya, is_weekend, season, school = feats
        score = 2
        if is_poya:
            score += 2
        if is_weekend:
            score += 1
        if season >= 1.0:
            score += 1
        level = max(1, min(5, score))
        return level, 70.0
