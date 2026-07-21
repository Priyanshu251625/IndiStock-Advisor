import json
import pandas as pd
import math


class ReasoningEngine:

    def __init__(self,
                 knowledge_file="knowledge/knowledge_base.json"):
        
        self.sector_aliases = {
            # Banking
            "finance": "banking",
            "financial": "banking",
            "financials": "banking",
            "financial services": "banking",
            "bank": "banking",
            "banks": "banking",

            # IT
            "technology": "it",
            "tech": "it",
            "software": "it",
            "information technology": "it",

            # Pharma
            "healthcare": "pharma",
            "health care": "pharma",
            "pharmaceutical": "pharma",
            "pharmaceuticals": "pharma",
            "medicine": "pharma",

            # FMCG
            "consumer": "fmcg",
            "consumer goods": "fmcg",
            "consumer staples": "fmcg",
            "fast moving consumer goods": "fmcg",

            # Energy
            "oil": "energy",
            "gas": "energy",
            "oil & gas": "energy",
            "oil and gas": "energy",

            # Infrastructure
            "construction": "infrastructure",
            "engineering": "infrastructure",
            "infra": "infrastructure",

            # Telecom
            "telecommunication": "telecom",
            "telecommunications": "telecom",
            "communication": "telecom",
            "communications": "telecom"
        }

        self.knowledge_file = knowledge_file
        self.knowledge = self.load_knowledge()
        self.feature_ranges = self.get_feature_ranges()

    def load_knowledge(self):

        with open(self.knowledge_file, "r") as f:
            return json.load(f)
        
    def get_feature_ranges(self):

        numeric_features = [
            "average_daily_return",
            "cumulative_return",
            "average_rsi",
            "average_volatility",
            "max_drawdown",
            "average_volume_ratio"
        ]

        ranges = {}

        for feature in numeric_features:

            values = [
                stock[feature]
                for stock in self.knowledge.values()
            ]

            ranges[feature] = {
                "min": min(values),
                "max": max(values)
            }

        return ranges
    


    def extract_features(self, processed_df):
        features = {
            "average_daily_return": float(processed_df["Daily_Return"].mean()),
            "cumulative_return": float(processed_df["Cumulative_Return"].iloc[-1]),
            "average_rsi": float(processed_df["RSI"].mean()),
            "average_volatility": float(processed_df["Volatility"].mean()),
            "max_drawdown": float(processed_df["Drawdown"].min()),
            "average_volume_ratio": float(processed_df["Volume_Ratio"].mean()),
            "trend": processed_df["Trend"].iloc[-1]
        }

        return features
    
    def normalize(self, feature, value):

        minimum = self.feature_ranges[feature]["min"]
        maximum = self.feature_ranges[feature]["max"]

        if maximum == minimum:
            return 0.0

        return (value - minimum) / (maximum - minimum)
    
    def calculate_similarity(self, stock_features, knowledge_features):

        distance = 0

        numeric_features = [
            "average_daily_return",
            "cumulative_return",
            "average_rsi",
            "average_volatility",
            "max_drawdown",
            "average_volume_ratio"
        ]

        for feature in numeric_features:

            stock_value = self.normalize(
                feature,
                stock_features[feature]
            )

            knowledge_value = self.normalize(
                feature,
                knowledge_features[feature]
            )

            distance += (
                stock_value - knowledge_value
            ) ** 2

        distance = math.sqrt(distance)

        # Small bonus if trend matches
        if stock_features["trend"] == knowledge_features["trend"]:
            distance *= 0.9

        return distance
    
    def find_similar_stocks(self, stock_features, top_n=3):

        similarities = []

        for stock, knowledge_features in self.knowledge.items():

            distance = self.calculate_similarity(
                stock_features,
                knowledge_features
            )

            similarities.append({
                "stock": stock,
                "distance": distance
            })

        similarities.sort(
            key=lambda x: x["distance"]
        )

        return similarities[:top_n]
    

    def recommend(self,stock_features,similar_stocks,user_preferences):

        score = 0
        reasons = []

        # Trend
        if stock_features["trend"] == "Bullish":
            score += 2
            reasons.append("The stock is currently in a bullish trend.")

        # Target Return
        if stock_features["cumulative_return"] >= user_preferences["target_return"]:
            score += 2
            reasons.append(
                "The cumulative return meets the user's target."
            )

        # Volatility
        risk = user_preferences["risk"]

        volatility = stock_features["average_volatility"]

        if risk == "low" and volatility < 0.015:
            score += 2
            reasons.append("Volatility is suitable for a low-risk investor.")

        elif risk == "medium" and volatility < 0.03:
            score += 2
            reasons.append("Volatility is suitable for a medium-risk investor.")

        elif risk == "high":
            score += 2
            reasons.append("High-risk investor accepts this volatility.")

        # RSI
        if 40 <= stock_features["average_rsi"] <= 70:
            score += 1
            reasons.append(
                "Momentum is healthy (RSI in a neutral range)."
            )

        # Similar Stocks
        bullish = 0

        for stock in similar_stocks:

            if self.knowledge[stock["stock"]]["trend"] == "Bullish":
                bullish += 1

        if bullish >= 2:
            score += 1
            reasons.append(
                "Most similar historical stocks were bullish."
            )


        if score >= 7:
            recommendation = "Buy"

        elif score >= 5:
            recommendation = "Hold"

        else:
            recommendation = "Avoid"

        confidence = min(round(score / 8, 2), 0.95)
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "score": score,
            "reasoning": reasons
        }
    

    def get_sector_stocks(self, sector):

        if not sector:
            return []

        sector = sector.lower().strip()
        sector = self.sector_aliases.get(sector, sector)

        stocks = []

        for _, data in self.knowledge.items():

            if data["sector"].lower() == sector:

                stocks.append({
                    "ticker": data["yahoo_ticker"],
                    "company_name": data["company_name"]
                })

        return stocks
    
    

    def analyze(self, processed_df, user_preferences):

        stock_features = self.extract_features(processed_df)

        similar_stocks = self.find_similar_stocks(
            stock_features
        )

        result = self.recommend(
            stock_features,
            similar_stocks,
            user_preferences
        )

        result["similar_stocks"] = similar_stocks
        result["stock_features"] = stock_features

        return result