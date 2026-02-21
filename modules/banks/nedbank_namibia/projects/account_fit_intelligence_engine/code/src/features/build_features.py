"""
Behaviour feature engineering for Account Fit Intelligence Engine.

This module extracts behaviour features from customer transaction history
to support account fit analysis and future recommendation algorithms.
"""

import pandas as pd
from typing import Dict, Any


# Transaction type categories
DIGITAL_TYPES = {
    "pos_purchase",
    "airtime_purchase",
    "electricity_purchase",
    "third_party_payment",
    "eft_transfer",
}

INFLOW_TYPES = {"income"}


def extract_behavioural_features(transactions: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract behavioural features from customer transaction history.
    
    Calculates transaction patterns, digital usage, and assigns a simple
    behaviour tag based on observable patterns.
    
    Args:
        transactions: DataFrame with customer transactions
        
    Returns:
        Dictionary containing:
            - txn_count: Total number of transactions
            - total_inflow: Sum of income transactions (NAD)
            - total_outflow: Sum of debit transactions (NAD)
            - atm_withdrawal_count: Number of ATM withdrawals
            - utility_count: Number of utility payments (airtime + electricity)
            - third_party_payment_count: Number of third-party payments
            - digital_ratio: Proportion of digital (non-ATM) transactions
            - behaviour_tag: Simple rule-based classification
            
    Example:
        >>> transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
        >>> customer_txns = transactions[transactions['customer_id'] == 'CUST_001']
        >>> features = extract_behavioural_features(customer_txns)
        >>> print(f"Digital ratio: {features['digital_ratio']:.2%}")
        >>> print(f"Behaviour: {features['behaviour_tag']}")
    """
    tx = transactions.copy()
    
    # Basic counts
    txn_count = len(tx)
    
    # Inflow vs outflow
    inflow = tx.loc[tx["type"].isin(INFLOW_TYPES), "amount"].sum()
    outflow = tx.loc[~tx["type"].isin(INFLOW_TYPES), "amount"].sum()
    
    # Transaction type counts
    atm_count = (tx["type"] == "atm_withdrawal").sum()
    utility_count = tx["type"].isin({"airtime_purchase", "electricity_purchase"}).sum()
    third_party_count = (tx["type"] == "third_party_payment").sum()
    
    # Digital usage ratio
    digital_count = tx["type"].isin(DIGITAL_TYPES).sum()
    digital_ratio = (digital_count / txn_count) if txn_count else 0.0
    
    # Simple behaviour tagging (rule-based, explainable)
    if txn_count == 0:
        tag = "no_activity"
    elif atm_count / max(txn_count, 1) >= 0.4:
        tag = "cash_heavy"
    elif digital_ratio >= 0.7:
        tag = "digital_first"
    elif utility_count >= 3:
        tag = "utilities_focused"
    else:
        tag = "mixed_usage"
    
    return {
        "txn_count": int(txn_count),
        "total_inflow": float(abs(inflow)),  # Make positive for display
        "total_outflow": float(outflow),
        "atm_withdrawal_count": int(atm_count),
        "utility_count": int(utility_count),
        "third_party_payment_count": int(third_party_count),
        "digital_ratio": float(round(digital_ratio, 4)),
        "behaviour_tag": tag,
    }
