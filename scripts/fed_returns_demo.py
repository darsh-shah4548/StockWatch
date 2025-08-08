import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.impact.loaders import load_fed
from logic.impact.returns import load_ivv_prices, attach_returns_df

def main():
    ivv = load_ivv_prices("data/ivv_prices.csv")
    fed = load_fed("data/fed_summary.csv")

    fed_with_returns = attach_returns_df(fed, ivv, release_col="release_date")
    fed_with_returns.to_csv("data/fed_with_returns.csv", index=False)
    print(f"✅ Wrote {len(fed_with_returns)} rows to data/fed_with_returns.csv")

if __name__ == "__main__":
    main()
