"""
Data schemas and validation for Account Fit Intelligence Engine.

This module defines the expected schemas for customer and transaction data
and provides validation functions to ensure data quality.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import pandas as pd


@dataclass
class Customer:
    """Customer profile data structure.

    Fields added in v0.2.1:
        customer_segment: Segment type — 'individual', 'sme', or 'business'.
            Determines cash deposit fee eligibility (individuals are always exempt).
        annual_turnover: Annual business turnover in NAD. Only relevant for sme/business.
            If None, turnover is unknown — deposit fee will not be charged and the
            customer will be flagged for manual review.
    """
    customer_id: str
    age: int
    residency: str
    income_gross_monthly: float
    customer_segment: str          # 'individual' | 'sme' | 'business'
    account_category: str
    account_type_id: str
    annual_turnover: Optional[float] = None   # NAD; None = unknown


@dataclass
class Transaction:
    """Transaction data structure."""
    transaction_id: str
    customer_id: str
    ts: str
    amount: float
    type: str
    merchant: str


# Customer Schema Definition
# annual_turnover is optional — NULL means unknown (do not charge deposit fee).
# customer_segment values: 'individual' | 'sme' | 'business'
CUSTOMER_SCHEMA = {
    'customer_id': 'string',
    'age': 'int',
    'residency': 'string',
    'income_gross_monthly': 'float',
    'customer_segment': 'string',
    'account_category': 'string',
    'account_type_id': 'string',
    'annual_turnover': 'float',      # optional — may be NaN/None
}

CUSTOMER_REQUIRED_COLUMNS = list(CUSTOMER_SCHEMA.keys())

# Transaction Schema Definition
TRANSACTION_SCHEMA = {
    'transaction_id': 'string',
    'customer_id': 'string',
    'ts': 'datetime',
    'amount': 'float',
    'type': 'string',
    'merchant': 'string',  # Can be null
    'channel': 'string',  # online, atm, pos
    'atm_owner': 'string',  # nedbank, other_bank (for atm_withdrawal)
    'pos_scope': 'string',  # local (for pos_purchase)
    'transfer_scope': 'string',  # v0.3.1: optional; "to_nedbank_account" | "to_other_bank" | ""
}

TRANSACTION_REQUIRED_COLUMNS = ['transaction_id', 'customer_id', 'ts', 'amount', 'type', 'merchant']

# Valid transaction types
# cash_deposit added in v0.2.1 — low frequency, sme/business only in synthetic data.
# cashout added in v0.3.0 — retail cash dispensed via POS terminal (e.g. CashOut at Shoprite).
# eft_transfer_internal / eft_transfer_external added in v0.3.1 — EFT sub-types by bank scope.
VALID_TRANSACTION_TYPES = [
    'pos_purchase',
    'airtime_purchase',
    'electricity_purchase',
    'third_party_payment',
    'atm_withdrawal',
    'eft_transfer',
    'eft_transfer_internal',   # v0.3.1: EFT to Nedbank account
    'eft_transfer_external',   # v0.3.1: EFT to other bank
    'income',
    'cash_deposit',
    'cashout',                 # v0.3.0: retail CashOut via POS terminal
]

# Valid residency values
VALID_RESIDENCY = ['namibian_resident', 'non_resident']


def validate_customer_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate customer DataFrame against expected schema.
    
    Args:
        df: Customer DataFrame to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Example:
        >>> customers = pd.read_csv('data/synthetic/customers_sample.csv')
        >>> is_valid, errors = validate_customer_data(customers)
        >>> if not is_valid:
        ...     print("Validation errors:", errors)
    """
    errors = []
    
    # TODO: Implement validation logic
    # - Check all required columns present
    # - Verify no duplicate customer_ids
    # - Check age range (18-100)
    # - Check income >= 0
    # - Verify residency in valid values
    # - Check customer_segment, account_category, account_type_id not null
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_transaction_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate transaction DataFrame against expected schema.
    
    Args:
        df: Transaction DataFrame to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Example:
        >>> transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
        >>> is_valid, errors = validate_transaction_data(transactions)
        >>> if not is_valid:
        ...     print("Validation errors:", errors)
    """
    errors = []
    
    # TODO: Implement validation logic
    # - Check all required columns present
    # - Verify no duplicate transaction_ids
    # - Check timestamps are valid and chronological
    # - Verify transaction types in valid list
    # - Check amount is numeric
    # - Verify merchant present for merchant-based transactions
    
    is_valid = len(errors) == 0
    return is_valid, errors


def check_referential_integrity(customers: pd.DataFrame, transactions: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Verify referential integrity between customers and transactions.
    
    Args:
        customers: Customer DataFrame
        transactions: Transaction DataFrame
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Example:
        >>> customers = pd.read_csv('data/synthetic/customers_sample.csv')
        >>> transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
        >>> is_valid, errors = check_referential_integrity(customers, transactions)
        >>> if not is_valid:
        ...     print("Referential integrity errors:", errors)
    """
    errors = []
    
    # TODO: Implement referential integrity checks
    # - Verify all transaction.customer_id exist in customer.customer_id
    # - Check for orphaned transactions
    # - Verify no customers without transactions (warning, not error)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def validate_all_data(customers: pd.DataFrame, transactions: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Run all validation checks on customer and transaction data.
    
    Args:
        customers: Customer DataFrame
        transactions: Transaction DataFrame
        
    Returns:
        Tuple of (is_valid, list_of_all_errors)
        
    Example:
        >>> customers = pd.read_csv('data/synthetic/customers_sample.csv')
        >>> transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
        >>> is_valid, errors = validate_all_data(customers, transactions)
        >>> if is_valid:
        ...     print("All data validation passed!")
        >>> else:
        ...     for error in errors:
        ...         print(f"Error: {error}")
    """
    all_errors = []
    
    # Validate customers
    customer_valid, customer_errors = validate_customer_data(customers)
    all_errors.extend(customer_errors)
    
    # Validate transactions
    transaction_valid, transaction_errors = validate_transaction_data(transactions)
    all_errors.extend(transaction_errors)
    
    # Check referential integrity
    integrity_valid, integrity_errors = check_referential_integrity(customers, transactions)
    all_errors.extend(integrity_errors)
    
    is_valid = len(all_errors) == 0
    return is_valid, all_errors
