# main.py

import csv
import json
import os
from typing import List, Callable, Optional

# === CPI imports ===
from data_fetchers.cpi_fetcher import fetch_cpi_rows                 # historic CPI (from saved HTML)
from data_fetchers.cpi_latest_fetcher import fetch_latest_cpi_row    # live CPI (requests)
from logic.cpi_summary_generator import generate_cpi_summary

# === Jobs imports ===
from data_fetchers.jobs_fetcher import fetch_all_jobs_reports        # historic Jobs (from saved HTML)
from data_fetchers.jobs_latest_fetcher import fetch_latest_job_row   # live Jobs (requests)
from logic.job_summary_generator import generate_jobs_summary

# === Fed imports ===
from data_fetchers.fed_fetcher import fetch_fed_rows                 # historic Fed (from saved HTML)
from data_fetchers.fed_latest_fetcher import fetch_latest_fed_row    # live Fed (requests)
from logic.fed_summary_generator import generate_fed_rate_summary

# === Unemployment imports ===
from data_fetchers.unemp_fetcher import fetch_unemp_rows             # historic Unemp (from saved HTML)
from data_fetchers.unemp_latest_fetcher import fetch_latest_unemp_row# live Unemp (requests)
from logic.unemp_summary_generator import generate_unemp_summary


# ------------------------------
# Helpers
# ------------------------------

def _pairwise_summaries(items: List, summarizer: Callable[[List], dict]) -> List[dict]:
    """
    Build summaries using [current, previous] windows, assuming items are newest -> oldest.
    """
    out = []
    for i in range(len(items) - 1):
        try:
            s = summarizer(items[i:i+2])
            if isinstance(s, dict) and "error" not in s:
                out.append(s)
        except Exception as e:
            print(f"⚠️ Skipping window at {i}: {e}")
    return out

def _write_csv(filename: str, rows: List[dict]) -> None:
    if not rows:
        print(f"⚠️ No rows to write for {filename}")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"📄 Wrote {len(rows)} rows to {filename}")

def insert_latest_at_top(filename: str, new_row: dict, label: str, unique_key: str) -> None:
    """
    Inserts the latest row at the top of the CSV file.
    Removes any existing row with the same unique_key to avoid duplicates.
    Creates the file if it doesn't exist.
    """
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing = list(csv.DictReader(f))

        # Remove duplicates based on the provided key (e.g., published_date, release_date)
        existing = [row for row in existing if row.get(unique_key) != new_row.get(unique_key)]

        # Insert latest at the top
        existing.insert(0, new_row)

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=new_row.keys())
            writer.writeheader()
            writer.writerows(existing)

        print(f"✅ Inserted latest {label} summary at the top of {filename} (duplicates removed by {unique_key})")
    else:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=new_row.keys())
            writer.writeheader()
            writer.writerow(new_row)
        print(f"✅ Created {filename} with the latest {label} summary")

def rebuild_historic(csv_file: str, fetch_historic_func: Callable[[], List], summarizer, label: str) -> List[dict]:
    """
    Rebuild the full historic CSV from saved HTML (skipping placeholder rows),
    and return the list of summary dicts (newest -> oldest).
    """
    try:
        rows = fetch_historic_func()  # newest -> oldest
    except Exception as e:
        print(f"❌ Failed to fetch historic {label} rows: {e}")
        return []

    if len(rows) < 2:
        print(f"⚠️ Not enough historic {label} rows to summarize.")
        return []

    summaries = _pairwise_summaries(rows, summarizer)
    _write_csv(csv_file, summaries)
    return summaries

def _get_reference(obj) -> Optional[str]:
    """
    Works for JobReportRow(reference), CpiReportRow(reference_month), FedRateRow(reference_month), UnempRow(reference_month)
    """
    return getattr(obj, "reference", None) or getattr(obj, "reference_month", None)

def add_latest(csv_file: str,
               fetch_latest_func,
               fetch_historic_func,
               summarizer,
               label: str,
               unique_key: str) -> dict | None:
    """
    Fetch latest live row, pair with the most recent *different-month* historic row,
    summarize, and insert at top of the CSV. Removes duplicates by unique_key.
    """
    latest_live = fetch_latest_func()
    if not latest_live:
        print(f"❌ Could not fetch latest {label} data from live site.")
        return None

    try:
        historic_rows = fetch_historic_func()  # newest -> oldest
    except Exception as e:
        print(f"❌ Failed to fetch historic {label} rows (for latest pairing): {e}")
        return None

    if not historic_rows:
        print(f"❌ No historic {label} rows found to pair with latest.")
        return None

    latest_ref = _get_reference(latest_live)

    # Pick the first historic row whose reference month differs from the latest's month
    prev_row = None
    for r in historic_rows:
        if _get_reference(r) and _get_reference(r) != latest_ref:
            prev_row = r
            break

    # Fallback (shouldn’t happen, but just in case)
    if prev_row is None:
        prev_row = historic_rows[0]

    try:
        latest_summary = summarizer([latest_live, prev_row])
    except Exception as e:
        print(f"❌ Failed to generate latest {label} summary: {e}")
        return None

    insert_latest_at_top(csv_file, latest_summary, label, unique_key=unique_key)
    print(f"\n📊 Latest {label} Summary:\n")
    print(json.dumps(latest_summary, indent=2))
    return latest_summary


# ------------------------------
# Main
# ------------------------------

def main():
    # === Rebuild historic CPI, then add latest CPI at top ===
    rebuild_historic(
        csv_file="cpi_summary.csv",
        fetch_historic_func=fetch_cpi_rows,
        summarizer=generate_cpi_summary,
        label="CPI"
    )
    add_latest(
        csv_file="cpi_summary.csv",
        fetch_latest_func=fetch_latest_cpi_row,
        fetch_historic_func=fetch_cpi_rows,
        summarizer=generate_cpi_summary,
        label="CPI",
        unique_key="published_date",
    )

    # === Rebuild historic Jobs, then add latest Jobs at top ===
    rebuild_historic(
        csv_file="jobs_summary.csv",
        fetch_historic_func=fetch_all_jobs_reports,
        summarizer=generate_jobs_summary,
        label="Jobs"
    )
    add_latest(
        csv_file="jobs_summary.csv",
        fetch_latest_func=fetch_latest_job_row,
        fetch_historic_func=fetch_all_jobs_reports,
        summarizer=generate_jobs_summary,
        label="Jobs",
        unique_key="published_date",
    )

    # === Rebuild historic Fed, then add latest Fed at top ===
    rebuild_historic(
        csv_file="fed_summary.csv",
        fetch_historic_func=fetch_fed_rows,
        summarizer=generate_fed_rate_summary,
        label="Fed"
    )
    add_latest(
        csv_file="fed_summary.csv",
        fetch_latest_func=fetch_latest_fed_row,
        fetch_historic_func=fetch_fed_rows,
        summarizer=generate_fed_rate_summary,
        label="Fed",
        unique_key="release_date",   # Fed uses release_date
    )

    # === Rebuild historic Unemployment, then add latest Unemployment at top ===
    rebuild_historic(
        csv_file="unemp_summary.csv",
        fetch_historic_func=fetch_unemp_rows,
        summarizer=generate_unemp_summary,
        label="Unemployment"
    )
    add_latest(
        csv_file="unemp_summary.csv",
        fetch_latest_func=fetch_latest_unemp_row,
        fetch_historic_func=fetch_unemp_rows,
        summarizer=generate_unemp_summary,
        label="Unemployment",
        unique_key="published_date",
    )


if __name__ == "__main__":
    main()
