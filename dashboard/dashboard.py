"""Beijing Air Quality Dashboard (Streamlit).

Run from the repository root:
    streamlit run dashboard/dashboard.py
"""
import calendar
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "air_quality_daily.csv"

# All concentrations are in µg/m³
POLLUTANTS = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]

# China national standard GB 3095-2012, Grade II, 24-hour average.
# O3 is excluded: the standard uses the daily maximum 8-hour average, not a daily mean.
CHINA_LIMITS = {"PM2.5": 75, "PM10": 150, "SO2": 150, "NO2": 80, "CO": 4000}
# WHO 2021 air quality guideline, 24-hour average
WHO_LIMITS = {"PM2.5": 15}

LIMIT_COLOR = "#d1495b"
LINE_COLOR = "#2a6f97"
BAR_COLOR = "#66c2a5"

st.set_page_config(page_title="Beijing Air Quality Dashboard", page_icon="🌫️", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, parse_dates=["date"])


def show(fig) -> None:
    st.pyplot(fig)
    plt.close(fig)


def add_limit_lines(ax, pollutant: str) -> None:
    if pollutant in CHINA_LIMITS:
        ax.axhline(
            CHINA_LIMITS[pollutant], color=LIMIT_COLOR, linestyle="--", linewidth=1.2,
            label=f"China 24-h limit ({CHINA_LIMITS[pollutant]})",
        )
    if pollutant in WHO_LIMITS:
        ax.axhline(
            WHO_LIMITS[pollutant], color="gray", linestyle=":", linewidth=1.2,
            label=f"WHO 24-h guideline ({WHO_LIMITS[pollutant]})",
        )


df = load_data()

# ---------------------------------------------------------------- sidebar filters
st.sidebar.title("Filters")
pollutant = st.sidebar.selectbox("Pollutant", POLLUTANTS, index=0)

all_stations = sorted(df["station"].unique())
stations = st.sidebar.multiselect("Stations", all_stations, default=all_stations)

min_date, max_date = df["date"].min().date(), df["date"].max().date()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

st.sidebar.caption(
    "Data: Beijing Multi-Site Air-Quality Data (UCI). "
    "Daily averages of hourly readings from 12 monitoring stations."
)

# ---------------------------------------------------------------- header
st.title("Beijing Air Quality Dashboard")
st.write(
    "Which stations are most polluted, how does pollution change over time and across "
    "the seasons, and how often are daily limits exceeded? "
    "Use the filters on the left to explore."
)

if not stations:
    st.warning("Select at least one station.")
    st.stop()
if len(date_range) != 2:
    st.info("Select an end date to apply the date range.")
    st.stop()

start, end = (pd.Timestamp(d) for d in date_range)
data = df[df["station"].isin(stations) & df["date"].between(start, end)]
if data.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------------------------------------------------------------- KPIs
china_limit = CHINA_LIMITS.get(pollutant)
station_mean = data.groupby("station")[pollutant].mean().sort_values()

col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Average {pollutant} (µg/m³)", f"{data[pollutant].mean():.1f}")
if china_limit is not None:
    share_above = (data[pollutant] > china_limit).mean()
    col2.metric(f"Readings above China limit ({china_limit})", f"{share_above:.0%}")
else:
    col2.metric("Readings above limit", "n/a")
col3.metric("Most polluted station", station_mean.index[-1], f"{station_mean.iloc[-1]:.1f} µg/m³", delta_color="off")
col4.metric("Cleanest station", station_mean.index[0], f"{station_mean.iloc[0]:.1f} µg/m³", delta_color="off")
st.caption("A reading is one station's daily average. Limits apply to 24-hour averages.")

tab_station, tab_trend, tab_season = st.tabs(["Station comparison", "Trends", "Seasonality"])

# ---------------------------------------------------------------- station comparison
with tab_station:
    st.subheader(f"{pollutant} by station")
    order = data.groupby("station")[pollutant].median().sort_values().index
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.boxplot(data=data, x="station", y=pollutant, order=order, color=BAR_COLOR, fliersize=2, ax=ax)
    add_limit_lines(ax, pollutant)
    ax.set_xlabel("Station (sorted by median)")
    ax.set_ylabel(f"Daily average {pollutant} (µg/m³)")
    ax.tick_params(axis="x", rotation=45)
    if ax.get_legend_handles_labels()[0]:
        ax.legend(loc="upper left")
    fig.tight_layout()
    show(fig)

    if china_limit is not None:
        st.subheader("Share of readings above the China 24-hour limit")
        exceed = (
            data.assign(above=data[pollutant] > china_limit)
            .groupby("station")["above"].mean().mul(100).sort_values()
        )
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.barh(exceed.index, exceed.values, color=LIMIT_COLOR)
        ax.set_xlabel("% of readings above limit")
        fig.tight_layout()
        show(fig)

    st.subheader("Summary statistics")
    st.dataframe(data.groupby("station")[pollutant].describe().round(1))

# ---------------------------------------------------------------- trends
with tab_trend:
    daily = data.groupby("date")[pollutant].mean()

    st.subheader(f"Daily {pollutant} with 30-day average")
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(daily.index, daily.values, color="lightgray", linewidth=0.8, label="Daily average")
    ax.plot(daily.index, daily.rolling(30, min_periods=10).mean(), color=LINE_COLOR, linewidth=2, label="30-day average")
    add_limit_lines(ax, pollutant)
    ax.set_xlabel("Date")
    ax.set_ylabel(f"{pollutant} (µg/m³)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    show(fig)

    st.subheader(f"Monthly average {pollutant}")
    monthly = daily.resample("MS").mean()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(monthly.index, monthly.values, color=LINE_COLOR, marker="o", markersize=4)
    ax.set_xlabel("Month")
    ax.set_ylabel(f"{pollutant} (µg/m³)")
    fig.tight_layout()
    show(fig)

# ---------------------------------------------------------------- seasonality
with tab_season:
    st.subheader(f"Average {pollutant} by calendar month")
    by_month = (
        data.assign(month=data["date"].dt.month)
        .groupby("month")[pollutant].mean()
        .reindex(range(1, 13))
    )
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(calendar.month_abbr[1:], by_month.values, color=BAR_COLOR)
    ax.set_ylabel(f"Average {pollutant} (µg/m³)")
    fig.tight_layout()
    show(fig)
    st.caption("Averages combine all selected years. The dataset starts in March 2013 and ends in February 2017.")
