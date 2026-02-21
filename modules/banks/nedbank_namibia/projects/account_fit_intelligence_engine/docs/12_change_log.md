# Change Log

## Purpose

This document tracks all significant changes, updates, and version history for the Account Fit Intelligence Engine.

## Version History

### v0.1.0 - Initial Scaffold (2024-01-20)

**Status:** Initial development

**Added:**
- Project structure and documentation
- Silver PAYU account configuration
- Synthetic data schemas (customers, transactions)
- Code stubs for core modules:
  - `schema.py` - Data schemas
  - `generate_synthetic.py` - Data generation
  - `load_data.py` - Data loading
  - `payu_fee_model.py` - Fee calculation
  - `build_features.py` - Feature engineering
  - `account_fit.py` - Account fit analysis
- Test framework (`test_smoke.py`)
- Jupyter notebooks for exploration and validation
- Comprehensive documentation (12 docs)

**Scope:**
- Single account type: Silver PAYU
- Synthetic data only
- Basic fee calculation (monthly fee + placeholder transaction fees)
- Behaviour feature extraction
- No multi-account comparison
- No recommendation engine

**Known Limitations:**
- Transaction fees unknown (using placeholder 0 NAD)
- Synthetic data not validated against real patterns
- No production deployment
- No API layer
- No user interface

**Next Steps:**
- Implement code stubs
- Generate initial synthetic data
- Validate fee calculation logic
- Test feature engineering pipeline

---

## Future Versions (Planned)

### v0.2.0 - Multi-Account Support (Planned)

**Planned Additions:**
- Savvy account configuration
- Gold PAYU account configuration
- Additional account types (2-3 total)
- Parallel fee calculations
- Basic comparison logic

**Scope:**
- Multiple account types
- Still synthetic data only
- Comparative fee analysis
- No recommendation logic yet

### v0.3.0 - Recommendation Engine (Planned)

**Planned Additions:**
- Account fit scoring algorithm
- Ranking and recommendation logic
- Confidence scores
- Comparison reports
- Enhanced feature engineering

**Scope:**
- Full comparison across accounts
- Recommendation generation
- Still synthetic data
- Internal tool (not customer-facing)

### v1.0.0 - Production Deployment (Planned)

**Planned Additions:**
- API layer (REST endpoints)
- Real data integration (with privacy controls)
- ML-based recommendations
- User interface (web)
- Production infrastructure
- Compliance framework (POPIA, etc.)
- Monitoring and logging
- A/B testing framework

**Scope:**
- Customer-facing deployment
- Real-time recommendations
- Full compliance
- Scalable infrastructure

---

## Change Categories

Changes are categorized as:
- **Added:** New features or capabilities
- **Changed:** Modifications to existing features
- **Deprecated:** Features marked for removal
- **Removed:** Deleted features
- **Fixed:** Bug fixes
- **Security:** Security-related changes

---

## Update Guidelines

**When to Update This Log:**
- New version released
- Significant feature added
- Breaking changes made
- Important bugs fixed
- Configuration changes
- Documentation updates

**Format:**
```
### vX.Y.Z - Version Name (YYYY-MM-DD)

**Added:**
- Feature 1
- Feature 2

**Changed:**
- Modification 1

**Fixed:**
- Bug fix 1

**Known Issues:**
- Issue 1
```

---

## Configuration Changes

### Account Configurations

**v0.1.0:**
- Added `silver_payu.yaml` with observed data from Nedbank Namibia

**Future:**
- Track changes to account configurations
- Document when fees or features are updated
- Note source of information (public docs, bank communication, etc.)

---

## Data Schema Changes

### v0.1.0 - Initial Schemas

**Customer Schema:**
- customer_id, age, residency, income_gross_monthly
- customer_segment, account_category, account_type_id

**Transaction Schema:**
- transaction_id, customer_id, ts, amount, type, merchant

**Future:**
- Track schema changes
- Document migration paths
- Maintain backward compatibility where possible

---

## Dependency Changes

### v0.1.0 - Initial Dependencies

**Core:**
- Python 3.8+
- pandas
- numpy
- pyyaml

**Testing:**
- pytest

**Notebooks:**
- jupyter

**Future:**
- Track dependency updates
- Document breaking changes
- Security updates

---

## Documentation Changes

### v0.1.0 - Initial Documentation

**Created:**
- 00_overview.md
- 01_problem_context.md
- 02_current_bank_flow.md
- 03_proposed_solution.md
- 04_system_architecture.md
- 05_data_model.md
- 06_feature_engineering.md
- 07_api_design.md
- 08_risk_and_compliance.md
- 09_business_impact.md
- 10_demo_and_usage.md
- 11_assumptions_and_limits.md
- 12_change_log.md (this file)

**Future:**
- Track significant documentation updates
- Note when assumptions change
- Document new limitations discovered

---

## Known Issues

### v0.1.0

**Issue 1: Transaction Fees Unknown**
- **Description:** Actual transaction fee structure not publicly available
- **Impact:** Cost estimates incomplete
- **Workaround:** Using placeholder value of 0 NAD with clear documentation
- **Resolution:** Update when fee information available

**Issue 2: Synthetic Data Not Validated**
- **Description:** Generated data patterns not validated against real customer behaviour
- **Impact:** Unknown accuracy of simulations
- **Workaround:** Use diverse patterns, document assumption
- **Resolution:** Validate when real data available (v1.0)

**Issue 3: No Multi-Account Comparison**
- **Description:** Only Silver PAYU implemented
- **Impact:** Cannot recommend alternative accounts
- **Workaround:** Document as v0.1 limitation
- **Resolution:** Planned for v0.2

---

## Breaking Changes

### v0.1.0
- None (initial version)

**Future:**
- Document any breaking changes to APIs, schemas, or configurations
- Provide migration guides
- Maintain backward compatibility where possible

---

## Deprecation Notices

### v0.1.0
- None (initial version)

**Future:**
- Announce features planned for removal
- Provide timeline for deprecation
- Suggest alternatives

---

## Security Updates

### v0.1.0
- None (synthetic data only, no security concerns)

**Future:**
- Document security patches
- Track vulnerability fixes
- Note compliance updates

---

## Performance Improvements

### v0.1.0
- None (initial version)

**Future:**
- Track optimization efforts
- Document performance benchmarks
- Note scalability improvements

---

## Acknowledgments

**v0.1.0:**
- Data sources: Nedbank Namibia public website
- Methodology: Standard banking analytics practices
- Tools: Python data science ecosystem

---

## Related Documentation

- See `11_assumptions_and_limits.md` for current limitations
- See `03_proposed_solution.md` for version roadmap
- See `README.md` for project overview
