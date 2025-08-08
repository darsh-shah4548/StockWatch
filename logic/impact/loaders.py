import pandas as pd

def load_cpi(path: str = "data/cpi_summary.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    # Standardize date column name
    if "published_date" in df.columns:
        df = df.rename(columns={"published_date": "release_date"})
    df["event_type"] = "cpi"
    return df

def load_jobs(path: str = "data/jobs_summary.csv"):
    df = pd.read_csv(path)
    # standardize to 'release_date' so returns code doesn't care about dataset type
    if "published_date" in df.columns:
        df = df.rename(columns={"published_date": "release_date"})
    df["event_type"] = "jobs"
    return df


def load_unemp(path: str = "data/unemp_summary.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    if "published_date" in df.columns:
        df = df.rename(columns={"published_date": "release_date"})
    df["event_type"] = "unemployment"
    return df

def load_fed(path: str = "data/fed_summary.csv"):
    df = pd.read_csv(path)
    # Standardize the release date column name
    if "decision_date" in df.columns:
        df = df.rename(columns={"decision_date": "release_date"})
    df["event_type"] = "fed"
    return df

