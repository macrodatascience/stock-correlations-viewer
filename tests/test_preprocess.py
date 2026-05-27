import polars as pl


def test_return_computation():

    df = pl.DataFrame({
        "Ticker": ["AAPL", "AAPL"],
        "Date": ["2024-01-01", "2024-01-02"],
        "Price": [100.0, 110.0],
    })

    df = (
        df.sort(["Ticker", "Date"])
        .with_columns(
            pl.col("Price")
            .pct_change()
            .over("Ticker")
            .alias("Return")
        )
    )

    assert round(df["Return"][1], 2) == 0.10