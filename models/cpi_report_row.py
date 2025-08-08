from dataclasses import dataclass

@dataclass
class CpiReportRow:
    date: str
    reference_month: str
    actual: str
    previous: str
    consensus: str
    forecast: str
