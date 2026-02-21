# Problem Context

## Purpose

This document describes the problem space that the Account Fit Intelligence Engine addresses, focusing on customer pain points and business opportunities in account selection.

## Scope

Analysis of account selection challenges for Nedbank Namibia's personal banking customers, specifically within the everyday banking category.

## Observed

From Nedbank Namibia's product offerings:

- Multiple account types exist within personal everyday banking (Silver PAYU, Savvy, Gold PAYU, etc.)
- Each account has different fee structures, features, and eligibility criteria
- Customers must navigate product comparison pages to understand differences
- Account switching or upgrades are possible but require customer initiative

## Inferred

Based on common banking industry patterns:

- Customers often select accounts based on incomplete information
- Fee structures are complex and difficult to compare without usage data
- Many customers may be on suboptimal accounts for their behaviour patterns
- Banks benefit from customers being on appropriate accounts (satisfaction + retention)

## Assumed

For problem framing:

- A significant portion of customers would benefit from account optimization
- Historical transaction data can predict future behaviour patterns
- Fee savings and feature alignment are primary drivers of account fit
- Customers value transparency in account recommendations

## Proposed

The problem we're solving:

**"How can we help customers identify the most cost-effective and feature-appropriate account based on their actual banking behaviour?"**

### Customer Pain Points

1. **Complexity:** Difficult to compare accounts without detailed fee calculations
2. **Opacity:** Transaction fees are not always clearly visible upfront
3. **Inertia:** Customers stay on initial accounts even when better options exist
4. **Time:** Manual comparison requires significant effort

### Business Opportunities

1. **Customer satisfaction:** Right-fit accounts improve experience
2. **Retention:** Proactive optimization builds trust
3. **Efficiency:** Automated analysis scales better than manual advice
4. **Transparency:** Clear recommendations differentiate from competitors

## Current State Challenges

- No automated way to simulate fees across account types
- No behaviour-based account recommendations
- Limited visibility into potential savings for customers
- Manual account reviews are resource-intensive

## Desired Future State

- Automated behaviour analysis and fee simulation
- Data-driven account recommendations
- Transparent cost-benefit analysis for customers
- Scalable intelligence across all account types

## Why This Matters

**For Customers:**
- Potential cost savings through optimized account selection
- Better feature alignment with actual needs
- Increased confidence in banking decisions

**For the Bank:**
- Improved customer satisfaction and retention
- Reduced support burden from account-related queries
- Competitive differentiation through transparency
- Data-driven product development insights

## Constraints

- Must work with publicly available product information
- Cannot use real customer data (synthetic only)
- Must clearly distinguish facts from assumptions
- Must be extensible to other banks and products

## Success Metrics (Future)

- Accuracy of fee predictions vs. actual costs
- Customer adoption of recommendations
- Measured cost savings for customers
- Reduction in account-related support queries

## Related Documentation

- See `02_current_bank_flow.md` for how customers currently select accounts
- See `03_proposed_solution.md` for our approach to solving this problem
