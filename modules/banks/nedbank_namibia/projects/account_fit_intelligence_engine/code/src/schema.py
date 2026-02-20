"""
Data schemas and validation for Account Fit Intelligence Engine.

This module defines the expected schemas for customer and transaction data
and provides validation functions to ensure data quality.
"""

from dataclasses import dataclass
from typing import List, Tuple
import pandas as pd


@dataclass
class Customer:
    """Customer profile data structure."""
    customer_id: str
    age: int
    residency: str
    income_gross_monthly: float
    customer_segment: str
    account_category: str
    account_type_id: str


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
CUSTOMER_SCHEMA = {
    'customer_id': 'string',
    'age': 'int',
    'residency': 'string',
    'income_gross_monthly': 'float',
    'customer_segment': 'string',
    'account_category': 'string',
    'account_type_id': 'string'
}

CUSTOMER_REQUIRED_COLUMNS = list(CUSTOMER_SCHEMA.keys())

# Transaction Schema Definition
TRANSACTION_SCHEMA = {
    'transaction_id': 'string',
    'customer_id': 'string',
    'ts': 'datetime',
    'amount': 'float',
    'type': 'string',
    'merchant': 'string'  # Can be null
}

TRANSACTION_REQUIRED_COLUMNS = list(TRANSACTION_SCHEMA.keys())

# Valid transaction types
VALID_TRANSACTION_TYPES = [
    'pos_purchase',
    'airtime_purchase',
    'electricity_purchase',
    'third_party_payment',
    'atm_withdrawal',
    'eft_transfer',
    'income'
]

# Valid residency values
VALID_RESIDENCY = ['namibian_resident', 'non_resident']
