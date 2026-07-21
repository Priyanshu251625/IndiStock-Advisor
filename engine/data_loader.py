import os
import pandas as pd
import yfinance as yf


class DataLoader:
    def __init__(self, data_path="data/raw"):
        self.data_path = data_path
        os.makedirs(self.data_path, exist_ok=True)

    def download_stock_data(self, ticker, start_date, end_date, save=True):
        """
        Download historical data for a single stock.
        """

        try:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True,
            )

            if data.empty:
                print(f"[WARNING] No data found for {ticker}")
                return None

            # Flatten MultiIndex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # Make Date a normal column
            data = data.reset_index()

            if save:
                filename = ticker.replace(".NS", "") + ".csv"
                filepath = os.path.join(self.data_path, filename)

                data.to_csv(filepath, index=False)

                print(f"[SUCCESS] {ticker} saved.")

            return data

        except Exception as e:
            print(f"[ERROR] {ticker}: {e}")
            return None
        
    def download_stock(self, ticker, start_date, end_date):
        return self.download_stock_data(
            ticker,
            start_date,
            end_date,
            save=False
        )

    def download_multiple_stocks(self, tickers, start_date, end_date):
        """
        Download historical data for multiple stocks.
        """

        for ticker in tickers:
            self.download_stock_data(
                ticker,
                start_date,
                end_date
            )

    