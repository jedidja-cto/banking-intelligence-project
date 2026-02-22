"""
Synthetic data generation for Account Fit Intelligence Engine.

This module generates realistic synthetic customer and transaction data
for testing and development purposes. No real customer data is used.

Changes in v0.2.1:
- Added customer_segment field: 'individual' | 'sme' | 'business'
- Added annual_turnover for sme/business customers (None for ~40% to simulate missing data)
- Added cash_deposit transactions for a subset of sme/business customers (low frequency)

Changes in v0.3.0:
- Added 'cashout' transaction type for cash_heavy customers (retail CashOut via POS terminal)
- Increased floor nedbank ATM count for cash_heavy archetype so some customers exceed free tier (3)

Changes in v0.3.1:
- Split EFT transfers: eft_transfer_internal (70%) / eft_transfer_external (30%)
- Set transfer_scope accordingly: "to_nedbank_account" or "to_other_bank"
- Spread cashout to mixed_usage (2 per customer) and utilities_focused (1-2 per customer)
  Guarantees >= 4 customers with cashout in a 20-customer run
- Added transfer_scope column to all transaction rows (empty "" where not applicable)
- Prints extra summary lines: cashout customer count, eft_internal count
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.paths import find_project_root

# Deterministic seed for reproducibility
SEED = 42

# Turnover ranges (NAD)
_TURNOVER_BELOW_THRESHOLD = (200_000, 1_299_999)   # sme/business: below N$1.3M
_TURNOVER_ABOVE_THRESHOLD = (1_300_001, 8_000_000)  # sme/business: above N$1.3M


def generate_customers_and_transactions(n_customers: int = 20, seed: int = SEED):
    """
    Generate synthetic customers with behaviour archetypes and their transactions.

    Behaviour archetypes:
    - digital_first: high digital ratio (>= 0.75), low ATM
    - cash_heavy: high ATM ratio (>= 0.40), lower digital
    - utilities_focused: >= 3 utility payments in period
    - mixed_usage: balanced

    Customer segments (v0.2.1):
    - individual:  ~50% of customers — always exempt from cash deposit fees
    - sme:         ~30% — fee applies only if annual_turnover > N$1.3M
    - business:    ~20% — fee applies only if annual_turnover > N$1.3M

    Annual turnover (v0.2.1):
    - Only assigned to sme/business (~60% get a value; ~40% left as None for realism)
    - Individuals always have None (irrelevant to the fee rule)

    Cash deposit transactions (v0.2.1):
    - Generated only for sme/business customers (2–5 txns each)
    - Represents branch or teller cash deposits

    v0.3.1 EFT split:
    - eft_transfer replaced by eft_transfer_internal (70%) / eft_transfer_external (30%)
    - transfer_scope set to "to_nedbank_account" or "to_other_bank" accordingly

    v0.3.1 cashout spread:
    - cash_heavy: 3–8 cashout (unchanged)
    - mixed_usage: exactly 2 cashout per customer
    - utilities_focused: 1–2 cashout per customer

    Args:
        n_customers: Number of customers to generate
        seed: Random seed for reproducibility

    Returns:
        Tuple of (customers_df, transactions_df)
    """
    rng = random.Random(seed)

    # Behaviour archetypes with weights
    archetypes = ['digital_first', 'cash_heavy', 'utilities_focused', 'mixed_usage']

    customers = []
    transactions = []
    txn_id = 1

    # v0.3.1: digital_types no longer includes generic 'eft_transfer' — now split into sub-types
    digital_types = ['pos_purchase', 'third_party_payment', 'eft_transfer_internal', 'eft_transfer_external']
    utility_types = ['airtime_purchase', 'electricity_purchase']

    # Merchants
    merchants = {
        'pos_purchase': ['groceries', 'fuel', 'retail_cashout', 'ecommerce'],
        'airtime_purchase': ['airtime'],
        'electricity_purchase': ['utilities'],
        'third_party_payment': ['transfer'],
        'eft_transfer_internal': ['transfer'],   # v0.3.1: Nedbank-to-Nedbank
        'eft_transfer_external': ['transfer'],   # v0.3.1: Nedbank-to-other-bank
        'eft_transfer': ['transfer'],            # legacy (kept for safety)
        'atm_withdrawal': [''],
        'cash_deposit': ['branch_teller'],
        'cashout': ['shoprite', 'spar', 'clicks', 'pep'],  # v0.3.0: retail CashOut terminals
    }

    # Generate data for January 2026
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31, 23, 59, 59)

    # Customer segment pool — deterministic distribution
    # ~50% individual, ~30% sme, ~20% business
    segment_pool = (
        ['individual'] * 50 +
        ['sme'] * 30 +
        ['business'] * 20
    )
    rng.shuffle(segment_pool)

    for i in range(1, n_customers + 1):
        customer_id = f'CUST_{i:03d}'

        # Customer profile
        age = rng.randint(22, 58)
        income = round(rng.uniform(4500, 35000), 2)

        # Assign customer segment
        customer_segment = segment_pool[(i - 1) % len(segment_pool)]

        # Determine annual_turnover
        # Individuals: always None
        # sme/business: 60% chance of known turnover, 40% chance of None (missing data)
        if customer_segment == 'individual':
            annual_turnover = None
        else:
            has_turnover = rng.random() < 0.60
            if has_turnover:
                # Mix: roughly half below threshold, half above
                if rng.random() < 0.50:
                    annual_turnover = round(rng.uniform(*_TURNOVER_BELOW_THRESHOLD), 2)
                else:
                    annual_turnover = round(rng.uniform(*_TURNOVER_ABOVE_THRESHOLD), 2)
            else:
                annual_turnover = None  # Unknown — deposit fee will not be charged

        customers.append({
            'customer_id': customer_id,
            'age': age,
            'residency': 'namibian_resident',
            'income_gross_monthly': income,
            'customer_segment': customer_segment,   # v0.2.1
            'account_category': 'everyday',
            'account_type_id': 'silver_payu',
            'annual_turnover': annual_turnover,     # v0.2.1
        })

        # Assign archetype with balanced weights
        # digital_first: 35%, cash_heavy: 25%, utilities_focused: 20%, mixed_usage: 20%
        archetype = rng.choices(
            ['digital_first', 'cash_heavy', 'utilities_focused', 'mixed_usage'],
            weights=[35, 25, 20, 20],
            k=1
        )[0]

        # Generate transactions based on archetype
        if archetype == 'digital_first':
            # High digital ratio (>= 0.75), low ATM
            n_txns = rng.randint(35, 55)
            digital_count = int(n_txns * rng.uniform(0.75, 0.90))
            atm_count = rng.randint(1, 3)
            utility_count = n_txns - digital_count - atm_count - 1  # -1 for income
            cashout_count = 0

        elif archetype == 'cash_heavy':
            # High ATM ratio (>= 0.40), lower digital
            # v0.3.0: raise floor ATM count to 4 so nedbank ATM users exceed free tier of 3
            n_txns = rng.randint(25, 45)
            atm_count = int(n_txns * rng.uniform(0.40, 0.55))
            atm_count = max(atm_count, 4)  # v0.3.0: ensure >= 4 ATM withdrawals for free-tier testing
            # Also generate cashout transactions for cash_heavy customers (3-8 per month)
            cashout_count = rng.randint(3, 8)
            digital_count = rng.randint(5, 10)
            utility_count = max(0, n_txns - digital_count - atm_count - cashout_count - 1)

        elif archetype == 'utilities_focused':
            # >= 3 utility payments
            n_txns = rng.randint(30, 50)
            utility_count = rng.randint(5, 10)
            atm_count = rng.randint(3, 8)
            digital_count = n_txns - utility_count - atm_count - 1
            cashout_count = rng.randint(1, 2)   # v0.3.1: 1–2 cashout per customer

        else:  # mixed_usage
            # Balanced
            n_txns = rng.randint(30, 50)
            digital_count = int(n_txns * rng.uniform(0.35, 0.55))
            atm_count = int(n_txns * rng.uniform(0.20, 0.35))
            utility_count = n_txns - digital_count - atm_count - 1
            cashout_count = 2   # v0.3.1: exactly 2 cashout per mixed_usage customer

        # Ensure counts are non-negative
        utility_count = max(0, utility_count)
        digital_count = max(0, digital_count)

        # Helper: build a standard transaction row
        def _txn(txn_type, amount, merchant, channel, atm_owner='', pos_scope='', transfer_scope=''):
            nonlocal txn_id
            ts = start_date + timedelta(
                days=rng.randint(1, 30),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59)
            )
            row = {
                'transaction_id': f'TXN_{txn_id:05d}',
                'customer_id': customer_id,
                'ts': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'type': txn_type,
                'merchant': merchant,
                'channel': channel,
                'atm_owner': atm_owner,
                'pos_scope': pos_scope,
                'transfer_scope': transfer_scope,  # v0.3.1
            }
            txn_id += 1
            return row

        # Generate income transaction (always first)
        ts_income = start_date + timedelta(days=rng.randint(0, 3), hours=rng.randint(0, 23))
        transactions.append({
            'transaction_id': f'TXN_{txn_id:05d}',
            'customer_id': customer_id,
            'ts': ts_income.strftime('%Y-%m-%d %H:%M:%S'),
            'amount': -income,
            'type': 'income',
            'merchant': '',
            'channel': '',
            'atm_owner': '',
            'pos_scope': '',
            'transfer_scope': '',   # v0.3.1: always empty for income
        })
        txn_id += 1

        # Generate digital transactions
        # v0.3.1: eft_transfer is now split into eft_transfer_internal (70%) / eft_transfer_external (30%)
        for _ in range(digital_count):
            # Pick from the updated digital_types pool
            txn_type_raw = rng.choices(
                ['pos_purchase', 'third_party_payment', 'eft_split'],
                weights=[40, 20, 40],   # ~40% will be some form of EFT
                k=1
            )[0]

            if txn_type_raw == 'eft_split':
                # 70% internal (to Nedbank), 30% external (to other bank)
                if rng.random() < 0.70:
                    txn_type = 'eft_transfer_internal'
                    transfer_scope = 'to_nedbank_account'
                else:
                    txn_type = 'eft_transfer_external'
                    transfer_scope = 'to_other_bank'
            else:
                txn_type = txn_type_raw
                transfer_scope = ''

            amount = round(rng.uniform(50, 800), 2)
            merchant = rng.choice(merchants[txn_type])

            if txn_type == 'pos_purchase':
                channel = 'pos'
                pos_scope = 'local'
            else:
                channel = 'online'
                pos_scope = ''

            transactions.append(_txn(
                txn_type, amount, merchant, channel,
                pos_scope=pos_scope, transfer_scope=transfer_scope
            ))

        # Generate ATM transactions
        for _ in range(atm_count):
            amount = round(rng.uniform(200, 1500), 2)
            # 70% Nedbank ATM, 30% other bank ATM
            atm_owner = rng.choices(['nedbank', 'other_bank'], weights=[70, 30], k=1)[0]
            transactions.append(_txn(
                'atm_withdrawal', amount, '', 'atm', atm_owner=atm_owner
            ))

        # Generate utility transactions
        for _ in range(utility_count):
            txn_type = rng.choice(utility_types)
            if txn_type == 'airtime_purchase':
                amount = round(rng.uniform(20, 150), 2)
            else:  # electricity
                amount = round(rng.uniform(100, 600), 2)
            merchant = rng.choice(merchants[txn_type])
            transactions.append(_txn(
                txn_type, amount, merchant, 'online'
            ))

        # Generate cashout transactions (v0.3.0 cash_heavy / v0.3.1 mixed_usage + utilities_focused)
        # Channel: pos. No transfer_scope.
        for _ in range(cashout_count):
            amount = round(rng.uniform(100, 1000), 2)
            ts_co = start_date + timedelta(
                days=rng.randint(1, 30),
                hours=rng.randint(8, 20),
                minutes=rng.randint(0, 59)
            )
            merchant = rng.choice(merchants['cashout'])
            transactions.append({
                'transaction_id': f'TXN_{txn_id:05d}',
                'customer_id': customer_id,
                'ts': ts_co.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'type': 'cashout',
                'merchant': merchant,
                'channel': 'pos',
                'atm_owner': '',
                'pos_scope': 'local',
                'transfer_scope': '',   # v0.3.1
            })
            txn_id += 1

        # v0.2.1: Generate cash_deposit transactions for sme/business customers only.
        # Frequency: 2–5 deposits per month (low frequency; branch/teller event).
        # Deposit amounts: N$500–N$20,000 (business cash handling range).
        if customer_segment in ('sme', 'business'):
            n_deposits = rng.randint(2, 5)
            for _ in range(n_deposits):
                amount = round(rng.uniform(500, 20_000), 2)
                ts_dep = start_date + timedelta(
                    days=rng.randint(1, 30),
                    hours=rng.randint(8, 16),   # branch hours
                    minutes=rng.randint(0, 59)
                )
                transactions.append({
                    'transaction_id': f'TXN_{txn_id:05d}',
                    'customer_id': customer_id,
                    'ts': ts_dep.strftime('%Y-%m-%d %H:%M:%S'),
                    'amount': amount,
                    'type': 'cash_deposit',
                    'merchant': 'branch_teller',
                    'channel': 'branch',
                    'atm_owner': '',
                    'pos_scope': '',
                    'transfer_scope': '',   # v0.3.1
                })
                txn_id += 1

    customers_df = pd.DataFrame(customers)
    transactions_df = pd.DataFrame(transactions)

    return customers_df, transactions_df


def main():
    """Generate synthetic data and save to CSV files."""
    print("Generating synthetic data with behaviour archetypes...")

    # Find project root
    PROJECT_ROOT = find_project_root(Path(__file__).resolve())

    # Generate data
    customers, transactions = generate_customers_and_transactions(n_customers=20, seed=SEED)

    # Output paths
    customers_path = PROJECT_ROOT / 'data' / 'synthetic' / 'customers_sample.csv'
    transactions_path = PROJECT_ROOT / 'data' / 'synthetic' / 'transactions_sample.csv'

    # Save to CSV
    customers.to_csv(customers_path, index=False)
    transactions.to_csv(transactions_path, index=False)

    # Summary (v0.2.1 lines)
    n_sme_biz = customers['customer_segment'].isin(['sme', 'business']).sum()
    n_turnover_known = customers['annual_turnover'].notna().sum()
    n_deposits = (transactions['type'] == 'cash_deposit').sum()

    print(f"Generated {len(customers)} customers:")
    print(f"  - Individual: {(customers['customer_segment'] == 'individual').sum()}")
    print(f"  - SME:        {(customers['customer_segment'] == 'sme').sum()}")
    print(f"  - Business:   {(customers['customer_segment'] == 'business').sum()}")
    print(f"  - Turnover known (sme/business): {n_turnover_known} / {n_sme_biz}")
    print(f"Generated {len(transactions)} transactions (incl. {n_deposits} cash_deposit events)")

    # v0.3.1: extra summary lines
    cashout_customers = transactions[transactions['type'] == 'cashout']['customer_id'].nunique()
    eft_internal_count = (transactions['type'] == 'eft_transfer_internal').sum()
    eft_external_count = (transactions['type'] == 'eft_transfer_external').sum()
    print(f"Cashout customers: {cashout_customers} / {len(customers)}")
    print(f"EFT-internal transactions: {eft_internal_count}  "
          f"EFT-external: {eft_external_count}")

    print(f"Files written to:")
    print(f"  - {customers_path}")
    print(f"  - {transactions_path}")


if __name__ == '__main__':
    main()
