# Code Directory

## Purpose

This directory contains the source code for the Account Fit Intelligence Engine.

## Structure

```
code/
├── README.md (this file)
└── src/
    ├── config.py              # Configuration loading utilities
    ├── schema.py              # Data schemas and validation
    ├── ingest/
    │   ├── generate_synthetic.py  # Synthetic data generation
    │   └── load_data.py           # Data loading utilities
    ├── fees/
    │   └── payu_fee_model.py      # Silver PAYU fee calculation
    ├── features/
    │   └── build_features.py      # Behaviour feature engineering
    └── engine/
        └── account_fit.py         # Account fit analysis orchestration
```

## Module Overview

### config.py
Utilities for loading and validating YAML configuration files.

**Key Functions:**
- `load_account_config(path)`: Load account type configuration
- `load_simulation_config(path)`: Load simulation parameters
- `load_features_config(path)`: Load feature definitions

### schema.py
Data schemas and validation logic for customers and transactions.

**Key Functions:**
- `validate_customer_data(df)`: Validate customer DataFrame
- `validate_transaction_data(df)`: Validate transaction DataFrame
- `check_referential_integrity(customers, transactions)`: Verify foreign keys

### ingest/generate_synthetic.py
Generate synthetic customer and transaction data.

**Key Functions:**
- `generate_customers(n_customers, seed)`: Generate customer profiles
- `generate_transactions(customers, months, seed)`: Generate transaction history

### ingest/load_data.py
Load and preprocess data from CSV files.

**Key Functions:**
- `load_customers(path)`: Load customer data
- `load_transactions(path)`: Load transaction data
- `load_all_data(data_dir)`: Load all datasets

### fees/payu_fee_model.py
Calculate fees for Silver PAYU account.

**Key Functions:**
- `calculate_monthly_fee(account_config, transactions)`: Calculate total monthly fees

### features/build_features.py
Extract behaviour features from transaction data.

**Key Functions:**
- `build_features(customers, transactions, time_period_months)`: Extract all features
- `calculate_frequency_features(transactions, months)`: Transaction frequency features
- `calculate_amount_features(transactions)`: Transaction amount features
- `calculate_diversity_features(transactions)`: Transaction diversity features

### engine/account_fit.py
Orchestrate account fit analysis.

**Key Functions:**
- `analyze_account_fit(customer_id, account_type, config_path, data_path)`: Full analysis
- `check_eligibility(customer, account_config)`: Verify eligibility
- `generate_fit_report(customer, features, fees, eligibility)`: Create report

## Usage

### Basic Usage

```python
from code.src.engine.account_fit import analyze_account_fit

result = analyze_account_fit(
    customer_id='CUST_001',
    account_type='silver_payu',
    config_path='configs/account_types/silver_payu.yaml',
    data_path='data/synthetic/'
)

print(result)
```

### Generate Data

```python
from code.src.ingest.generate_synthetic import generate_customers, generate_transactions

customers = generate_customers(n_customers=100, seed=42)
transactions = generate_transactions(customers=customers, months=6, seed=42)
```

### Calculate Fees

```python
import yaml
from code.src.fees.payu_fee_model import calculate_monthly_fee

with open('configs/account_types/silver_payu.yaml', 'r') as f:
    config = yaml.safe_load(f)

fees = calculate_monthly_fee(config, transactions)
```

### Build Features

```python
from code.src.features.build_features import build_features

features = build_features(customers, transactions, time_period_months=6)
```

## Development Guidelines

### Code Style
- Follow PEP 8 style guide
- Use type hints for function signatures
- Write comprehensive docstrings (Google style)
- Keep functions focused and testable

### Documentation
- Every function must have a docstring
- Include Args, Returns, Raises sections
- Provide usage examples in docstrings
- Document assumptions and limitations

### Testing
- Write unit tests for all functions
- Use pytest framework
- Aim for >80% code coverage
- Test edge cases and error conditions

### Error Handling
- Validate inputs at function boundaries
- Raise informative exceptions
- Log warnings for data quality issues
- Fail fast with clear error messages

## Dependencies

**Core:**
- pandas: Data manipulation
- numpy: Numerical operations
- pyyaml: Configuration parsing

**Testing:**
- pytest: Test framework

**Future:**
- scikit-learn: ML models (v1.0)
- fastapi: API layer (v1.0)

## Installation

```bash
# Install dependencies (when requirements.txt is created)
pip install pandas numpy pyyaml pytest

# Or use requirements.txt
pip install -r requirements.txt
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_smoke.py -v

# Run with coverage
pytest tests/ --cov=code/src --cov-report=html
```

## Related Documentation

- See `docs/04_system_architecture.md` for architecture details
- See `docs/05_data_model.md` for data schemas
- See `docs/06_feature_engineering.md` for feature logic
- See `docs/10_demo_and_usage.md` for usage examples
