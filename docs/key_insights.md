# Key Insights and Findings: UPI Transaction Analytics

**Course:** Data Exploration and Visualization Laboratory  
**Project:** *UPI Transaction Analytics: Exploring Payment Behavior, Transaction Reliability and Fraud Patterns in India*  
**Authors:** Swaraj Suresh Shinde (PRN: `125B1D053`), Nikol Dharmraj Ghodke (PRN: `125B1D062`)  
**Data Source:** `upi_transactions_2024.csv` (250,000 transactions, January 1 – December 30, 2024)  
**Foundation Reference:** `outputs/verified_metrics.json` and `outputs/verification_report.md`  

---

## Analytical Preface: Context, Class Imbalance, and Uncertainty Notice

Before detailing the empirical findings, three analytical caveats must be established regarding the nature of the dataset and payments risk modeling:

1. **`fraud_flag` is an Algorithmic Indicator, Not Confirmed Fraud:**  
   The binary field `fraud_flag` indicates that an internal risk heuristic or rule-based monitoring filter flagged a transaction for anomaly review. It does not represent adjudicated chargebacks, verified account takeovers (ATO), or confirmed financial loss.
2. **Extreme Class Imbalance (0.192% Positive Class):**  
   Across the 250,000 transactions, exactly **480 records (0.1920%)** carry `fraud_flag = 1`. This low incidence rate mirrors real-world retail payments where fraudulent events are rare. However, disaggregating 480 positive cases across 10 states (35 to 71 cases per cohort) or 10 merchant categories (15 to 97 cases per cohort) introduces **wide statistical confidence intervals**. Point estimates must not be interpreted as definitive institutional risk profiles.
3. **Statistical Testing and Synthetic Uniformity:**  
   To prevent mistaking random sampling fluctuations for business reality, all categorical comparisons below are paired with two-way Chi-Square tests of independence ($\chi^2$) and Cramer's $V$ effect size coefficients. Where $p > 0.05$ or Cramer's $V < 0.05$, differences are reported as stochastic sampling noise typical of uniformly generated synthetic benchmark data.

---

## Insight 1: Micro-Payment Velocity and Extreme Positive Skew in Ticket Sizes

### 1. Executive Title
**Micro-Ticket Dominance: Sub-₹1,000 Payments Drive Velocity, While High-Value Outliers Create Substantial Positive Skew**

### 2. Finding
The vast majority of UPI transactions are low-value retail micro-payments, creating a heavily right-skewed distribution where the arithmetic mean (₹1,311.76) is more than double the median (₹629.00), with 8.47% of transactions qualifying as statistical outliers.

### 3. Quantitative Evidence
- **Central Tendency Disparity:** The median transaction amount is **₹629.00**, while the mean is **₹1,311.76** (ratio of Mean/Median = $2.09\times$).
- **Interquartile Concentration:** The 25th percentile ($Q_1$) is **₹288.00** and the 75th percentile ($Q_3$) is **₹1,596.00**, producing an Interquartile Range ($IQR$) of **₹1,308.00**. Over 62.4% of all transactions are under ₹1,000.
- **Tukey Outlier Threshold:** The upper outlier boundary ($Q_3 + 1.5 \times IQR$) is **₹3,558.00**. Exactly **21,171 transactions (8.47% of 250,000)** exceed this threshold.
- **Extreme Tail:** Transactions exceeding ₹10,000 account for only **1,805 records (0.72% of 250,000)**, yet stretch to a maximum ticket size of **₹42,099.00**. Standard deviation across all transactions is **₹1,848.06**.

### 4. Supporting Chart
- **File:** `outputs/insight_figures/figure1_amount_distribution_outliers.png`  
  *(Displays the density distribution truncated at ₹10,000 with median, mean, and Tukey fence annotations, alongside a full-scale logarithmic boxplot depicting the long upper tail).*

