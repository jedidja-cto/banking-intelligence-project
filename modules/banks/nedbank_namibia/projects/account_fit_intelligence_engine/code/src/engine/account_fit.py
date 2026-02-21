"""
Account fit analysis engine — Silver PAYU v0.2.1

This module orchestrates the account fit analysis process, combining
configuration loading, data processing, fee calculation, and behavioural
feature extraction to produce a comprehensive account fit report.

Changes in v0.2.1:
- Loads customers_sample.csv and builds customer_map for fast lookup
- Integrates compute_cash_deposit_fee into per-customer variable fee pipeline
- Reads account_class from config (no hardcoding)
- Adds deposit eligibility line to per-customer output (only if relevant)
- Adds ASSUMPTIONS footer block flagging customers with missing turnover
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
# This allows imports to work regardless of execution location
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import load_account_config
from ingest.load_data import load_transactions
from fees.tariff_engine import (
    load_fee_schedule,
    compute_variable_fees,
    compute_cash_deposit_fee,
)
from features.build_features import extract_behavioural_features
from utils.paths import find_project_root

import pandas as pd


def load_customers(customers_path: str) -> pd.DataFrame:
    """Load customers CSV and return as DataFrame."""
    return pd.read_csv(customers_path)


def build_customer_map(customers_df: pd.DataFrame) -> dict:
    """
    Build a fast-lookup dict: customer_id -> {segment, annual_turnover}.

    Args:
        customers_df: Customers DataFrame (must have customer_id, customer_segment,
                      and annual_turnover columns)

    Returns:
        Dict keyed on customer_id
    """
    customer_map = {}
    for _, row in customers_df.iterrows():
        turnover_val = row.get('annual_turnover', None)
        # NaN from CSV read becomes None for clean downstream handling
        if pd.isna(turnover_val):
            turnover_val = None
        customer_map[row['customer_id']] = {
            'customer_segment': str(row.get('customer_segment', 'individual')),
            'annual_turnover': turnover_val,
        }
    return customer_map


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

    # Get account class for POS fee determination — config-driven, never hardcoded
    account_class = account_config.get('account_class', 'current')

    # Load data
    transactions = load_transactions(str(tx_path))
    customers_df = load_customers(str(customers_path))
    customer_map = build_customer_map(customers_df)

    # Extract turnover threshold from fee schedule config
    turnover_threshold = (
        fee_schedule.get('cash_deposit', {}).get('turnover_threshold', 1_300_000)
    )

    # Compute variable fees (POS, ATM, online) for all customers
    variable_fees = compute_variable_fees(transactions, fee_schedule, account_class)

    # Get unique customers
    unique_customers = transactions["customer_id"].unique()

    # Collect results for all customers
    results = []
    flagged_turnover_customers = []  # customers with missing turnover + deposit txns

    for customer_id in unique_customers:
        tx_customer = transactions[transactions["customer_id"] == customer_id]

        # Customer profile from map (safe defaults if customer not in customers_df)
        cust_info = customer_map.get(customer_id, {
            'customer_segment': 'individual',
            'annual_turnover': None,
        })
        customer_segment = cust_info['customer_segment']
        annual_turnover = cust_info['annual_turnover']

        # Get fixed fee from config
        fixed_fee = account_config.get('monthly_fee', 30.0)

        # Get variable fee (POS, ATM, online) from tariff engine
        customer_var_fees = variable_fees.get(customer_id, {})
        tx_variable_fee = customer_var_fees.get('variable_total', 0.0)
        by_type = customer_var_fees.get('by_type', {})

        # Count cash_deposit transactions for this customer (no phantom fees)
        deposit_txn_count = int((tx_customer['type'] == 'cash_deposit').sum())

        # Compute cash deposit fee (v0.2.1)
        deposit_result = compute_cash_deposit_fee(
            customer_segment,
            annual_turnover,
            deposit_txn_count,
            fee_schedule,
        )
        deposit_fee = deposit_result['fee']
        eligibility_status = deposit_result['eligibility_status']
        deposit_flags = deposit_result['flags']

        # Accumulate flag if customer needs turnover for deposit fee determination
        if deposit_flags.get('turnover_required_for_deposit_fee'):
            flagged_turnover_customers.append(customer_id)

        # Total variable fee = transaction fees + deposit fee
        variable_fee = round(tx_variable_fee + deposit_fee, 2)

        # Total fee
        total_fee = round(fixed_fee + variable_fee, 2)

        # Top 3 fee drivers (from transaction fees only, then add deposit if applicable)
        fee_drivers = dict(by_type)
        if deposit_fee > 0:
            fee_drivers['cash_deposit'] = fee_drivers.get('cash_deposit', 0.0) + deposit_fee
        top_drivers = sorted(fee_drivers.items(), key=lambda x: x[1], reverse=True)[:3]

        # Extract behavioural features (v0.2.1: pass segment + turnover info)
        features = extract_behavioural_features(
            tx_customer,
            customer_segment=customer_segment,
            annual_turnover=annual_turnover,
            turnover_threshold=turnover_threshold,
        )

        # Determine whether to show deposit line in output:
        # show if customer has deposit txns OR is flagged for missing turnover
        show_deposit_line = (deposit_txn_count > 0) or deposit_flags.get(
            'turnover_required_for_deposit_fee', False
        )

        results.append({
            'customer_id': customer_id,
            'customer_segment': customer_segment,
            'txn_count': features['txn_count'],
            'digital_ratio': features['digital_ratio'],
            'behaviour_tag': features['behaviour_tag'],
            'total_inflow': features['total_inflow'],
            'total_outflow': features['total_outflow'],
            'fixed_fee': fixed_fee,
            'variable_fee': variable_fee,
            'total_fee': total_fee,
            'top_drivers': top_drivers,
            'deposit_fee': deposit_fee,
            'deposit_eligibility': eligibility_status,
            'deposit_txn_count': deposit_txn_count,
            'show_deposit_line': show_deposit_line,
        })

    # -------------------------------------------------------------------------
    # Output: multi-customer summary table
    # -------------------------------------------------------------------------
    print("\n" + "="*62)
    print("Silver PAYU Multi-Customer Intelligence Report  v0.2.1")
    print("="*62)
    print(f"\nAccount Type: {account_config['account_type_id']}")
    print(f"Account Class: {account_class}  (POS pricing path: {account_class})")
    print(f"Total Customers: {len(unique_customers)}")
    print("")

    for r in results:
        seg_label = r['customer_segment'].upper()[:3]  # IND, SME, BUS
        line1 = (f"{r['customer_id']:<11} [{seg_label}] "
                 f"{r['txn_count']:>3}tx {r['digital_ratio']*100:>5.1f}% "
                 f"{r['behaviour_tag']:<17}")
        line2 = f"  In: N${r['total_inflow']:>10,.2f}  Out: N${r['total_outflow']:>10,.2f}"
        line3 = (f"  Fixed: N${r['fixed_fee']:>5.2f}  "
                 f"Var: N${r['variable_fee']:>6.2f}  "
                 f"Total: N${r['total_fee']:>6.2f}")

        print(line1)
        print(line2)
        print(line3)

        # Show deposit eligibility line only if relevant
        if r['show_deposit_line']:
            dep_fee_str = f"N${r['deposit_fee']:.2f}" if r['deposit_fee'] > 0 else "FREE"
            print(f"  Deposit: {r['deposit_eligibility']:<24}  {dep_fee_str} "
                  f"({r['deposit_txn_count']} events)")

        # Show top 3 variable fee drivers if any
        if r['top_drivers']:
            drivers_str = "  Top fees: " + ", ".join(
                [f"{tx_type} N${amt:.2f}" for tx_type, amt in r['top_drivers']]
            )
            print(drivers_str)

        print("")

    print("="*62)

    # -------------------------------------------------------------------------
    # Footer: behaviour distribution + assumptions
    # -------------------------------------------------------------------------
    print("\nBehaviour Distribution:")
    behaviour_counts: dict = {}
    for r in results:
        tag = r['behaviour_tag']
        behaviour_counts[tag] = behaviour_counts.get(tag, 0) + 1

    for tag, count in sorted(behaviour_counts.items()):
        print(f"  {tag:<17} {count:>3} customers")

    print("\nDeposit Eligibility Distribution:")
    eligibility_counts: dict = {}
    for r in results:
        status = r['deposit_eligibility']
        eligibility_counts[status] = eligibility_counts.get(status, 0) + 1
    for status, count in sorted(eligibility_counts.items()):
        print(f"  {status:<28} {count:>3} customers")

    avg_digital_ratio = sum(r['digital_ratio'] for r in results) / len(results)
    avg_total_fee = sum(r['total_fee'] for r in results) / len(results)
    print(f"\nAverage Digital Ratio: {avg_digital_ratio:.1%}")
    print(f"Average Total Fee:     N${avg_total_fee:.2f}")

    # ASSUMPTIONS block — surface missing-data flags transparently
    print("\n" + "-"*62)
    print("ASSUMPTIONS:")
    n_flagged = len(flagged_turnover_customers)
    if n_flagged > 0:
        print(f"  * {n_flagged} customer(s) had missing annual_turnover with cash deposit activity")
        print(f"    → cash deposit fee NOT charged (policy: do_not_charge_flag)")
        print(f"    → flagged for manual turnover verification")
    else:
        print("  * No customers flagged for missing turnover")
    print("  * account_class read from silver_payu.yaml — no hardcoded values")
    print("  * Deposit fee value (N$25.00) is a placeholder pending Nedbank tariff publication")
    print("="*62 + "\n")


if __name__ == '__main__':
    main()
