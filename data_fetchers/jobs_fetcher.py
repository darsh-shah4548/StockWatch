# data_fetchers/jobs_fetcher.py

from bs4 import BeautifulSoup
import os
from typing import List
from models.job_report import JobReportRow

def fetch_all_jobs_reports() -> List[JobReportRow]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "nfp_investing.html")  # Your manually saved HTML file

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        table = soup.find("table", {"id": "eventHistoryTable227"})
        if not table:
            raise Exception("Could not find table with id 'eventHistoryTable227'.")

        rows = table.find("tbody").find_all("tr")
        job_reports = []

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 5:
                try:
                    actual_value = cells[2].text.strip()

                    # Skip upcoming forecast row with no actual value
                    if not actual_value or actual_value.upper() == "N/A":
                        continue

                    date_text = cells[0].text.strip()
                    report = JobReportRow(
                        date=date_text,                                 # e.g., "Sep 04, 2020 (Aug)"
                        reference=date_text.split("(")[-1].strip(")"), # e.g., "Aug"
                        actual=actual_value,
                        forecast=cells[3].text.strip(),
                        previous=cells[4].text.strip(),
                        consensus=cells[3].text.strip(),  # Using forecast as consensus
                    )
                    job_reports.append(report)
                except Exception as e:
                    print(f"kipped row due to parse error: {e}")
                    continue

        print(f"Parsed {len(job_reports)} job reports from local file (skipping placeholder rows).")
        return job_reports

    except Exception as e:
        print(f"Error reading local HTML file: {e}")
        return []
