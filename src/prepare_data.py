"""Build the compact daily dataset used by the dashboard.

Input : data/raw/all_data.csv (hourly readings, one row per station-hour; needs the
        columns station, year, month, day and the pollutant columns below)
Output: data/air_quality_daily.csv (daily mean per station and pollutant)

Run from the repository root:
    python src/prepare_data.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "all_data.csv"
OUT_PATH = ROOT / "data" / "air_quality_daily.csv"

POLLUTANTS = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]


def main() -> None:
    usecols = ["station", "year", "month", "day", *POLLUTANTS]
    hourly = pd.read_csv(RAW_PATH, usecols=usecols)

    hourly["date"] = pd.to_datetime(hourly[["year", "month", "day"]])

    # Missing hourly values (if any) are ignored when averaging
    daily = (
        hourly.groupby(["station", "date"], as_index=False)[POLLUTANTS]
        .mean()
        .sort_values(["station", "date"])
    )
    daily[POLLUTANTS] = daily[POLLUTANTS].round(2)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(OUT_PATH, index=False)
    print(f"{len(hourly):,} hourly rows -> {len(daily):,} station-days saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
