import polars as pl

from src.analytics import (
    build_pairwise_correlation_series
)

def test_pairwise_correlation_series():

    df = pl.DataFrame({
        "Date": [
            "2024-01-01",
            "2024-01-01",
            "2024-01-02",
            "2024-01-02",
            "2024-01-03",
            "2024-01-03",
        ],

        "Ticker": [
            "AAPL",
            "MSFT",
            "AAPL",
            "MSFT",
            "AAPL",
            "MSFT",
        ],

        "Return": [
            0.01,
            0.02,
            0.03,
            0.04,
            0.05,
            0.06,
        ],
    }).with_columns(
        pl.col("Date").str.strptime(pl.Date)
    )

    lf = df.lazy()

    out = build_pairwise_correlation_series(
        lf=lf,
        ticker_a="AAPL",
        ticker_b="MSFT",
        end_date=df["Date"].max(),
        window=2,
    )

    assert len(out) > 0