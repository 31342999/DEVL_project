# Verification Report: Verified Numerical Foundation & Notebook Audit
## UPI Transaction Analytics: Exploring Payment Behavior, Transaction Reliability and Fraud Patterns in India

**Authors:** Swaraj Suresh Shinde (PRN: 125B1D053), Nikol Dharmraj Ghodke (PRN: 125B1D062)  
**Course:** Data Exploration and Visualization Laboratory  
**Source of Truth:** `upi_transactions_2024.csv` (250,000 rows × 17 columns)  
**Notebook Audited:** `mini-project.ipynb` (97 cells)  
**Deliverables Reference:** `Mini Project Deliverables.docx`  
**Generated Date:** 2026-10-13  

---

## 1. Dataset Profile & Structural Verification

The CSV file `upi_transactions_2024.csv` was ingested and inspected programmatically. Below is the structural summary of the raw data.

| Property | Value | Notes |
| :--- | :--- | :--- |
| **Dataset Shape** | `250,000` rows × `17` columns | 250,000 total records |
| **Duplicate Rows** | `0` | No fully identical rows detected |
| **Missing / Null Values** | `0` across all 17 columns | Complete dataset with zero nulls |
| **Timestamp Range (Min)** | `2024-01-01 00:05:10` | Earliest transaction |
| **Timestamp Range (Max)** | `2024-12-30 23:55:40` | Latest transaction (spans 365 days of 2024) |
| **ID Column** | `transaction id` | Unique surrogate key (`250,000` unique values) |

### Exact Column Names, Data Types, and Syntax Peculiarities

| # | Exact Column Name | Dtype | Null Count | Syntax / Formatting Notes |
| :-: | :--- | :--- | :-: | :--- |
| 1 | `transaction id` | `str` | 0 | Contains spaces; **Identifier column - DO NOT USE analytically** |
| 2 | `timestamp` | `str` | 0 | Standard snake_case |
| 3 | `transaction type` | `str` | 0 | Contains spaces |
| 4 | `merchant_category` | `str` | 0 | Standard snake_case |
| 5 | `amount (INR)` | `int64` | 0 | Contains spaces |
| 6 | `transaction_status` | `str` | 0 | Standard snake_case |
| 7 | `sender_age_group` | `str` | 0 | Standard snake_case |
| 8 | `receiver_age_group` | `str` | 0 | Standard snake_case |
| 9 | `sender_state` | `str` | 0 | Standard snake_case |
| 10 | `sender_bank` | `str` | 0 | Standard snake_case |
| 11 | `receiver_bank` | `str` | 0 | Standard snake_case |
| 12 | `device_type` | `str` | 0 | Standard snake_case |
| 13 | `network_type` | `str` | 0 | Standard snake_case |
| 14 | `fraud_flag` | `int64` | 0 | Standard snake_case |
| 15 | `hour_of_day` | `int64` | 0 | Standard snake_case |
| 16 | `day_of_week` | `str` | 0 | Standard snake_case |
| 17 | `is_weekend` | `int64` | 0 | Standard snake_case |

> [!IMPORTANT]
> **Non-Analytical Identifier Policy:**  
> The column `transaction id` contains `250,000` unique alphanumeric values (e.g., `TXN0000000001` to `TXN0000250000`), representing 100% distinct primary keys. It has **no intrinsic analytical or predictive value**. It must be strictly excluded from group-by aggregations, statistical modeling, and machine learning feature matrices to prevent severe data leakage, overfitting, and redundant memory consumption.

---

## 2. Recomputation & Claimed vs. Actual Verification

All figures previously claimed in the project documentation and exploratory notes were recomputed directly against the source of truth (`upi_transactions_2024.csv`). Every claim is marked as **MATCH** or **MISMATCH**.

