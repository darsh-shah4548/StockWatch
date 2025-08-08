# StockWatch
## Macroeconomic Events & S&P 500 Same-Day Impact

## 📌 Overview
This project analyzes how key U.S. macroeconomic events — starting with **Non-Farm Payrolls (Jobs Reports)** — impact the **same-day returns** of the S&P 500 ETF (`IVV`).  
The analysis explores:
- Headline **surprise** effects (actual vs forecast jobs numbers)
- **Revision effects** (changes to the previous month’s reported jobs)
- Visual relationships between these metrics and same-day market moves.

The work is modular so we can extend it later to include CPI, FOMC, and other macro events.

---

## 📂 Project Structure
```
.
├── data/                       # Data files
│   ├── all_events_tidy.csv     # Cleaned, combined dataset
│   ├── raw_jobs_data/          # Original jobs report data
│   └── raw_market_data/        # Original IVV market data
├── data_fetchers/                  # python fetching files for fetching the data
│   ├── cpi_fetcher.py
│   ├── job_fetcher.py
│   └── fed_fetcher.py
├── scripts/                    # Python scripts for processing & plotting
│   ├── combine_all_events_tidy.py
│   ├── process_jobs_data.py
│   ├── visualizations.ipynb
│   
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

---

## 📊 Analyses Completed
### 1. **Headline Surprise vs Same-Day Return**
- **Surprise** = `(Actual Jobs - Forecast Jobs)` in thousands.
- Examines whether larger positive or negative surprises correlate with same-day S&P 500 returns.
- Plots:
  - Scatter with regression line
  - Points colored by surprise sign (Positive = green, Negative = red)
  - Top 5 largest surprises annotated with `Reference Month` & release date.

### 2. **Previous Month Revision vs Same-Day Return**
- **Revision** = `(Revised Previous Month Jobs - Initially Reported Jobs)`.
- Checks if market reacts not only to the headline number but also to changes in the prior month’s data.
- Plots:
  - Revision (in thousands) vs same-day returns
  - Points colored by headline surprise sign
  - Top 5 largest revisions annotated

### 3. **COVID-19 Period Handling**
- Option to exclude March–July 2020 to avoid extreme outliers in both job numbers and market moves.

---

## 📦 Setup & Installation
1. **Clone this repo**:
   ```bash
   git clone https://github.com/darsh-shah4548/StockWatch.git
   cd StockWatch
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ How to Run

### Load the Tidy Dataset
```python
import pandas as pd

df = pd.read_csv("data/all_events_tidy.csv", parse_dates=["release_date"])
```

### Run Headline Surprise Plot
```python
from scripts.plot_surprise_vs_return import plot_jobs_surprise_vs_return
plot_jobs_surprise_vs_return(df, exclude_covid=True)
```

### Run Revision Plot
```python
from scripts.plot_revision_vs_return import plot_revision_vs_return
plot_revision_vs_return(df, exclude_covid=True)
```

---

## 📝 Notes
- **Data Source**: Investing.com, processed using custom Python scrapers.
- **Market Data**: IVV ETF daily prices.
- **Next Steps**:
  - Extend analysis to CPI, FOMC, Retail Sales.
  - Explore multi-day market impact (t+1, t+5).
  - Build combined regression models with both surprise & revision variables.

---

## 📜 License
MIT License — see [LICENSE](LICENSE) file for details.

---

## 👤 Author
**Darsh Shah**  
Application Specialist: Data Specialist @ CSU Housing & Dining Services  
M.S. in Data Science, CU Boulder
