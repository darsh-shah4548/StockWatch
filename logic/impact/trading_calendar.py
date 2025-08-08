# logic/impact/trading_calendar.py
import pandas as pd

def to_ny_date(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.replace(r"\s*\(.*\)", "", regex=True)
    return pd.to_datetime(cleaned, errors="coerce").dt.tz_localize("America/New_York").dt.normalize()

def next_trading_day(d: pd.Timestamp, ivv_index: pd.DatetimeIndex) -> pd.Timestamp | None:
    """
    Map a datetime to the next trading day present in ivv_index.
    Returns None if d is after the last available trading day.
    """
    if pd.isna(d):
        return None

    if d.tzinfo is None:
        d = d.tz_localize("America/New_York").normalize()
    else:
        d = d.tz_convert("America/New_York").normalize()

    # If the requested date is beyond our price history, bail out
    last = ivv_index.max()
    if d > last:
        return None

    while d not in ivv_index:
        d = (d + pd.Timedelta(days=1)).normalize()
        if d > last:
            return None
    return d
