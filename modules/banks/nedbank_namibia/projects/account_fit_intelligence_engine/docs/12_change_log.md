# Change Log

## Purpose

This document tracks all significant changes, updates, and version history for the Account Fit Intelligence Engine.

## Version History

### v0.4.1 — Hardening (2026-02-24)

**Status:** Released

**Added:**
- Golden regression tests for PAYU and Basic Banking frozen outputs (`tests/test_golden_outputs.py`).
- Exact line-match snapshot protection in `tests/golden/`.

**Fixed:**
- Compare-mode cost semantics for Basic Banking (“Cost fees n/a” instead of misleading N$0.00).
- Guarded recommendation rules to handle accounts with missing cost data.
- Enforced ≤59 character terminal width in compare mode via `clamp59()`.

**Verification:**
- Full regression suite passing.
- Deterministic synthetic data generation verified.

---

### v0.4.0 — Compare Mode + Recommendation Engine (2026-02-23)

**Status:** Released

**Added:**
- `--mode compare` for side-by-side account analysis.
- Deterministic recommendation engine logic.
- Pure analysis function `analyze_customer_for_account`.

---

### v0.3.1 — Executive Summary + Footer Rollups (2026-02-22)

**Status:** Released

**Added:**
- Basic Banking: per-customer EXEC SUMMARY block (max 59-char lines).
- Footer rollups for ATM excess and migration candidates.

---

### v0.3.0 — Generic KPI Engine + Basic Banking (2026-02-21)

**Status:** Released

**New Files:**
- `configs/account_types/basic_banking.yaml` — Basic Banking account config (free_tier, kpi_profile)
- `configs/kpis/basic_banking_kpis.yaml` — KPI definitions, migration signals, insight messages
- `code/src/engine/kpi_engine.py` — Generic KPI engine + AST-validated SafeExpressionEvaluator

**Changed:**
- `code/src/schema.py` — Added `cashout` to `VALID_TRANSACTION_TYPES`
- `code/src/ingest/generate_synthetic.py` — Generates cashout transactions (cash_heavy archetype, 3–8/month); Nedbank ATM floor raised to 4 for free-tier testing
- `code/src/features/build_features.py` — Added 6 new feature keys: `nedbank_atm_withdrawal_count`, `cashout_count`, `digital_txn_count`, `total_payments`, `pos_purchase_count`, `charged_txn_count` (all default 0 — backward-compatible); new params: `fee_schedule`, `account_class`
- `code/src/engine/account_fit.py` — Added `load_kpi_config_for_account()`, `DEFAULT_ACCOUNT` constant, KPI summary block per customer; PAYU v0.2.1 output unchanged
- `configs/account_types/silver_payu.yaml` — Added `kpi_profile: null` (multi-account architecture readiness)

**Architecture decisions:**
- `SafeExpressionEvaluator`: uses `ast.parse` + allow-list of safe AST node types. No bare `eval()`. Only `max()`/`min()` calls allowed. All other builtins blanked.
- `excess_atm_cost`: computed via real Nedbank ATM `per_step` tariff rule (N$10/N$300 step), applied only to withdrawals beyond the free tier of 3. Not a formula scalar.
- `charged_txn_count`: derived by calling `tariff_engine.compute_variable_fees()` — single source of truth, no approximation.
- PAYU path: KPI engine activated only when `kpi_profile` is set in account YAML. `kpi_profile: null` in `silver_payu.yaml` ensures zero impact on PAYU output.

**Verification:**
- `generate_synthetic.py` — exit 0; produces cashout txns and nedbank ATM withdrawals > 3 for cash_heavy customers
- `account_fit.py` (basic_banking) — exit 0; KPI block printed per customer, payu_upgrade_candidate signal fires for cash_heavy customers, excess_atm_cost > 0 where applicable
- `account_fit.py` (silver_payu) — exit 0; output equivalent to v0.2.1

---

### v0.2.1 — Turnover-Aware Deposit Fees + Configurable POS Classification (2026-02-21)

**Status:** Released

**Added:**
- `customer_segment` field to `Customer` schema: `individual | sme | business`
- `annual_turnover: Optional[float]` field to `Customer` schema (None = unknown)
- `cash_deposit` transaction type to `VALID_TRANSACTION_TYPES` and synthetic generator
- `cash_deposit` fee block in `nedbank_2026_27.yaml` (flat_per_event, N$25 placeholder, turnover_threshold=1.3M)
- `resolve_deposit_eligibility()` shared helper in `tariff_engine.py` — single source of logic
- `compute_cash_deposit_fee()` in `tariff_engine.py` — returns fee, eligibility_status, flags dict
- `deposit_fee_eligibility_status` derived feature in `build_features.py` (imports shared helper)
- `cash_deposit_count` feature in `build_features.py`
- Customer loading + `customer_map` in `account_fit.py` engine
- Per-customer deposit eligibility line in report output (only shown when relevant)
- Footer `ASSUMPTIONS` block in engine report — flags customers with missing turnover

**Changed:**
- `account_fit.py` now loads `customers_sample.csv` and wires customer_segment + annual_turnover through the pipeline
- `generate_synthetic.py` generates segment distribution (~50% individual, ~30% sme, ~20% business) and cash_deposit events for sme/business
- Total variable fee in output now correctly includes deposit fee contribution
- `charge_policy_when_turnover_missing: do_not_charge_flag` — conservative safe default

**Key Design Decisions:**
- No phantom fees: deposit fee = N$0 if no cash_deposit transactions exist for customer
- `account_class` for POS fees remains config-driven — zero hardcoded values in Python
- Logic lives in one place (tariff_engine); build_features imports rather than duplicates

**Known Limitations (v0.2.1):**
- Cash deposit fee value (N$25.00) is a placeholder; update `nedbank_2026_27.yaml` when confirmed
- Only January 2026 (1-month window) simulated in synthetic data

---

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
- See `project_state.md` for current lifecycle status

---

## Version Map

- **v0.2.1** — PAYU fee engine (Turnover-aware)
- **v0.3.1** — Basic Banking KPI + exec summary
- **v0.4.0** — Compare mode + recommendation engine
- **v0.4.1** — Hardening + golden tests
