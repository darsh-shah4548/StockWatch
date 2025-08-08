# data_fetchers/unemp_fetcher.py

import os
import re
from bs4 import BeautifulSoup
from models.unemp_row import UnempRow

def _extract_reference_month(date_text: str) -> str:
    # 'Aug 01, 2025  (Jul)' -> 'Jul'
    m = re.search(r"\(([^)]+)\)", date_text or "")
    return m.group(1).strip() if m else ""

def _clean_cell_text(el) -> str:
    if el is None:
        return ""
    t = el.get_text(strip=True)
    return t if t and t != "\xa0" else ""

def fetch_unemp_rows() -> list[UnempRow]:
    """
    Parse unemployment rate history from local saved HTML (unemp_investing.html).
    Skips rows where Actual is blank/N/A (upcoming placeholders).
    Returns newest -> oldest.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "unemp_investing.html")

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        table = soup.find("table", id="eventHistoryTable300")
        if not table:
            raise RuntimeError("Unemployment table not found (eventHistoryTable300).")

        tbody = table.find("tbody") or table
        rows = tbody.find_all("tr")

        out: list[UnempRow] = []
        for tr in rows:
            tds = tr.find_all("td")
            # [0]=Release Date, [1]=Time, [2]=Actual, [3]=Forecast, [4]=Previous, [5]=icon
            if len(tds) < 5:
                continue

            date_text = _clean_cell_text(tds[0])
            actual = _clean_cell_text(tds[2])
            forecast = _clean_cell_text(tds[3])
            previous = _clean_cell_text(tds[4])

            # Skip placeholders (no actual yet)
            if not actual or actual.upper() == "N/A":
                continue

            out.append(UnempRow(
                date=date_text,
                reference_month=_extract_reference_month(date_text),
                actual=actual,
                forecast=forecast,
                previous=previous,
                consensus=forecast,  # treat Forecast as Consensus
            ))

        return out

    except Exception as e:
        print(f"❌ Error reading local Unemployment HTML file: {e}")
        return []
