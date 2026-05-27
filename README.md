# Stock Correlations Viewer

A lightweight Streamlit app for viewing rolling stock return correlations based on the given stock_data.zip file.

The app preprocesses historical stock price data, computes daily returns, and displays:

- correlation heatmap based on the rolling window
- correlation table
- pairwise correlation chart based on the rolling window 

---

## Project Structure

```text
STOCK-CORRELATIONS-VIEWER/
│
├── data/
│   ├── raw/
│   │   └── stock_data.zip
│   └── processed/
│       └── returns.parquet
│
├── src/
│   ├── config.py
│   ├── preprocess.py
│   ├── analytics.py
│   └── __init__.py
│
├── app/
│   ├── streamlit_app.py
│   └── __init__.py
│
├── tests/
│   ├── test_preprocess.py
│   ├── test_cleaning.py
│   ├── test_analytics.py
│   ├── test_pairwise_corr.py
│   └── __init__.py
├── requirements.txt
└── README.md
```

---

## Architecture

```text
Raw STOCK_DATA.ZIP CSV files
        ↓
src/preprocess.py
        ↓
Clean prices + compute daily returns
        ↓
data/processed/returns.parquet
        ↓
src/analytics.py
        ↓
Streamlit dashboard
```

The dashboard uses Polars `LazyFrame` through `scan_parquet()` so the app only loads the selected tickers and rolling window needed for the current view.

---

## Input Data

Place the input ZIP file here:

```text
data/raw/stock_data.zip
```

Each CSV inside the ZIP should contain:

```text
Ticker,Date,Price
AAPL,2024-01-01,185.64
MSFT,2024-01-01,370.21
```

Required columns:

| Column | Description |
|---|---|
| `Ticker` | Stock ticker |
| `Date` | Trading date in `YYYY-MM-DD` format |
| `Price` | Stock price |

---

## Setup

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Preprocess Data

Run this once before starting the app:

```bash
python -m src.preprocess
```

This creates:

```text
data/processed/returns.parquet
```

---

## Run the App

From the project root:

```bash
streamlit run app/streamlit_app.py
```

---

## App Features

### Rolling Correlations Heatmap

Shows the correlation matrix for selected tickers over the selected rolling window.

### Correlations Table

Shows the same correlations in numeric table format.

### Rolling Pairwise Correlation

Shows how the correlation between two selected tickers evolves over time.

---

## Configuration

Edit settings in:

```text
src/config.py
```

Important settings:

```python
MIN_HISTORY_RATIO = 0.95
MAX_ABS_RETURN = 0.50
FROZEN_PRICE_THRESHOLD = 250
DEFAULT_ROLLING_WINDOW = 20
MAX_TICKERS = 10
```

Meaning:

|           Setting        |                   Purpose                              |
|--------------------------|--------------------------------------------------------|
| `MIN_HISTORY_RATIO`      | Keeps only tickers with sufficient historical coverage |
| `MAX_ABS_RETURN`         | Removes extreme daily return outliers                  |
| `FROZEN_PRICE_THRESHOLD` | Detects suspicious frozen market days                  |
| `DEFAULT_ROLLING_WINDOW` | Default rolling correlation window                     |
| `MAX_TICKERS`            | Maximum tickers allowed in heatmap                     |

---

## Run Tests

```bash
pytest -v tests
```

---

## Notes

This project is intentionally made lightweight.

It avoids building a full global correlation matrix for all stocks. Instead, it:

1. preprocesses returns once
2. stores them as Parquet
3. lazily reads the returns data
4. computes correlations only on the selected tickers for the specific rolling window

This keeps the dashboard responsive and memory-efficient.