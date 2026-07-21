import json
import os

import pandas as pd


metadata = {
    "BHARTIARTL": {
        "company_name": "Bharti Airtel",
        "sector": "Telecom",
        "yahoo_ticker": "BHARTIARTL.NS"
    },
    "HDFCBANK": {
        "company_name": "HDFC Bank",
        "sector": "Banking",
        "yahoo_ticker": "HDFCBANK.NS"
    },
    "ICICIBANK": {
        "company_name": "ICICI Bank",
        "sector": "Banking",
        "yahoo_ticker": "ICICIBANK.NS"
    },
    "INFY": {
        "company_name": "Infosys",
        "sector": "IT",
        "yahoo_ticker": "INFY.NS"
    },
    "ITC": {
        "company_name": "ITC",
        "sector": "FMCG",
        "yahoo_ticker": "ITC.NS"
    },
    "LT": {
        "company_name": "Larsen & Toubro",
        "sector": "Infrastructure",
        "yahoo_ticker": "LT.NS"
    },
    "RELIANCE": {
        "company_name": "Reliance Industries",
        "sector": "Energy",
        "yahoo_ticker": "RELIANCE.NS"
    },
    "SBIN": {
        "company_name": "State Bank of India",
        "sector": "Banking",
        "yahoo_ticker": "SBIN.NS"
    },
    "SUNPHARMA": {
        "company_name": "Sun Pharma",
        "sector": "Pharma",
        "yahoo_ticker": "SUNPHARMA.NS"
    },
    "TCS": {
        "company_name": "Tata Consultancy Services",
        "sector": "IT",
        "yahoo_ticker": "TCS.NS"
    }
}


class KnowledgeBase:

    def __init__(
        self,
        processed_path="data/processed",
        knowledge_path="knowledge"
    ):
        self.processed_path = processed_path
        self.knowledge_path = knowledge_path

        os.makedirs(self.knowledge_path, exist_ok=True)

    def load_stock(self, filename):

        filepath = os.path.join(self.processed_path, filename)

        df = pd.read_csv(
            filepath,
            parse_dates=["Date"]
        )

        return df

    def get_training_data(
        self,
        df,
        train_end="2024-03-31"
    ):
        return df[df["Date"] <= train_end]

    def summarize_stock(self, df):

        return {
            "average_daily_return": float(df["Daily_Return"].mean()),
            "cumulative_return": float(df["Cumulative_Return"].iloc[-1]),
            "average_rsi": float(df["RSI"].mean()),
            "average_volatility": float(df["Volatility"].mean()),
            "max_drawdown": float(df["Drawdown"].min()),
            "average_volume_ratio": float(df["Volume_Ratio"].mean()),
            "trend": df["Trend"].mode()[0]
        }

    def build_knowledge_base(self):

        knowledge = {}

        for filename in os.listdir(self.processed_path):

            if not filename.endswith(".csv"):
                continue

            stock_name = filename.replace(".csv", "")

            df = self.load_stock(filename)
            df = self.get_training_data(df)

            summary = self.summarize_stock(df)

            summary.update(
                metadata.get(
                    stock_name,
                    {
                        "company_name": stock_name,
                        "sector": "Unknown",
                        "yahoo_ticker": f"{stock_name}.NS"
                    }
                )
            )

            knowledge[stock_name] = summary

        return knowledge

    def save_knowledge(
        self,
        knowledge,
        filename="knowledge_base.json"
    ):

        filepath = os.path.join(
            self.knowledge_path,
            filename
        )

        with open(filepath, "w") as f:
            json.dump(
                knowledge,
                f,
                indent=4
            )

        print(f"[SUCCESS] Knowledge Base saved to {filepath}")