# data_fetchers/fed_fetcher.py

import os
import re
from bs4 import BeautifulSoup
from models.fed_rate_row import FedRateRow

def _month_from_date(date_text: str) -> str:
    """
    'Jul 30, 2025 ' -> 'Jul'
    """
    m = re.match(r"\s*([A-Za-z]{3})\s+\d{1,2},\s+\d{4}", (date_text or "").strip())
    return m.group(1) if m else ""

def _clean_cell_text(el) -> str:
    if el is None:
        return ""
    t = el.get_text(strip=True)
    return t if t and t != "\xa0" else ""

def fetch_fed_rows() -> list[FedRateRow]:
    """
    Parse historic Fed rate decisions from a local saved Investing.com HTML file (fed_investing.html).
    Skips placeholder rows with no Actual.
    Returns rows newest -> oldest.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "fed_investing.html")

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        table = soup.find("table", id="eventHistoryTable168")
        if not table:
            raise RuntimeError("Fed table not found (eventHistoryTable168).")

        tbody = table.find("tbody") or table
        rows = tbody.find_all("tr")

        out: list[FedRateRow] = []
        for tr in rows:
            tds = tr.find_all("td")
            # Expected: [0]=Release Date, [1]=Time, [2]=Actual, [3]=Forecast, [4]=Previous, [5]=icon
            if len(tds) < 5:
                continue

            date_text = _clean_cell_text(tds[0])
            actual = _clean_cell_text(tds[2])
            forecast = _clean_cell_text(tds[3])
            previous = _clean_cell_text(tds[4])

            # Skip upcoming placeholders where Actual is blank/N/A
            if not actual or actual.upper() == "N/A":
                continue

            out.append(FedRateRow(
                date=date_text,
                reference_month=_month_from_date(date_text),
                actual=actual,
                forecast=forecast,
                previous=previous,
                consensus=forecast,  # treat Forecast as Consensus
            ))

        return out

    except Exception as e:
        print(f"❌ Error reading local Fed HTML file: {e}")
        return []
