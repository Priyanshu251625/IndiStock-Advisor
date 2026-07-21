import pandas as pd

from config import (
    TRAIN_STOCKS,
    VALIDATION_START,
    VALIDATION_END,
)

from engine.data_loader import DataLoader
from engine.feature_engineering import FeatureEngineer
from engine.reasoning_engine import ReasoningEngine

loader = DataLoader()
engineer = FeatureEngineer()
reasoner = ReasoningEngine()

user_preferences = {
    "risk": "medium",
    "target_return": 0.15
}

results = []

for stock in TRAIN_STOCKS:

    raw_df = loader.download_stock(
        stock,
        VALIDATION_START,
        VALIDATION_END
    )

    if raw_df is None:
        continue

    processed_df = engineer.process_dataframe(raw_df)

    features = reasoner.extract_features(processed_df)

    similar = reasoner.find_similar_stocks(features)

    recommendation = reasoner.recommend(
        features,
        similar,
        user_preferences
    )

    actual_return = features["cumulative_return"]

    if recommendation["recommendation"] == "Buy":
        correct = actual_return >= 0.10

    elif recommendation["recommendation"] == "Hold":
        correct = -0.05 <= actual_return < 0.10

    else:  # Avoid
        correct = actual_return < 0


    results.append({
        "Stock": stock,
        "Score": recommendation['score'],
        "Similar Stock": similar[0]["stock"],
        "Recommendation": recommendation["recommendation"],
        "Confidence": recommendation["confidence"],
        "Actual Return (%)": round(actual_return * 100, 2),
        "Trend": features["trend"],
        "Correct": correct
    })


df = pd.DataFrame(results)

print(df)

accuracy = df["Correct"].mean() * 100

print(f"\nValidation Accuracy: {accuracy:.2f}%")