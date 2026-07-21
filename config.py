import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL = "llama-3.3-70b-versatile"

TRAIN_STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "ITC.NS",
    "LT.NS",
    "BHARTIARTL.NS",
    "SBIN.NS",
    "SUNPHARMA.NS"
]

TRAIN_START = "2024-01-01"
TRAIN_END = "2024-03-31"

VALIDATION_START = "2024-04-01"
VALIDATION_END = "2024-07-31"