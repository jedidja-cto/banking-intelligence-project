Namibia Financial Systems Intelligence Lab
===========================================

Project vision
--------------

This repository is the home of the **Namibia Financial Systems Intelligence Lab**.
The goal is to build a structured, transparent view of Namibia’s financial
infrastructure: banks, regulators, payment rails, and related institutions.

The lab focuses on:

- Mapping institutions and their roles in the financial system
- Understanding services, customer journeys, and data flows
- Identifying opportunities for safer, more inclusive, and more efficient finance
- Doing all of this using public information and synthetic data only

What this repo does
-------------------

This repository provides a modular, documented map of:

- **Banks** (for example, Nedbank Namibia)
- **Regulators** (for example, the Bank of Namibia)
- **Rails and schemes** (for example, Namclear payment rails)

Each module contains:

- A concise description of the institution and why it matters
- Documentation of services, user journeys, and data layers
- A backlog of opportunities and questions
- A clear record of sources and coverage

Repository structure
--------------------

At a high level, the repository is organised as follows:

- `assets/` – Diagrams, images, and other static assets
- `docs/` – Lab-wide methodology, glossary, and risk notes
- `modules/` – Institution-specific modules
  - `banks/` – Bank modules (for example `nedbank_namibia/`)
  - `regulators/` – Regulator modules (for example `bank_of_namibia/`)
  - `rails/` – Payment and settlement rails (for example `namclear/`)
- `templates/` – Reusable templates for new modules and documentation
- `tools/` – Scripts and utilities that help maintain the lab (no scraping)

Each module follows a consistent structure:

- `README.md` – Module summary and status
- `docs/` – Module documentation set
  - `00_module_overview.md`
  - `01_service_map.md`
  - `02_user_journeys.md`
  - `03_data_layer_map.md`
  - `04_opportunity_backlog.md`
  - `sources.md`
  - `coverage.md`
- `projects/` – Project-specific work anchored in this module

How to add a new module
-----------------------

When adding a new institution (bank, regulator, rail, or other), follow this
pattern:

1. Choose the appropriate category under `modules/`:
   - `modules/banks/`
   - `modules/regulators/`
   - `modules/rails/`
2. Create a new folder using a clear, lowercase, snake_case name, for example:
   - `modules/banks/example_bank/`
   - `modules/regulators/example_regulator/`
3. Inside the new folder, create:
   - `README.md`
   - `docs/` with the standard documentation files:
     - `00_module_overview.md`
     - `01_service_map.md`
     - `02_user_journeys.md`
     - `03_data_layer_map.md`
     - `04_opportunity_backlog.md`
     - `sources.md`
     - `coverage.md`
   - `projects/` for module-related projects and experiments
4. Fill in:
   - The module `README.md` with:
     - What the institution is
     - Why it matters in the financial system
     - The current analysis status checklist
   - The module `docs/` files as you progressively refine the analysis.
5. Link any diagrams or artefacts into `assets/` and reference them from the
   module.

Public-data-only policy
-----------------------

This lab has a strict **public-data-only** policy:

- No confidential or non-public information is allowed in this repository.
- No credentialed or authenticated data sources may be used.
- No scraping code may be added to this repository.
- Synthetic data is encouraged where needed to illustrate flows or scenarios.

Analysts must follow the methodology described in `docs/methodology.md`, and
should always be explicit about whether a statement is:

- Observed
- Inferred
- Assumed
- Proposed

Assumptions must never be presented as facts, and sources should be cited in
each module’s `docs/sources.md`.

