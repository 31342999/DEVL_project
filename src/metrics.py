"""
UPI Transaction Analytics - Analytical Metrics & Aggregation Engine
"""
import pandas as pd
import numpy as np

def compute_kpis(df):
    """
    Computes summary KPI indicators dynamically from a filtered DataFrame.
    """
    n_total = len(df)
    if n_total == 0:
        return {
            "n_total": 0, "total_value": 0.0, "total_value_cr": 0.0,
            "avg_amount": 0.0, "n_success": 0, "success_rate": 0.0,
            "n_failed": 0, "failure_rate": 0.0, "n_fraud": 0, "fraud_rate": 0.0
        }
        
    total_val = float(df["amount"].sum())
    total_val_cr = total_val / 10_000_000.0
    avg_amt = float(df["amount"].mean())
    
    n_succ = int((df["transaction_status"] == "SUCCESS").sum())
    succ_rate = (n_succ / n_total) * 100.0
    
    n_fail = int((df["transaction_status"] == "FAILED").sum())
    fail_rate = (n_fail / n_total) * 100.0
    
    n_frd = int((df["fraud_flag"] == 1).sum())
    frd_rate = (n_frd / n_total) * 100.0
    
    return {
        "n_total": n_total,
        "total_value": total_val,
        "total_value_cr": total_val_cr,
        "avg_amount": avg_amt,
        "n_success": n_succ,
        "success_rate": succ_rate,
        "n_failed": n_fail,
        "failure_rate": fail_rate,
        "n_fraud": n_frd,
        "fraud_rate": frd_rate
    }

def compute_hourly_traffic(df):
    """
    Computes hourly volume and failure rate series.
    """
    hourly = df.groupby("hour").agg(
        volume=("transaction_id", "count"),
        failed=("transaction_status", lambda s: (s == "FAILED").sum())
    ).reset_index()
    hourly["failure_rate"] = (hourly["failed"] / hourly["volume"] * 100.0).fillna(0)
    return hourly

def compute_bank_metrics(df, n_total=None):
    """
    Computes bank market share, volume, failure count, and failure rate.
    """
    total_records = n_total if n_total is not None else len(df)
    bank_df = df.groupby("sender_bank").agg(
        total_tx=("transaction_id", "count"),
        failed_tx=("transaction_status", lambda s: (s == "FAILED").sum()),
        total_amt=("amount", "sum")
    ).reset_index()
    bank_df["market_share_pct"] = (bank_df["total_tx"] / total_records * 100.0) if total_records > 0 else 0
    bank_df["failure_rate_pct"] = (bank_df["failed_tx"] / bank_df["total_tx"] * 100.0).fillna(0)
    bank_df["value_cr"] = bank_df["total_amt"] / 10_000_000.0
    return bank_df.sort_values(by="total_tx", ascending=False)
