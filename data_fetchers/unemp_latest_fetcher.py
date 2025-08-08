# data_fetchers/unemp_latest_fetcher.py

import re
import requests
from bs4 import BeautifulSoup
from models.unemp_row import UnempRow

INVESTING_UNEMP_URL = "https://www.investing.com/economic-calendar/unemployment-rate-300"

def _extract_reference_month(date_text: str) -> str:
    m = re.search(r"\(([^)]+)\)", date_text or "")
    return m.group(1).strip() if m else ""

def _clean_cell_text(el) -> str:
    if el is None:
        return ""
    t = el.get_text(strip=True)
    return t if t and t != "\xa0" else ""

def fetch_latest_unemp_row() -> UnempRow | None:
    """
    Fetch ONLY the most recent unemployment row (top of the table).
    Returns None if fetching/parsing fails.
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
        resp = requests.get(INVESTING_UNEMP_URL, headers=headers, timeout=12)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", id="eventHistoryTable300")
        if not table:
            print("⚠️ Unemployment table not found (eventHistoryTable300).")
            return None

        tbody = table.find("tbody")
        if not tbody:
            print("⚠️ Unemployment table has no <tbody>.")
            return None

        first_row = tbody.find("tr")
        if not first_row:
            print("⚠️ No rows found in Unemployment table.")
            return None

        tds = first_row.find_all("td")
        if len(tds) < 5:
            print("⚠️ Unexpected unemployment table structure.")
            return None

        date_text = _clean_cell_text(tds[0])
        _time = _clean_cell_text(tds[1])  # unused
        actual = _clean_cell_text(tds[2])
        forecast = _clean_cell_text(tds[3])
        previous = _clean_cell_text(tds[4])

        return UnempRow(
            date=date_text,
            reference_month=_extract_reference_month(date_text),
            actual=actual,
            forecast=forecast,
            previous=previous,
            consensus=forecast,  # using Forecast as Consensus
        )

    except Exception as e:
        print(f"❌ Error fetching latest Unemployment row: {e}")
        return None
