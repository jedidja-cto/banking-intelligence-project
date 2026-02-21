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
from fees.tariff_engine import load_fee_schedule, compute_variable_fees
from features.build_features import extract_behavioural_features
from utils.paths import find_project_root


def main():
    """Execute the Silver PAYU fee calculation and behavioural analysis pipeline."""
    
    # Reliably locate project root
    PROJECT_ROOT = find_project_root(Path(__file__).resolve())
    
    config_path = PROJECT_ROOT / "configs" / "account_types" / "silver_payu.yaml"
    fee_schedule_path = PROJECT_ROOT / "configs" / "fee_schedules" / "nedbank_2026_27.yaml"
    customers_path = PROJECT_ROOT / "data" / "synthetic" / "customers_sample.csv"
    tx_path = PROJECT_ROOT / "data" / "synthetic" / "transactions_sample.csv"
    
    # Load configuration
    account_config = load_account_config(str(config_path))
    fee_schedule = load_fee_schedule(str(fee_schedule_path))
    
    # Load transaction data
    transactions = load_transactions(str(tx_path))
    
    # Get account class for POS fee determination
    account_class = account_config.get('account_class', 'current')
    
    # Compute variable fees for all customers
    variable_fees = compute_variable_fees(transactions, fee_schedule, account_class)
    
    # Get unique customers
    unique_customers = transactions["customer_id"].unique()
    
    # Collect results for all customers
    results = []
    for customer_id in unique_customers:
        tx_customer = transactions[transactions["customer_id"] == customer_id]
        
        # Get fixed fee from config
        fixed_fee = account_config.get('monthly_fee', 30.0)
        
        # Get variable fee from tariff engine
        customer_var_fees = variable_fees.get(customer_id, {})
        variable_fee = customer_var_fees.get('variable_total', 0.0)
        by_type = customer_var_fees.get('by_type', {})
        
        # Calculate total fee
        total_fee = fixed_fee + variable_fee
        
        # Get top 3 fee drivers
        top_drivers = sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:3]
        
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
            'fixed_fee': fixed_fee,
            'variable_fee': variable_fee,
            'total_fee': total_fee,
            'top_drivers': top_drivers
        })
    
    # Output multi-customer summary table with stable column widths
    # Designed for narrow terminals (59 chars)
    print("\n" + "="*58)
    print("Silver PAYU Multi-Customer Intelligence Report")
    print("="*58)
    print(f"\nAccount Type: {account_config['account_type_id']}")
    print(f"Total Customers: {len(unique_customers)}")
    print("")
    
    for r in results:
        # Multi-line format per customer with fee breakdown
        line1 = f"{r['customer_id']:<11} {r['txn_count']:>3}tx {r['digital_ratio']*100:>5.1f}% {r['behaviour_tag']:<17}"
        line2 = f"  In: N${r['total_inflow']:>10,.2f}  Out: N${r['total_outflow']:>10,.2f}"
        line3 = f"  Fixed: N${r['fixed_fee']:>5.2f}  Var: N${r['variable_fee']:>6.2f}  Total: N${r['total_fee']:>6.2f}"
        
        print(line1)
        print(line2)
        print(line3)
        
        # Show top 3 variable fee drivers if any
        if r['top_drivers']:
            drivers_str = "  Top fees: " + ", ".join([f"{tx_type} N${amt:.2f}" for tx_type, amt in r['top_drivers']])
            print(drivers_str)
        
        print("")
    
    print("="*58)
    
    # Footer summary
    print("\nBehaviour Distribution:")
    behaviour_counts = {}
    for r in results:
        tag = r['behaviour_tag']
        behaviour_counts[tag] = behaviour_counts.get(tag, 0) + 1
    
    for tag, count in sorted(behaviour_counts.items()):
        print(f"  {tag:<17} {count:>3} customers")
    
    avg_digital_ratio = sum(r['digital_ratio'] for r in results) / len(results)
    avg_total_fee = sum(r['total_fee'] for r in results) / len(results)
    print(f"\nAverage Digital Ratio: {avg_digital_ratio:.1%}")
    print(f"Average Total Fee: N${avg_total_fee:.2f}")
    print("="*58 + "\n")


if __name__ == '__main__':
    main()
