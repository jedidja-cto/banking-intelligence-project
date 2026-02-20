"""
Data loading utilities for Account Fit Intelligence Engine.

This module provides functions to load customer and transaction data
from CSV files with proper type conversion and validation.
"""

import pandas as pd
from pathlib import Path


def load_customers(path: str) -> pd.DataFrame:
    """
    Load customer data from CSV file.
    
    Args:
        path: Path to customers CSV file
        
    Returns:
        DataFrame with customer data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        
    Example:
        >>> customers = load_customers('data/synthetic/customers_sample.csv')
        >>> print(customers.head())
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Customer data file not found: {path}")
    
    return pd.read_csv(file_path)


def load_transactions(path: str) -> pd.DataFrame:
    """
    Load transaction data from CSV file.
    
    Args:
        path: Path to transactions CSV file
        
    Returns:
        DataFrame with transaction data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        
    Example:
        >>> transactions = load_transactions('data/synthetic/transactions_sample.csv')
        >>> print(transactions.head())
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Transaction data file not found: {path}")
    
    return pd.read_csv(file_path)
