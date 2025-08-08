# models/unemp_row.py
from dataclasses import dataclass

@dataclass
class UnempRow:
    date: str
    reference_month: str
    actual: str
    forecast: str
    previous: str
    consensus: str  # same as forecast
