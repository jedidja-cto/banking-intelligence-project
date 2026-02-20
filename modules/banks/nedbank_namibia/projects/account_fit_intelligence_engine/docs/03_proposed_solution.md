Proposed solution
=================

Purpose
-------

Describe the proposed v0.1 solution for estimating fees on the Silver Pay-as-you-use account using synthetic transaction behaviour.

Scope
-----

- Single account type: silver_payu.
- Personal customers only.
- Synthetic transaction histories, no real customer data.

Observed
--------

- Public product information defines the Silver Pay-as-you-use positioning, eligibility, and headline monthly fee.

Inferred
--------

- A configuration-driven engine can separate account definitions from behaviour data and be extended to additional account types without redesigning the core.

Assumed
-------

- Fee structures can be represented in configuration files once full fee tables are captured.
- For v0.1, only the fixed monthly fee is modelled; variable fees are left as placeholders.

Proposed
--------

- Implement a configuration-first engine that:
  - Reads account configuration for silver_payu.
  - Generates or ingests synthetic transaction data.
  - Computes fixed monthly fee plus a placeholder variable fee estimate.
  - Produces outputs suitable for later dashboards or APIs.

