# Technical Code Walkthrough: Architecture, Data Pipelines & Modeling

**Project:** *UPI Transaction Analytics: Exploring Payment Behavior, Transaction Reliability and Fraud Patterns in India*  
**Authors:** Swaraj Suresh Shinde (PRN: `125B1D053`), Nikol Dharmraj Ghodke (PRN: `125B1D062`)  
**Course:** Data Exploration and Visualization Laboratory  
**Files Audited:** [`upi_transactions_2024.csv`](file:///d:/nikol/collage/devel/project/data/upi_transactions_2024.csv), [`app.py`](file:///d:/nikol/collage/devel/project/app.py), [`src/data_loader.py`](file:///d:/nikol/collage/devel/project/src/data_loader.py), [`src/metrics.py`](file:///d:/nikol/collage/devel/project/src/metrics.py), and [`notebooks/mini-project_corrected.ipynb`](file:///d:/nikol/collage/devel/project/notebooks/mini-project_corrected.ipynb)  

---

## 1. Data Ingestion, Preprocessing & Defensive Validation

Data ingestion across both the exploratory notebook and the interactive Streamlit dashboard is governed by defensive engineering principles implemented in [`src/data_loader.py`](file:///d:/nikol/collage/devel/project/src/data_loader.py).

### 1.1 Portable Multi-Path Resolution
To ensure reproducibility across evaluation machines without machine-specific hardcoded paths, `get_dataset_path()` checks relative paths systematically:
1. `data/upi_transactions_2024.csv` (structured project location)
2. `upi_transactions_2024.csv` (project root)
3. Working directory fallback

### 1.2 Schema Validation and Identifier Exclusion
The raw CSV contains 17 columns with non-standard formatting, such as spaces in `transaction id` and `transaction type`, and unit annotations in `amount (INR)`. The loader:
- Verifies the presence of all 17 required columns, raising explicit exceptions if columns are absent.
- Standardizes identifiers into clean snake_case: `transaction_id`, `transaction_type`, and `amount`.
- Enforces data type coercion: converts `amount` to `float64` and `fraud_flag` to `int64`.
- **Non-Analytical Identifier Policy:** The column `transaction_id` contains 250,000 distinct alphanumeric primary keys (`TXN0000000001` through `TXN0000250000`). It is strictly excluded from group-by aggregations and feature encoding matrices.

### 1.3 Datetime Parsing & Temporal Derivations
- Parsing is executed via `pd.to_datetime(df['timestamp'], errors='coerce')`. In this dataset, all 250,000 records parse cleanly into timestamps spanning from `2024-01-01 00:05:10` to `2024-12-30 23:55:40`.
- Five reliable temporal fields are derived directly from the verified datetime index:
  - `date`: `dt.date` for discrete calendar range filtering.
  - `hour`: `dt.hour` (0 to 23) for diurnal traffic curves.
  - `month_name`: Full month string (`January` through `December`).
  - `day_name`: Full weekday string (`Monday` through `Sunday`).
  - `is_weekend_calc`: Binary indicator (`1` if Saturday/Sunday, `0` otherwise).

### 1.4 Missing and Duplicate Values
Validation routines verify that the dataset contains **zero null values** across all 17 fields and **zero duplicate rows**, guaranteeing that exploratory metrics are computed on complete data without imputation artifacts.

---

## 2. Harmonized Analytical Logic: Notebook to Dashboard Reuse

A key achievement of the refactored architecture is the exact mathematical alignment between the Jupyter exploratory notebook ([`notebooks/mini-project_corrected.ipynb`](file:///d:/nikol/collage/devel/project/notebooks/mini-project_corrected.ipynb)) and the interactive Streamlit dashboard ([`app.py`](file:///d:/nikol/collage/devel/project/app.py)).

### 2.1 Disambiguation of Cohort Rates vs. Population Shares
In preliminary analyses, a frequent pitfall was confusing **share of total failures** with **cohort failure probability**. The production logic in `src/metrics.py` enforces explicit mathematical formulations:

$$\text{Cohort Failure Rate (\%)} = \frac{\sum \text{FAILED transactions within cohort}}{\sum \text{Total transactions within cohort}} \times 100$$

$$\text{Share of All Failures (\%)} = \frac{\sum \text{FAILED transactions within cohort}}{12,376 \text{ (Total system failures)}} \times 100$$

- **Why this matters:** Android accounts for **74.97% of all system failures** (9,278 / 12,376). However, this is because Android represents **75.11% of all network transactions** (187,777 / 250,000). Android's cohort failure rate is **4.94%**, which is identical to iOS (**4.93%**).
- Similarly, 4G accounts for **60.31% of all failures** (7,464 / 12,376) because it carries **59.93% of all traffic** (149,813 / 250,000). Its cohort failure rate is **4.98%**, virtually indistinguishable from 5G (**4.86%**).

### 2.2 Security Indicator Formulation
$$\text{Fraud-Flagged Occurrence Rate (\%)} = \frac{\sum \text{fraud\_flag = 1 within cohort}}{\sum \text{Total transactions within cohort}} \times 100$$
The dashboard labels this metric strictly as **"Fraud-Flagged (Indicator)"** rather than "Confirmed Fraud", accurately communicating that the flag represents an internal rule trigger (baseline: 0.1920%, or 480 / 250,000).

---

## 3. Feature Encoding Strategy (`pd.get_dummies`)

In [`notebooks/mini-project_corrected.ipynb`](file:///d:/nikol/collage/devel/project/notebooks/mini-project_corrected.ipynb), preparing the dataset for classification requires transforming multi-category string columns into numeric dummy vectors.

```python
feature_cols = [
    'transaction type', 'merchant_category', 'amount (INR)',
    'sender_age_group', 'receiver_age_group', 'sender_state',
    'sender_bank', 'receiver_bank', 'device_type',
    'network_type', 'hour_of_day', 'day_of_week', 'is_weekend'
]

X = pd.get_dummies(df[feature_cols], drop_first=True)
```

### 3.1 Why `transaction id` Must Be Excluded
If `transaction id` were retained, one-hot encoding 250,000 unique categorical values would generate a matrix with 250,000 sparse columns. This would immediately exhaust system RAM, trigger memory crashes, and cause complete data leakage (the model would memorize IDs rather than learning generalizable patterns).

### 3.2 The Role of `drop_first=True`
- When converting categorical variables into dummy indicators, retaining all $k$ categories introduces perfect linear multicollinearity (the "dummy variable trap"), because the $k$-th category can be predicted as $1 - \sum_{i=1}^{k-1} x_i$.
- Setting `drop_first=True` removes the first reference category for each feature, resulting in $k - 1$ columns per factor.
- For example, `device_type` (3 levels: Android, iOS, Web) yields 2 dummy columns (`device_type_Web`, `device_type_iOS`), with Android serving as the reference baseline ($0, 0$).
- Across the 13 feature columns, this yields exactly **57 numeric features**.

---

## 4. Machine Learning Experiment: Transaction Failure Prediction

> [!NOTE]
> **Context:** The predictive modeling pipeline in Section 4 of the notebook is an **academic side experiment** designed to test whether technical transaction failures can be predicted from standard transaction metadata. It is **not** the central operational engine of the interactive dashboard, which focuses on exploratory data analysis and descriptive visualization.

### 4.1 Stratified Train/Test Split
Because the dataset exhibits a 95.05% SUCCESS to 4.95% FAILED class imbalance, a standard random split risks sampling variability in minority failure counts. The pipeline employs an 80/20 stratified split:

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```
- **Training Set (80%):** 200,000 transactions (190,099 SUCCESS, 9,901 FAILED).
- **Test Set (20%):** 50,000 transactions (47,525 SUCCESS, 2,475 FAILED).
- Stratification guarantees that the 4.95% failure proportion is preserved identically across training and testing splits.

### 4.2 Feature Scaling and Optimizer Convergence
In the preliminary notebook, training unscaled data triggered an optimization warning:
```text
ConvergenceWarning: lbfgs failed to converge after 1000 iteration(s) (status=1):
STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT.
```
- **Root Cause:** Continuous feature `amount (INR)` ranges from ₹10 to ₹42,099 with a standard deviation of ₹1,848, whereas dummy features are binary ($0$ or $1$). In the unscaled feature space, gradient updates along the amount axis oscillate wildly while dummy weights update slowly, preventing the L-BFGS quasi-Newton solver from finding the gradient minimum within 1,000 iterations.
- **Resolution:** In [`notebooks/mini-project_corrected.ipynb`](file:///d:/nikol/collage/devel/project/notebooks/mini-project_corrected.ipynb), continuous features are normalized using `StandardScaler` fitted strictly on `X_train` and transformed on `X_test`, eliminating the convergence warning.

---

## 5. Model Evaluation and Performance Recomputation

### 5.1 Baseline Logistic Regression (Unweighted)

```python
model_base = LogisticRegression(max_iter=1000)
model_base.fit(X_train_scaled, y_train)
y_pred_base = model_base.predict(X_test_scaled)
```

**Recomputed Evaluation Metrics:**
- **Overall Accuracy:** `0.9505` (**95.05%**)
- **Confusion Matrix** (Rows: Actual `[FAILED, SUCCESS]`, Columns: Predicted `[FAILED, SUCCESS]`):
  $$\begin{bmatrix} 0 & 2,475 \\ 0 & 47,525 \end{bmatrix}$$
- **Classification Report:**
  | Class | Precision | Recall | F1-Score | Support |
  | :--- | :---: | :---: | :---: | :---: |
  | **FAILED** | `0.00` | `0.00` | `0.00` | 2,475 |
  | **SUCCESS** | `0.95` | `1.00` | `0.97` | 47,525 |

#### Why 95.05% Accuracy is Meaningless
In an imbalanced classification setting where 95.05% of instances belong to the majority class (`SUCCESS`), overall accuracy is an uninformative metric. A naive "dummy classifier" that predicts `SUCCESS` for every transaction automatically achieves 95.05% accuracy while identifying **zero failed transactions** (Recall = 0.00, F1 = 0.00).

---

### 5.2 Balanced Logistic Regression (`class_weight="balanced"`)

To address majority class dominance, `class_weight="balanced"` weights class penalties inversely proportional to class frequencies:

$$w_j = \frac{N}{2 \times N_j} \implies w_{\text{SUCCESS}} = \frac{200,000}{2 \times 190,099} \approx 0.526, \quad w_{\text{FAILED}} = \frac{200,000}{2 \times 9,901} \approx 10.10$$

```python
model_bal = LogisticRegression(max_iter=1000, class_weight="balanced")
model_bal.fit(X_train_scaled, y_train)
y_pred_bal = model_bal.predict(X_test_scaled)
```

**Recomputed Evaluation Metrics:**
- **Overall Accuracy:** `0.5206` (**52.06%**, or ~51.84% unscaled)
- **Confusion Matrix** (Rows: Actual `[FAILED, SUCCESS]`, Columns: Predicted `[FAILED, SUCCESS]`):
  $$\begin{bmatrix} 1,208 & 1,267 \\ 22,702 & 24,823 \end{bmatrix}$$
- **Classification Report:**
  | Class | Precision | Recall | F1-Score | Support |
  | :--- | :---: | :---: | :---: | :---: |
  | **FAILED** | `0.05` (5.05%) | `0.49` (48.81%) | `0.09` | 2,475 |
  | **SUCCESS** | `0.95` | `0.52` | `0.67` | 47,525 |

---

### 5.3 Critical Analytical Insight: The Illusion of Model "Improvement"

In the preliminary student notebook (Cell 96), the result was interpreted as:
> *"After balancing the class weights, it became better at detecting failed transactions, with a recall of 0.49..."*

**Scientific Reality:**  
The model did **not** learn to detect failed transactions. It is effectively guessing at random:
1. As proven by our Chi-Square independence tests ($\chi^2 p > 0.27$, Cramer's $V < 0.004$), failure status in this dataset is **statistically independent of all input features** (bank, device, network, type, state). There is **zero true predictive signal**.
2. Applying balanced class weights heavily penalizes minority-class false negatives, shifting the intercept/decision threshold until the model predicts `FAILED` for approximately half the test set (23,910 out of 50,000 transactions, or 47.8%).
3. If an agent randomly guesses `FAILED` 50% of the time on a dataset with a 4.95% failure rate:
   - **Expected Recall:** $\approx 50\%$ (Actual: **48.81%**)
   - **Expected Precision:** Equal to the population prior rate $\approx 4.95\%$ (Actual: **5.05%**)
   - **Expected Accuracy:** $\approx 50\%$ (Actual: **52.06%**)
4. The balanced model acts as an unweighted random coin flip. It demonstrates the fundamental principle that machine learning cannot extract predictive signal from features where none exists.

---

## 6. Advanced Modeling Recommendations for Imbalanced Payment Data

If working with real-world production payment streams where genuine failure signals exist, academic teams should apply the following methodologies:

1. **Adopt PR-AUC Over ROC-AUC:**  
   In heavily imbalanced regimes (4.95% or 0.19%), the Receiver Operating Characteristic (ROC-AUC) curve can be overly optimistic because the large volume of true negatives deflates the False Positive Rate. The **Precision-Recall Area Under Curve (PR-AUC)** focuses exclusively on the minority positive class and provides a much more honest assessment of classifier utility.
2. **Probability Calibration & Cost-Sensitive Threshold Tuning:**  
   Instead of using the default classification threshold of $0.50$, output raw calibrated probabilities (`predict_proba`) and tune the operational decision boundary $\tau$ using an explicit financial cost matrix:
   $$\text{Total Expected Cost} = C_{\text{FP}} \times N_{\text{FP}} + C_{\text{FN}} \times N_{\text{FN}}$$
   In banking routing, a False Negative (unanticipated transaction failure) incurs customer friction, while a False Positive (unnecessary rerouting to an expensive secondary gateway) incurs minor switching fees.
3. **Incorporate Dynamic Real-Time Telemetry:**  
   Static demographic attributes (state, age group) do not drive payment failure. Real-world payment gateway switches (such as Juspay or Razorpay Optimizer) train models on dynamic telemetry features:
   - Moving 60-second success rate of the destination bank CBS.
   - P95 latency and HTTP round-trip timeout counts on bank API endpoints.
   - Device battery level, connectivity switching flags, and historical retry frequencies.
