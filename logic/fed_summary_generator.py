# logic/fed_summary_generator.py

from typing import List, Dict, Any, Optional
from models.fed_rate_row import FedRateRow

def _parse_pct(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    try:
        return float(val.replace("%", "").strip())
    except Exception:
        return None

def generate_fed_rate_summary(rate_rows: List[FedRateRow]) -> Dict[str, Any]:
    """
    Expects newest -> oldest rows.
    Uses previous row's *actual* as prior policy rate when available.
    """
    if not rate_rows or len(rate_rows) < 2:
        raise ValueError("Need at least two rows of data")

    latest = rate_rows[0]
    prev = rate_rows[1]

    actual = _parse_pct(latest.actual)                 # e.g., 4.50
    forecast = _parse_pct(latest.forecast)             # e.g., 4.50
    prev_actual = _parse_pct(prev.actual)              # preferred "previous" comparator
    # Fallback to the "Previous" column on latest row if prev.actual is missing
    if prev_actual is None:
        prev_actual = _parse_pct(latest.previous)

    # Compute deltas
    change_val = (actual - prev_actual) if (actual is not None and prev_actual is not None) else None
    surprise_val = (actual - forecast) if (actual is not None and forecast is not None) else None

    # Direction text
    if actual is not None and prev_actual is not None:
        if actual > prev_actual:
            direction = "The Federal Reserve raised rates"
        elif actual < prev_actual:
            direction = "The Federal Reserve cut rates"
        else:
            direction = "The Federal Reserve held rates steady"
    else:
        direction = "Fed decision update unavailable"

    # Surprise phrasing
    if surprise_val is not None:
        if surprise_val < 0:
            surprise_phrase = f"dovish surprise ({surprise_val:+.2f}pp vs forecast)"
        elif surprise_val > 0:
            surprise_phrase = f"hawkish surprise ({surprise_val:+.2f}pp vs forecast)"
        else:
            surprise_phrase = "in line with expectations"
        surprise_out = f"{surprise_val:+.2f}%"
    else:
        surprise_phrase = None
        surprise_out = "N/A"

    # Build commentary
    previous_rate_text = f"{prev_actual:.2f}%" if prev_actual is not None else (latest.previous or "N/A")
    commentary = f"{direction} to {latest.actual or 'N/A'} (vs {previous_rate_text} previously)."
    if forecast is not None:
        commentary += f" Market expected {latest.forecast or 'N/A'}, {surprise_phrase}."

    return {
        "release_date": latest.date or "N/A",
        "actual_rate": latest.actual or "N/A",
        "forecast": latest.forecast or "N/A",
        "previous_rate": latest.previous or (f"{prev_actual:.2f}%" if prev_actual is not None else "N/A"),
        "change": f"{change_val:+.2f}%" if change_val is not None else "N/A",
        "surprise": surprise_out,
        "meta_commentary": commentary
    }
