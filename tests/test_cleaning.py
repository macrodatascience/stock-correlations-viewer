import polars as pl


def test_remove_null_dates():

    df = pl.DataFrame({
        "Ticker": ["AAPL", "MSFT"],
        "Date": ["2024-01-01", None],
        "Price": [100.0, 200.0],
    })

    cleaned = df.filter(
        pl.col("Date").is_not_null()
    )

    assert cleaned.height == 1