import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.impact.loaders import load_jobs
from logic.impact.returns import load_ivv_prices, attach_returns_df

def main():
    ivv = load_ivv_prices("data/ivv_prices.csv")
    jobs = load_jobs("data/jobs_summary.csv")

    jobs_with_returns = attach_returns_df(jobs, ivv, release_col="release_date")
    jobs_with_returns.to_csv("data/jobs_with_returns.csv", index=False)
    print(f"✅ Wrote {len(jobs_with_returns)} rows to data/jobs_with_returns.csv")

if __name__ == "__main__":
    main()
