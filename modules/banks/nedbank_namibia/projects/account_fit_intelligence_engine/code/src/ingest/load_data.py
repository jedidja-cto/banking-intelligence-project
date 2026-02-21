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


def load_all_data(data_dir: str = 'data/synthetic/') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load all data files from a directory.
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        Tuple of (customers DataFrame, transactions DataFrame)
        
    Raises:
        FileNotFoundError: If required files don't exist
        ValueError: If data format is invalid
        
    Example:
        >>> customers, transactions = load_all_data('data/synthetic/')
        >>> print(f"Loaded {len(customers)} customers and {len(transactions)} transactions")
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Load customers
    customers_path = data_path / 'customers_sample.csv'
    customers = load_customers(str(customers_path))
    
    # Load transactions
    transactions_path = data_path / 'transactions_sample.csv'
    transactions = load_transactions(str(transactions_path))
    
    # TODO: Add data validation
    # - Check referential integrity
    # - Validate schemas
    # - Log data quality warnings
    
    return customers, transactions


def preprocess_data(customers: pd.DataFrame, transactions: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Preprocess loaded data for analysis.
    
    Args:
        customers: Raw customer DataFrame
        transactions: Raw transaction DataFrame
        
    Returns:
        Tuple of (preprocessed customers, preprocessed transactions)
        
    Example:
        >>> customers, transactions = load_all_data('data/synthetic/')
        >>> customers, transactions = preprocess_data(customers, transactions)
    """
    # TODO: Implement preprocessing logic
    # - Handle missing values
    # - Remove duplicates
    # - Filter invalid records
    # - Add derived columns if needed
    # - Sort data appropriately
    
    return customers, transactions
