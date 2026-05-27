import zipfile
import polars as pl

from src.config import (
    ZIP_PATH,
    RETURNS_PATH,
    MIN_HISTORY_RATIO,
    MAX_ABS_RETURN,
    FROZEN_PRICE_THRESHOLD,
)


def build_returns_from_zip(zip_path) -> pl.DataFrame:
    """
    Build a cleaned daily returns dataset from zipped stock price CSV files.

    The function:
    - loads all CSV files from a ZIP archive
    - cleans and validates ticker, date, and price fields
    - removes invalid, null, and duplicate rows
    - filters tickers with insufficient historical coverage
    - removes frozen market days with unusually low price variation
    - computes daily percentage returns per ticker
    - filters extreme return outliers

    Parameters
    ----------
    zip_path : str | Path
        Path to the ZIP archive containing stock CSV files.

    Returns
    -------
    pl.DataFrame
        Polars DataFrame containing:

        - Date   : trading date
        - Ticker : stock ticker
        - Return : daily percentage return

    Notes
    -----
    The output is intended for rolling correlation analysis and lightweight interactive pairwise visualizations.
    """
    
    frames = []

    with zipfile.ZipFile(zip_path) as z:

        for file in z.namelist():

            if not file.endswith(".csv"):
                continue

            with z.open(file) as f:

                df = pl.read_csv(
                    f,
                    schema={
                        "Ticker": pl.Utf8,
                        "Date": pl.Utf8,
                        "Price": pl.Float64,
                    },
                )

                df = (
                    df.rename({c: c.strip() for c in df.columns})
                    .with_columns([
                        pl.col("Ticker")
                        .cast(pl.Utf8)
                        .str.strip_chars()
                        .cast(pl.Categorical),

                        pl.col("Date")
                        .cast(pl.Utf8)
                        .str.strip_chars()
                        .str.replace_all(r"\s+", "")
                        .str.strptime(
                            pl.Date,
                            "%Y-%m-%d",
                            strict=False,
                        ),

                        pl.col("Price").cast(pl.Float64),
                    ])
                    .filter(
                        pl.col("Ticker").is_not_null()
                        & pl.col("Date").is_not_null()
                        & pl.col("Price").is_not_null()
                        & (pl.col("Price") > 0)
                    )
                    .unique(
                        subset=["Ticker", "Date"],
                        keep="last",
                    )
                )

                if df.height > 0:
                    frames.append(df)

    if not frames:
        raise ValueError("No valid CSV data found in ZIP file.")

    prices = pl.concat(frames)

    expected_days = (
        prices
        .select("Date")
        .unique()
        .height
    )

    coverage = (
        prices
        .group_by("Ticker")
        .agg(
            pl.col("Date")
            .n_unique()
            .alias("days")
        )
        .with_columns(
            (
                pl.col("days") / expected_days
            ).alias("coverage_ratio")
        )
    )

    valid_tickers = coverage.filter(
        pl.col("coverage_ratio") >= MIN_HISTORY_RATIO
    ).select("Ticker")

    prices = prices.join(
        valid_tickers,
        on="Ticker",
        how="inner",
    )

    bad_dates = (
        prices
        .group_by("Date")
        .agg(
            pl.n_unique("Price")
            .alias("unique_prices")
        )
        .filter(
            pl.col("unique_prices") <= FROZEN_PRICE_THRESHOLD
        )
        .select("Date")
    )

    prices = prices.join(
        bad_dates,
        on="Date",
        how="anti",
    )

    prices = (
        prices
        .sort(["Ticker", "Date"])
        .with_columns(
            pl.col("Price")
            .pct_change()
            .over("Ticker")
            .alias("Return")
        )
    )

    prices = prices.filter(
        pl.col("Return").is_null()
        | (pl.col("Return").abs() < MAX_ABS_RETURN)
    )

    returns = prices.select([
        "Date",
        "Ticker",
        "Return",
    ])

    return returns


def main():
    returns = build_returns_from_zip(ZIP_PATH)

    RETURNS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    returns.write_parquet(
        RETURNS_PATH,
        compression="zstd",
    )

    print("DONE")
    print(returns.shape)
    print(f"Saved to: {RETURNS_PATH}")


if __name__ == "__main__":
    main()