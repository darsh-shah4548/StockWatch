# data_fetchers/cpi_fetcher.py

import os
import re
from bs4 import BeautifulSoup
from models.cpi_report_row import CpiReportRow

def _extract_reference_month(release_date_text: str) -> str:
    """
    Extracts the month inside parentheses from strings like:
    'Aug 12, 2025  (Jul)' -> 'Jul'
    Returns '' if not found.
    """
    m = re.search(r"\(([^)]+)\)", release_date_text or "")
    return m.group(1).strip() if m else ""

def _clean_cell_text(el) -> str:
    """Get stripped text, return '' for blanks like &nbsp;"""
    if el is None:
        return ""
    t = el.get_text(strip=True)
    return t if t != "\xa0" else ""

def fetch_cpi_rows() -> list[CpiReportRow]:
    try:
        # Path to local HTML (same folder as this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, "cpi_investing.html")

        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Be specific to avoid grabbing the wrong table
        table = soup.find("table", id="eventHistoryTable733") or soup.find("table")
        if not table:
            raise RuntimeError("CPI table not found in HTML.")

        tbody = table.find("tbody") or table
        rows = tbody.find_all("tr")

        results: list[CpiReportRow] = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            actual_value = _clean_cell_text(cols[2])

            # Skip upcoming forecast row with no actual value
            if not actual_value or actual_value.upper() == "N/A":
                continue

            release_date = _clean_cell_text(cols[0])
            forecast = _clean_cell_text(cols[3])
            previous = _clean_cell_text(cols[4])

            reference_month = _extract_reference_month(release_date)

            results.append(
                CpiReportRow(
                    date=release_date,
                    reference_month=reference_month,
                    actual=actual_value,
                    previous=previous,
                    consensus=forecast,
                    forecast=forecast,
                )
            )


        return results

    except Exception as e:
        print(f"❌ Error reading local HTML file: {e}")
        return []
