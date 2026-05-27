import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import streamlit as st
import plotly.express as px

from src.config import (
    RETURNS_PATH,
    DEFAULT_ROLLING_WINDOW,
    MAX_TICKERS,
)

from src.analytics import (
    load_returns_lazy,
    get_available_tickers,
    build_window_matrix,
    build_pairwise_correlation_series
)

# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------

st.set_page_config(
    page_title="Rolling Correlations",
    layout="wide",
)

st.title("Rolling Correlations Dashboard")

# ---------------------------------------------------------
# LOAD LAZYFRAME
# ---------------------------------------------------------

@st.cache_resource
def load_data():

    return load_returns_lazy(RETURNS_PATH)

lf = load_data()

# ---------------------------------------------------------
# TICKERS
# ---------------------------------------------------------

tickers = sorted(get_available_tickers(lf))

if "selected_tickers" not in st.session_state:
    st.session_state.selected_tickers = tickers[:5]
    
selected = st.sidebar.multiselect(
    "Tickers",
    options = tickers,
    default=st.session_state.selected_tickers,
    key="selected_tickers",
    max_selections=MAX_TICKERS,
)

if len(selected) == 0:
    st.warning("Select at least one ticker.")
    st.stop()
    
# ---------------------------------------------------------
# DATE RANGE
# ---------------------------------------------------------

dates = (
    lf.select("Date")
    .unique()
    .collect()
    .to_series()
    .sort()
    .to_list()
)

end_date = st.sidebar.selectbox(
    "End Date",
    dates,
    index=len(dates)-1,
)

window = st.sidebar.slider(
    "Rolling Window",
    5,
    100,
    DEFAULT_ROLLING_WINDOW,
)

# ---------------------------------------------------------
# BUILD SELECTED TICKER RETURNS MATRIX IN WIDE FORMAT
# ---------------------------------------------------------

wide = build_window_matrix(
    lf,
    selected,
    end_date,
    window,
)

# ---------------------------------------------------------
# COMPUTE CORRELATIONS ON THE SELECTED SUBSET
# ---------------------------------------------------------

pdf = (
    wide
    .drop("Date")
    .to_pandas()
)

corr = pdf.corr()
corr_display = corr.round(3)

# ---------------------------------------------------------
# CORRELATION ANALYSIS SUMMARY
# ---------------------------------------------------------

window_start = wide["Date"].min()
window_end = wide["Date"].max()

full_start = min(dates)
full_end = max(dates)

col1, col2, col3 = st.columns(3)

col1.metric(
    f"**Window Start**",
    str(window_start),
)

col2.metric(
    f"**Window End**",
    str(window_end),
)

col3.metric(
    f"**Stocks**",
    len(selected),
)

st.caption(
    f"""
    ***Correlation Basis***:  {window}-day rolling window using the computed historical daily returns

    ***Full Available Date Range***:  {full_start} → {full_end}
    """
)

# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

fig = px.imshow(
    corr_display,
    text_auto=True,
    aspect="auto",
    title=f"{window}-Day Rolling Correlations",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.dataframe(corr_display)

# ---------------------------------------------------------
# ROLLING PAIRWISE CORRELATION
# ---------------------------------------------------------

st.subheader("Rolling Pairwise Correlation")

if len(selected) < 2:
    st.warning("Select at least 2 tickers.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    ticker_a = st.selectbox(
        "Ticker A",
        selected,
        index=0,
    )

with col2:
    ticker_b = st.selectbox(
        "Ticker B",
        selected,
        index=min(1, len(selected)-1),
    )

if ticker_a == ticker_b:
    st.warning("Choose two different tickers.")


rolling_series = build_pairwise_correlation_series(
    lf,
    ticker_a,
    ticker_b,
    end_date,
    window,
)

fig_line = px.line(
    x=rolling_series.index,
    y=rolling_series.values,
    labels={
        "x": "Date",
        "y": "Correlation",
    },
    title=(
        f"{window}-Day Historical Rolling Correlation: "
        f"{ticker_a} vs {ticker_b}"
    ),
)

fig_line.update_layout(
    yaxis_range=[-1, 1]
)

st.plotly_chart(
    fig_line,
    use_container_width=True,
)