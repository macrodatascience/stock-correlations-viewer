import polars as pl

from src.analytics import build_window_matrix


def test_build_window_matrix():

    df = pl.DataFrame({
        "Date": [
            "2024-01-01",
            "2024-01-01",
            "2024-01-02",
            "2024-01-02",
        ],
        "Ticker": [
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
        ],
    }).with_columns(
        pl.col("Date").str.strptime(pl.Date)
    )

    lf = df.lazy()

    out = build_window_matrix(
        lf=lf,
        tickers=["AAPL", "MSFT"],
        end_date=df["Date"].max(),
        window=2,
    )

    assert out.height == 2
    assert "AAPL" in out.columns
    assert "MSFT" in out.columns
    assert "NVDA" not in out.columns