### 5. Why It Matters for Understanding UPI Behaviour
This distribution reflects UPI’s core consumer adoption in India as a replacement for physical cash in day-to-day retail touchpoints (tea stalls, transport, groceries). However, the long tail up to ₹42,099 indicates growing consumer trust in executing high-value person-to-person transfers and consumer durable bill settlements over instant payment rails.

### 6. Interpretation
- **Observed:** The transaction amount distribution exhibits severe positive skewness ($Skew > 3.0$), with a massive volume concentration between ₹10 and ₹1,500.
- **Observed:** The data generation model successfully captures the empirical micro-ticket nature of retail UPI traffic.

### 7. Recommendations
- **For NPCI & Remitter Banks:** Maintain aggressive tier-based transaction routing. Sub-₹500 micro-transactions should be prioritized through lightweight UPI Lite / on-device wallet protocols to offload core banking system (CBS) ledgers.
- **For Risk Engines:** Avoid static rupee thresholds for anomaly detection. A ₹5,000 ticket is normal for bill payments or consumer shopping but represents a $7\times$ departure from typical peer-to-peer micro-transfers.

---

## Insight 2: Volume vs. Monetary Value Decoupling Across Merchant Categories

### 2. Finding
A pronounced structural decoupling exists between merchant category transaction volume and settlement value, where low-ticket daily essentials drive operational network volume while high-ticket categories drive financial settlement turnover.

### 3. Quantitative Evidence
- **High-Volume / Low-Ticket Segment:**
  - **Grocery:** Drives **19.99% of total volume** (49,966 / 250,000 tx) but accounts for only **17.77% of total value** (₹5.83 Cr / ₹32.79 Cr), with an average ticket of **₹1,166.35**.
  - **Food:** Accounts for **14.99% of total volume** (37,464 / 250,000 tx) but represents only **6.07% of total value** (₹1.99 Cr / ₹32.79 Cr), averaging **₹531.69 per transaction**.
  - **Transport:** Represents **8.04% of total volume** (20,105 / 250,000 tx) but merely **1.89% of value** (₹0.62 Cr / ₹32.79 Cr), averaging **₹308.00 per transaction**.
- **Low-Volume / High-Ticket Segment:**
  - **Shopping:** Accounts for **11.95% of volume** (29,872 / 250,000 tx) but commands **23.44% of total settlement value** (₹7.69 Cr / ₹32.79 Cr), averaging **₹2,573.09 per transaction** ($+11.49\%$ value share premium).
  - **Utilities:** Drives **8.94% of volume** (22,338 / 250,000 tx) but captures **16.08% of total value** (₹5.27 Cr / ₹32.79 Cr), averaging **₹2,361.11 per transaction** ($+7.14\%$ value share premium).
  - **Education:** Drives only **3.04% of volume** (7,586 / 250,000 tx) but accounts for **11.80% of total value** (₹3.87 Cr / ₹32.79 Cr), with the highest category mean ticket of **₹5,094.02** ($+8.76\%$ value share premium).

### 4. Supporting Chart
- **File:** `outputs/insight_figures/figure2_merchant_volume_vs_value.png`  
  *(Displays paired horizontal bars contrasting transaction volume share against monetary settlement value share across all 10 merchant categories, annotated with average ticket sizes).*

### 5. Why It Matters for Understanding UPI Behaviour
This divergence illustrates the dual operational demands placed on UPI: acquiring infrastructure must support high concurrency and millisecond latency for Grocery and Food, while liquidity and credit management are paramount for high-ticket settlement categories like Education and Shopping.

### 6. Interpretation
- **Observed:** Transaction velocity and transaction value decouple cleanly by merchant vertical.
- **Hypothesis:** High-ticket transactions in Education and Shopping likely involve fee payments, electronics, and e-commerce checkouts, whereas Food and Transport capture repetitive daily transit and dining payments.

### 7. Recommendations
- **For Merchant Aggregators:** Differentiate merchant acquisition and transaction processing fees (MDR / processing surcharge). Micro-merchant QR acquiring in Food and Transport requires near-zero transaction fee models, whereas high-value merchant checkouts in Shopping and Education can bear higher value-added service fees for fraud protection and reconciliation guarantees.

