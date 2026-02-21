"""
Account fit analysis engine.

This module orchestrates the account fit analysis process, combining
configuration loading, data processing, fee calculation, and behavioural
feature extraction to produce a comprehensive account fit report.
"""

from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import load_account_config
from ingest.load_data import load_transactions
from fees.payu_fee_model import calculate_monthly_fee
from features.build_features import extract_behavioural_features


def main():
    """Execute the Silver PAYU fee calculation and behavioural analysis pipeline."""
    
    # Define paths relative to project root
    BASE = Path(__file__).resolve().parents[3]
    
    config_path = BASE / "configs" / "account_types" / "silver_payu.yaml"
    tx_path = BASE / "data" / "synthetic" / "transactions_sample.csv"
    
    # Load configuration
    account_config = load_account_config(str(config_path))
    
    # Load transaction data
    transactions = load_transactions(str(tx_path))
    
    # Filter to first customer for v0.1.1 (single customer analysis)
    customer_id = transactions["customer_id"].iloc[0]
    tx_customer = transactions[transactions["customer_id"] == customer_id]
    
    # Calculate fees
    result = calculate_monthly_fee(account_config, tx_customer)
    
    # Extract behavioural features
    features = extract_behavioural_features(tx_customer)
    
    # Output results
    print("\n" + "="*60)
    print("Silver PAYU Account Intelligence Report")
    print("="*60)
    print(f"\nCustomer ID: {customer_id}")
    print(f"Account Type: {account_config['account_type_id']}")
    
    print("\n--- Fee Estimate ---")
    print(f"Fixed Monthly Fee:       N${result['fixed_monthly_fee']:.2f}")
    print(f"Variable Fee Estimate:   N${result['variable_fee_estimate']:.2f}")
    print(f"Total Estimated Fee:     N${result['total_estimated_fee']:.2f}")
    print(f"\nNotes: {result['notes']}")
    
    print("\n--- Behavioural Profile ---")
    print(f"Transaction Count:       {features['txn_count']}")
    print(f"Total Inflow:            N${features['total_inflow']:.2f}")
    print(f"Total Outflow:           N${features['total_outflow']:.2f}")
    print(f"ATM Withdrawals:         {features['atm_withdrawal_count']}")
    print(f"Utility Payments:        {features['utility_count']}")
    print(f"Third-Party Payments:    {features['third_party_payment_count']}")
    print(f"Digital Ratio:           {features['digital_ratio']:.1%}")
    print(f"Behaviour Tag:           {features['behaviour_tag']}")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