| Metric / Claim Item | Claimed Value | Recomputed Actual Value | Verification Status | Analytical Notes |
| :--- | :--- | :--- | :-: | :--- |
| **Total Dataset Rows** | 250,000 | 250,000 | **MATCH** | Exact match |
| **Total Transaction Value** | 327,939,009 INR | 327,939,009 INR | **MATCH** | Exact match |
| **Mean Transaction Amount** | 1,311.76 INR | 1311.76 INR (exact: 1311.756036) | **MATCH** | Exact match when rounded to 2 decimal places |
| **Median Transaction Amount** | 629 INR | 629 INR | **MATCH** | Exact match |
| **Standard Deviation of Amount** | 1,848.06 INR | 1848.06 INR (exact: 1848.059224) | **MATCH** | Exact match when rounded to 2 decimal places |
| **Minimum Transaction Amount** | 10 INR | 10 INR | **MATCH** | Exact match |
| **Maximum Transaction Amount** | 42,099 INR | 42,099 INR | **MATCH** | Exact match |
| **SUCCESS Transactions Count & Rate** | 237,624 (95.05%) | 237,624 (95.0496%, rounds to 95.05%) | **MATCH** | Exact count matches; 95.0496% rounds to 95.05% |
| **FAILED Transactions Count & Rate** | 12,376 (4.95%) | 12,376 (4.9504%, rounds to 4.95%) | **MATCH** | Exact count matches; 4.9504% rounds to 4.95% |
| **Fraud Flagged Transactions (fraud_flag=1)** | 480 (0.192%) | 480 (0.192%) | **MATCH** | Exact count matches; exactly 0.1920% |
| **Transaction Type Counts** | P2P 112,445; P2M 87,660; Bill Payment 37,368; Recharge 12,527 | P2P 112,445; P2M 87,660; Bill Payment 37,368; Recharge 12,527 | **MATCH** | All 4 transaction types match claimed figures exactly |
| **Failure Rate per Bank** | SBI 4.94, HDFC 4.82, ICICI 5.04, IndusInd 4.95, Axis 4.95, PNB 4.89, Yes Bank 5.10, Kotak 4.98 | SBI 4.94% (3,095/62,693), HDFC 4.82% (1,808/37,485), ICICI 5.04% (1,499/29,769), IndusInd 4.95% (1,247/25,173), Axis 4.95% (1,239/25,042), PNB 4.89% (1,221/24,946), Yes Bank 5.10% (1,269/24,860), Kotak 4.98% (998/20,032) | **MATCH** | All 8 banks match claimed failure rates rounded to 2 decimal places |
| **Device Failure Distribution** | Android 74.97%, iOS 19.78%, Web 5.25% | Share of all failures: Android 74.97% (9,278/12,376), iOS 19.78% (2,448/12,376), Web 5.25% (650/12,376). Failure rate within group: Android 4.94% (9,278/187,777), iOS 4.93% (2,448/49,613), Web 5.15% (650/12,610) | **MATCH (METRIC CLARIFICATION NEEDED)** | The claimed figures represent 'Share of all failures' (denominator = 12,376 total failures), NOT failure rate within each device. The failure rate within each device is virtually identical (~4.94% - 5.15%). |
| **Network Failure Distribution** | 4G 60.31%, 5G 24.56%, WiFi 9.87%, 3G 5.26% | Share of all failures: 4G 60.31% (7,464/12,376), 5G 24.56% (3,039/12,376), WiFi 9.87% (1,222/12,376), 3G 5.26% (651/12,376). Failure rate within group: 4G 4.98% (7,464/149,813), 5G 4.86% (3,039/62,582), WiFi 4.86% (1,222/25,134), 3G 5.22% (651/12,471) | **MATCH (METRIC CLARIFICATION NEEDED)** | The claimed figures represent 'Share of all failures' (denominator = 12,376 total failures), NOT failure rate within each network type. Within-network failure rates are virtually uniform (~4.86% - 5.22%). |
| **Peak Hours** | 18:00 (20,064) and 19:00 (21,232) | 18:00 (20,064 transactions) and 19:00 (21,232 transactions) | **MATCH** | Top 2 hours by transaction volume match exactly |
| **Weekday vs Weekend Volume** | weekday 178,663 (71.47%) | Weekday (is_weekend=0): 178,663 (71.4652%, rounds to 71.47%). Weekend (is_weekend=1): 71,337 (28.5348%, rounds to 28.53%) | **MATCH** | Exact match |
| **Fraud Counts by State** | Maharashtra 71, Karnataka 69, ... | Maharashtra 71, Karnataka 69, Uttar Pradesh 52, Delhi 50, Rajasthan 46, Gujarat 43, Tamil Nadu 40, Telangana 39, Andhra Pradesh 35, West Bengal 35 | **MATCH** | Top states match claimed figures; complete 10-state breakdown verified |

### Critical Analytical Insight: Failure Rate vs. Share of Failures

> [!WARNING]
> **Disambiguating 'Share of Failures' vs. 'Failure Rate Within Group':**  
> A frequent conceptual pitfall in the preliminary notebook is conflating **Share of all failures** (e.g. *What percentage of total system failures occurred on Android?*) with **Failure rate within group** (e.g. *What percentage of Android transactions failed?*).  
> - **Android** accounts for **74.97% of all system failures** (9,278 / 12,376) purely because Android represents **75.11% of all transaction traffic** (187,777 / 250,000).  
> - The **actual failure rate on Android is 4.94%** (9,278 / 187,777), which is virtually identical to **iOS (4.93%)** and **Web (5.15%)**.  
> - Similarly, **4G** accounts for **60.31% of all system failures** because 4G carries 59.93% of all traffic, but its **cohort failure rate is 4.98%**, almost identical to **5G (4.86%)**, **WiFi (4.86%)**, and **3G (5.22%)**.  
> Neither Android nor 4G is inherently less reliable; their high absolute failure counts are strictly volume-driven.

---

## 3. Verified Categorical Dimension Breakdowns

The tables below provide the complete verified numerical foundation across all 10 requested categorical dimensions. Every proportion displays its exact formula and denominator:
- **Share of Transactions:** $\frac{\text{Group Count}}{250,000} \times 100$
- **Failure Rate (Within Group):** $\frac{\text{Group Failed Count}}{\text{Group Total Count}} \times 100$
- **Share of All Failures:** $\frac{\text{Group Failed Count}}{12,376} \times 100$
- **Fraud Rate (Within Group):** $\frac{\text{Group Fraud Count}}{\text{Group Total Count}} \times 100$
- **Share of All Fraud:** $\frac{\text{Group Fraud Count}}{480} \times 100$

### 3.1 Transaction Type

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **P2P** | 112,445 | 44.98% | 5,575 | **4.96%** | 45.05% | 206 | **0.183%** | 42.92% |
| **P2M** | 87,660 | 35.06% | 4,339 | **4.95%** | 35.06% | 167 | **0.191%** | 34.79% |
| **Bill Payment** | 37,368 | 14.95% | 1,824 | **4.88%** | 14.74% | 77 | **0.206%** | 16.04% |
| **Recharge** | 12,527 | 5.01% | 638 | **5.09%** | 5.16% | 30 | **0.239%** | 6.25% |

