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
    print("\n" + "="*90)
    print("Silver PAYU Multi-Customer Intelligence Report")
    print("="*90)
    print(f"\nAccount Type: {account_config['account_type_id']}")
    print(f"Total Customers: {len(unique_customers)}")
    
    print("\n" + "-"*90)
    print(f"{'Customer ID':<13} {'Txns':<6} {'Digital%':<11} {'Behaviour':<18} {'Inflow':<15} {'Outflow':<15} {'Est.Fee':<12}")
    print("-"*90)
    
    for r in results:
        inflow_str = f"N${r['total_inflow']:,.2f}"
        outflow_str = f"N${r['total_outflow']:,.2f}"
        fee_str = f"N${r['total_estimated_fee']:,.2f}"
        print(f"{r['customer_id']:<13} {r['txn_count']:<6} {r['digital_ratio']*100:<11.1f} {r['behaviour_tag']:<18} {inflow_str:<15} {outflow_str:<15} {fee_str:<12}")
    
    print("="*90)
    
    # Footer summary
    print("\nBehaviour Distribution:")
    behaviour_counts = {}
    for r in results:
        tag = r['behaviour_tag']
        behaviour_counts[tag] = behaviour_counts.get(tag, 0) + 1
    
    for tag, count in sorted(behaviour_counts.items()):
        print(f"  {tag:<18} {count:>3} customers")
    
    avg_digital_ratio = sum(r['digital_ratio'] for r in results) / len(results)
    print(f"\nAverage Digital Ratio: {avg_digital_ratio:.1%}")
    print("="*90 + "\n")


if __name__ == '__main__':
    main()
