from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

ZIP_PATH = RAW_DIR / "stock_data.zip"

RETURNS_PATH = PROCESSED_DIR / "returns.parquet"

# Minimum ratio of historical data points required for a ticker to be included in the analysis. 
# This helps ensure that correlations are based on sufficient data and not skewed by tickers with sparse histories.
MIN_HISTORY_RATIO = 0.95

# Maximum absolute return to consider valid. This helps filter out data errors and extreme outliers that can skew correlations.
MAX_ABS_RETURN = 0.50

# Threshold for number of unique prices on a given date to consider it valid. 
# 5% of the ticker universe is a reasonable threshold to filter out days with data issues (e.g. holidays, outages).
FROZEN_PRICE_THRESHOLD = 250

# Default rolling window size in days for correlation calculations. Adjust based on typical market cycles and for desired insights.
DEFAULT_ROLLING_WINDOW = 20    

# Limit the number of tickers in the dashboard to prevent crowded visualizations and poor correlations readability
MAX_TICKERS = 10               