"""
UPI Transaction Analytics - Exploratory Analysis Static Visualizations
Recreates every chart from mini-project.ipynb using Matplotlib and Seaborn.
"""
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st


def _fig_to_png(fig: plt.Figure) -> bytes:
    """Helper to export figure to PNG bytes and close it cleanly."""
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# 1. Distribution of UPI Transaction Types
def chart_1(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.countplot(data=_df, x="transaction_type", ax=ax)
    ax.set_title("Distribution of UPI Transaction Types")
    ax.set_xlabel("Transaction Type")
    ax.set_ylabel("Number of Transactions")
    return _fig_to_png(fig)


# 2. Distribution of Transaction Status
def chart_2(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.countplot(data=_df, x="transaction_status", ax=ax)
    ax.set_title("Distribution of Transaction Status")
    ax.set_xlabel("Transaction Status")
    ax.set_ylabel("Number of Transactions")
    return _fig_to_png(fig)


# 3. Transaction Amount by Transaction Type
def chart_3(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.boxplot(data=_df, x="transaction_type", y="amount", ax=ax)
    ax.set_title("Transaction Amount by Transaction Type")
    ax.set_xlabel("Transaction Type")
    ax.set_ylabel("Transaction Amount (INR)")
    return _fig_to_png(fig)


# 4. Transaction Status by Transaction Type
def chart_4(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.countplot(data=_df, x="transaction_type", hue="transaction_status", ax=ax)
    ax.set_title("Transaction Status by Transaction Type")
    ax.set_xlabel("Transaction Type")
    ax.set_ylabel("Number of Transactions")
    ax.legend(title="Transaction Status")
    return _fig_to_png(fig)


# 5. Transactions by Merchant Category
def chart_5(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    merchant_counts = _df["merchant_category"].value_counts()
    merchant_counts.plot(kind="bar", ax=ax)
    ax.set_title("Transactions by Merchant Category")
    ax.set_xlabel("Merchant Category")
    ax.set_ylabel("Number of Transactions")
    ax.tick_params(axis="x", rotation=45)
    return _fig_to_png(fig)


# 6. UPI Transactions by Hour
def chart_6(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.countplot(data=_df, x="hour", ax=ax)
    ax.set_title("UPI Transactions by Hour")
    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Number of Transactions")
    return _fig_to_png(fig)


# 7. UPI Transactions by Day of the Week
def chart_7(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.countplot(data=_df, x="day_name", ax=ax)
    ax.set_title("UPI Transactions by Day of the Week")
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Number of Transactions")
    ax.tick_params(axis="x", rotation=30)
    return _fig_to_png(fig)


# 8. Weekday vs Weekend Transactions
def chart_8(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.countplot(data=_df, x="is_weekend_calc", ax=ax)
    ax.set_title("Weekday vs Weekend Transactions")
    ax.set_xlabel("0=weekday, 1=weekend")
    ax.set_ylabel("Number of Transactions")
    return _fig_to_png(fig)


# 9. Top Banks by no. of transactions
def chart_9(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bank_count = _df["sender_bank"].value_counts()
    bank_count.plot(kind="bar", ax=ax)
    ax.set_title("Top Banks by no. of transactions")
    ax.set_xlabel("Sender Bank")
    ax.set_ylabel("No. of transactions")
    ax.tick_params(axis="x", rotation=45)
    return _fig_to_png(fig)


# 10. Top States by Transaction count
def chart_10(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    state_counts = _df["sender_state"].value_counts()
    state_counts.plot(kind="bar", ax=ax)
    ax.set_title("Top States by Transaction count")
    ax.set_xlabel("States")
    ax.set_ylabel("No. of transactions")
    ax.tick_params(axis="x", rotation=45)
    return _fig_to_png(fig)


# 11. Average Transaction Amount by Transaction Type
def chart_11(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    average_amount = _df.groupby("transaction_type")["amount"].mean()
    average_amount.plot(kind="bar", ax=ax)
    ax.set_title("Average Transaction Amount by Transaction Type")
    ax.set_xlabel("Transaction Type")
    ax.set_ylabel("Average Amount (INR)")
    ax.tick_params(axis="x", rotation=45)
    return _fig_to_png(fig)


# 12. Fraud Percentage by Transaction Type
def chart_12(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    fraud_transactions = _df[_df["fraud_flag"] == 1]
    fraud_type_count = fraud_transactions["transaction_type"].value_counts()
    total_type_count = _df["transaction_type"].value_counts()
    fraud_type_percentage = (fraud_type_count / total_type_count) * 100
    fraud_type_percentage.sort_values().plot(kind="bar", ax=ax)
    ax.set_title("Fraud Percentage by Transaction Type")
    ax.set_xlabel("Transaction Type")
    ax.set_ylabel("Fraud Percentage (%)")
    ax.tick_params(axis="x", rotation=45)
    return _fig_to_png(fig)


# 13. Transaction Amount vs Hour of the Day
def chart_13(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.scatter(_df["hour"], _df["amount"], alpha=0.3, s=8)
    ax.set_title("Transaction Amount vs Hour of the Day")
    ax.set_xlabel("Hour of the Day")
    ax.set_ylabel("Transaction Amount (INR)")
    return _fig_to_png(fig)


# 14. Distribution and Skewness of UPI Transaction Amounts
def chart_14(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.histplot(_df["amount"], bins=30, kde=True, ax=ax)
    ax.set_title("Distribution and Skewness of UPI Transaction Amounts")
    ax.set_xlabel("Transaction Amount (INR)")
    ax.set_ylabel("Frequency")
    return _fig_to_png(fig)


# 15. Correlation Heatmap
def chart_15(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    data = _df[["amount", "hour", "is_weekend_calc", "fraud_flag"]].rename(
        columns={"amount": "amount (INR)", "hour": "hour_of_day", "is_weekend_calc": "is_weekend"}
    )
    correlation = data.corr()
    sns.heatmap(correlation, annot=True, ax=ax, cmap="coolwarm", fmt=".4f")
    ax.set_title("Correlation Heatmap of UPI Transactions")
    return _fig_to_png(fig)


# 16. Box Plot of UPI Transaction Amounts
def chart_16(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.boxplot(x=_df["amount"], ax=ax)
    ax.set_title("Box Plot of UPI Transaction Amounts")
    ax.set_xlabel("Transaction Amount (INR)")
    return _fig_to_png(fig)


# 17. Fraud Transactions by Device and Network Type
def chart_17(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    fraud_transactions = _df[_df["fraud_flag"] == 1]
    sns.countplot(data=fraud_transactions, x="device_type", hue="network_type", ax=ax)
    ax.set_title("Fraud Transactions by Device and Network Type")
    ax.set_xlabel("Device Type")
    ax.set_ylabel("Number of Fraud Transactions")
    return _fig_to_png(fig)


# 18. Top States by Fraud-Flagged Transactions
def chart_18(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    fraud_transactions = _df[_df["fraud_flag"] == 1]
    fraud_state_count = fraud_transactions["sender_state"].value_counts()
    fraud_state_count.plot(kind="bar", ax=ax)
    ax.set_title("Top States by Fraud-Flagged Transactions")
    ax.set_xlabel("State")
    ax.set_ylabel("Number of Fraud-Flagged Transactions")
    ax.tick_params(axis="x", rotation=45)
    return _fig_to_png(fig)


# 19. Failure-rate heatmap: sender_state x network_type
def chart_19(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    failed = (_df["transaction_status"] == "FAILED").astype(int)
    df_temp = pd.DataFrame({
        "sender_state": _df["sender_state"],
        "network_type": _df["network_type"],
        "failed": failed
    })
    pt = df_temp.pivot_table(index="sender_state", columns="network_type", values="failed", aggfunc="mean") * 100
    sns.heatmap(pt, annot=True, ax=ax, fmt=".2f", cmap="YlOrRd")
    ax.set_title("Failure Rate (%) by Sender State and Network Type")
    ax.set_xlabel("Network Type")
    ax.set_ylabel("Sender State")
    return _fig_to_png(fig)


# 20. Failure rate and fraud rate by hour of day
def chart_20(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    failed = (_df["transaction_status"] == "FAILED").astype(int)
    df_temp = pd.DataFrame({
        "hour_of_day": _df["hour"],
        "failed": failed,
        "fraud_flag": _df["fraud_flag"]
    })
    h = df_temp.groupby("hour_of_day")[["failed", "fraud_flag"]].mean() * 100
    h.plot(ax=ax)
    ax.set_title("Failure Rate and Fraud Rate by Hour of Day")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Rate (%)")
    return _fig_to_png(fig)


# 21. Transaction Count by Merchant Category
def chart_21(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    cnt = _df["merchant_category"].value_counts()
    ax.pie(cnt, labels=cnt.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Transaction Count by Merchant Category")
    return _fig_to_png(fig)


# 22. Transaction Value by Merchant Category
def chart_22(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    val = _df.groupby("merchant_category")["amount"].sum()
    ax.pie(val, labels=val.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Transaction Value by Merchant Category")
    return _fig_to_png(fig)


# 23. Sender age group x receiver age group
def chart_23(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ct = pd.crosstab(_df["sender_age_group"], _df["receiver_age_group"], normalize="index") * 100
    sns.heatmap(ct, annot=True, ax=ax, fmt=".1f", cmap="Blues")
    ax.set_title("Sender Age Group vs Receiver Age Group (Row-Normalized %)")
    ax.set_xlabel("Receiver Age Group")
    ax.set_ylabel("Sender Age Group")
    return _fig_to_png(fig)


# 24. Failure Rate by Sender Bank
def chart_24(_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    failed = (_df["transaction_status"] == "FAILED").astype(int)
    rates = _df.assign(_failed=failed).groupby("sender_bank")["_failed"].mean() * 100.0
    rates = rates.sort_values(ascending=False)
    overall_rate = failed.mean() * 100.0

    bars = ax.bar(rates.index, rates.values, color="#4C72B0", width=0.6)
    ax.axhline(overall_rate, color="#D9534F", linestyle="--", linewidth=1.2, label=f"Overall baseline ({overall_rate:.2f}%)")

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.2f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold"
        )

    ax.set_title("Failure Rate by Sender Bank")
    ax.set_xlabel("Sender Bank")
    ax.set_ylabel("Failure Rate (%)")
    ax.set_ylim(0, 6.5)
    ax.tick_params(axis="x", rotation=30)
    ax.legend(loc="upper right", framealpha=0.8)
    return _fig_to_png(fig)


# Registry list of 24 charts with metadata and callable functions
CHARTS_REGISTRY = [
    {"id": 1, "title": "Distribution of UPI Transaction Types", "fn": chart_1},
    {"id": 2, "title": "Distribution of Transaction Status", "fn": chart_2},
    {"id": 3, "title": "Transaction Amount by Transaction Type", "fn": chart_3},
    {"id": 4, "title": "Transaction Status by Transaction Type", "fn": chart_4},
    {"id": 5, "title": "Transactions by Merchant Category", "fn": chart_5},
    {"id": 6, "title": "UPI Transactions by Hour", "fn": chart_6},
    {"id": 7, "title": "UPI Transactions by Day of the Week", "fn": chart_7},
    {"id": 8, "title": "Weekday vs Weekend Transactions", "fn": chart_8},
    {"id": 9, "title": "Top Banks by no. of transactions", "fn": chart_9},
    {"id": 10, "title": "Top States by Transaction count", "fn": chart_10},
    {"id": 11, "title": "Average Transaction Amount by Transaction Type", "fn": chart_11},
    {"id": 12, "title": "Fraud Percentage by Transaction Type", "fn": chart_12},
    {"id": 13, "title": "Transaction Amount vs Hour of the Day", "fn": chart_13},
    {"id": 14, "title": "Distribution and Skewness of UPI Transaction Amounts", "fn": chart_14},
    {"id": 15, "title": "Correlation Heatmap of UPI Transactions", "fn": chart_15},
    {"id": 16, "title": "Box Plot of UPI Transaction Amounts", "fn": chart_16},
    {"id": 17, "title": "Fraud Transactions by Device and Network Type", "fn": chart_17},
    {"id": 18, "title": "Top States by Fraud-Flagged Transactions", "fn": chart_18},
    {"id": 19, "title": "Failure-rate heatmap: sender_state x network_type", "fn": chart_19},
    {"id": 20, "title": "Failure rate and fraud rate by hour of day", "fn": chart_20},
    {"id": 21, "title": "Transaction Count by Merchant Category", "fn": chart_21},
    {"id": 22, "title": "Transaction Value by Merchant Category", "fn": chart_22},
    {"id": 23, "title": "Sender age group x receiver age group (row-normalized)", "fn": chart_23},
    {"id": 24, "title": "Failure Rate by Sender Bank", "fn": chart_24},
]

CHARTS_BY_ID = {c["id"]: c["fn"] for c in CHARTS_REGISTRY}


@st.cache_data(show_spinner=False)
def get_chart_png(chart_id: int, _df: pd.DataFrame) -> bytes:
    """Cached generator returning PNG bytes for requested chart ID."""
    fn = CHARTS_BY_ID.get(chart_id)
    if fn is None:
        raise ValueError(f"Unknown chart_id: {chart_id}")
    return fn(_df)