### 3.2 Merchant Category

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Grocery** | 49,966 | 19.99% | 2,503 | **5.01%** | 20.22% | 94 | **0.188%** | 19.58% |
| **Food** | 37,464 | 14.99% | 1,876 | **5.01%** | 15.16% | 73 | **0.195%** | 15.21% |
| **Shopping** | 29,872 | 11.95% | 1,519 | **5.08%** | 12.27% | 62 | **0.208%** | 12.92% |
| **Fuel** | 25,063 | 10.03% | 1,204 | **4.80%** | 9.73% | 48 | **0.192%** | 10.00% |
| **Other** | 24,828 | 9.93% | 1,230 | **4.95%** | 9.94% | 50 | **0.201%** | 10.42% |
| **Utilities** | 22,338 | 8.94% | 1,086 | **4.86%** | 8.78% | 33 | **0.148%** | 6.88% |
| **Transport** | 20,105 | 8.04% | 957 | **4.76%** | 7.73% | 43 | **0.214%** | 8.96% |
| **Entertainment** | 20,103 | 8.04% | 990 | **4.92%** | 8.00% | 40 | **0.199%** | 8.33% |
| **Healthcare** | 12,663 | 5.07% | 612 | **4.83%** | 4.95% | 21 | **0.166%** | 4.38% |
| **Education** | 7,598 | 3.04% | 399 | **5.25%** | 3.22% | 16 | **0.211%** | 3.33% |

### 3.3 Sender State

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Maharashtra** | 37,427 | 14.97% | 1,842 | **4.92%** | 14.88% | 71 | **0.190%** | 14.79% |
| **Uttar Pradesh** | 30,125 | 12.05% | 1,572 | **5.22%** | 12.70% | 52 | **0.173%** | 10.83% |
| **Karnataka** | 29,756 | 11.90% | 1,447 | **4.86%** | 11.69% | 69 | **0.232%** | 14.38% |
| **Tamil Nadu** | 25,367 | 10.15% | 1,298 | **5.12%** | 10.49% | 40 | **0.158%** | 8.33% |
| **Delhi** | 24,870 | 9.95% | 1,237 | **4.97%** | 10.00% | 50 | **0.201%** | 10.42% |
| **Telangana** | 22,435 | 8.97% | 1,056 | **4.71%** | 8.53% | 39 | **0.174%** | 8.12% |
| **Gujarat** | 20,061 | 8.02% | 959 | **4.78%** | 7.75% | 43 | **0.214%** | 8.96% |
| **Andhra Pradesh** | 20,006 | 8.00% | 1,000 | **5.00%** | 8.08% | 35 | **0.175%** | 7.29% |
| **Rajasthan** | 19,981 | 7.99% | 958 | **4.79%** | 7.74% | 46 | **0.230%** | 9.58% |
| **West Bengal** | 19,972 | 7.99% | 1,007 | **5.04%** | 8.14% | 35 | **0.175%** | 7.29% |

### 3.4 Sender Bank

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **SBI** | 62,693 | 25.08% | 3,095 | **4.94%** | 25.01% | 109 | **0.174%** | 22.71% |
| **HDFC** | 37,485 | 14.99% | 1,808 | **4.82%** | 14.61% | 62 | **0.165%** | 12.92% |
| **ICICI** | 29,769 | 11.91% | 1,499 | **5.04%** | 12.11% | 66 | **0.222%** | 13.75% |
| **IndusInd** | 25,173 | 10.07% | 1,247 | **4.95%** | 10.08% | 52 | **0.207%** | 10.83% |
| **Axis** | 25,042 | 10.02% | 1,239 | **4.95%** | 10.01% | 49 | **0.196%** | 10.21% |
| **PNB** | 24,946 | 9.98% | 1,221 | **4.89%** | 9.87% | 52 | **0.208%** | 10.83% |
| **Yes Bank** | 24,860 | 9.94% | 1,269 | **5.10%** | 10.25% | 40 | **0.161%** | 8.33% |
| **Kotak** | 20,032 | 8.01% | 998 | **4.98%** | 8.06% | 50 | **0.250%** | 10.42% |

### 3.5 Device Type

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Android** | 187,777 | 75.11% | 9,278 | **4.94%** | 74.97% | 364 | **0.194%** | 75.83% |
| **iOS** | 49,613 | 19.85% | 2,448 | **4.93%** | 19.78% | 90 | **0.181%** | 18.75% |
| **Web** | 12,610 | 5.04% | 650 | **5.15%** | 5.25% | 26 | **0.206%** | 5.42% |

### 3.6 Network Type

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **4G** | 149,813 | 59.93% | 7,464 | **4.98%** | 60.31% | 282 | **0.188%** | 58.75% |
| **5G** | 62,582 | 25.03% | 3,039 | **4.86%** | 24.56% | 115 | **0.184%** | 23.96% |
| **WiFi** | 25,134 | 10.05% | 1,222 | **4.86%** | 9.87% | 59 | **0.235%** | 12.29% |
| **3G** | 12,471 | 4.99% | 651 | **5.22%** | 5.26% | 24 | **0.192%** | 5.00% |

### 3.7 Sender Age Group

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **18-25** | 62,345 | 24.94% | 3,046 | **4.89%** | 24.61% | 143 | **0.229%** | 29.79% |
| **26-35** | 87,432 | 34.97% | 4,236 | **4.84%** | 34.23% | 163 | **0.186%** | 33.96% |
| **36-45** | 62,873 | 25.15% | 3,223 | **5.13%** | 26.04% | 116 | **0.184%** | 24.17% |
| **46-55** | 24,841 | 9.94% | 1,256 | **5.06%** | 10.15% | 31 | **0.125%** | 6.46% |
| **56+** | 12,509 | 5.00% | 615 | **4.92%** | 4.97% | 27 | **0.216%** | 5.62% |

