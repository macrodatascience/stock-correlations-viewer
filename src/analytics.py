import polars as pl
import pandas as pd


def load_returns_lazy(path):
    """
    Lazily load the returns parquet dataset.

    Parameters
    ----------
    path : str | Path
        Path to the generated returns.parquet file.

    Returns
    -------
    pl.LazyFrame
        LazyFrame containing returns data.
    """
    
    return pl.scan_parquet(path)


def get_available_tickers(lf):
    """
    Retrieve the list of unique tickers available in the dataset.

    Parameters
    ----------
    lf : pl.LazyFrame
        LazyFrame containing returns data.

    Returns
    -------
    list[str]
        Sorted list of available stock tickers.
    """
    
    return (
        lf.select("Ticker")
        .unique()
        .collect()
        .to_series()
        .to_list()
    )


def build_window_matrix(
    lf,
    tickers,
    end_date,
    window,
):
    """
    Build a rolling-window wide returns matrix for selected tickers.

    The resulting matrix is pivoted into wide format:
    rows represent dates and columns represent tickers.

    Parameters
    ----------
    lf : pl.LazyFrame
        LazyFrame containing returns data.

    tickers : list[str]
        Selected tickers to include.

    end_date : date
        Final date of the rolling analysis window.

    window : int
        Number of trading days in the rolling window.

    Returns
    -------
    pl.DataFrame
        Wide-format returns matrix with dates as rows
        and tickers as columns.
    """

    filtered = (
        lf.filter(
            pl.col("Ticker")
            .is_in(tickers)
        )
        .filter(
            pl.col("Date") <= end_date
        )
        .collect()
    )

    recent_dates = (
        filtered
        .select("Date")
        .unique()
        .sort("Date")
        .tail(window)
    )

    filtered = filtered.join(
        recent_dates,
        on="Date",
        how="inner",
    )

    wide = (
        filtered
        .pivot(
            values="Return",
            index="Date",
            on="Ticker",
            aggregate_function="first",
        )
        .sort("Date")
        .drop_nulls()
    )

    return wide


def build_pairwise_correlation_series(
    lf,
    ticker_a,
    ticker_b,
    end_date,
    window,
):
    """
    Compute the rolling correlation series between two tickers.

    Parameters
    ----------
    lf : pl.LazyFrame
        LazyFrame containing returns data.

    ticker_a : str
        First ticker.

    ticker_b : str
        Second ticker.

    end_date : date
        Final date of the analysis period.

    window : int
        Rolling correlation window length.

    Returns
    -------
    pandas.Series
        Rolling correlation values indexed by date.
    """
    
    df = (
        lf.filter(
            pl.col("Ticker").is_in([ticker_a, ticker_b])
        )
        .filter(
            pl.col("Date") <= end_date
        )
        .collect()
    )

    wide = (
        df.pivot(
            values="Return",
            index="Date",
            on="Ticker",
            aggregate_function="first",
        )
        .sort("Date")
        .drop_nulls()
    )

    pdf = (
        wide
        .to_pandas()
        .set_index("Date")
    )

    rolling_corr = (
        pdf[ticker_a]
        .rolling(window)
        .corr(pdf[ticker_b])
    )

    return rolling_corr.dropna()