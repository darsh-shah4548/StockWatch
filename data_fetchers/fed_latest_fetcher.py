# data_fetchers/fed_latest_fetcher.py

import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from models.fed_rate_row import FedRateRow

INVESTING_FED_URL = "https://www.investing.com/economic-calendar/interest-rate-decision-168"

def _month_from_date(date_text: str) -> str:
    m = re.match(r"\s*([A-Za-z]{3})\s+\d{1,2},\s+\d{4}", (date_text or "").strip())
    return m.group(1) if m else ""

def _parse_date(date_text: str) -> datetime | None:
    if not date_text:
        return None
    s = date_text.strip()
    # Normalize multiple spaces
    s = re.sub(r"\s+", " ", s)
    for fmt in ("%b %d, %Y",):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def _clean_cell_text(el) -> str:
    if el is None:
        return ""
    t = el.get_text(strip=True)
    return t if t and t != "\xa0" else ""

def fetch_latest_fed_row() -> FedRateRow | None:
    """
    Choose the next upcoming Fed meeting (soonest future date) if Actual is blank.
    Otherwise choose the most recent past meeting (has Actual).
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get(INVESTING_FED_URL, headers=headers, timeout=12)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", id="eventHistoryTable168")
        if not table:
            print("⚠️ Fed table not found (eventHistoryTable168).")
            return None

        tbody = table.find("tbody")
        if not tbody:
            print("⚠️ Fed table has no <tbody>.")
            return None

        rows = tbody.find_all("tr")
        if not rows:
            print("⚠️ No rows found in Fed table.")
            return None

        # Collect candidates with parsed dates
        future = []  # rows with no Actual (upcoming)
        past = []    # rows with Actual
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 5:
                continue

            date_text = _clean_cell_text(tds[0])
            dt = _parse_date(date_text)
            if not dt:
                continue

            _time = _clean_cell_text(tds[1])  # unused
            actual = _clean_cell_text(tds[2])
            forecast = _clean_cell_text(tds[3])
            previous = _clean_cell_text(tds[4])

            record = {
                "date_text": date_text,
                "dt": dt,
                "actual": actual,
                "forecast": forecast,
                "previous": previous,
            }

            if actual and actual.upper() != "N/A":
                past.append(record)
            else:
                future.append(record)

        # Pick soonest future if available; else most recent past
        chosen = None
        if future:
            chosen = min(future, key=lambda r: r["dt"])
        elif past:
            chosen = max(past, key=lambda r: r["dt"])
        else:
            print("⚠️ No valid Fed rows after parsing.")
            return None

        return FedRateRow(
            date=chosen["date_text"],
            reference_month=_month_from_date(chosen["date_text"]),
            actual=chosen["actual"],
            forecast=chosen["forecast"],
            previous=chosen["previous"],
            consensus=chosen["forecast"],
        )

    except Exception as e:
        print(f"❌ Error fetching latest Fed row: {e}")
        return None
