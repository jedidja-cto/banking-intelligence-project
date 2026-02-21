# Change Log

## Version History

### v0.1.2 (2026-02-21)

**Path Resolution & Multi-Customer Reporting**

- **Fixed**: Reliable project root path resolution
  - Added `utils/paths.py` module with `find_project_root()` function
  - Replaced brittle `Path.parents[3]` logic with robust upward directory search
  - Script now works regardless of execution location (repo root or subdirectory)
  
- **Added**: Multi-customer intelligence reporting
  - Engine now processes all customers in transaction dataset
  - Generates summary table with key metrics per customer
  - Displays: customer_id, txn_count, digital_ratio, behaviour_tag, inflows, outflows, estimated fees
  - Clean, aligned tabular output format
  
- **Documentation**: Created usage guide and changelog
  - Added `10_demo_and_usage.md` with prerequisites, installation, and expected output
  - Added `12_change_log.md` to track version history

### v0.1.1 (2024-01-22)

**Behavioural Features & Tagging**

- **Added**: Behavioural feature extraction module (`features/build_features.py`)
  - Transaction count and volume metrics
  - Digital vs. cash usage ratios
  - Transaction type breakdowns (ATM, utilities, third-party payments)
  - Rule-based behaviour tagging system
  
- **Enhanced**: Account fit report now includes behavioural profile
  - Digital ratio calculation
  - Behaviour tags: `digital_first`, `cash_heavy`, `utilities_focused`, `mixed_usage`, `no_activity`
  - Explainable, deterministic classification logic

### v0.1.0 (2024-01-20)

**Initial Fee Engine**

- **Created**: Core fee calculation engine for Silver PAYU account
  - Configuration loading from YAML (`config.py`)
  - Transaction data ingestion (`ingest/load_data.py`)
  - Fee calculation model (`fees/payu_fee_model.py`)
  - Main orchestration script (`engine/account_fit.py`)
  
- **Features**:
  - Fixed monthly fee calculation (N$30)
  - Placeholder for variable transaction fees (pending public data)
  - Single customer analysis
  - Basic intelligence report output

### v0.1 (2024-01-15)

**Project Scaffold**

- **Created**: Initial project structure
  - Directory layout: `code/`, `configs/`, `data/`, `docs/`, `notebooks/`, `tests/`
  - Documentation framework
  - Data schema definitions
  - Configuration templates

## Roadmap

### Planned Features

- **v0.2.0**: Transaction fee structure integration (when data becomes available)
- **v0.3.0**: Account fit scoring and recommendation engine
- **v0.4.0**: Multi-account type comparison
- **v0.5.0**: Time-series analysis and trend detection

## Notes

- Transaction fees remain unknown and are not included in cost estimates
- All fee calculations are based on publicly available information
- Synthetic data is used for development and testing
