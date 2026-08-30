import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def format_currency(amount, currency_symbol="$"):
    """Format amount as currency"""
    return f"{currency_symbol}{amount:,.2f}"

def format_percentage(value, decimals=1):
    """Format value as percentage"""
    return f"{value:.{decimals}f}%"

def calculate_date_difference(start_date, end_date, unit='days'):
    """Calculate difference between two dates"""
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)

    delta = end_date - start_date

    if unit == 'days':
        return delta.days
    elif unit == 'weeks':
        return delta.days // 7
    elif unit == 'months':
        return delta.days // 30
    else:
        return delta.days

def safe_divide(numerator, denominator, default=0):
    """Safe division to avoid division by zero"""
    try:
        return numerator / denominator if denominator != 0 else default
    except:
        return default

def generate_random_id(prefix="ID", length=8):
    """Generate a random ID with prefix"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    random_string = ''.join(random.choice(chars) for _ in range(length))
    return f"{prefix}_{random_string}"

def validate_dataframe_columns(df, required_columns):
    """Validate that dataframe contains required columns"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return True

def clean_dataframe(df, fill_numeric_na='median', fill_categorical_na='mode'):
    """Clean dataframe by handling missing values"""
    df_clean = df.copy()

    # Handle numeric columns
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_clean[col].isna().any():
            if fill_numeric_na == 'median':
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            elif fill_numeric_na == 'mean':
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            else:
                df_clean[col] = df_clean[col].fillna(0)

    # Handle categorical columns
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df_clean[col].isna().any():
            if fill_categorical_na == 'mode':
                mode_val = df_clean[col].mode()
                if not mode_val.empty:
                    df_clean[col] = df_clean[col].fillna(mode_val[0])
                else:
                    df_clean[col] = df_clean[col].fillna('Unknown')
            else:
                df_clean[col] = df_clean[col].fillna('Unknown')

    return df_clean

def export_to_csv(df, filename, include_timestamp=True):
    """Export dataframe to CSV with optional timestamp"""
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename}_{timestamp}.csv"

    df.to_csv(filename, index=False)
    return filename

def get_file_size_mb(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    return 0

def create_backup_file(filepath):
    """Create a backup of a file"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(filepath, backup_path)
        return backup_path
    return None