# logic/impact/returns.py
import pandas as pd
from .trading_calendar import to_ny_date, next_trading_day

def load_ivv_prices(ivv_csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(ivv_csv_path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
    df = df.dropna(subset=["Date"])
    df["Date"] = df["Date"].dt.tz_convert("America/New_York").dt.normalize()
    if "Close" not in df.columns:
        raise ValueError("IVV CSV missing 'Close' column after parsing.")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df[["Date", "Close"]].dropna().sort_values("Date").reset_index(drop=True)
    return df

def attach_returns_df(events: pd.DataFrame, ivv_df: pd.DataFrame, release_col: str = "release_date") -> pd.DataFrame:
    ivv = ivv_df.copy().set_index("Date")
    events = events.copy()

    events[release_col] = to_ny_date(events[release_col])
    ivv_index = ivv.index

    t0_list, t1_list, same_list, next_list = [], [], [], []
    for d in events[release_col]:
        t0 = next_trading_day(d, ivv_index)
        t0_list.append(t0)

        if t0 is None:
            # Future event beyond available prices
            t1_list.append(None)
            same_list.append(None)
            next_list.append(None)
            continue

        # prior close
        try:
            prev_idx = ivv_index.get_loc(t0) - 1
            prev_close = ivv.iloc[prev_idx]["Close"]
        except Exception:
            prev_close = None

        # next trading day
        t1 = next_trading_day(t0 + pd.Timedelta(days=1), ivv_index)
        t1_list.append(t1)

        # same-day and next-day returns
        try:
            close_t0 = ivv.loc[t0, "Close"]
            same_ret = (close_t0 / prev_close) - 1 if prev_close is not None else None
        except Exception:
            same_ret = None

        try:
            close_t1 = ivv.loc[t1, "Close"] if t1 is not None else None
            next_ret = (close_t1 / close_t0) - 1 if (close_t1 is not None and close_t0 is not None) else None
        except Exception:
            next_ret = None

        same_list.append(same_ret)
        next_list.append(next_ret)

    events["ivv_same_day_return"] = same_list
    events["ivv_next_day_return"] = next_list
    events["t0"] = t0_list
    events["t1"] = t1_list

    # Optional: drop rows we couldn’t price (future events)
    events = events[events["t0"].notna()].reset_index(drop=True)

    return events

