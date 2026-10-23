# Beijing Air Quality Dashboard

Interactive Streamlit dashboard that compares air quality across 12 Beijing monitoring stations, shows how pollution changes over time and by season, and tracks how often daily readings exceed national and WHO limits.

**Live demo:** [https://arwendy-beijing-air-quality.streamlit.app/](https://arwendy-beijing-air-quality.streamlit.app/)

<!-- ![Dashboard preview](images/dashboard_preview.png) -->
    
## Questions the dashboard answers

1. **Which stations are the most polluted?** Boxplots, a ranking of stations, and summary statistics for any pollutant.
2. **How does pollution change over time?** Daily readings with a 30-day average, plus monthly averages.
3. **When is air quality worst?** Average level by calendar month.
4. **How often are daily limits exceeded?** Share of readings above the China national 24-hour limit (and the WHO guideline for PM2.5).

Filters: pollutant (PM2.5, PM10, SO2, NO2, CO, O3), stations, and date range.

## Key Findings (PM2.5)

- The average daily PM2.5 across all stations is **79.7 µg/m³**. **40.4%** of station-days exceed China's 24-hour limit (75 µg/m³) and **91.4%** exceed the WHO guideline (15 µg/m³).
- **Stations differ by about 30%.** Dongsi has the highest average (86.0 µg/m³, 43.3% of days above the China limit) and Dingling the lowest (66.4 µg/m³, 32.3%). The three lowest stations (Dingling, Huairou, Changping) are all in the outer northern districts.
- **Pollution is strongly seasonal.** Winter (Dec-Feb) averages 95.4 µg/m³ versus 64.7 µg/m³ in summer (Jun-Aug), about 47% higher. December is the worst month (103.9) and August the best (53.5). This is consistent with winter heating and weaker dispersion, but this dataset alone cannot show the cause.
- **The yearly trend is not monotonic.** Averaged over March-February years, PM2.5 fell from 86.8 (2013-14) to 81.1 (2014-15) and 73.1 (2015-16), then rose to 77.9 (2016-17).
- The highest single daily reading is **567.4 µg/m³** (Dongsi, 25 December 2015).

## Data

- **Source:** [Beijing Multi-Site Air-Quality Data](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data) (UCI Machine Learning Repository). Citation: Zhang, S., Guo, B., Dong, A., He, J., Xu, Z. and Chen, S.X. (2017). *Cautionary tales on air-quality improvement in Beijing.* Proceedings of the Royal Society A, 473, 20170457.
- **Coverage:** 12 national monitoring stations, hourly readings from 1 March 2013 to 28 February 2017 (420,768 hourly rows).
- **Used in the dashboard:** `data/air_quality_daily.csv`, the daily average per station and pollutant (17,532 station-days, about 1 MB). Daily averages match how the China and WHO 24-hour limits are defined, and keep the app fast.
- All concentrations are in µg/m³.

### Reference limits used

| Pollutant | China GB 3095-2012, Grade II (24-hour) | WHO 2021 guideline (24-hour) |
|---|---|---|
| PM2.5 | 75 | 15 |
| PM10 | 150 | not shown |
| SO2 | 150 | not shown |
| NO2 | 80 | not shown |
| CO | 4,000 | not shown |
| O3 | not shown (the standard uses the daily maximum 8-hour average) | not shown |

## Repository Structure

```
├── dashboard/
│   └── dashboard.py          # Streamlit app
├── data/
│   ├── air_quality_daily.csv # daily data used by the app
│   └── raw/                  # hourly file (not committed, see below)
├── src/
│   └── prepare_data.py       # hourly -> daily
├── images/
├── requirements.txt
└── README.md
```

## How to Run

```bash
git clone https://github.com/arwendy123/beijing-air-quality-dashboard.git
cd beijing-air-quality-dashboard
pip install -r requirements.txt
streamlit run dashboard/dashboard.py
```

### Rebuild the daily data (optional)

The hourly file is about 49 MB and is not committed. To rebuild `air_quality_daily.csv`, put the merged hourly data in `data/raw/all_data.csv` (columns: `station`, `year`, `month`, `day`, `PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`) and run:

```bash
python src/prepare_data.py
```

Missing hourly values, if any, are ignored when computing daily averages.

## Limitations

- Four years of data; the first and last years are partial, so calendar-year comparisons are not used.
- Limits apply to 24-hour averages. Station-day readings are compared with the limit, which is not the same as the official compliance calculation (annual averages and percentile rules).
- Seasonal and station differences are descriptive. The data has no information on emissions sources or weather in the daily file.

## Tools

Python, Pandas, Matplotlib, Seaborn, Streamlit