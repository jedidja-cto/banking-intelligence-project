# Data Directory

## Purpose

This directory contains synthetic datasets for the Account Fit Intelligence Engine.

## Data Policy

**CRITICAL:** This project uses synthetic data only. No real customer data is used or stored.

- All data is artificially generated
- No web scraping
- No real customer information
- Safe for public repositories and sharing

## Directory Structure

```
data/
├── README.md (this file)
└── synthetic/
    ├── customers_sample.csv
    └── transactions_sample.csv
```

## Synthetic Data

### customers_sample.csv

Sample customer profiles for testing and development.

**Columns:**
- `customer_id`: Unique customer identifier (format: CUST_XXX)
- `age`: Customer age in years (18-65)
- `residency`: Residency status (namibian_resident)
- `income_gross_monthly`: Gross monthly income in NAD (3000-50000)
- `customer_segment`: Banking segment (personal)
- `account_category`: Account category (everyday)
- `account_type_id`: Current account type (silver_payu)

**Generation:**
- 100-500 customers
- Age: Normal distribution (mean=35, std=12)
- Income: Log-normal distribution within Silver PAYU range
- All customers are Namibian residents (v0.1)

### transactions_sample.csv

Sample transaction history for testing and development.

**Columns:**
- `transaction_id`: Unique transaction identifier (format: TXN_XXXXX)
- `customer_id`: Customer identifier (foreign key to customers)
- `ts`: Transaction timestamp (ISO 8601 format)
- `amount`: Transaction amount in NAD (positive for debits, negative for credits)
- `type`: Transaction type (see types below)
- `merchant`: Merchant name (if applicable)

**Transaction Types:**
- `pos_purchase`: Point of sale purchase
- `airtime_purchase`: Airtime top-up
- `electricity_purchase`: Electricity payment
- `third_party_payment`: Payment to third party
- `atm_withdrawal`: ATM cash withdrawal
- `eft_transfer`: Electronic funds transfer
- `income`: Salary/income deposit

**Generation:**
- 6 months of transaction history
- ~15 transactions per customer per month (Poisson distribution)
- Transaction amounts: Log-normal distribution (mean=200, std=150)
- Type distribution: POS (40%), ATM (15%), Airtime (15%), Electricity (10%), EFT (10%), Third-party (5%), Income (5%)

## Data Generation

To generate new synthetic data:

```python
from code.src.ingest.generate_synthetic import generate_customers, generate_transactions

# Generate customers
customers = generate_customers(n_customers=100, seed=42)
customers.to_csv('data/synthetic/customers_sample.csv', index=False)

# Generate transactions
transactions = generate_transactions(customers=customers, months=6, seed=42)
transactions.to_csv('data/synthetic/transactions_sample.csv', index=False)
```

Or use the command line (when implemented):

```bash
python -m code.src.ingest.generate_synthetic --customers 100 --months 6
```

## Data Quality

**Validation Checks:**
- No duplicate IDs
- All foreign keys valid
- Values within expected ranges
- Required fields not null
- Timestamps chronological

**Known Limitations:**
- Patterns may not reflect real customer behaviour
- Distributions are assumptions, not validated
- No seasonal or temporal patterns (v0.1)
- No correlation between customer attributes and behaviour (v0.1)

## Data Schema

See `docs/05_data_model.md` for detailed schema documentation.

## Data Usage

**Loading Data:**

```python
import pandas as pd

customers = pd.read_csv('data/synthetic/customers_sample.csv')
transactions = pd.read_csv('data/synthetic/transactions_sample.csv')
```

**Validation:**

```python
from code.src.schema import validate_customer_data, validate_transaction_data

validate_customer_data(customers)
validate_transaction_data(transactions)
```

## Future Data Sources

**v0.2-0.3:**
- Expanded synthetic data with more diverse patterns
- Multiple account types
- Temporal patterns

**v1.0:**
- Real customer data integration (with privacy controls)
- Historical account switching data
- Customer satisfaction data
- Support interaction history

**Privacy Requirements for Real Data:**
- Encryption at rest and in transit
- Access controls and audit logs
- Anonymization where possible
- POPIA compliance
- Data retention policies

## Related Documentation

- See `docs/05_data_model.md` for schema details
- See `docs/11_assumptions_and_limits.md` for data limitations
- See `code/src/schema.py` for validation logic