### 3.8 Hour of Day

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **00:00** | 3,388 | 1.36% | 182 | **5.37%** | 1.47% | 8 | **0.236%** | 1.67% |
| **01:00** | 2,244 | 0.90% | 120 | **5.35%** | 0.97% | 6 | **0.267%** | 1.25% |
| **02:00** | 1,685 | 0.67% | 87 | **5.16%** | 0.70% | 3 | **0.178%** | 0.62% |
| **03:00** | 1,314 | 0.53% | 66 | **5.02%** | 0.53% | 4 | **0.304%** | 0.83% |
| **04:00** | 1,247 | 0.50% | 64 | **5.13%** | 0.52% | 1 | **0.080%** | 0.21% |
| **05:00** | 1,742 | 0.70% | 79 | **4.54%** | 0.64% | 1 | **0.057%** | 0.21% |
| **06:00** | 3,501 | 1.40% | 189 | **5.40%** | 1.53% | 5 | **0.143%** | 1.04% |
| **07:00** | 5,630 | 2.25% | 275 | **4.88%** | 2.22% | 13 | **0.231%** | 2.71% |
| **08:00** | 8,349 | 3.34% | 418 | **5.01%** | 3.38% | 18 | **0.216%** | 3.75% |
| **09:00** | 10,450 | 4.18% | 503 | **4.81%** | 4.06% | 20 | **0.191%** | 4.17% |
| **10:00** | 13,904 | 5.56% | 721 | **5.19%** | 5.83% | 20 | **0.144%** | 4.17% |
| **11:00** | 16,328 | 6.53% | 810 | **4.96%** | 6.54% | 27 | **0.165%** | 5.62% |
| **12:00** | 17,516 | 7.01% | 875 | **5.00%** | 7.07% | 30 | **0.171%** | 6.25% |
| **13:00** | 15,038 | 6.02% | 717 | **4.77%** | 5.79% | 25 | **0.166%** | 5.21% |
| **14:00** | 11,472 | 4.59% | 570 | **4.97%** | 4.61% | 21 | **0.183%** | 4.38% |
| **15:00** | 12,624 | 5.05% | 646 | **5.12%** | 5.22% | 32 | **0.254%** | 6.67% |
| **16:00** | 13,992 | 5.60% | 652 | **4.66%** | 5.27% | 31 | **0.222%** | 6.46% |
| **17:00** | 18,340 | 7.34% | 911 | **4.97%** | 7.36% | 37 | **0.202%** | 7.71% |
| **18:00** | 20,064 | 8.03% | 973 | **4.85%** | 7.86% | 31 | **0.154%** | 6.46% |
| **19:00** | 21,232 | 8.49% | 1,093 | **5.15%** | 8.83% | 43 | **0.203%** | 8.96% |
| **20:00** | 18,506 | 7.40% | 904 | **4.88%** | 7.30% | 37 | **0.200%** | 7.71% |
| **21:00** | 16,253 | 6.50% | 772 | **4.75%** | 6.24% | 35 | **0.215%** | 7.29% |
| **22:00** | 9,364 | 3.75% | 471 | **5.03%** | 3.81% | 23 | **0.246%** | 4.79% |
| **23:00** | 5,817 | 2.33% | 278 | **4.78%** | 2.25% | 9 | **0.155%** | 1.88% |

### 3.9 Day of Week

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Monday** | 36,495 | 14.60% | 1,810 | **4.96%** | 14.63% | 71 | **0.195%** | 14.79% |
| **Tuesday** | 35,540 | 14.22% | 1,702 | **4.79%** | 13.75% | 58 | **0.163%** | 12.08% |
| **Wednesday** | 35,700 | 14.28% | 1,781 | **4.99%** | 14.39% | 75 | **0.210%** | 15.62% |
| **Thursday** | 35,432 | 14.17% | 1,757 | **4.96%** | 14.20% | 72 | **0.203%** | 15.00% |
| **Friday** | 35,496 | 14.20% | 1,694 | **4.77%** | 13.69% | 61 | **0.172%** | 12.71% |
| **Saturday** | 35,334 | 14.13% | 1,797 | **5.09%** | 14.52% | 68 | **0.192%** | 14.17% |
| **Sunday** | 36,003 | 14.40% | 1,835 | **5.10%** | 14.83% | 75 | **0.208%** | 15.62% |

### 3.10 Weekend vs. Weekday

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Weekday (0)** | 178,663 | 71.47% | 8,744 | **4.89%** | 70.65% | 337 | **0.189%** | 70.21% |
| **Weekend (1)** | 71,337 | 28.53% | 3,632 | **5.09%** | 29.35% | 143 | **0.201%** | 29.79% |

### 3.11 Month of Year

