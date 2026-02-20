# Account Fit Intelligence Engine

## Purpose
Estimate what a customer would pay on a given account type based on their transaction behaviour, then evolve into a recommendation engine as more account types are added.

## Status
Scaffolded. First account type captured: Silver Pay-as-you-use (PAYU).

## What this project delivers
- A synthetic dataset generator for Namibian-style transaction patterns
- A fee impact simulator for configured account types
- A feature pipeline that turns transactions into behavioural signals
- A results view (later: dashboard and or API)

## Repository map
- `docs/` Full case study and system documentation
- `configs/` Account type definitions, simulation settings, feature definitions
- `data/` Synthetic data only (no real customer data)
- `code/` Source code and tests
- `notebooks/` Exploration and validation notebooks

## Rules
- Public information only
- No scraping
- No real customer data
- All assumptions must be explicitly labelled

## Next milestone
Implement `silver_payu.yaml` as a fee model config and generate the first synthetic dataset.

