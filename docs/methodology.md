Methodology
===========

This lab uses a simple but strict framework for classifying every analytical
statement. Each statement should be explicitly tagged or at least mentally
classified as one of:

Observed
--------

Facts directly seen in primary sources.

- Examples:
  - Content on an official website
  - Text in an annual report or policy paper
  - Numbers in published financial statements
- Requirements:
  - Must be backed by a concrete, citable source
  - Should be reproducible by another analyst using the same source

Inferred
--------

Conclusions drawn logically from observed facts.

- Examples:
  - Deducing a likely customer segment from a described product
  - Inferring a risk control from the way a process is described
- Requirements:
  - Must be traceable back to specific observed facts
  - The reasoning should be explainable in a few clear steps

Assumed
-------

Statements taken as working assumptions where data is missing or ambiguous.

- Examples:
  - Assuming a standard KYC process where documentation is silent
  - Assuming a typical batch processing window when no timing is given
- Requirements:
  - Must be explicitly labelled as assumptions
  - Must be clearly separated from observed facts
  - Should be revisited and either confirmed (as observed) or removed

Proposed
--------

Ideas, hypotheses, or recommendations that go beyond current observed reality.

- Examples:
  - Suggestions for improved customer journeys
  - Proposed architectures or data models
  - Policy or product recommendations
- Requirements:
  - Must be grounded in observed and inferred material where possible
  - Should make the intended benefits and trade-offs explicit

Strict rule
-----------

Never present assumptions as facts.

Whenever an assumption is used:

- Label it clearly as an assumption.
- Track it in the relevant module’s `04_opportunity_backlog.md` or `coverage.md`
  as something to validate.
- Update the classification if and when supporting evidence is found.

