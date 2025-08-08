# models/fed_rate_row.py
from dataclasses import dataclass

@dataclass
class FedRateRow:
    date: str
    reference_month: str
    actual: str
    forecast: str
    previous: str
    consensus: str  # same as forecast
