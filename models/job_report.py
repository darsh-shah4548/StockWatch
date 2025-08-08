# models/jobs_report.py

from dataclasses import dataclass

@dataclass
class JobReportRow:
    date: str             # e.g., "2025-08-01"
    reference: str        # e.g., "Jul"
    actual: str           # e.g., "73K"
    previous: str         # e.g., "14K"
    consensus: str        # e.g., "110K"
    forecast: str         # e.g., "110K"