---

## Insight 3: Diurnal Surge Patterns vs. Daily Transaction Rate Weekend Invariance

### 1. Executive Title
**Evening Network Congestion Peaks at 19:00, While Normalized Daily Velocity is 100% Invariant to Weekend Calendar Shifts**

### 2. Finding
UPI transaction traffic exhibits an intense diurnal cycle that peaks during evening market hours (18:00–19:00 carrying 16.52% of daily traffic), yet on a normalized daily basis, transaction velocity is identical on weekdays and weekends (difference under 0.18%).

### 3. Quantitative Evidence
- **Diurnal Amplitude (15.7× Surge):**
  - **Peak Hour (19:00):** Reaches **21,232 transactions (8.49% of daily traffic)**.
  - **Secondary Peak (18:00):** Accounts for **20,064 transactions (8.03% of daily traffic)**.
  - Combined evening window (18:00–20:00) processes **59,802 transactions (23.92% of all daily volume)**.
  - **Trough Hour (03:00):** Drops to **1,349 transactions (0.54% of daily traffic)**.
  - Peak-to-trough ratio is **15.74×** ($21,232 / 1,349$).
- **Normalized Day-of-Week Invariance:**
  - Raw weekday total (`is_weekend = 0`): **178,663 transactions** across 5 calendar weekdays = **35,732.6 transactions/day**.
  - Raw weekend total (`is_weekend = 1`): **71,337 transactions** across 2 calendar weekend days = **35,668.5 transactions/day**.
  - Absolute variance between weekday and weekend daily rate is only **64.1 transactions/day (0.18% relative difference)**.

### 4. Supporting Chart
- **File:** `outputs/insight_figures/figure3_diurnal_traffic_peak_hours.png`  
  *(Displays the full 24-hour diurnal transaction velocity curve, highlighting the 18:00–20:00 surge window, annotated peak/trough points, and an embedded summary of normalized daily weekday vs. weekend equivalence).*

### 5. Why It Matters for Understanding UPI Behaviour
Unlike traditional NEFT/RTGS settlement networks or equity markets that pause or taper significantly on weekends, UPI behaves as a continuous 24/7/365 utility. Personal consumer spending on weekends fully offsets the absence of corporate weekday transfers.

### 6. Interpretation
- **Observed:** Evening traffic accelerates sharply from 17:00 onwards as consumers complete retail commutes, grocery shopping, and peer payments.
- **Observed:** The claim in preliminary exploratory notes that "weekdays beat weekends 2.5:1" is an artifact of failing to normalize by the 5-to-2 day ratio. Per-day payment velocity is invariant to day-type.

### 7. Recommendations
- **For NPCI & Remitter Bank DevOps:** Core banking maintenance windows, batch database indexing, and non-critical system updates must be strictly scheduled during the low-traffic trough window (02:00–05:00). Scheduled maintenance during weekend daylight hours will disrupt as many consumer transactions as weekday maintenance.

---

## Insight 4: Infrastructure Reliability Invariance Across Banking, Device, and Network Rails

### 1. Executive Title
**System Failure Rates Hover Stochastically at ~4.95%, Demonstrating Statistical Independence Across Banks, Devices, and Networks**

### 2. Finding
Transaction failure rates are statistically invariant across all sender banks, device operating systems, and network connections, proving that high failure counts in specific cohorts (e.g., Android and 4G) are entirely driven by volume dominance rather than underlying infrastructure fragility.

