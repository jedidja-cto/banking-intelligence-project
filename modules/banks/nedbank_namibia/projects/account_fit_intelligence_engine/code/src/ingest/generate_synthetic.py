"""
Synthetic data generation for Account Fit Intelligence Engine.

This module generates realistic synthetic customer and transaction data
for testing and development purposes. No real customer data is used.
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


def generate_customers_and_transactions(n_customers: int = 20, seed: int = SEED):
    """
    Generate synthetic customers with behaviour archetypes and their transactions.
    
    Behaviour archetypes:
    - digital_first: high digital ratio (>= 0.75), low ATM
    - cash_heavy: high ATM ratio (>= 0.40), lower digital
    - utilities_focused: >= 3 utility payments in period
    - mixed_usage: balanced
    
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
    
    # Transaction types for PAYU
    digital_types = ['pos_purchase', 'third_party_payment', 'eft_transfer']
    utility_types = ['airtime_purchase', 'electricity_purchase']
    
    # Merchants
    merchants = {
        'pos_purchase': ['groceries', 'fuel', 'retail_cashout', 'ecommerce'],
        'airtime_purchase': ['airtime'],
        'electricity_purchase': ['utilities'],
        'third_party_payment': ['transfer'],
        'eft_transfer': ['transfer'],
        'atm_withdrawal': ['']
    }
    
    # Generate data for January 2026
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 31, 23, 59, 59)
    
    for i in range(1, n_customers + 1):
        customer_id = f'CUST_{i:03d}'
        
        # Customer profile
        age = rng.randint(22, 58)
        income = round(rng.uniform(4500, 35000), 2)
        
        customers.append({
            'customer_id': customer_id,
            'age': age,
            'residency': 'namibian_resident',
            'income_gross_monthly': income,
            'customer_segment': 'personal',
            'account_category': 'everyday',
            'account_type_id': 'silver_payu'
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
            
        elif archetype == 'cash_heavy':
            # High ATM ratio (>= 0.40), lower digital
            n_txns = rng.randint(25, 45)
            atm_count = int(n_txns * rng.uniform(0.40, 0.55))
            digital_count = rng.randint(5, 10)
            utility_count = n_txns - digital_count - atm_count - 1
            
        elif archetype == 'utilities_focused':
            # >= 3 utility payments
            n_txns = rng.randint(30, 50)
            utility_count = rng.randint(5, 10)
            atm_count = rng.randint(3, 8)
            digital_count = n_txns - utility_count - atm_count - 1
            
        else:  # mixed_usage
            # Balanced
            n_txns = rng.randint(30, 50)
            digital_count = int(n_txns * rng.uniform(0.35, 0.55))
            atm_count = int(n_txns * rng.uniform(0.20, 0.35))
            utility_count = n_txns - digital_count - atm_count - 1
        
        # Ensure counts are non-negative
        utility_count = max(0, utility_count)
        
        # Generate income transaction (always first)
        ts = start_date + timedelta(days=rng.randint(0, 3), hours=rng.randint(0, 23))
        transactions.append({
            'transaction_id': f'TXN_{txn_id:05d}',
            'customer_id': customer_id,
            'ts': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'amount': -income,
            'type': 'income',
            'merchant': ''
        })
        txn_id += 1
        
        # Generate digital transactions
        for _ in range(digital_count):
            txn_type = rng.choice(digital_types)
            amount = round(rng.uniform(50, 800), 2)
            merchant = rng.choice(merchants[txn_type])
            ts = start_date + timedelta(days=rng.randint(1, 30), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
            
            transactions.append({
                'transaction_id': f'TXN_{txn_id:05d}',
                'customer_id': customer_id,
                'ts': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'type': txn_type,
                'merchant': merchant
            })
            txn_id += 1
        
        # Generate ATM transactions
        for _ in range(atm_count):
            amount = round(rng.uniform(200, 1500), 2)
            ts = start_date + timedelta(days=rng.randint(1, 30), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
            
            transactions.append({
                'transaction_id': f'TXN_{txn_id:05d}',
                'customer_id': customer_id,
                'ts': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'type': 'atm_withdrawal',
                'merchant': ''
            })
            txn_id += 1
        
        # Generate utility transactions
        for _ in range(utility_count):
            txn_type = rng.choice(utility_types)
            if txn_type == 'airtime_purchase':
                amount = round(rng.uniform(20, 150), 2)
            else:  # electricity
                amount = round(rng.uniform(100, 600), 2)
            
            merchant = rng.choice(merchants[txn_type])
            ts = start_date + timedelta(days=rng.randint(1, 30), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
            
            transactions.append({
                'transaction_id': f'TXN_{txn_id:05d}',
                'customer_id': customer_id,
                'ts': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'type': txn_type,
                'merchant': merchant
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
    
    print(f"Generated {len(customers)} customers")
    print(f"Generated {len(transactions)} transactions")
    print(f"Files written to:")
    print(f"  - {customers_path}")
    print(f"  - {transactions_path}")


if __name__ == '__main__':
    main()
