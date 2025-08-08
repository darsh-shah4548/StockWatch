# logic/unemp_summary_generator.py

from typing import List, Dict, Any, Optional
from models.unemp_row import UnempRow

def _parse_pct(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    try:
        return float(val.replace("%", "").strip())
    except Exception:
        return None

def generate_unemp_summary(rows: List[UnempRow]) -> Dict[str, Any]:
    """
    Expects newest -> oldest rows.
    Compares latest vs previous month, computes surprise vs forecast.
    """
    if not rows or len(rows) < 2:
        raise ValueError("Need at least two rows of data")

    latest = rows[0]
    prev = rows[1]

    actual = _parse_pct(latest.actual)
    forecast = _parse_pct(latest.forecast)
    prev_actual = _parse_pct(prev.actual)

    change_val = (actual - prev_actual) if (actual is not None and prev_actual is not None) else None
    surprise_val = (actual - forecast) if (actual is not None and forecast is not None) else None

    # Direction text (higher unemployment is generally negative for labor market)
    if actual is not None and prev_actual is not None:
        if actual > prev_actual:
            direction = "Unemployment ticked up"
        elif actual < prev_actual:
            direction = "Unemployment ticked down"
        else:
            direction = "Unemployment was unchanged"
    else:
        direction = "Unemployment update unavailable"

    # Surprise phrasing: lower-than-forecast unemployment is generally risk-on
    if surprise_val is not None:
        if surprise_val < 0:
            surprise_phrase = f"positive surprise ({surprise_val:+.1f}pp vs forecast)"
        elif surprise_val > 0:
            surprise_phrase = f"negative surprise ({surprise_val:+.1f}pp vs forecast)"
        else:
            surprise_phrase = "in line with expectations"
        surprise_out = f"{surprise_val:+.1f}%"
    else:
        surprise_phrase = None
        surprise_out = "N/A"

    commentary = f"{direction} to {latest.actual or 'N/A'} (vs {prev.actual or 'N/A'} last month)."
    if forecast is not None:
        commentary += f" Market expected {latest.forecast or 'N/A'}, {surprise_phrase}."

    return {
        "reference_month": latest.reference_month or "N/A",
        "published_date": latest.date or "N/A",
        "unemployment_rate": latest.actual or "N/A",
        "previous_unemployment_rate": prev.actual or "N/A",
        "consensus": latest.consensus or "N/A",
        "forecast": latest.forecast or "N/A",
        "surprise": surprise_out,
        "change_from_previous": f"{change_val:+.1f}%" if change_val is not None else "N/A",
        "meta_commentary": commentary
    }
