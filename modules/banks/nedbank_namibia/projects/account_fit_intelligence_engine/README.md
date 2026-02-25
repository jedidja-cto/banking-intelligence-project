# Account Fit Intelligence Engine

**Version:** 0.1  
**Bank:** Nedbank Namibia  
**Focus:** Silver Pay-as-you-use (PAYU) account simulator

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white)
![YAML](https://img.shields.io/badge/yaml-%23ffffff.svg?style=flat&logo=yaml&logoColor=151515)
![Pytest](https://img.shields.io/badge/pytest-%23C1E814.svg?style=flat&logo=pytest&logoColor=black)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=flat&logo=git&logoColor=white)


## Purpose

This project simulates customer behaviour and fee calculations for Nedbank Namibia's Silver PAYU account. It is intentionally scoped to a single account type in v0.1 to:

1. Establish robust data models and schemas
2. Validate fee calculation logic with synthetic data
3. Build reusable feature engineering patterns
4. Create a foundation for multi-account comparison (v0.2+)

This is NOT yet a recommendation engine. It's a behaviour + fee simulator designed for future extension.

## Why Start with One Account?

Starting with Silver PAYU allows us to:
- Perfect the architecture before scaling
- Validate assumptions with a well-documented product
- Build confidence in synthetic data generation
- Establish clear patterns for adding more accounts

## Project Structure

```
account_fit_intelligence_engine/
├── README.md (this file)
├── docs/                    # Detailed documentation
├── configs/                 # Account and simulation configs
├── data/                    # Synthetic datasets
├── code/                    # Source implementation
├── tests/                   # Test suites
├── notebooks/               # Exploratory analysis
└── assets/                  # Supporting materials
```

## Quick Start

1. Review documentation in `docs/00_overview.md`
2. Examine Silver PAYU config in `configs/account_types/silver_payu.yaml`
3. Generate synthetic data: `python code/src/ingest/generate_synthetic.py`
4. Run smoke tests: `pytest tests/test_smoke.py`
5. Explore notebooks for fee model validation

## Built With

- **Python**: Core logic and analysis engine.
- **Pandas**: High-performance data manipulation and analysis.
- **PyYAML**: Configuration management for account rules and fee schedules.
- **AST (Abstract Syntax Tree)**: Safe formula evaluation in the KPI engine.
- **Pytest**: Industry-standard testing framework for unit and regression tests.
- **Jupyter**: Interactive data exploration and model validation.

## Taxonomy


All references use consistent naming:
- `customer_segment`: personal
- `account_family`: accounts
- `account_category`: everyday
- `account_type_id`: silver_payu

## Roadmap

- **v0.1** (current): Silver PAYU simulator
- **v0.2**: Add Savvy, Gold PAYU accounts
- **v0.3**: Comparative analysis and fit scoring
- **v1.0**: ML-based recommendation engine

## Data Policy

This project uses synthetic data only. No real customer information is used or stored.

## Documentation Index

See `docs/` for detailed documentation on problem context, architecture, data models, and more.
