# Demo and Usage

## Purpose

This document provides usage examples and demonstrations of the Account Fit Intelligence Engine v0.1.

## Scope

Practical usage guide for v0.1 (Silver PAYU simulator), including setup, execution, and output interpretation.

## Setup

### Prerequisites

- Python 3.8+
- Required packages: pandas, numpy, pyyaml, pytest
- Jupyter (for notebooks)

### Installation

```bash
cd modules/banks/nedbank_namibia/projects/account_fit_intelligence_engine

# Install dependencies (when requirements.txt is created)
pip install -r requirements.txt
```

## Usage Examples

### Example 1: Generate Synthetic Data

```python
from code.src.ingest.generate_synthetic import generate_customers, generate_transactions

# Generate 100 customers
customers = generate_customers(n_customers=100, seed=42)
customers.to_csv('data/synthetic/customers_sample.csv', index=False)

# Generate 6 months of transactions
transactions = generate_transactions(
    customers=customers,
    months=6,
    seed=42
)
transactions.to_csv('data/synthetic/transactions_sample.csv', index=False)

print(f"Generated {len(customers)} customers")
print(f"Generated {len(transactions)} transactions")
```

### Example 2: Calculate Fees for Silver PAYU

```python
import yaml
import pandas as pd
from code.src.fees.payu_fee_model import calculate_monthly_fee

# Load configuration
with open('configs/account_types/silver_payu.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Load transactions for a customer
transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
customer_txns = transactions[transactions['customer_id'] == 'CUST_001']

# Calculate fees
fees = calculate_monthly_fee(config, customer_txns)

print(f"Monthly Fee: {fees['monthly_fee_fixed']} NAD")
print(f"Transaction Fee Estimate: {fees['transaction_fee_estimate']} NAD")
print(f"Total Estimate: {fees['total_monthly_estimate']} NAD")
print(f"Notes: {fees['notes']}")
```

**Expected Output:**
```
Monthly Fee: 30.0 NAD
Transaction Fee Estimate: 0.0 NAD
Total Estimate: 30.0 NAD
Notes: Transaction fees unknown; using placeholder value of 0. Actual costs may vary.
```

### Example 3: Extract Behaviour Features

```python
from code.src.features.build_features import build_features

# Load data
customers = pd.read_csv('data/synthetic/customers_sample.csv')
transactions = pd.read_csv('data/synthetic/transactions_sample.csv')

# Build features
features = build_features(customers, transactions, time_period_months=6)

# View features for one customer
customer_features = features[features['customer_id'] == 'CUST_001']
print(customer_features.to_dict('records')[0])
```

**Expected Output:**
```python
{
    'customer_id': 'CUST_001',
    'txn_count_monthly': 15.2,
    'txn_amount_monthly_avg': 3250.50,
    'pos_purchase_freq': 6.1,
    'atm_withdrawal_freq': 2.3,
    'airtime_purchase_freq': 2.3,
    'electricity_purchase_freq': 1.5,
    'eft_transfer_freq': 1.5,
    'third_party_payment_freq': 0.8,
    'income_freq': 0.8,
    'avg_transaction_amount': 213.70,
    'max_transaction_amount': 1200.00,
    'transaction_diversity': 7
}
```

### Example 4: Full Account Fit Analysis

```python
from code.src.engine.account_fit import analyze_account_fit

# Analyze fit for a customer
result = analyze_account_fit(
    customer_id='CUST_001',
    account_type='silver_payu',
    config_path='configs/account_types/silver_payu.yaml',
    data_path='data/synthetic/'
)

print(f"Customer: {result['customer_id']}")
print(f"Account: {result['account_type']}")
print(f"\nFee Analysis:")
print(f"  Monthly Fee: {result['fees']['monthly_fee_fixed']} NAD")
print(f"  Total Estimate: {result['fees']['total_monthly_estimate']} NAD")
print(f"\nBehaviour Summary:")
print(f"  Transactions/month: {result['features']['txn_count_monthly']}")
print(f"  Transaction diversity: {result['features']['transaction_diversity']}")
print(f"\nEligibility: {result['eligibility_status']}")
```

## Jupyter Notebook Demos

### Notebook 1: Data Exploration

**File:** `notebooks/00_exploration.ipynb`

**Contents:**
- Load and inspect synthetic data
- Visualize customer distributions (age, income)
- Analyze transaction patterns
- Identify data quality issues

