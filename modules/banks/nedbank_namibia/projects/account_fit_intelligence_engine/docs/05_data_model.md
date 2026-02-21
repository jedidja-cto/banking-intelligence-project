# Data Model

## Purpose

This document defines the data schemas for customers, transactions, and derived features used in the Account Fit Intelligence Engine.

## Scope

Data model for v0.1 synthetic data, designed for extensibility to real data sources in future versions.

## Observed

Standard banking data elements:
- Customer demographics (age, income, residency)
- Transaction attributes (amount, type, timestamp, merchant)
- Account metadata (type, segment, category)

## Inferred

Required data elements based on fee calculation and behaviour analysis:
- Customer eligibility fields (for account matching)
- Transaction categorization (for fee application)
- Temporal patterns (for behaviour features)

## Assumed

For synthetic data generation:
- Income distribution follows realistic patterns
- Transaction types align with Silver PAYU capabilities
- Temporal patterns reflect typical banking behaviour

## Proposed

### Customer Schema

**File:** `data/synthetic/customers_sample.csv`

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| customer_id | string | Unique customer identifier | CUST_001 | Primary key, format: CUST_XXX |
| age | integer | Customer age in years | 28 | 18-100 |
| residency | string | Residency status | namibian_resident | Values: namibian_resident, non_resident |
| income_gross_monthly | float | Gross monthly income (NAD) | 15000.00 | 0-1000000 |
| customer_segment | string | Banking segment | personal | Fixed: personal (for v0.1) |
| account_category | string | Account category | everyday | Fixed: everyday (for v0.1) |
| account_type_id | string | Current account type | silver_payu | Values: silver_payu, savvy, gold_payu, etc. |

**Eligibility Mapping:**
- Silver PAYU: age >= 18, residency = namibian_resident, income 3000-50000

**Sample Data:**
```csv
customer_id,age,residency,income_gross_monthly,customer_segment,account_category,account_type_id
CUST_001,28,namibian_resident,15000.00,personal,everyday,silver_payu
CUST_002,35,namibian_resident,8500.00,personal,everyday,silver_payu
CUST_003,42,namibian_resident,25000.00,personal,everyday,silver_payu
```

### Transaction Schema

**File:** `data/synthetic/transactions_sample.csv`

| Column | Type | Description | Example | Constraints |
|--------|------|-------------|---------|-------------|
| transaction_id | string | Unique transaction identifier | TXN_00001 | Primary key, format: TXN_XXXXX |
| customer_id | string | Customer identifier | CUST_001 | Foreign key to customers |
| ts | datetime | Transaction timestamp | 2024-01-15 14:30:00 | ISO 8601 format |
| amount | float | Transaction amount (NAD) | 250.50 | Positive for debits, negative for credits |
| type | string | Transaction type | pos_purchase | See transaction types below |
| merchant | string | Merchant name (if applicable) | Shoprite | Null for non-merchant transactions |

**Transaction Types:**

| Type | Description | Fee Applicability |
|------|-------------|-------------------|
| pos_purchase | Point of sale purchase | Per-transaction fee (unknown) |
| airtime_purchase | Airtime top-up | Per-transaction fee (unknown) |
| electricity_purchase | Electricity payment | Per-transaction fee (unknown) |
| third_party_payment | Payment to third party | Per-transaction fee (unknown) |
| atm_withdrawal | ATM cash withdrawal | Per-transaction fee (unknown) |
| eft_transfer | Electronic funds transfer | Per-transaction fee (unknown) |
| income | Salary/income deposit | Typically no fee |

**Sample Data:**
```csv
transaction_id,customer_id,ts,amount,type,merchant
TXN_00001,CUST_001,2024-01-15 14:30:00,250.50,pos_purchase,Shoprite
TXN_00002,CUST_001,2024-01-16 09:15:00,50.00,airtime_purchase,MTC
TXN_00003,CUST_001,2024-01-18 11:45:00,500.00,atm_withdrawal,
TXN_00004,CUST_001,2024-01-20 08:00:00,-12000.00,income,Employer
```

### Feature Schema (Derived)

**Purpose:** Behaviour features extracted from transaction history