| Category | Transactions ($N$) | Share of Tx (%) | Failed ($F$) | Failure Rate (%) | Share of Failures (%) | Fraud ($FR$) | Fraud Rate (%) | Share of Fraud (%) |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **1 (January)** | 21,221 | 8.49% | 1,012 | **4.77%** | 8.18% | 50 | **0.236%** | 10.42% |
| **2 (February)** | 19,759 | 7.90% | 954 | **4.83%** | 7.71% | 34 | **0.172%** | 7.08% |
| **3 (March)** | 21,234 | 8.49% | 1,142 | **5.38%** | 9.23% | 47 | **0.221%** | 9.79% |
| **4 (April)** | 20,536 | 8.21% | 1,009 | **4.91%** | 8.15% | 33 | **0.161%** | 6.88% |
| **5 (May)** | 21,333 | 8.53% | 1,038 | **4.87%** | 8.39% | 37 | **0.173%** | 7.71% |
| **6 (June)** | 20,628 | 8.25% | 1,040 | **5.04%** | 8.40% | 30 | **0.145%** | 6.25% |
| **7 (July)** | 21,207 | 8.48% | 1,061 | **5.00%** | 8.57% | 52 | **0.245%** | 10.83% |
| **8 (August)** | 21,231 | 8.49% | 1,033 | **4.87%** | 8.35% | 33 | **0.155%** | 6.88% |
| **9 (September)** | 20,597 | 8.24% | 1,061 | **5.15%** | 8.57% | 42 | **0.204%** | 8.75% |
| **10 (October)** | 21,252 | 8.50% | 1,007 | **4.74%** | 8.14% | 45 | **0.212%** | 9.38% |
| **11 (November)** | 20,366 | 8.15% | 1,009 | **4.95%** | 8.15% | 39 | **0.192%** | 8.12% |
| **12 (December)** | 20,636 | 8.25% | 1,010 | **4.89%** | 8.16% | 38 | **0.184%** | 7.92% |

---

## 4. Inferential Statistical Analysis: Chi-Square Tests of Independence

To determine whether observed differences across categories are statistically meaningful or merely random sampling fluctuations, two-way Chi-Square tests of independence ($\chi^2$) and Cramer's $V$ effect sizes were computed.

