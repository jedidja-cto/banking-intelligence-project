"""
Account fit analysis engine.

This module orchestrates the account fit analysis process, combining
configuration loading, data processing, fee calculation, and behavioural
feature extraction to produce a comprehensive account fit report.
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
# This allows imports to work regardless of execution location
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import load_account_config
from ingest.load_data import load_transactions
from fees.payu_fee_model import calculate_monthly_fee
from features.build_features import extract_behavioural_features
from utils.paths import find_project_root


def main():
    """Execute the Silver PAYU fee calculation and behavioural analysis pipeline."""
    
    # Reliably locate project root
    PROJECT_ROOT = find_project_root(Path(__file__).resolve())
    
    config_path = PROJECT_ROOT / "configs" / "account_types" / "silver_payu.yaml"
    customers_path = PROJECT_ROOT / "data" / "synthetic" / "customers_sample.csv"
    tx_path = PROJECT_ROOT / "data" / "synthetic" / "transactions_sample.csv"
    
    # Load configuration
    account_config = load_account_config(str(config_path))
    
    # Load transaction data
    transactions = load_transactions(str(tx_path))
    
    # Get unique customers
    unique_customers = transactions["customer_id"].unique()
    
    # Collect results for all customers
    results = []
    for customer_id in unique_customers:
        tx_customer = transactions[transactions["customer_id"] == customer_id]
        
        # Calculate fees
        fee_result = calculate_monthly_fee(account_config, tx_customer)
        
        # Extract behavioural features
        features = extract_behavioural_features(tx_customer)
        
        # Combine results
        results.append({
            'customer_id': customer_id,
            'txn_count': features['txn_count'],
            'digital_ratio': features['digital_ratio'],
            'behaviour_tag': features['behaviour_tag'],
            'total_inflow': features['total_inflow'],
            'total_outflow': features['total_outflow'],
            'total_estimated_fee': fee_result['total_estimated_fee']
        })
    
    # Output multi-customer summary table
    print("\n" + "="*80)
    print("Silver PAYU Multi-Customer Intelligence Report")
    print("="*80)
    print(f"\nAccount Type: {account_config['account_type_id']}")
    print(f"Total Customers: {len(unique_customers)}")
    
    print("\n" + "-"*80)
    print(f"{'Customer ID':<12} {'Txns':<6} {'Digital%':<10} {'Behaviour':<18} {'Inflow':<12} {'Outflow':<12} {'Est.Fee':<10}")
    print("-"*80)
    
    for r in results:
        print(f"{r['customer_id']:<12} {r['txn_count']:<6} {r['digital_ratio']*100:<10.1f} {r['behaviour_tag']:<18} N${r['total_inflow']:<11.2f} N${r['total_outflow']:<11.2f} N${r['total_estimated_fee']:<9.2f}")
    
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
