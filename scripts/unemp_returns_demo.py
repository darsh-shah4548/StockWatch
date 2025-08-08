import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.impact.loaders import load_unemp
from logic.impact.returns import load_ivv_prices, attach_returns_df

def main():
    ivv = load_ivv_prices("data/ivv_prices.csv")
    unemp = load_unemp("data/unemp_summary.csv")

    unemp_with_returns = attach_returns_df(unemp, ivv, release_col="release_date")
    unemp_with_returns.to_csv("data/unemp_with_returns.csv", index=False)
    print(f"✅ Wrote {len(unemp_with_returns)} rows to data/unemp_with_returns.csv")

if __name__ == "__main__":
    main()
