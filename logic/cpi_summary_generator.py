# logic/cpi_summary_generator.py

from models.cpi_report_row import CpiReportRow
from typing import Dict, Any, List, Optional

def _parse_percent(val: str) -> Optional[float]:
    """
    Convert '2.7%' -> 2.7 (float), blank/None -> None.
    """
    if not val:
        return None
    try:
        return float(val.replace("%", "").strip())
    except ValueError:
        return None

def generate_cpi_summary(cpi_rows: List[CpiReportRow]) -> Dict[str, Any]:
    """
    Generate a CPI summary comparing the latest and previous months.
    Assumes rows are sorted newest -> oldest.
    """
    if not cpi_rows or len(cpi_rows) < 2:
        raise Exception("Need at least two rows of CPI data.")

    latest = cpi_rows[0]
    previous = cpi_rows[1]

    # Parse values
    actual = _parse_percent(latest.actual)
    consensus = _parse_percent(latest.consensus)
    previous_actual = _parse_percent(previous.actual)

    # Calculate surprise and change
    surprise = (actual - consensus) if actual is not None and consensus is not None else None
    change = (actual - previous_actual) if actual is not None and previous_actual is not None else None

    # Direction commentary
    if actual is not None and previous_actual is not None:
        if actual > previous_actual:
            direction = "Headline CPI rose"
        elif actual < previous_actual:
            direction = "Headline CPI declined"
        else:
            direction = "Headline CPI remained flat"
    else:
        direction = "Headline CPI update unavailable"

    # Surprise commentary (lower-than-expected CPI = positive for markets)
    if surprise is not None:
        if surprise < 0:
            surprise_comment = f" This was a positive surprise for markets ({surprise:+.1f}pp vs forecast)."
        elif surprise > 0:
            surprise_comment = f" This was a negative surprise for markets ({surprise:+.1f}pp vs forecast)."
        else:
            surprise_comment = " CPI was exactly in line with expectations."
    else:
        surprise_comment = ""

    # Full commentary
    commentary = f"{direction} to {latest.actual} (vs {previous.actual} last month).{surprise_comment}"

    return {
        "reference_month": latest.reference_month or "N/A",
        "published_date": latest.date or "N/A",
        "headline_cpi": latest.actual or "N/A",
        "previous_cpi": previous.actual or "N/A",
        "consensus": latest.consensus or "N/A",
        "forecast": latest.forecast or "N/A",
        "surprise": f"{surprise:+.1f}pp" if surprise is not None else "N/A",
        "change_from_previous": f"{change:+.1f}pp" if change is not None else "N/A",
        "meta_commentary": commentary
    }
