# System Architecture

## Purpose

This document describes the technical architecture of the Account Fit Intelligence Engine, including component design, data flow, and extensibility patterns.

## Scope

Architecture for v0.1 (Silver PAYU simulator) with design considerations for future multi-account capabilities.

## Observed

Technical constraints and requirements:
- Python-based implementation (standard for data science projects)
- YAML for configuration (human-readable, version-controllable)
- CSV for synthetic data (simple, portable)
- Jupyter notebooks for exploration (standard in analytics)

## Inferred

Architecture needs based on solution requirements:
- Modular design for component reusability
- Clear separation of concerns (config, data, logic, presentation)
- Testable components with minimal dependencies
- Extensible patterns for adding accounts

## Assumed

For architectural decisions:
- Python 3.8+ environment
- Local execution (no distributed computing needed for v0.1)
- File-based storage sufficient (no database required yet)
- Single-user development workflow

## Proposed

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Configuration Layer                      │
│  (YAML files: account types, simulation params, features)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│     (Synthetic customers + transactions, loaded via          │
│      ingest modules)                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Processing Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Feature    │  │     Fee      │  │   Account    │      │
│  │ Engineering  │  │  Calculation │  │     Fit      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Output Layer                            │
│        (Reports, visualizations, notebooks)                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Design

#### 1. Configuration Layer

**Purpose:** Define account types and simulation parameters

**Components:**
- `configs/account_types/silver_payu.yaml` — Account definition
- `configs/simulation.yaml` — Simulation parameters
- `configs/features.yaml` — Feature definitions

**Design Pattern:** Configuration-driven development
- Accounts defined declaratively
- Easy to add new accounts without code changes
- Version-controlled product definitions

#### 2. Data Layer

**Purpose:** Provide synthetic customer and transaction data

**Components:**
- `code/src/schema.py` — Data schemas and validation
- `code/src/ingest/generate_synthetic.py` — Data generation
- `code/src/ingest/load_data.py` — Data loading utilities
- `data/synthetic/` — Generated datasets

**Design Pattern:** Schema-first data modeling
- Explicit schemas for validation
- Reproducible data generation
- Clear separation of generation and consumption

#### 3. Processing Layer

**Purpose:** Transform data and calculate account fit

**Components:**

**3a. Fee Calculation**
- `code/src/fees/payu_fee_model.py` — Silver PAYU fee logic
- Inputs: account config, transactions
- Outputs: fee breakdown (monthly + transaction estimates)

**3b. Feature Engineering**
- `code/src/features/build_features.py` — Behaviour extraction
- Inputs: customer data, transactions
- Outputs: behaviour features (transaction frequency, amounts, types)

**3c. Account Fit Engine**
- `code/src/engine/account_fit.py` — Orchestration
- Inputs: config, data, features, fees
- Outputs: fit analysis report

**Design Pattern:** Pipeline architecture
- Each component has single responsibility
- Clear input/output contracts
- Composable for future workflows

#### 4. Validation Layer

**Purpose:** Test and validate components

**Components:**
- `tests/test_smoke.py` — Basic integration tests
- `notebooks/00_exploration.ipynb` — Data exploration
- `notebooks/01_fee_model_validation.ipynb` — Fee logic validation

**Design Pattern:** Test-driven validation
- Automated tests for core logic
- Interactive notebooks for exploration
- Continuous validation as code evolves

### Data Flow (v0.1)

```
1. Load silver_payu.yaml config
   ↓
2. Generate synthetic customers + transactions
   ↓
3. Validate data against schemas
   ↓
4. Extract behaviour features
   ↓
5. Calculate fees using PAYU model
   ↓
6. Generate fit report
   ↓
7. Output results (console, notebook, file)
```

### Module Structure

```
code/
├── README.md
└── src/
    ├── config.py              # Config loading utilities
    ├── schema.py              # Data schemas
    ├── ingest/
    │   ├── generate_synthetic.py
    │   └── load_data.py
    ├── fees/
    │   └── payu_fee_model.py
    ├── features/
    │   └── build_features.py
    └── engine/
        └── account_fit.py
```

### Key Design Decisions

**1. File-Based Configuration**
- YAML for human readability
- Git-friendly (easy to track changes)
- No database overhead for v0.1

**2. Synthetic Data Generation**
- Reproducible with seed values
- Controlled distribution of patterns
- Safe for public repositories

**3. Modular Fee Models**
- Each account type has own fee module
- Shared interface for consistency
- Easy to add new fee structures

**4. Schema Validation**
- Explicit schemas prevent data errors
- Clear contracts between components
- Self-documenting data structures

**5. Notebook-Driven Exploration**
- Interactive validation of logic
- Visual inspection of results
- Documentation of assumptions

### Extensibility Patterns

**Adding New Account Types (v0.2):**

1. Create `configs/account_types/{new_account}.yaml`
2. Implement `code/src/fees/{new_account}_fee_model.py`
3. Update `account_fit.py` to load new config
4. Add validation notebook

**No changes needed to:**
- Data schemas
- Feature engineering
- Core engine logic

**Adding New Features:**

1. Define in `configs/features.yaml`
2. Implement extraction in `build_features.py`
3. Update tests

**Scaling to Multi-Account Comparison (v0.3):**

1. Extend `account_fit.py` to iterate over multiple configs
2. Add comparison logic (fee differences, feature gaps)
3. Implement ranking algorithms

### Technology Stack

**Core:**
- Python 3.8+
- PyYAML (config parsing)
- Pandas (data manipulation)
- NumPy (numerical operations)

**Testing:**
- pytest (unit tests)
- Jupyter (exploratory validation)

**Future Considerations:**
- scikit-learn (ML models in v1.0)
- FastAPI (API layer if needed)
- PostgreSQL (if moving beyond synthetic data)

### Performance Considerations

**v0.1 Scale:**
- 100-1000 synthetic customers
- 10,000-100,000 transactions
- Single-threaded execution sufficient
- Sub-second processing time expected

**Future Scale (v1.0):**
- May need batch processing for large datasets
- Consider caching for repeated calculations
- Optimize feature engineering for production

### Security and Privacy

**v0.1:**
- Synthetic data only (no privacy concerns)
- No authentication/authorization needed
- Local execution only

**Future:**
- If using real data: encryption, access controls, audit logs
- If deploying API: authentication, rate limiting, input validation
- Compliance with banking regulations (POPIA, GDPR, etc.)

### Error Handling

**Configuration Errors:**
- Validate YAML structure on load
- Fail fast with clear error messages
- Provide schema documentation

**Data Errors:**
- Schema validation before processing
- Handle missing values gracefully
- Log data quality issues

**Calculation Errors:**
- Validate inputs to fee models
- Handle edge cases (zero transactions, etc.)
- Return error states, not silent failures

### Monitoring and Logging

**v0.1:**
- Console logging for debugging
- Test output for validation
- Notebook outputs for exploration

**Future:**
- Structured logging (JSON format)
- Metrics collection (processing time, error rates)
- Alerting for anomalies

## Related Documentation

- See `05_data_model.md` for detailed schema definitions
- See `06_feature_engineering.md` for behaviour analysis logic
- See `07_api_design.md` for future API considerations
