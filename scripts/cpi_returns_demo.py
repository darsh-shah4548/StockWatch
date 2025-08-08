import pandas as pd
from logic.impact.loaders import load_cpi
from logic.impact.returns import load_ivv_prices, attach_returns_df

def main():
    ivv = load_ivv_prices("data/ivv_prices.csv")
    cpi = load_cpi("data/cpi_summary.csv")

    cpi_with_returns = attach_returns_df(cpi, ivv, release_col="release_date")
    cpi_with_returns.to_csv("data/cpi_with_returns.csv", index=False)
    print(f"✅ Wrote {len(cpi_with_returns)} rows to data/cpi_with_returns.csv")

if __name__ == "__main__":
    main()
