# data_fetchers/job_latest_fetcher.py

import re
import requests
from bs4 import BeautifulSoup
from models.job_report import JobReportRow

INVESTING_JOBS_URL = "https://www.investing.com/economic-calendar/nonfarm-payrolls-227"

def _extract_reference_month(date_text: str) -> str:
    """
    Extracts the month abbreviation from strings like:
    'Aug 02, 2024  (Jul)' -> 'Jul'
    """
    m = re.search(r"\(([^)]+)\)", date_text or "")
    return m.group(1).strip() if m else ""

def _clean_cell_text(el) -> str:
    """Return stripped cell text, handling &nbsp; as blank."""
    if el is None:
        return ""
    t = el.get_text(strip=True)
    return t if t != "\xa0" else ""

def fetch_latest_job_row() -> JobReportRow | None:
    """
    Fetches ONLY the most recent NFP (jobs) row from Investing.com.
    Returns None if fetching or parsing fails.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            )
        }
        resp = requests.get(INVESTING_JOBS_URL, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        table = soup.find("table", {"id": "eventHistoryTable227"})
        if not table:
            print("⚠️ Could not find NFP table with id 'eventHistoryTable227'.")
            return None

        first_row = table.find("tbody").find("tr")
        if not first_row:
            print("⚠️ No rows found in NFP table.")
            return None

        cells = first_row.find_all("td")
        if len(cells) < 5:
            print("⚠️ Unexpected NFP table structure.")
            return None

        date_text = _clean_cell_text(cells[0])
        reference_month = _extract_reference_month(date_text)
        actual = _clean_cell_text(cells[2])
        forecast = _clean_cell_text(cells[3])
        previous = _clean_cell_text(cells[4])

        return JobReportRow(
            date=date_text,
            reference=reference_month,
            actual=actual,
            forecast=forecast,
            previous=previous,
            consensus=forecast,  # Using forecast as consensus
        )

    except Exception as e:
        print(f"❌ Error fetching latest job row: {e}")
        return None
