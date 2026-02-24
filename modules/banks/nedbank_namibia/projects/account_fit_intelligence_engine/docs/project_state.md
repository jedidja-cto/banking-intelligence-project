# Project State

## Current Version
**v0.5.0**

## Status
**PORTFOLIO READY — BATCH INTELLIGENCE ACTIVE**

## Portfolio Mode
- **New Logic**: Portfolio engine for batch aggregation and target ranking.
- **Reporting**: Concise executive summary and top-target lists.
- **Rules**: Enforced ≤59 char terminal clamp via `clamp59()`.
- **Export**: JSON export for downstream systems.

## Frozen Outputs
The following single-account outputs are snapshot-frozen and protected by golden regression tests:
- **Silver PAYU**: v0.2.1 snapshot
- **Basic Banking**: v0.3.1 snapshot

Golden tests exist in `tests/test_golden_outputs.py` and must remain green for all release cycles.

## Compare Mode
- **Cost Semantics**: Fixed (Basic Banking shows "fees n/a" instead of N$0.00).
- **Terminal Width**: ≤59 char terminal clamp enforced via `clamp59()`.

## Quality Gates
- **Unit/Integration Tests**: `pytest` passing.
- **Regression Tests**: Golden snapshots active and verified.
- **Reproduction**: Deterministic synthetic data generation verified.

## Next Target
**v0.6.0 — Dashboard Integration**
