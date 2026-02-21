# Overview — Account Fit Intelligence Engine v0.1

## Purpose

This document provides a high-level overview of the Account Fit Intelligence Engine project, its objectives, scope, and positioning within the broader banking intelligence initiative.

## Scope

**v0.1 Focus:**
- Single account type: Silver Pay-as-you-use (PAYU)
- Customer segment: Personal banking
- Account category: Everyday banking
- Capabilities: Behaviour simulation + fee calculation

**Out of Scope for v0.1:**
- Multi-account comparison
- Recommendation algorithms
- Real customer data
- Production deployment

## Observed

The following information is directly observed from Nedbank Namibia's public documentation:

- Silver PAYU is a personal everyday banking account
- Monthly fee: 30 NAD
- Eligibility: Namibian residents, age 18+, income 3000-50000 NAD
- Onboarding channels: web callback, Facebook Identity, branch, call center
- Core capabilities: transfers, payments, airtime, electricity, card management, withdrawals
- Cross-sell opportunities: overdraft, credit card, personal loan, home loan, insurance

## Inferred

Based on standard banking practices and product positioning:

- Silver PAYU targets entry-level to mid-income customers
- Pay-as-you-use model suggests transaction-based fees (details not publicly available)
- Product sits in a tiered offering (likely below Gold, above basic accounts)

## Assumed

For v0.1 simulation purposes:

- Transaction fee structure is unknown; placeholders used
- Customer behaviour patterns are modeled synthetically
- Feature importance for account fit will be validated in future versions

## Proposed

This project proposes:

1. A modular architecture that can scale to multiple account types
2. Synthetic data generation for safe experimentation
3. Clear separation between observed facts and assumptions
4. Incremental development: simulator → comparator → recommender

## Project Positioning

This is the first project under the Nedbank Namibia module, serving as:
- A proof of concept for the intelligence engine approach
- A template for future bank-specific projects
- A foundation for cross-bank comparative analysis (future)

## Success Criteria for v0.1

- [ ] Accurate representation of Silver PAYU configuration
- [ ] Synthetic data generation pipeline
- [ ] Fee calculation logic (with documented limitations)
- [ ] Reusable feature engineering patterns
- [ ] Clear documentation of assumptions vs. facts
- [ ] Extensible architecture for v0.2+

## Next Steps

1. Review problem context (`01_problem_context.md`)
2. Understand current bank flow (`02_current_bank_flow.md`)
3. Examine proposed solution (`03_proposed_solution.md`)
4. Study system architecture (`04_system_architecture.md`)
