"""
Account fit analysis engine.

This module orchestrates the account fit analysis process, combining
configuration loading, data processing, and fee calculation to produce
a comprehensive account fit report.
"""

from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import load_account_config
from ingest.load_data import load_transactions
from fees.payu_fee_model import calculate_monthly_fee


def main():
    """Execute the Silver PAYU fee calculation pipeline."""
    
    # Define paths relative to project root
    BASE = Path(__file__).resolve().parents[3]
    
    config_path = BASE / "configs" / "account_types" / "silver_payu.yaml"
    tx_path = BASE / "data" / "synthetic" / "transactions_sample.csv"
    
    # Load configuration
    account_config = load_account_config(str(config_path))
    
    # Load transaction data
    transactions = load_transactions(str(tx_path))
    
    # Calculate fees
    result = calculate_monthly_fee(account_config, transactions)
    
    # Output results
    print("\n" + "="*60)
    print("Silver PAYU Monthly Fee Estimate")
    print("="*60)
    print(f"Fixed Monthly Fee:       N${result['fixed_monthly_fee']:.2f}")
    print(f"Variable Fee Estimate:   N${result['variable_fee_estimate']:.2f}")
    print(f"Total Estimated Fee:     N${result['total_estimated_fee']:.2f}")
    print(f"\nNotes: {result['notes']}")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
