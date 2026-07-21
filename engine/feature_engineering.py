import os
import pandas as pd

from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator


class FeatureEngineer:

    def __init__(
        self,
        raw_path="data/raw",
        processed_path="data/processed"
    ):
        self.raw_path = raw_path
        self.processed_path = processed_path

        os.makedirs(self.processed_path, exist_ok=True)

    def load_stock(self, filename):
        filepath = os.path.join(self.raw_path, filename)

        df = pd.read_csv(filepath)

        return df

    def calculate_features(self, df):

        # Performance
        df["Daily_Return"] = df["Close"].pct_change()
        df["Cumulative_Return"] = (
            (1 + df["Daily_Return"]).cumprod() - 1
        )

        # Trend
        df["SMA20"] = SMAIndicator(
            close=df["Close"],
            window=20
        ).sma_indicator()

        df["SMA50"] = SMAIndicator(
            close=df["Close"],
            window=50
        ).sma_indicator()

        df["EMA20"] = EMAIndicator(
            close=df["Close"],
            window=20
        ).ema_indicator()

        # Momentum
        df["RSI"] = RSIIndicator(
            close=df["Close"]
        ).rsi()

        macd = MACD(close=df["Close"])
        df["MACD"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()

        # Risk
        df["Volatility"] = (
            df["Daily_Return"]
            .rolling(window=20)
            .std()
        )

        rolling_max = df["Close"].cummax()
        df["Drawdown"] = (
            df["Close"] - rolling_max
        ) / rolling_max

        # Volume
        volume_avg = df["Volume"].rolling(window=20).mean()
        df["Volume_Ratio"] = (
            df["Volume"] / volume_avg
        )

        # Trend Label
        df["Trend"] = "Sideways"
        df.loc[df["SMA20"] > df["SMA50"], "Trend"] = "Bullish"
        df.loc[df["SMA20"] < df["SMA50"], "Trend"] = "Bearish"

        df = df.dropna().reset_index(drop=True)

        return df
    
    def save_stock(self, df, filename):
        filepath = os.path.join(self.processed_path, filename)
        df.to_csv(filepath, index=False)

        print(f"[SUCCESS] {filename} processed.")

    def process_all_stocks(self):

        for filename in os.listdir(self.raw_path):

            if filename.endswith(".csv"):

                df = self.load_stock(filename)
                df = self.calculate_features(df)
                self.save_stock(df, filename)


    def process_dataframe(self, stock_df):

        return self.calculate_features(stock_df)