import pandas as pd
import numpy as np
from typing import Union

def parse_magnitude(val: object) -> Union[float, None]:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return np.nan
    s = str(val).strip()
    if s == "" or s.upper() == "N/A":
        return np.nan
    sign = -1.0 if s.startswith("-") else 1.0
    s_clean = s.replace("+", "").replace("-", "")
    try:
        if s_clean.endswith("pp"):
            return sign * float(s_clean[:-2].strip())
        if s_clean.endswith("%"):
            return sign * float(s_clean[:-1].strip())
        if s_clean.endswith(("K","k")):
            return sign * float(s_clean[:-1].strip())      # thousands
        if s_clean.endswith(("M","m")):
            return sign * float(s_clean[:-1].strip())*1000 # millions -> thousands
        return sign * float(s_clean)
    except Exception:
        return np.nan

def winsorize(series: pd.Series, p=0.01):
    lo, hi = series.quantile(p), series.quantile(1-p)
    return series.clip(lo, hi)

def main():
    df = pd.read_csv("data/all_events_tidy.csv")
    # Parse numerics
    df["surprise_num"] = df["surprise"].apply(parse_magnitude)
    df["revision_change_num"] = df["revision_change"].apply(parse_magnitude)
    df["same_day_return"] = pd.to_numeric(df.get("same_day_return", df.get("ivv_same_day_return")), errors="coerce")
    df["next_day_return"] = pd.to_numeric(df.get("next_day_return", df.get("ivv_next_day_return")), errors="coerce")
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    # Optional: trim crazy outliers to make averages interpretable
    trimmed = df.copy()
    for col in ["same_day_return", "next_day_return"]:
        trimmed[col] = winsorize(trimmed[col])

    # --- 1) Bucketed effects: surprise > 0 vs < 0 (by event type)
    def bucket_by_sign(g: pd.DataFrame):
        pos = g[g["surprise_num"] > 0]
        neg = g[g["surprise_num"] < 0]
        return pd.Series({
            "N_pos": len(pos), "mean_same_pos": pos["same_day_return"].mean(), "mean_next_pos": pos["next_day_return"].mean(),
            "N_neg": len(neg), "mean_same_neg": neg["same_day_return"].mean(), "mean_next_neg": neg["next_day_return"].mean(),
            "diff_same_pos_minus_neg": (pos["same_day_return"].mean() - neg["same_day_return"].mean()),
            "diff_next_pos_minus_neg": (pos["next_day_return"].mean() - neg["next_day_return"].mean()),
        })

    sign_table = (trimmed
                  .dropna(subset=["event_type","surprise_num","same_day_return","next_day_return"])
                  .groupby("event_type", as_index=True, sort=True)
                  .apply(bucket_by_sign, include_groups=False))

    print("\n=== Surprise buckets (surprise > 0 vs < 0) — means by event type ===")
    print(sign_table.round(4))
    sign_table.to_csv("data/out_surprise_buckets.csv")

    # --- 2) Jobs revisions: big down vs big up
    jobs = trimmed[trimmed["event_type"] == "jobs"].copy()
    jobs = jobs.dropna(subset=["revision_change_num","same_day_return","next_day_return"])

    def cut_revision(x):
        if x <= -50: return "down_big(≤-50K)"
        if x >=  50: return "up_big(≥+50K)"
        return "small(>-50K & <+50K)"

    if not jobs.empty:
        jobs["rev_bucket"] = jobs["revision_change_num"].apply(cut_revision)
        rev_table = jobs.groupby("rev_bucket").agg(
            N=("revision_change_num","size"),
            mean_same=("same_day_return","mean"),
            mean_next=("next_day_return","mean"),
            median_same=("same_day_return","median"),
            median_next=("next_day_return","median"),
            pct_pos_same=("same_day_return", lambda x: float((x>0).mean()*100)),
            pct_pos_next=("next_day_return", lambda x: float((x>0).mean()*100)),
        ).sort_index()
        print("\n=== Jobs revisions — bucketed impact ===")
        print(rev_table.round(4))
        rev_table.to_csv("data/out_jobs_revision_buckets.csv")

        # Show top 10 biggest absolute revisions with returns
        top10 = jobs.reindex(jobs["revision_change_num"].abs().sort_values(ascending=False).index).head(10)
        cols = [c for c in ["release_date","reference_month","revision_change","surprise","same_day_return","next_day_return","meta_commentary"] if c in top10.columns]
        print("\n=== Jobs — top 10 absolute revisions ===")
        print(top10[cols].to_string(index=False))
        top10.to_csv("data/out_jobs_top10_revisions.csv", index=False)
    else:
        print("\n(No jobs rows with revision data.)")

    # --- 3) Quick overall summary table (winsorized)
    overall = trimmed.groupby("event_type").agg(
        N=("event_type","size"),
        mean_same=("same_day_return","mean"),
        mean_next=("next_day_return","mean"),
        median_same=("same_day_return","median"),
        median_next=("next_day_return","median"),
        pct_pos_same=("same_day_return", lambda x: float((x>0).mean()*100)),
        pct_pos_next=("next_day_return", lambda x: float((x>0).mean()*100)),
    )
    print("\n=== Overall summary (winsorized 1% tails) ===")
    print(overall.round(4))
    overall.to_csv("data/out_overall_summary.csv")

if __name__ == "__main__":
    main()