**Key Visualizations:**
- Customer age distribution
- Income distribution
- Transaction type frequency
- Transaction amount distribution
- Temporal patterns

### Notebook 2: Fee Model Validation

**File:** `notebooks/01_fee_model_validation.ipynb`

**Contents:**
- Test fee calculation logic
- Compare fees across different usage patterns
- Validate against known scenarios
- Document limitations

**Key Analyses:**
- Fee calculation for low/medium/high usage customers
- Sensitivity analysis (how fees change with behaviour)
- Edge case testing (zero transactions, extreme values)

# Commands

**Generate synthetic data:**
```bash
python code/src/ingest/generate_synthetic.py
```

**Run Silver PAYU report:**
```bash
python code/src/engine/account_fit.py --account silver_payu
```

**Run Basic Banking report:**
```bash
python code/src/engine/account_fit.py --account basic_banking
```

**Compare accounts for a customer:**
```bash
python modules/banks/nedbank_namibia/projects/account_fit_intelligence_engine/code/src/engine/account_fit.py --mode compare --customer CUST_015
```

**Run portfolio mode:**
```bash
python modules/banks/nedbank_namibia/projects/account_fit_intelligence_engine/code/src/engine/account_fit.py --mode portfolio --account-set retail_personal
```

**Export portfolio results to JSON:**
```bash
python modules/banks/nedbank_namibia/projects/account_fit_intelligence_engine/code/src/engine/account_fit.py --mode portfolio --account-set retail_personal --export-json outputs/portfolio.json
```

**Run regression and smoke tests:**
```bash
python -m pytest -q
```

> [!NOTE]
> Single-account outputs for Silver PAYU (v0.2.1) and Basic Banking (v0.3.1) are snapshot-frozen and protected by line-for-line golden regression tests.

## Command-Line Usage (Future)

```bash
# Generate synthetic data
python -m code.src.ingest.generate_synthetic --customers 100 --months 6

# Analyze account fit
python -m code.src.engine.account_fit \
    --customer CUST_001 \
    --account silver_payu \
    --config configs/account_types/silver_payu.yaml

# Run tests
pytest tests/
```

## Output Interpretation

### Fee Breakdown

**monthly_fee_fixed:** The known monthly account fee (30 NAD for Silver PAYU)

**transaction_fee_estimate:** Estimated transaction fees (currently 0 due to unknown fee structure)

**total_monthly_estimate:** Sum of fixed and variable fees

**notes:** Important limitations and assumptions

### Behaviour Features

**High transaction frequency (>20/month):**
- Active user, high engagement
- May benefit from accounts with transaction bundles

**Low transaction frequency (<5/month):**
- Light user
- Fixed monthly fee may be disproportionate
- May benefit from lower-tier account

**High transaction diversity (>5 types):**
- Uses many banking services
- Needs full-featured account
- Good fit for Silver PAYU

**Low transaction diversity (<3 types):**
- Limited service usage
- May be over-paying for unused features
- Consider simpler account

### Eligibility Status

**Eligible:** Customer meets all criteria (age, residency, income)

**Not Eligible:** Customer fails one or more criteria
- Details provided in output
- Recommendation: Consider alternative accounts

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Golden Regression Tests

```bash
python -m pytest tests/test_golden_outputs.py -q
```

### Run Smoke Test

```bash
pytest tests/test_smoke.py -v
```

**Expected Output:**
```
tests/test_smoke.py::test_config_loads PASSED
tests/test_smoke.py::test_data_generation PASSED
tests/test_smoke.py::test_fee_calculation PASSED
tests/test_smoke.py::test_feature_engineering PASSED
tests/test_smoke.py::test_account_fit_analysis PASSED
```

## Troubleshooting

### Issue: Config file not found

**Error:** `FileNotFoundError: configs/account_types/silver_payu.yaml`

**Solution:** Ensure you're running from the project root directory

### Issue: Missing dependencies

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:** Install required packages: `pip install pandas numpy pyyaml pytest`

### Issue: Invalid data format

**Error:** `ValueError: Invalid customer data schema`

**Solution:** Regenerate synthetic data or check CSV format matches schema

## Next Steps

After running demos:

1. Review generated data in `data/synthetic/`
2. Explore notebooks for detailed analysis
3. Modify configs to test different scenarios
4. Review documentation for extending to new accounts (v0.2)

## Related Documentation

- See `05_data_model.md` for data schemas
- See `06_feature_engineering.md` for feature details
- See `11_assumptions_and_limits.md` for limitations
