# logic/jobs_summary_generator.py

from typing import List, Dict, Any
from models.job_report import JobReportRow

def generate_jobs_summary(job_reports: List[JobReportRow]) -> Dict[str, Any]:
    # Filter only rows with actual values
    valid_reports = [row for row in job_reports if row.actual and row.actual.lower() != ""]
    
    # Reverse order since Investing.com lists most recent first
    valid_reports = list(reversed(valid_reports))

    if len(valid_reports) < 2:
        return {"error": "Not enough data to calculate revisions or surprise."}

    latest = valid_reports[-1]     # Now truly the latest (bottom of the original table)
    previous = valid_reports[-2]   # Second-to-last in reversed list

    def parse_jobs(value: str) -> int:
        value = value.upper().replace("K", "").replace(",", "").strip()
        try:
            return int(float(value))
        except ValueError:
            return None

    actual = parse_jobs(latest.actual)
    consensus = parse_jobs(latest.consensus)
    prev_actual = parse_jobs(previous.actual)
    revised = parse_jobs(latest.previous)

    surprise = actual - consensus if actual is not None and consensus is not None else None
    revision_change = revised - prev_actual if revised is not None and prev_actual is not None else None

    revision_comment = ""
    if revision_change is not None:
        if revision_change < -100:
            revision_comment = f"{previous.reference} was sharply revised down by {abs(revision_change)}K."
        elif revision_change < 0:
            revision_comment = f"{previous.reference} was revised down by {abs(revision_change)}K."
        elif revision_change > 0:
            revision_comment = f"{previous.reference} was revised up by {revision_change}K."
        else:
            revision_comment = f"{previous.reference} was unchanged."

    meta_comment = f"{latest.reference} jobs report showed {actual}K vs {consensus}K expected."
    if surprise is not None:
        if surprise < -50:
            meta_comment += " Significant downside surprise."
        elif surprise < 0:
            meta_comment += " Slight downside miss."
        elif surprise > 50:
            meta_comment += " Big upside surprise."
        elif surprise > 0:
            meta_comment += " Slight upside beat."

    if revision_comment:
        meta_comment += f" {revision_comment}"

    return {
        "latest_reference_month": latest.reference,
        "published_date": latest.date,
        "actual_jobs": latest.actual,
        "consensus_jobs": latest.consensus,
        "surprise": f"{surprise}K" if surprise is not None else "N/A",
        "previous_month_reference": previous.reference,
        "original_value": previous.actual,
        "revised_value": latest.previous,
        "revision_change": f"{revision_change}K" if revision_change is not None else "N/A",
        "revision_commentary": revision_comment,
        "meta_commentary": meta_comment
    }