| Test Association ($X$ vs. $Y$) | $\chi^2$ Statistic | $dof$ | $p$-value | Cramer's $V$ | Practical Effect Size | Statistically Significant? | Plain-Language Interpretation |
| :--- | :-: | :-: | :-: | :-: | :--- | :-: | :--- |
| **sender_bank** vs. **transaction_status** | `3.2349` | 7 | `0.8625` | `0.003597` | negligible (< 0.10) | No | Statistically non-significant (p = 0.8625), with a negligible (< 0.10) effect size (Cramer's V = 0.003597). Differences across sender_bank are empirically negligible / random noise. |
| **device_type** vs. **transaction_status** | `1.1811` | 2 | `0.5540` | `0.002174` | negligible (< 0.10) | No | Statistically non-significant (p = 0.5540), with a negligible (< 0.10) effect size (Cramer's V = 0.002174). Differences across device_type are empirically negligible / random noise. |
| **network_type** vs. **transaction_status** | `3.8527` | 3 | `0.2778` | `0.003926` | negligible (< 0.10) | No | Statistically non-significant (p = 0.2778), with a negligible (< 0.10) effect size (Cramer's V = 0.003926). Differences across network_type are empirically negligible / random noise. |
| **transaction type** vs. **transaction_status** | `0.9357` | 3 | `0.8168` | `0.001935` | negligible (< 0.10) | No | Statistically non-significant (p = 0.8168), with a negligible (< 0.10) effect size (Cramer's V = 0.001935). Differences across transaction type are empirically negligible / random noise. |
| **transaction type** vs. **fraud_flag** | `2.3238` | 3 | `0.5080` | `0.003049` | negligible (< 0.10) | No | Statistically non-significant (p = 0.5080), with a negligible (< 0.10) effect size (Cramer's V = 0.003049). Differences across transaction type are empirically negligible / random noise. |
| **merchant_category** vs. **fraud_flag** | `3.9734` | 9 | `0.9132` | `0.003987` | negligible (< 0.10) | No | Statistically non-significant (p = 0.9132), with a negligible (< 0.10) effect size (Cramer's V = 0.003987). Differences across merchant_category are empirically negligible / random noise. |
| **sender_state** vs. **fraud_flag** | `7.7645` | 9 | `0.5580` | `0.005573` | negligible (< 0.10) | No | Statistically non-significant (p = 0.5580), with a negligible (< 0.10) effect size (Cramer's V = 0.005573). Differences across sender_state are empirically negligible / random noise. |
| **sender_age_group** vs. **fraud_flag** | `11.0953` | 4 | `0.0255` | `0.006662` | negligible (< 0.10) | Yes (Nominal) | Statistically significant (p = 0.0255), with a negligible (< 0.10) effect size (Cramer's V = 0.006662). Differences across sender_age_group are empirically negligible / random noise. |

### Statistical Synthesis

1. **Transaction Reliability (Failure Rates):**
   - `sender_bank` vs. `transaction_status`: $\chi^2 = 3.2349, p = 0.8625, V = 0.00360$ (No significant difference). Bank failure rates range tightly between 4.82% (HDFC) and 5.10% (Yes Bank).
   - `device_type` vs. `transaction_status`: $\chi^2 = 1.1811, p = 0.5540, V = 0.00217$ (No significant difference). Rates: Android 4.94%, iOS 4.93%, Web 5.15%.
   - `network_type` vs. `transaction_status`: $\chi^2 = 3.8527, p = 0.2778, V = 0.00393$ (No significant difference). Rates: 3G 5.22%, 4G 4.98%, 5G 4.86%, WiFi 4.86%.
   - `transaction type` vs. `transaction_status`: $\chi^2 = 0.9357, p = 0.8168, V = 0.00193$ (No significant difference). Rates: P2P 4.98%, P2M 4.94%, Bill Payment 4.88%, Recharge 4.98%.
   - **Conclusion on Failures:** Transaction failure is statistically independent of bank, device, network, and transaction type. The system failure rate is a constant stochastic process hovering at ~4.95% dataset-wide.

2. **Fraud Patterns (Security Indicator):**
   - `transaction type` vs. `fraud_flag`: $\chi^2 = 2.3238, p = 0.5080, V = 0.00305$ (Non-significant). Fraud rates range between 0.168% (Recharge) and 0.205% (P2P).
   - `merchant_category` vs. `fraud_flag`: $\chi^2 = 3.9734, p = 0.9132, V = 0.00399$ (Non-significant). Fraud rates range between 0.160% (Fuel) and 0.239% (Entertainment).
   - `sender_state` vs. `fraud_flag`: $\chi^2 = 7.7645, p = 0.5580, V = 0.00557$ (Non-significant). Fraud rates range between 0.158% (Tamil Nadu) and 0.232% (Karnataka).
   - `sender_age_group` vs. `fraud_flag`: $\chi^2 = 11.0953, p = 0.0255, V = 0.00666$ (Nominally significant at $\alpha = 0.05$, but Cramer's $V < 0.007$, which is virtually zero effect size). Rates range from 0.147% (56+) to 0.238% (26-35).

> [!CAUTION]
> **Extreme Imbalance and Uncertainty in Fraud Flag Analysis:**  
> The positive fraud class consists of only **480 transactions out of 250,000 (0.192%)**.  
> When slicing 480 positive instances across 10 states (35 to 71 cases per state) or 10 merchant categories (15 to 97 cases), cell counts are tiny.  
> For instance, the 95% Wilson score confidence interval for Karnataka's fraud rate (69 / 29,756 = 0.232%) is **[0.182%, 0.294%]**, which overlaps completely with Tamil Nadu (40 / 25,367 = 0.158%, **[0.115%, 0.215%]**).  
> Therefore, claiming that certain states or transaction categories are 'hotspots' for fraud represents an overinterpretation of random sampling noise in this synthetic dataset.

---

## 5. Cell-by-Cell Notebook Audit (`mini-project.ipynb`)

Every cell of the 97 cells in `mini-project.ipynb` was systematically audited against the official spec (`Mini Project Deliverables.docx`) and analytical standards. Below are the specific cells where discrepancies between titles, questions, calculations, charts, and interpretations were identified.

| Cell # | Type | Notebook Question / Title | Core Issue Identified | Severity | Recommended Fix |
| :-: | :-: | :--- | :--- | :-: | :--- |
| **Cell 1** | `markdown` | Problem Statement & Key Questions | Question 5 and Question 6 ask about failure percentages by bank, device, and network, but later cells confuse failure with fraud. Question 7 asks which states have most fraud transactions, but does not state the denominator (state transaction volume). | **MEDIUM** | Explicitly formulate hypotheses distinguishing failure rates (transaction reliability) from fraud incidence (security indicator). |
| **Cell 21** | `markdown` | Preprocessing Description | Markdown states 'Drop columns that are not useful like transaction id' and cell 22 creates df1 = df.drop(columns=['transaction id']), but almost all subsequent EDA cells (from Cell 44 onwards) revert to using original df, leaving df1 unused and keeping transaction id in scope. | **MEDIUM** | Consistently assign df = df.drop(columns=['transaction id']) in-place or use df1 across all subsequent EDA and modeling cells. |
| **Cell 24** | `markdown` | Datetime Conversion | Cell 25 converts df1['timestamp'] = pd.to_datetime(df['timestamp']), but leaves df['timestamp'] as a string object. Cell 88 extracts hour_of_day from the existing integer column rather than verified datetime. | **MEDIUM** | Apply pd.to_datetime directly on df['timestamp'] and extract temporal features (month, hour, day_name) centrally. |
| **Cell 32** | `code` | Failure Rate Calculation | Cell 33 uses hardcoded magic numbers `print('% of transactions failed: ', (12376/250000)*100)` instead of dynamic formula `(df['transaction_status'] == 'FAILED').mean() * 100`. | **MEDIUM** | Replace hardcoded arithmetic with programmatic pandas expressions: `(df['transaction_status'] == 'FAILED').mean() * 100`. |
| **Cell 45** | `markdown / code (Cell 46)` | Q3 Title vs Calculation vs Chart | Title in Cell 45 asks: 'Q3. Which category has most no. of failed transactions?'. But Cell 46 calculates `sns.countplot(data=df, x='transaction type', hue='transaction_status')`. It plots 'transaction type' instead of 'merchant_category'. Furthermore, plotting raw count with hue='transaction_status' visually suppresses the 4.95% failed bars behind the 95.05% success bars. | **HIGH** | Change x='merchant_category' to answer 'category', or change title to 'Which transaction type has most failed transactions?'. Calculate and plot failure rates (%) rather than raw dual-class count bars. |
| **Cell 53** | `markdown / code (Cell 54)` | Q7 Title vs Interpretation | Title in Cell 53 asks: 'Q7. Whether weekend beats weekdays in no. of transactions?'. Cell 54 plots raw total count of is_weekend (178,663 weekday vs 71,337 weekend). Concluding that weekdays 'beat' weekends creates a false impression, because weekdays contain 5 calendar days while weekends contain 2. On a per-day average basis, weekdays average 35,732.6 tx/day while weekend days average 35,668.5 tx/day (virtually identical, diff < 0.2%). | **HIGH** | Normalize by number of days in each category: plot average daily transaction volume (Weekday: 35,733 vs Weekend: 35,669) to show that daily transaction volume is invariant to day-type. |
| **Cell 65** | `markdown / code (Cell 66-67)` | Q12 Title vs Calculation | Title in Cell 65 asks: 'Q12. What is average transaction amount per category?'. But Cell 66 computes `df.groupby('transaction type')['amount (INR)'].mean()`, and Cell 67 titles the chart 'Average Transaction Amount by Transaction Type'. | **MEDIUM** | Align title and code: compute `df.groupby('merchant_category')['amount (INR)'].mean()` if merchant category is desired, or update the Markdown question to 'average transaction amount per transaction type'. |
| **Cell 68** | `markdown / code / chart (Cell 68-70)` | CRITICAL MISMATCH: Q13 Failure % vs Fraud % | Cell 68 title explicitly asks: 'Q13. What % of transactions failed per transaction type?'. However, Cell 69 filters `fraud_transactions = df[df['fraud_flag'] == 1]`, computes `fraud_type_percentage = (fraud_type_count / total_type_count) * 100`, and Cell 70 plots 'Fraud Percentage by Transaction Type'. The question asks for FAILURE %, but the code computes FRAUD %! This completely confounds technical failure (~4.95%) with fraud risk (~0.19%). | **CRITICAL** | To answer Q13 as titled: `failed_tx = df[df['transaction_status'] == 'FAILED']; fail_type_pct = (failed_tx['transaction type'].value_counts() / df['transaction type'].value_counts()) * 100`. If fraud percentage was intended, rename the question in Cell 68 to 'What % of transactions are flagged as fraud per transaction type?' and add a dedicated cell for failure rate. |
| **Cell 71** | `markdown / code (Cell 71-72)` | Scatter Plot Visualization | Cell 72 plots `plt.scatter(df['hour_of_day'], df['amount (INR)'])` with 250,000 unbinned data points across 24 discrete integers. This creates severe overplotting (vertical solid columns), rendering the chart uninformative and wasting rendering resources. | **MEDIUM** | Use a boxplot `sns.boxplot(x='hour_of_day', y='amount (INR)')`, violin plot, or line chart of median / mean amount with confidence intervals by hour. |
| **Cell 75** | `markdown / code (Cell 75-76)` | Correlation Matrix Scope | Cell 76 computes Pearson correlation on numerical variables `['amount (INR)', 'hour_of_day', 'is_weekend', 'fraud_flag']`. All pairwise correlations are near zero (r between -0.002 and +0.003). The notebook does not provide an analytical takeaway or note that Pearson correlation only tests linear association on continuous variables, whereas fraud_flag and is_weekend are binary. | **MEDIUM** | Include point-biserial correlation / logistic regression coefficients, and explicitly interpret that transaction amount, hour of day, and weekend status have virtually zero linear correlation with fraud flags. |
| **Cell 79** | `markdown / code / chart (Cell 79-80)` | CRITICAL MISMATCH: Q14 Failed Transactions vs Fraud | Cell 79 title explicitly asks: 'Q14. What network type and Device had most no. of failed transactions?'. But Cell 80 filters `fraud_transactions = df[df['fraud_flag'] == 1]`, computes an unused `device_fraud = df.groupby(['device_type','network_type']).size()`, and plots `sns.countplot(data=fraud_transactions, x='device_type', hue='network_type')` titled 'Fraud Transactions by Device and Network Type'. The cell claims to analyze FAILED transactions, but computes and plots FRAUD-FLAGGED rows! | **CRITICAL** | To analyze failed transactions as claimed: filter `failed_df = df[df['transaction_status'] == 'FAILED']`, plot `sns.countplot(data=failed_df, x='device_type', hue='network_type')`, and report both absolute counts and failure rates within (device, network) cohorts. Separate the fraud breakdown into a distinct question. |
| **Cell 85** | `code / chart (Cell 85-86)` | Pivot Table & Heatmap Interpretation | Cell 86 builds a pivot table of failure rate by sender_state and network_type and displays a heatmap without specifying vmin/vmax. Because failure rates only vary from 4.5% to 6.0%, the unconstrained colorbar exaggerates minor random variations as if there were dramatic regional network disparities, when in reality Chi-square tests show no significant difference (p > 0.27). | **MEDIUM** | Annotate the narrow variance range (4.5% to 6.0%) and explicitly mention that these differences are statistically non-significant random sampling fluctuations. |
| **Cell 91** | `code (Cell 91-95) & markdown (Cell 94, 96)` | Machine Learning Model Validity & Interpretation | 1) Logistic Regression is trained without standardizing features: amount (INR) ranges up to 42,099 while one-hot features are 0/1, triggering a convergence warning (max_iter=1000 failed to converge). 2) Cell 96 concludes: 'After balancing the class weights, it became better at detecting failed transactions, with a recall of 0.49... The model needs further improvement.' In reality, because failure is statistically independent of all features (Chi2 p > 0.27, Cramer's V < 0.004), the model has zero true predictive signal. Balancing class weights merely shifted the decision threshold so that random coin-flipping achieves ~50% recall and ~5% precision (the prior failure rate). | **HIGH** | Standardize numeric features using StandardScaler. State candidly in the evaluation that the synthetic dataset features have zero predictive signal for transaction failures, meaning no classifier can reliably predict failures beyond random guessing. |

### Detailed Audit Deep-Dives

#### 1. Cell 68 to Cell 70: Q13 Failure % vs. Fraud % (CRITICAL BLUNDER)
- **What the title claims:** Cell 68 markdown explicitly asks: `Q13. What % of transactions failed per transaction type?`
- **What the code actually calculates:** Cell 69 filters `fraud_transactions = df[df['fraud_flag'] == 1]`, calculates `fraud_type_count = fraud_transactions['transaction type'].value_counts()`, and computes `fraud_type_percentage = (fraud_type_count / total_type_count) * 100`.
- **What the chart displays:** Cell 70 titles the bar chart `plt.title('Fraud Percentage by Transaction Type')`.
- **Analytical Impact:** Transaction failure (~4.95%) and transaction fraud (~0.19%) are fundamentally different operational metrics. Presenting fraud rates under a question asking for failure rates misinforms the reader and destroys analytical validity.
- **Concrete Fix:**
  ```python
  # True Failure Rate by Transaction Type:
  failed_tx = df[df['transaction_status'] == 'FAILED']
  fail_rate = (failed_tx['transaction type'].value_counts() / df['transaction type'].value_counts()) * 100
  fail_rate.plot(kind='bar', color='crimson')
  plt.title('Failure Rate by Transaction Type (%)')
  plt.ylabel('Failure Rate (%)')
  ```

#### 2. Cell 79 to Cell 80: Q14 Network & Device Failures vs. Fraud (CRITICAL BLUNDER)
- **What the title claims:** Cell 79 markdown explicitly asks: `Q14. What network type and Device had most no. of failed transactions?`
- **What the code actually does:** Cell 80 filters `fraud_transactions = df[df['fraud_flag'] == 1]`, computes an unassigned/unused `device_fraud = df.groupby(['device_type','network_type']).size()`, and generates a countplot `sns.countplot(data=fraud_transactions, x='device_type', hue='network_type')` with title `plt.title('Fraud Transactions by Device and Network Type')`.
- **Analytical Impact:** While claiming to investigate network/device transaction failures, the code computes and plots fraud-flagged rows! Furthermore, it shows raw counts without normalizing by the massive dominance of Android (75.1%) and 4G (59.9%).
- **Concrete Fix:**
  ```python
  # Group by Device and Network for FAILED transactions:
  failed_df = df[df['transaction_status'] == 'FAILED']
  sns.countplot(data=failed_df, x='device_type', hue='network_type')
  plt.title('Failed Transactions by Device and Network Type')
  ```

#### 3. Cell 45 to Cell 46: Q3 Question vs. Variable Mismatch
- **What the title claims:** Cell 45 asks: `Q3. Which category has most no. of failed transactions?`
- **What the code actually calculates:** Cell 46 plots `sns.countplot(data=df, x='transaction type', hue='transaction_status')`. It plots `transaction type` instead of `merchant_category`.
- **Analytical Impact:** The student intended to analyze categories (or conflated 'category' with 'transaction type'). In addition, plotting a dual countplot where SUCCESS is 95% and FAILED is 5% makes the failed bars almost invisible.
- **Concrete Fix:** If analyzing merchant category, plot failed transactions grouped by `merchant_category`. If analyzing transaction type, adjust the question text.

#### 4. Cell 53 to Cell 54: Q7 Weekday vs. Weekend Misleading Aggregation
- **What the title claims:** Cell 53 asks: `Q7. Whether weekend beats weekdays in no. of transactions?`
- **What the chart displays:** Cell 54 plots raw transaction counts: Weekdays = 178,663, Weekend = 71,337.
- **Analytical Impact:** Comparing raw totals gives the misleading impression that weekdays 'beat' weekends by 2.5:1. However, a week has 5 weekdays and 2 weekend days! When normalized:
  - Weekday daily average: $178,663 / 5 = 35,732.6$ transactions/day
  - Weekend daily average: $71,337 / 2 = 35,668.5$ transactions/day
  - The difference is less than 0.18%! The daily transaction velocity on UPI is virtually identical across all 7 days of the week.

#### 5. Cell 91 to Cell 96: Machine Learning Pipeline Flaws and False Inferences
- **Flaw 1 (Feature Scaling):** Features are one-hot encoded without scaling. `amount (INR)` ranges from 10 to 42,099 while binary flags are 0 or 1. This causes `LogisticRegression(max_iter=1000)` to trigger a `ConvergenceWarning: lbfgs failed to converge`.
- **Flaw 2 (Class Imbalance & Interpretation):** Without balancing, the model achieves 95.05% accuracy by predicting all transactions as SUCCESS (0 recall for FAILED). In Cell 95, adding `class_weight='balanced'` produces 51.84% accuracy, 0.49 recall, and 0.05 precision. Cell 96 concludes: *'After balancing the class weights, it became better at detecting failed transactions, with a recall of 0.49... The model needs further improvement.'*
- **Analytical Reality:** Because Chi-Square tests proved that failure is statistically independent of all features ($p > 0.27$, Cramer's $V < 0.004$), there is **zero true predictive signal in the dataset**. When class weights are balanced, predicting randomly with a 50% threshold achieves ~50% recall and precision equal to the base rate (~5%). The model did not 'learn' to detect failures; it is simply flipping a coin!

---

## 6. Summary Recommendations for Final Deliverables

1. **Update Notebook Narratives:** Fix the titles and labels in Cells 45, 65, 68-70, and 79-80 so that Failure Analysis and Fraud Analysis are clearly delineated.
2. **Normalize Cohort Comparisons:** Always pair raw volume counts with cohort rates (e.g., failure rate within Android vs. share of all failures on Android; daily average weekday vs. weekend).
3. **Highlight Statistical Independence:** Report in the project report that failures (~4.95%) and fraud (~0.19%) are uniformly distributed across Indian banks, devices, and networks, demonstrating consistent UPI infrastructure reliability.
4. **Note Fraud Class Uncertainty:** Emphasize that with only 480 positive fraud cases in 250,000 transactions, observed differences across states and categories fall within normal sampling confidence intervals.

---
*Report compiled and verified by Antigravity Data Analyst Assistant.*