# UPI Transaction Analytics: Exploring Payment Behavior, Transaction Reliability and Fraud Patterns in India

**Course:** Data Exploration and Visualization Laboratory  
**Authors:**  
- Swaraj Suresh Shinde (PRN: `125B1D053`)  
- Nikol Dharmraj Ghodke (PRN: `125B1D062`)  

**Dataset Source:** [Kaggle UPI Transactions 2024 Dataset](https://www.kaggle.com/datasets/skullagos5246/upi-transactions-2024-dataset) (250,000 records)  

---

## 1. Project Overview

Unified Payments Interface (UPI) is the cornerstone of retail digital payments in India, processing billions of transactions monthly. This academic mini-project investigates transaction velocity, banking infrastructure reliability, payment failure distribution, and security anomaly detection across 250,000 transactions spanning the entire 2024 calendar year.

The project delivers:
1. **Verified Numerical Foundation:** Exhaustive verification of all descriptive metrics and inferential Chi-Square ($\chi^2$) independence tests across banks, devices, and networks.
2. **Interactive Streamlit + Plotly Dashboard (`app.py`):** A responsive, multi-filter analytical application featuring dynamic KPI cards, dual-axis and log-scale visualizations, cohort heatmaps, and filtered CSV export.
3. **Audited & Corrected Notebooks:** Rectification of metric conflations (failure rate vs. fraud rate) and machine learning evaluation pitfalls present in preliminary exploratory analyses.
4. **Structured Technical Documentation:** Academic reports detailing technology selection, payments risk insights, and full code walkthroughs.

---

## 2. Directory Structure

```text
upi-transaction-analytics/
├── app.py                             # Main Streamlit interactive dashboard application
├── requirements.txt                   # Exact pinned dependencies verified for runtime
├── README.md                          # Project documentation and setup guide
├── data/
│   └── upi_transactions_2024.csv      # Source of truth dataset (250,000 rows × 17 cols)
├── notebooks/
│   ├── mini-project.ipynb             # Original preliminary student notebook
│   └── mini-project_corrected.ipynb   # Audited, bug-fixed, and fully documented notebook
├── src/
│   ├── __init__.py                    # Source package marker
│   ├── data_loader.py                 # Defensive data ingestion & temporal feature derivation
│   └── metrics.py                     # Dynamic KPI and aggregation computation routines
├── docs/
│   ├── tools_and_technologies.md      # Tool selection rationale and technology comparison
│   ├── key_insights.md                # 6 data-backed senior payments-risk insights
│   └── code_walkthrough.md            # Detailed engineering and modeling pipeline walkthrough
└── outputs/
    ├── verified_metrics.json          # Machine-readable numerical benchmark foundation
    ├── verification_report.md         # Comprehensive claims verification & audit report
    └── insight_figures/               # High-resolution (300 DPI) publication figures (PNG)
        ├── figure1_amount_distribution_outliers.png
        ├── figure2_merchant_volume_vs_value.png
        ├── figure3_diurnal_traffic_peak_hours.png
        ├── figure4_infrastructure_reliability_invariance.png
        ├── figure5_geographic_volume_vs_fraud_flags.png
        └── figure6_fraud_flag_rates_and_uncertainty.png
```

---

## 3. Installation and Setup Guide

The project is built on Python 3.12 (compatible with Python 3.10+). Follow the operating-system-specific instructions below to set up a clean virtual environment and run the dashboard locally.

### Windows (PowerShell / Command Prompt)

```powershell
# 1. Clone or navigate to the project directory
cd upi-transaction-analytics

# 2. Create a clean virtual environment
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\activate

# 4. Upgrade pip and install exact dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Launch the Streamlit dashboard
streamlit run app.py
```

### macOS and Linux (Bash / Zsh)

```bash
# 1. Clone or navigate to the project directory
cd upi-transaction-analytics

# 2. Create a clean virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Upgrade pip and install exact dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Launch the Streamlit dashboard
streamlit run app.py
```

Upon launching, Streamlit will serve the dashboard locally at `http://localhost:8501`.

---

## 4. How to Use the Dashboard & Filters

The dashboard adapts dynamically to any filter combination. All KPI metrics, visualizations, and analytical tabs recalculate immediately based on the active subset:

| Filter Widget | Control Type | Description & Usage |
| :--- | :--- | :--- |
| **Date Range** | Date Picker | Filter transactions within specific calendar windows across 2024. |
| **Transaction Type** | Multiselect | Select one or more types (`P2P`, `P2M`, `Bill Payment`, `Recharge`). |
| **Merchant Category**| Multiselect | Filter across 10 commercial verticals (e.g., `Grocery`, `Food`, `Shopping`). |
| **Sender State** | Multiselect | Filter across 10 Indian states (e.g., `Maharashtra`, `Karnataka`, `Delhi`). |
| **Sender Bank** | Multiselect | Analyze individual banking partner volumes (e.g., `SBI`, `HDFC`, `ICICI`). |
| **Transaction Status**| Multiselect | Inspect specific outcomes (`SUCCESS` or `FAILED`). |
| **Device Type** | Multiselect | Filter by user platform (`Android`, `iOS`, `Web`). |
| **Network Type** | Multiselect | Filter by connectivity standard (`4G`, `5G`, `WiFi`, `3G`). |
| **Fraud Indicator** | Dropdown | Toggle between `All Transactions`, `Fraud-Flagged Only (1)`, and `Non-Fraud Only (0)`. |
| **Amount Range** | Dual Slider | Restrict transactions between ₹10 and ₹42,099. |
| **Reset All Filters**| Action Button | Instantly clears all active selections and restores the full 250,000 transaction dataset. |

### Exporting Filtered Data
At the bottom of the dashboard, toggle the **"Inspect Sample Data & Export Filtered Subset"** checkbox to preview records in a tabular viewer and click **"Download Filtered Data as CSV"** to save the active view.

---

## 5. Troubleshooting Common Issues

1. **`Dataset not found` Error:**  
   Ensure `upi_transactions_2024.csv` is present in the `data/` directory or project root. The `src/data_loader.py` module automatically checks both locations.
2. **Port 8501 Already in Use:**  
   If another application is using port 8501, specify a custom port:
   ```bash
   streamlit run app.py --server.port 8502
   ```
3. **Module Import Errors:**  
   Ensure the virtual environment is activated (`(venv)` appears in your prompt) and dependencies are installed via `pip install -r requirements.txt`.
4. **Empty Filter State:**  
   If conflicting filters result in zero matching records, the dashboard displays an alert rather than crashing. Click **"Reset All Filters"** in the sidebar to return to the full dataset.

---

## 6. Dataset Attribution and Academic Integrity

- **Dataset:** [UPI Transactions 2024 Dataset](https://www.kaggle.com/datasets/skullagos5246/upi-transactions-2024-dataset) hosted on Kaggle.
- **Volume:** 250,000 synthetic transaction records representing payment behavior, temporal cycles, infrastructure telemetry, and security heuristics in India.
- **Academic Purpose:** Developed exclusively for academic analysis and demonstration under the *Data Exploration and Visualization Laboratory* course.
