System architecture
===================

Purpose
-------

Describe the high-level architecture of the Account Fit Intelligence Engine for the Silver Pay-as-you-use account.

Scope
-----

- Components required for v0.1:
  - Configuration layer.
  - Synthetic data generation and loading.
  - Fee calculation logic for silver_payu.
  - Feature extraction pipeline.

Observed
--------

- The project structure separates configuration, data, code, notebooks, and assets into dedicated folders.

Inferred
--------

- A modular layout will make it easier to extend the engine to additional account types and customer segments.

Assumed
-------

- Deployment and runtime environment details are not yet specified.
- Integration with external systems (for example APIs or dashboards) will be handled in later versions.

Proposed
--------

- Use a simple, file-based architecture for v0.1, with clear boundaries between configuration, synthetic data, fee logic, and features.

