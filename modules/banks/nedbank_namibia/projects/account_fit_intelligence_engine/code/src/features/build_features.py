"""
Behaviour feature engineering for Account Fit Intelligence Engine.

This module extracts behaviour features from customer transaction history
to support account fit analysis and future recommendation algorithms.

Changes in v0.2.1:
- Added cash_deposit_count feature
- Added deposit_fee_eligibility_status derived feature (uses shared helper from tariff_engine)
- extract_behavioural_features now accepts customer_segment, annual_turnover, turnover_threshold

Changes in v0.3.0:
- Extended feature contract with KPI-required keys (all additive, default 0 — backward-compatible):
    nedbank_atm_withdrawal_count, cashout_count, digital_txn_count, total_payments,
    pos_purchase_count, charged_txn_count
- charged_txn_count is computed via tariff_engine per-transaction fees (not approximated)

Changes in v0.3.1 (additive only):
- Added eft_transfer_internal and eft_transfer_external to DIGITAL_TYPES and PAYMENT_TYPES
- Added new feature keys:
    online_subscription_used: 1 if any txn channel in {"online","app","ussd"} else 0
    eft_to_nedbank_count: count(type==eft_transfer_internal)
    eft_to_otherbank_count: count(type==eft_transfer_external)
- Extended cashout_count to also count pos_purchase where merchant=="retail_cashout" (OR clause)
- Handles missing columns gracefully (transfer_scope, channel may be absent in older CSVs)
"""

import pandas as pd
from typing import Any, Dict, Optional

# Import shared eligibility helper — single source of logic, no duplication
from fees.tariff_engine import resolve_deposit_eligibility, compute_variable_fees


# Transaction type categories
DIGITAL_TYPES = {
    "pos_purchase",
    "airtime_purchase",
    "electricity_purchase",
    "third_party_payment",
    "eft_transfer",
    "eft_transfer_internal",   # v0.3.1
    "eft_transfer_external",   # v0.3.1
}

# Transaction types considered as "payments" (everything except income + cash_deposit)
PAYMENT_TYPES = {
    "pos_purchase",
    "airtime_purchase",
    "electricity_purchase",
    "third_party_payment",
    "eft_transfer",
    "eft_transfer_internal",   # v0.3.1
    "eft_transfer_external",   # v0.3.1
    "atm_withdrawal",
    "cashout",
}

INFLOW_TYPES = {"income"}

# Digital channels for online_subscription_used feature
_DIGITAL_CHANNELS = {"online", "app", "ussd"}


