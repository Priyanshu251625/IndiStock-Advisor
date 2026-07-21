from config import (
    TRAIN_STOCKS,
    TRAIN_START,
    TRAIN_END
)

from engine.data_loader import DataLoader

loader = DataLoader()

loader.download_multiple_stocks(
    TRAIN_STOCKS,
    TRAIN_START,
    TRAIN_END
)