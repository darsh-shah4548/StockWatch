import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd

def main():
    # Load each dataset
    cpi = pd.read_csv("data/cpi_with_returns.csv")
    jobs = pd.read_csv("data/jobs_with_returns.csv")
    unemp = pd.read_csv("data/unemp_with_returns.csv")
    fed = pd.read_csv("data/fed_with_returns.csv")

    # Standardize column names if needed
    datasets = [cpi, jobs, unemp, fed]
    for df in datasets:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        # Keep only key columns
        df = df.dropna(subset=["release_date"])
    
    # Combine them
    combined = pd.concat(datasets, ignore_index=True)

    # Sort by release date
    combined = combined.sort_values("release_date").reset_index(drop=True)

    # Save master dataset
    combined.to_csv("data/all_events_with_returns.csv", index=False)
    print(f"✅ Combined dataset saved with {len(combined)} rows.")

if __name__ == "__main__":
    main()