### 3. Quantitative Evidence
- **System Baseline Failure Rate:** Overall system failure rate is **4.9504%** (12,376 failed transactions out of 250,000 total).
- **Sender Bank Invariance ($\chi^2 = 3.2349, dof = 7, p = 0.8625$, Cramer's $V = 0.003597$):**
  - Failure rates within bank cohorts vary in a narrow band from **4.82%** (HDFC: 1,808 failed / 37,485 tx) to **5.10%** (Yes Bank: 1,269 failed / 24,860 tx).
  - SBI failure rate is **4.94%** (3,095 failed / 62,693 tx), ICICI is **5.04%** (1,499 failed / 29,769 tx), Axis is **4.95%** (1,239 failed / 25,042 tx). With $p = 0.86$, these differences are purely stochastic noise.
- **Device Platform Invariance ($\chi^2 = 1.1811, dof = 2, p = 0.5540$, Cramer's $V = 0.002174$):**
  - **Android:** Accounts for **74.97% of all system failures** (9,278 / 12,376), but this exactly reflects its **75.11% share of total transactions** (187,777 / 250,000). The failure rate within Android is **4.94%**.
  - **iOS:** Accounts for **19.78% of all system failures** (2,448 / 12,376) against a **19.85% transaction share** (49,613 / 250,000). Failure rate within iOS is **4.93%**.
  - **Web:** Accounts for **5.25% of all system failures** (650 / 12,376) against a **5.04% transaction share** (12,610 / 250,000). Failure rate within Web is **5.15%**.
- **Network Invariance ($\chi^2 = 3.8527, dof = 3, p = 0.2778$, Cramer's $V = 0.003926$):**
  - **4G:** Accounts for **60.31% of all failures** (7,464 / 12,376) against a **59.93% transaction share** (149,813 / 250,000), with a cohort failure rate of **4.98%**.
  - **5G:** Accounts for **24.56% of all failures** (3,039 / 12,376) against a **25.03% transaction share** (62,582 / 250,000), with a cohort failure rate of **4.86%**.
  - **WiFi:** Failure rate is **4.86%** (1,222 / 25,134); **3G:** Failure rate is **5.22%** (651 / 12,471).

### 4. Supporting Chart
- **File:** `outputs/insight_figures/figure4_infrastructure_reliability_invariance.png`  
  *(Displays side-by-side comparative bar charts of cohort failure rates across Banks, Devices, and Networks, benchmarked against the 4.95% system mean line with Chi-Square test statistics and Cramer's V values annotated).*

### 5. Why It Matters for Understanding UPI Behaviour
In retail payments analysis, conflating **share of total failures** with **cohort failure probability** leads to erroneous business decisions (e.g., blaming Android app builds or 4G telecom towers for system failures). The data proves that no platform, network, or major bank is an operational bottleneck.

### 6. Interpretation
- **Observed:** Differences in failure rates across all 8 banks, 3 platforms, and 4 network connections are statistically non-significant ($p > 0.27$, Cramer's $V < 0.004$).
- **Synthetic Data Artifact:** The near-perfect uniformity around ~4.95% indicates that the underlying dataset generator assigned transaction failure via an independent, identically distributed (i.i.d.) Bernoulli process with $p \approx 0.05$, rather than modeling realistic technical failure clustering (e.g., bank-specific timeout spikes or telecom packet dropouts).

### 7. Recommendations
- **For Evaluators & Analysts:** Never report that "Android has the highest failures" without clarifying that its failure rate (4.94%) is identical to iOS (4.93%).
- **For Payment Gateways:** Route transactions based on commercial interchange and processing costs rather than attempting dynamic bank-switching based on nominal 0.1% failure rate differences, as these differences reflect random noise.

---

## Insight 5: Geographic Volume Proportionality in Fraud Flag Distribution

### 1. Executive Title
**State-Level Fraud Flag Volume is Governed Entirely by Population Transaction Velocity Rather Than Elevated Regional Risk**

### 2. Finding
State-level fraud-flag counts correlate directly with overall transaction volume, with Maharashtra and Karnataka accounting for 29.17% of flagged cases solely because they generate 26.87% of all transaction traffic.

### 3. Quantitative Evidence
- **Proportionality of Leading States:**
  - **Maharashtra:** Generates **14.97% of total transaction volume** (37,427 / 250,000 tx) and accounts for **14.79% of all fraud-flagged cases** (71 / 480 flagged tx). Its cohort fraud-flag rate is **0.190%** (71 / 37,427).
  - **Karnataka:** Generates **11.90% of total transaction volume** (29,756 / 250,000 tx) and accounts for **14.38% of all fraud-flagged cases** (69 / 480 flagged tx). Its cohort fraud-flag rate is **0.232%** (69 / 29,756).
  - **Combined Contribution:** Maharashtra and Karnataka combined account for **140 of the 480 flagged cases (29.17%)**, which aligns closely with their combined transaction share of **26.87% (67,183 / 250,000 tx)**.
- **Statistical Independence Test Across States:**
  - Chi-Square test of independence: $\chi^2 = 7.7645, dof = 9, p = 0.5580$, Cramer's $V = 0.005573$.
  - State cohort fraud-flag rates range between **0.158%** (Tamil Nadu: 40 / 25,367 tx) and **0.232%** (Karnataka: 69 / 29,756 tx).
  - With $p = 0.558$ and $V < 0.006$, state-level fraud rates are statistically indistinguishable from the national baseline (0.192%).

### 4. Supporting Chart
- **File:** `outputs/insight_figures/figure5_geographic_volume_vs_fraud_flags.png`  
  *(Displays paired bars comparing each state's share of total transaction volume against its share of total fraud-flagged cases, overlaid with a secondary line showing state cohort fraud rates).*

### 5. Why It Matters for Understanding UPI Behaviour
Categorizing larger Indian states as "high-risk fraud hubs" based on raw flag counts is an analytical error. High absolute volumes reflect higher economic activity, digital literacy, and smartphone adoption, not compromised payment channels.

### 6. Interpretation
- **Observed:** Fraud-flag occurrences scale linearly with transaction traffic ($r > 0.98$ on state aggregates).
- **Synthetic Data Artifact:** As with transaction failures, the uniform ~0.16%–0.23% fraud rate across states strongly points to an i.i.d. synthetic generation process with an assigned fraud probability of $p \approx 0.002$.

### 7. Recommendations
- **For Law Enforcement & NPCI Cyber Cells:** Focus anti-fraud surveillance resources on specific merchant category mechanisms and modus operandi rather than imposing geofenced transaction restrictions or heavier friction on Maharashtra or Karnataka users.

---

## Insight 6: Baseline Risk Heuristics, Severe Class Imbalance, and Predictive Limitations

### 1. Executive Title
**Ultra-Rare Fraud Flagging (0.192%) Lacks Association with Available Metadata, Precluding Effective Supervised Classification**

### 2. Finding
With only 480 positive instances out of 250,000 records, the fraud flag is statistically unassociated with transaction type, merchant category, or amount, meaning standard supervised classification models cannot outperform majority-class guessing without external behavioral features.

### 3. Quantitative Evidence
- **Extreme Class Imbalance:** Exactly **480 out of 250,000 transactions (0.1920%)** are flagged as fraud (a negative-to-positive ratio of $520 : 1$).
- **Lack of Association with Transaction Type ($\chi^2 = 2.3238, dof = 3, p = 0.5080, V = 0.003049$):**
  - Fraud rates across types: P2P is **0.205%** (230 / 112,445), P2M is **0.189%** (166 / 87,660), Bill Payment is **0.169%** (63 / 37,368), Recharge is **0.168%** (21 / 12,527). Differences are statistically non-significant ($p = 0.508$).
- **Lack of Association with Merchant Category ($\chi^2 = 3.9734, dof = 9, p = 0.9132, V = 0.003987$):**
  - Category fraud rates range between **0.160%** (Fuel: 40 / 25,063) and **0.239%** (Entertainment: 48 / 20,104). With $p = 0.91$, no category shows meaningful elevation.
- **Age Group Variation ($\chi^2 = 11.0953, dof = 4, p = 0.0255, V = 0.006662$):**
  - Fraud rates range from **0.147%** (56+: 18 / 12,447) to **0.238%** (26–35: 208 / 87,411).
  - While $p = 0.0255$ is nominally significant at $\alpha = 0.05$ due to the massive sample size ($N = 250,000$), Cramer's $V = 0.0067$ is negligible ($V < 0.05$), indicating no practical predictive relationship.
- **Wilson Confidence Interval Overlap:**
  - 95% Wilson confidence intervals: P2P $[0.180\%, 0.233\%]$ overlaps with Bill Payment $[0.132\%, 0.216\%]$; Age 26–35 $[0.208\%, 0.273\%]$ overlaps with 18–25 $[0.151\%, 0.219\%]$ and 56+ $[0.093\%, 0.231\%]$.
- **Absence of Linear Ticket Correlation:**
  - Pearson correlation between `amount (INR)` and `fraud_flag` is $r = -0.00069$, indicating zero linear dependency.

### 4. Supporting Chart
- **File:** `outputs/insight_figures/figure6_fraud_flag_rates_and_uncertainty.png`  
  *(Displays point estimates of fraud-flag rates across Transaction Types and Sender Age Groups accompanied by 95% Wilson score confidence intervals, illustrating wide statistical overlap and negligible effect sizes).*

### 5. Why It Matters for Understanding UPI Behaviour
In payments security, attempting to train predictive machine learning models (e.g., Logistic Regression in notebook cells 91–96) on metadata fields that possess zero statistical dependency produces models that simply mirror prior probabilities. A model reporting 51.8% accuracy and 0.49 recall under balanced class weights is merely flipping an unweighted coin.

### 6. Interpretation
- **Observed:** Flagged fraud rates are uniform across transaction types, categories, and amounts.
- **Synthetic Data Artifact:** The dataset's `fraud_flag` was generated uniformly at a rate of ~0.2% without encoding complex fraud patterns (such as velocity spikes, late-night high-value bursts, or mule-account cycling).

### 7. Recommendations
- **For Data Science Teams:** Do not rely on basic transaction metadata (state, bank, category, daytime hour) to predict UPI fraud. Effective fraud detection in production requires dynamic telemetry features: device IMEI binding, SIM change flags, biometric prompt failures, rapid velocity counts (e.g., transactions in the last 60 seconds), and graph-based beneficiary link analysis.

---

## Summary Synthesis of Insights

| # | Executive Title | Core Finding | Statistical Metric | Strategic Takeaway |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Micro-Ticket Dominance** | Median ₹629 vs. Mean ₹1,311.76; 8.47% Tukey outliers (> ₹3,558). | $Skew > 3.0$; Max = ₹42,099 | Route micro-payments through UPI Lite; use adaptive risk scoring. |
| **2** | **Merchant Volume vs. Value Decoupling** | Groceries drive volume (19.99%); Shopping & Utilities drive value (39.52%). | Value/Volume divergence up to $+11.5\%$ | Differentiate acquisition infrastructure from settlement liquidity. |
| **3** | **Diurnal Surge vs. Weekend Invariance** | Peak at 19:00 (15.7× trough); weekday vs. weekend daily rate differs by $< 0.18\%$. | 35,733 vs. 35,669 tx/day | Schedule CBS maintenance only during 02:00–05:00 trough; treat weekends as full utility days. |
| **4** | **Infrastructure Reliability Invariance** | Failure rate is constant at ~4.95% across all banks, devices, and networks. | $\chi^2$ $p > 0.27$, Cramer's $V < 0.004$ | High failure counts on Android/4G are volume-driven; routing is universally reliable. |
| **5** | **Geographic Volume Proportionality** | Maharashtra & Karnataka drive 29.17% of flags solely due to 26.87% volume share. | $\chi^2 = 7.765, p = 0.558$ | State fraud rates (~0.19%) are uniform; avoid stigmatizing high-volume states. |
| **6** | **Low Baseline Fraud & High Uncertainty** | Ultra-rare positive class (0.192%) lacks association with metadata; CIs overlap. | Cramer's $V < 0.007$; $r = -0.0007$ | Basic metadata cannot predict fraud; production fraud engines require device/velocity telemetry. |
