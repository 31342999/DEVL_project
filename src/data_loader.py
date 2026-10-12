"""
UPI Transaction Analytics - Data Ingestion & Preprocessing Module
"""
import pathlib
import pandas as pd

def get_dataset_path(preferred_filename="upi_transactions_2024.csv"):
    """
    Locates the dataset by checking relative project paths:
    1. data/upi_transactions_2024.csv
    2. upi_transactions_2024.csv (root)
    """
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    
    candidates = [
        base_dir / "data" / preferred_filename,
        base_dir / preferred_filename,
        pathlib.Path(preferred_filename)
    ]
    
    for path in candidates:
        if path.exists():
            return path
            
    return candidates[0]  # Return primary expected location if missing

def load_data(csv_path=None):
    """
    Defensively loads and pre-processes upi_transactions_2024.csv.
    Returns (df, error_message).
    """
    target_path = pathlib.Path(csv_path) if csv_path else get_dataset_path()
    
    if not target_path.exists():
        return None, f"Dataset not found at: `{target_path}`. Ensure upi_transactions_2024.csv is present in 'data/' or project root."
    
    try:
        df = pd.read_csv(target_path)
    except Exception as e:
        return None, f"Error reading CSV file: {str(e)}"
        
    required_cols = [
        "transaction id", "timestamp", "transaction type", "merchant_category",
        "amount (INR)", "transaction_status", "sender_age_group", "receiver_age_group",
        "sender_state", "sender_bank", "receiver_bank", "device_type",
        "network_type", "fraud_flag", "hour_of_day", "day_of_week", "is_weekend"
    ]
    
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        return None, f"Dataset schema error: missing required columns: {missing_cols}"
        
    # Standardize column identifiers
    df = df.rename(columns={
        "transaction id": "transaction_id",
        "transaction type": "transaction_type",
        "amount (INR)": "amount"
    })
    
    # Types and parsing
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["fraud_flag"] = pd.to_numeric(df["fraud_flag"], errors="coerce").fillna(0).astype(int)
    
    df["parsed_timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["parsed_timestamp"].isna().sum() > 0:
        df = df.dropna(subset=["parsed_timestamp"]).copy()
        
    df["date"] = df["parsed_timestamp"].dt.date
    df["hour"] = df["parsed_timestamp"].dt.hour
    df["month_name"] = df["parsed_timestamp"].dt.strftime("%B")
    df["month_num"] = df["parsed_timestamp"].dt.month
    df["day_name"] = df["parsed_timestamp"].dt.strftime("%A")
    df["is_weekend_calc"] = df["parsed_timestamp"].dt.dayofweek.isin([5, 6]).astype(int)
    
    # Strip string columns
    str_cols = [
        "transaction_type", "merchant_category", "transaction_status",
        "sender_age_group", "receiver_age_group", "sender_state",
        "sender_bank", "receiver_bank", "device_type", "network_type"
    ]
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
        
    return df, None
