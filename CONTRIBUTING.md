Contributing to the Namibia Financial Systems Intelligence Lab
==============================================================

Thank you for contributing to this lab. The purpose of this repository is to
build a rigorous, public, and reusable map of Namibia’s financial system.

Core principles
---------------

- Use only public information and synthetic data.
- Be explicit about uncertainty and assumptions.
- Prefer clarity and traceability over completeness.
- Keep modules small, well-scoped, and composable.

Methodology
-----------

All analysis in this repository must follow the methodology defined in
`docs/methodology.md`. In particular, every analytical statement should be
classifiable as one of:

- Observed
- Inferred
- Assumed
- Proposed

Assumptions must never be presented as facts.

Data and sources
----------------

- Only public, non-confidential information may be used.
- Cite sources in the relevant module’s `docs/sources.md`.
- If you construct synthetic data, clearly label it as synthetic and describe
  the generation logic at a high level.

Module contributions
--------------------

When creating or updating a module:

- Keep the module’s `README.md` up to date with:
  - What the institution is
  - Why it matters in the financial system
  - The current analysis status checklist
- Update the module’s `docs/` files as appropriate:
  - `00_module_overview.md` for a narrative overview
  - `01_service_map.md` for services and products
  - `02_user_journeys.md` for customer journeys
  - `03_data_layer_map.md` for systems and data flows
  - `04_opportunity_backlog.md` for opportunities and hypotheses
  - `sources.md` for references
  - `coverage.md` for how complete the analysis is

Code and tools
--------------

- Do not add scraping code to this repository.
- Tools in `tools/` should focus on:
  - Data modelling
  - Visualisation and diagram generation
  - Documentation quality checks
- Respect the public-data-only policy and never embed secrets or credentials.

Workflow
--------

1. Create a branch describing the change you are making.
2. Make your edits to modules and docs, keeping changes focused and coherent.
3. Run any available checks or tests.
4. Open a pull request describing:
   - What changed
   - Why it matters
   - Any follow-up work or known limitations

License
-------

By contributing to this repository, you agree that your contributions are
licensed under the MIT License found in `LICENSE`.

