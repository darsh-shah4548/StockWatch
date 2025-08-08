import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd


def _first_nonnull(df, cols):
    """Return the first non-null column among cols (as a Series)."""
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return pd.Series([None] * len(df))
    out = df[cols[0]].copy()
    for c in cols[1:]:
        out = out.fillna(df[c])
    return out


def _select_and_rename_common(df, mappings, event_type_fixed=None):
    """
    Map a wide event-specific DF into a tidy shape:
    release_date, event_type, headline_value, forecast_value, surprise, change_from_previous,
    revision_value, revision_change, meta_commentary, same_day_return, next_day_return
    """
    df = df.copy()

    # Choose columns by priority lists
    out = pd.DataFrame({
        "release_date": _first_nonnull(df, mappings["release_date"]),
        "event_type": df[mappings["event_type"]] if isinstance(mappings["event_type"], str)
                      else _first_nonnull(df, mappings["event_type"]),
        "headline_value": _first_nonnull(df, mappings["headline_value"]),
        "forecast_value": _first_nonnull(df, mappings["forecast_value"]),
        "surprise": _first_nonnull(df, mappings["surprise"]),
        "change_from_previous": _first_nonnull(df, mappings["change_from_previous"]),
        "revision_value": _first_nonnull(df, mappings["revision_value"]),
        "revision_change": _first_nonnull(df, mappings["revision_change"]),
        "meta_commentary": _first_nonnull(df, mappings["meta_commentary"]),
        "same_day_return": _first_nonnull(df, mappings["same_day_return"]),
        "next_day_return": _first_nonnull(df, mappings["next_day_return"]),
    })

    if event_type_fixed:
        out["event_type"] = event_type_fixed

    # Keep a reference month if present (nice to group by later)
    ref_cols = [c for c in ["reference_month", "latest_reference_month"] if c in df.columns]
    out["reference_month"] = _first_nonnull(df, ref_cols) if ref_cols else None

    # Ensure proper dtypes
    out["release_date"] = pd.to_datetime(out["release_date"], errors="coerce")
    out = out.sort_values("release_date").reset_index(drop=True)

    return out


def load_and_tidy_all(
    cpi_path="data/cpi_with_returns.csv",
    jobs_path="data/jobs_with_returns.csv",
    unemp_path="data/unemp_with_returns.csv",
    fed_path="data/fed_with_returns.csv",
):
    # --- CPI ---
    cpi = pd.read_csv(cpi_path)
    cpi_map = {
        "release_date": ["release_date", "published_date"],
        "event_type": "event_type",
        "headline_value": ["headline_cpi"],
        "forecast_value": ["forecast", "consensus"],
        "surprise": ["surprise"],
        "change_from_previous": ["change_from_previous"],
        "revision_value": [],          # N/A for CPI
        "revision_change": [],         # N/A for CPI
        "meta_commentary": ["meta_commentary"],
        "same_day_return": ["ivv_same_day_return"],
        "next_day_return": ["ivv_next_day_return"],
    }
    cpi_tidy = _select_and_rename_common(cpi, cpi_map, event_type_fixed="cpi")

    # --- Jobs ---
    jobs = pd.read_csv(jobs_path)
    jobs_map = {
        "release_date": ["release_date", "published_date"],
        "event_type": "event_type",
        "headline_value": ["actual_jobs"],
        "forecast_value": ["consensus_jobs"],
        "surprise": ["surprise"],              # e.g., "-33K"
        "change_from_previous": [],            # generally N/A for headline level; leave blank
        "revision_value": ["revised_value"],   # revised prior-month level (e.g., "14K")
        "revision_change": ["revision_change"],# delta vs original prior (e.g., "-133K")
        "meta_commentary": ["meta_commentary"],
        "same_day_return": ["ivv_same_day_return"],
        "next_day_return": ["ivv_next_day_return"],
    }
    jobs_tidy = _select_and_rename_common(jobs, jobs_map, event_type_fixed="jobs")

    # --- Unemployment ---
    unemp = pd.read_csv(unemp_path)
    unemp_map = {
        "release_date": ["release_date", "published_date"],
        "event_type": "event_type",
        "headline_value": ["unemployment_rate"],
        "forecast_value": ["forecast", "consensus"],
        "surprise": ["surprise"],
        "change_from_previous": ["change_from_previous"],
        "revision_value": [],          # N/A
        "revision_change": [],         # N/A
        "meta_commentary": ["meta_commentary"],
        "same_day_return": ["ivv_same_day_return"],
        "next_day_return": ["ivv_next_day_return"],
    }
    unemp_tidy = _select_and_rename_common(unemp, unemp_map, event_type_fixed="unemployment")

    # --- Fed ---
    fed = pd.read_csv(fed_path)
    fed_map = {
        "release_date": ["release_date"],
        "event_type": "event_type",
        "headline_value": ["actual_rate"],
        "forecast_value": ["forecast"],
        "surprise": ["surprise"],
        "change_from_previous": ["change"],    # rate change vs prior meeting
        "revision_value": [],                  # N/A
        "revision_change": [],                 # N/A
        "meta_commentary": ["meta_commentary"],
        "same_day_return": ["ivv_same_day_return"],
        "next_day_return": ["ivv_next_day_return"],
    }
    fed_tidy = _select_and_rename_common(fed, fed_map, event_type_fixed="fed")

    # Combine
    combined = pd.concat([cpi_tidy, jobs_tidy, unemp_tidy, fed_tidy], ignore_index=True)
    # Drop rows with no date (just in case)
    combined = combined.dropna(subset=["release_date"]).sort_values(["release_date", "event_type"]).reset_index(drop=True)

    return combined


def main():
    out_path = "data/all_events_tidy.csv"
    combined = load_and_tidy_all()
    combined.to_csv(out_path, index=False)
    print(f"✅ Wrote {len(combined)} rows to {out_path}")


if __name__ == "__main__":
    main()
