"""
Behaviour feature engineering for Account Fit Intelligence Engine.

This module extracts behaviour features from customer transaction history
to support account fit analysis and future recommendation algorithms.

Changes in v0.2.1:
- Added cash_deposit_count feature
- Added deposit_fee_eligibility_status derived feature (uses shared helper from tariff_engine)
- extract_behavioural_features now accepts customer_segment, annual_turnover, turnover_threshold
"""

import pandas as pd
from typing import Any, Dict, Optional

# Import shared eligibility helper — single source of logic, no duplication
from fees.tariff_engine import resolve_deposit_eligibility


# Transaction type categories
DIGITAL_TYPES = {
    "pos_purchase",
    "airtime_purchase",
    "electricity_purchase",
    "third_party_payment",
    "eft_transfer",
}

INFLOW_TYPES = {"income"}


def extract_behavioural_features(
    transactions: pd.DataFrame,
    customer_segment: str = "individual",
    annual_turnover: Optional[float] = None,
    turnover_threshold: float = 1_300_000,
) -> Dict[str, Any]:
    """
    Extract behavioural features from customer transaction history.

    Calculates transaction patterns, digital usage, and assigns a simple
    behaviour tag based on observable patterns.

    Args:
        transactions:       DataFrame with customer transactions
        customer_segment:   'individual', 'sme', or 'business' — used to derive
                            deposit_fee_eligibility_status (v0.2.1)
        annual_turnover:    Annual NAD turnover; None = unknown (v0.2.1)
        turnover_threshold: Threshold above which deposit fee applies (v0.2.1)

    Returns:
        Dictionary containing:
            - txn_count: Total number of transactions
            - total_inflow: Sum of income transactions (NAD)
            - total_outflow: Sum of debit transactions (NAD)
            - atm_withdrawal_count: Number of ATM withdrawals
            - cash_deposit_count: Number of branch cash deposits (v0.2.1)
            - utility_count: Number of utility payments (airtime + electricity)
            - third_party_payment_count: Number of third-party payments
            - digital_ratio: Proportion of digital (non-ATM) transactions
            - behaviour_tag: Simple rule-based classification
            - deposit_fee_eligibility_status: 'individual' | 'sme_below_threshold' |
              'sme_above_threshold' | 'unknown' (v0.2.1)

    Example:
        >>> transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
        >>> customer_txns = transactions[transactions['customer_id'] == 'CUST_001']
        >>> features = extract_behavioural_features(
        ...     customer_txns, customer_segment='sme', annual_turnover=2_000_000)
        >>> print(f"Digital ratio: {features['digital_ratio']:.2%}")
        >>> print(f"Deposit eligibility: {features['deposit_fee_eligibility_status']}")
    """
    tx = transactions.copy()

    # Basic counts
    txn_count = len(tx)

    # Inflow vs outflow
    inflow = tx.loc[tx["type"].isin(INFLOW_TYPES), "amount"].sum()
    outflow = tx.loc[~tx["type"].isin(INFLOW_TYPES), "amount"].sum()

    # Transaction type counts
    atm_count = (tx["type"] == "atm_withdrawal").sum()
    cash_deposit_count = (tx["type"] == "cash_deposit").sum()   # v0.2.1
    utility_count = tx["type"].isin({"airtime_purchase", "electricity_purchase"}).sum()
    third_party_count = (tx["type"] == "third_party_payment").sum()

    # Digital usage ratio (cash_deposit is a branch event — not digital)
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

    # v0.2.1: deposit eligibility status — uses shared helper from tariff_engine
    deposit_eligibility = resolve_deposit_eligibility(
        customer_segment, annual_turnover, turnover_threshold
    )

    return {
        "txn_count": int(txn_count),
        "total_inflow": float(abs(inflow)),   # Make positive for display
        "total_outflow": float(outflow),
        "atm_withdrawal_count": int(atm_count),
        "cash_deposit_count": int(cash_deposit_count),          # v0.2.1
        "utility_count": int(utility_count),
        "third_party_payment_count": int(third_party_count),
        "digital_ratio": float(round(digital_ratio, 4)),
        "behaviour_tag": tag,
        "deposit_fee_eligibility_status": deposit_eligibility,  # v0.2.1
    }