| Feature | Type | Description | Calculation |
|---------|------|-------------|-------------|
| txn_count_monthly | integer | Average transactions per month | COUNT(transactions) / months |
| txn_amount_monthly_avg | float | Average monthly transaction volume | SUM(amount) / months |
| pos_purchase_freq | float | POS purchase frequency | COUNT(type=pos_purchase) / months |
| atm_withdrawal_freq | float | ATM withdrawal frequency | COUNT(type=atm_withdrawal) / months |
| airtime_purchase_freq | float | Airtime purchase frequency | COUNT(type=airtime_purchase) / months |
| electricity_purchase_freq | float | Electricity payment frequency | COUNT(type=electricity_purchase) / months |
| eft_transfer_freq | float | EFT transfer frequency | COUNT(type=eft_transfer) / months |
| third_party_payment_freq | float | Third-party payment frequency | COUNT(type=third_party_payment) / months |
| income_freq | float | Income deposit frequency | COUNT(type=income) / months |
| avg_transaction_amount | float | Average transaction size | AVG(amount WHERE amount > 0) |
| max_transaction_amount | float | Largest transaction | MAX(amount) |
| transaction_diversity | float | Unique transaction types used | COUNT(DISTINCT type) |

### Fee Calculation Schema

**Purpose:** Fee breakdown for account fit analysis

| Field | Type | Description |
|-------|------|-------------|
| account_type_id | string | Account type analyzed |
| monthly_fee_fixed | float | Fixed monthly fee (NAD) |
| transaction_fee_estimate | float | Estimated transaction fees (NAD) |
| total_monthly_estimate | float | Total estimated monthly cost (NAD) |
| fee_calculation_notes | string | Limitations and assumptions |

**Example Output:**
```json
{
  "account_type_id": "silver_payu",
  "monthly_fee_fixed": 30.00,
  "transaction_fee_estimate": 0.00,
  "total_monthly_estimate": 30.00,
  "fee_calculation_notes": "Transaction fees unknown; using placeholder value of 0. Actual costs may vary."
}
```

### Data Quality Rules

**Customer Data:**
- No duplicate customer_ids
- Age within valid range (18-100)
- Income >= 0
- Residency must be valid value
- All taxonomy fields must match controlled vocabulary

**Transaction Data:**
- No duplicate transaction_ids
- All customer_ids must exist in customer table
- Timestamps must be valid and chronological
- Amount must be numeric (positive for debits, negative for credits)
- Type must be from defined list
- Merchant required for merchant-based transactions

**Referential Integrity:**
- Every transaction.customer_id must have matching customer.customer_id
- Transaction types must align with account capabilities

### Synthetic Data Generation Rules

**Customer Distribution:**
- Age: Normal distribution, mean=35, std=12, min=18, max=65
- Income: Log-normal distribution within Silver PAYU range (3000-50000)
- Residency: 100% namibian_resident for v0.1
- Sample size: 100-500 customers

**Transaction Distribution:**
- Transactions per customer per month: Poisson distribution, lambda=15
- Transaction amounts: Log-normal distribution, mean=200, std=150
- Transaction types: Weighted by typical usage patterns
  - pos_purchase: 40%
  - atm_withdrawal: 15%
  - airtime_purchase: 15%
  - electricity_purchase: 10%
  - eft_transfer: 10%
  - third_party_payment: 5%
  - income: 5%
- Time period: 3-6 months of history

### Data Validation

**On Load:**
- Schema validation (column names, types)
- Constraint validation (ranges, foreign keys)
- Data quality checks (nulls, duplicates)

**On Processing:**
- Feature calculation validation (no NaN, Inf)
- Fee calculation validation (non-negative)
- Output schema validation

### Future Extensions

**v0.2+:**
- Add account balance snapshots
- Include card transaction details
- Add merchant category codes (MCC)
- Include geographic data (branch, ATM locations)

**v1.0:**
- Real customer data integration (with privacy controls)
- Historical account switching data
- Customer satisfaction scores
- Support interaction history

## Related Documentation

- See `06_feature_engineering.md` for feature calculation details
- See `04_system_architecture.md` for data flow
- See `code/src/schema.py` for implementation