def extract_behavioural_features(
    transactions: pd.DataFrame,
    customer_segment: str = "individual",
    annual_turnover: Optional[float] = None,
    turnover_threshold: float = 1_300_000,
    fee_schedule: Optional[Dict[str, Any]] = None,
    account_class: str = "current",
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
        fee_schedule:       Full fee schedule dict from YAML — used to derive
                            charged_txn_count via real tariff engine (v0.3.0).
                            If None, charged_txn_count defaults to 0.
        account_class:      'current' or 'savings' — for POS fee determination (v0.3.0)

    Returns:
        Dictionary containing:
            --- Existing keys (v0.2.1, unchanged) ---
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

            --- v0.3.0 keys (all default 0 if absent) ---
            - nedbank_atm_withdrawal_count: ATM withdrawals at Nedbank ATMs
            - cashout_count: Retail CashOut txns (type='cashout' OR pos_purchase at retail_cashout)
            - digital_txn_count: Count of transactions in DIGITAL_TYPES
            - total_payments: Count of all payment transactions (non-income, non-deposit)
            - pos_purchase_count: Count of POS purchase transactions
            - charged_txn_count: Count of transactions that incur a fee (via tariff engine)

            --- v0.3.1 keys (all default 0 if absent) ---
            - online_subscription_used: 1 if any txn channel in {online,app,ussd} else 0
            - eft_to_nedbank_count: count(type==eft_transfer_internal)
            - eft_to_otherbank_count: count(type==eft_transfer_external)

    Example:
        >>> transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
        >>> customer_txns = transactions[transactions['customer_id'] == 'CUST_001']
        >>> features = extract_behavioural_features(customer_txns)
        >>> print(f"Digital ratio: {features['digital_ratio']:.2%}")
    """
    tx = transactions.copy()

    # Basic counts
    txn_count = len(tx)

    # Inflow vs outflow
    inflow = tx.loc[tx["type"].isin(INFLOW_TYPES), "amount"].sum()
    outflow = tx.loc[~tx["type"].isin(INFLOW_TYPES), "amount"].sum()

    # --- Existing transaction type counts ---
    atm_count = int((tx["type"] == "atm_withdrawal").sum())
    cash_deposit_count = int((tx["type"] == "cash_deposit").sum())   # v0.2.1
    utility_count = int(tx["type"].isin({"airtime_purchase", "electricity_purchase"}).sum())
    third_party_count = int((tx["type"] == "third_party_payment").sum())

    # Digital usage ratio (cash_deposit is a branch event — not digital)
    digital_count = int(tx["type"].isin(DIGITAL_TYPES).sum())
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

    # -------------------------------------------------------------------------
    # v0.3.0: Extended feature contract (all additive, backward-compatible)
    # -------------------------------------------------------------------------

    # Nedbank ATM withdrawal count (from atm_owner column)
    if "atm_owner" in tx.columns:
        nedbank_atm_count = int(
            ((tx["type"] == "atm_withdrawal") & (tx["atm_owner"] == "nedbank")).sum()
        )
    else:
        nedbank_atm_count = 0

    # Retail CashOut count — v0.3.1: also include pos_purchase where merchant=="retail_cashout"
    cashout_type_mask = tx["type"] == "cashout"
    if "merchant" in tx.columns:
        pos_cashout_mask = (tx["type"] == "pos_purchase") & (tx["merchant"] == "retail_cashout")
        cashout_count = int((cashout_type_mask | pos_cashout_mask).sum())
    else:
        cashout_count = int(cashout_type_mask.sum())

    # Digital transaction count (raw count, not ratio)
    digital_txn_count = digital_count

    # Total payments (non-income, non-cash_deposit)
    total_payments = int(tx["type"].isin(PAYMENT_TYPES).sum())

    # POS purchase count
    pos_purchase_count = int((tx["type"] == "pos_purchase").sum())

    # Charged transaction count — derive from tariff engine (real fees, no approximation)
    if fee_schedule is not None and txn_count > 0:
        # Build a single-customer DataFrame slice and use compute_variable_fees
        # We need a customer_id column; use a sentinel if it was sliced already
        if "customer_id" not in tx.columns or tx["customer_id"].nunique() != 1:
            tx_for_fee = tx.copy()
            tx_for_fee["customer_id"] = "__feature_eval__"
            sentinel_id = "__feature_eval__"
        else:
            tx_for_fee = tx
            sentinel_id = tx["customer_id"].iloc[0]

        fee_results = compute_variable_fees(tx_for_fee, fee_schedule, account_class)
        by_type = fee_results.get(sentinel_id, {}).get("by_type", {})
        # Count transactions per charged type
        charged_txn_count = 0
        for txn_type, total_fee in by_type.items():
            if total_fee > 0:
                charged_txn_count += int((tx["type"] == txn_type).sum())
    else:
        charged_txn_count = 0

    # -------------------------------------------------------------------------
    # v0.3.1: New features (all default 0 — backward-compatible, missing cols handled)
    # -------------------------------------------------------------------------

    # online_subscription_used: 1 if any txn channel in {online, app, ussd}
    if "channel" in tx.columns:
        online_subscription_used = int(tx["channel"].isin(_DIGITAL_CHANNELS).any())
    else:
        online_subscription_used = 0

    # EFT sub-type counts
    eft_to_nedbank_count = int((tx["type"] == "eft_transfer_internal").sum())
    eft_to_otherbank_count = int((tx["type"] == "eft_transfer_external").sum())

    return {
        # --- v0.2.1 keys (unchanged) ---
        "txn_count": int(txn_count),
        "total_inflow": float(abs(inflow)),   # Make positive for display
        "total_outflow": float(outflow),
        "atm_withdrawal_count": atm_count,
        "cash_deposit_count": cash_deposit_count,          # v0.2.1
        "utility_count": int(utility_count),
        "third_party_payment_count": int(third_party_count),
        "digital_ratio": float(round(digital_ratio, 4)),
        "behaviour_tag": tag,
        "deposit_fee_eligibility_status": deposit_eligibility,  # v0.2.1

        # --- v0.3.0 keys (all default 0 — backward-compatible) ---
        "nedbank_atm_withdrawal_count": nedbank_atm_count,
        "cashout_count": cashout_count,                    # v0.3.1: extended OR clause
        "digital_txn_count": digital_txn_count,
        "total_payments": total_payments,
        "pos_purchase_count": pos_purchase_count,
        "charged_txn_count": charged_txn_count,

        # --- v0.3.1 keys (all default 0 — backward-compatible) ---
        "online_subscription_used": online_subscription_used,
        "eft_to_nedbank_count": eft_to_nedbank_count,
        "eft_to_otherbank_count": eft_to_otherbank_count,
    }
