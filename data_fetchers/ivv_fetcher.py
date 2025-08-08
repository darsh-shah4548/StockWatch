# data_fetchers/ivv_fetcher.py
import os
from datetime import datetime
import pandas as pd
import yfinance as yf

def get_ivv_prices(start: str = "2018-01-01",
                   end: str | None = None,
                   cache_path: str = "data/ivv_prices.csv") -> pd.DataFrame:
    """
    Download (or load cached) IVV daily prices (auto-adjusted).
    Index is normalized to America/New_York midnight.
    """
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    if end is None:
        end = datetime.utcnow().date().isoformat()

    # Load cache if it exists and already covers the requested window
    if os.path.isfile(cache_path):
        try:
            cached = pd.read_csv(cache_path, parse_dates=["Date"])
            cached["Date"] = (
                cached["Date"]
                .dt.tz_localize("UTC")
                .dt.tz_convert("America/New_York")
                .dt.normalize()
            )
            cached.set_index("Date", inplace=True)
            if cached.index.min().date().isoformat() <= start and cached.index.max().date().isoformat() >= end:
                return cached
        except Exception:
            pass  # fall through to re-download if cache is broken

    # Download fresh
    df = yf.download("IVV", start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError("No IVV data downloaded.")

    # Normalize index to NY time midnight for easy merging with event dates
    df.index = (
        pd.to_datetime(df.index)
        .tz_localize("UTC")
        .tz_convert("America/New_York")
        .normalize()
    )

    # Save cache
    out = df.reset_index().rename(columns={"index": "Date"})
    out.to_csv(cache_path, index=False)

    return df

if __name__ == "__main__":
    ivv = get_ivv_prices()
    print(ivv.tail())
