# data_fetchers/cpi_latest_fetcher.py

import re
import requests
from bs4 import BeautifulSoup
from models.cpi_report_row import CpiReportRow

INVESTING_CPI_URL = "https://www.investing.com/economic-calendar/cpi-733"

def _extract_reference_month(release_date_text: str) -> str:
    """
    Extracts the month inside parentheses, e.g.:
    'Aug 12, 2025  (Jul)' -> 'Jul'
    """
    m = re.search(r"\(([^)]+)\)", release_date_text or "")
    return m.group(1).strip() if m else ""

def _clean_cell_text(el) -> str:
    """Return stripped text, treating non-breaking spaces as blanks."""
    if el is None:
        return ""
    t = el.get_text(strip=True)
    return t if t and t != "\xa0" else ""

def fetch_latest_cpi_row() -> CpiReportRow | None:
    """
    Fetch ONLY the most recent CPI row from Investing.com (top row of the table).
    Returns None if fetching or parsing fails.
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
        resp = requests.get(INVESTING_CPI_URL, headers=headers, timeout=12)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the CPI table (YoY headline CPI has id 733 on Investing)
        table = soup.find("table", id="eventHistoryTable733")
        if not table:
            print("CPI table not found (eventHistoryTable733).")
            return None

        tbody = table.find("tbody")
        if not tbody:
            print("CPI table has no <tbody>.")
            return None

        first_row = tbody.find("tr")
        if not first_row:
            print("No rows found in CPI table.")
            return None

        cols = first_row.find_all("td")
        # Expected columns:
        # [0]=Release Date, [1]=Time, [2]=Actual, [3]=Forecast, [4]=Previous, [5]=icon (optional)
        if len(cols) < 5:
            print("Unexpected CPI table structure.")
            return None

        release_date = _clean_cell_text(cols[0])
        _time = _clean_cell_text(cols[1])  # not used
        actual = _clean_cell_text(cols[2])
        forecast = _clean_cell_text(cols[3])
        previous = _clean_cell_text(cols[4])

        reference_month = _extract_reference_month(release_date)

        return CpiReportRow(
            date=release_date,
            reference_month=reference_month,
            actual=actual,
            previous=previous,
            consensus=forecast,  # using Forecast as Consensus
            forecast=forecast,
        )

    except Exception as e:
        print(f"Error fetching latest CPI row: {e}")
        return None
