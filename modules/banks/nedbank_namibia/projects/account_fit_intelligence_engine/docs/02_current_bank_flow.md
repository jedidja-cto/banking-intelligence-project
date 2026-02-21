# Current Bank Flow

## Purpose

This document maps the current customer journey for account selection at Nedbank Namibia, identifying decision points and information gaps.

## Scope

Personal banking account selection process, from initial research through account opening, focusing on the everyday banking category.

## Observed

From Nedbank Namibia's public channels:

**Account Discovery:**
- Website navigation: Personal → Accounts → Everyday banking
- Product comparison pages list account types with key features
- Fee schedules available but require detailed reading
- Marketing materials highlight benefits, not cost comparisons

**Silver PAYU Onboarding Channels:**
- Web callback request
- Facebook Identity + Today selfie verification
- In-branch application
- Call center assistance

**Eligibility Verification:**
- Namibian residency required
- Age 18+
- Income range: 3000-50000 NAD gross monthly
- KYC: ID/passport, proof of income, additional checks if needed

## Inferred

Based on typical banking flows:

**Customer Decision Process:**
1. Customer identifies need for banking account
2. Browses bank website or visits branch
3. Reviews 3-5 account options
4. Compares based on visible features (monthly fee, card type, etc.)
5. Makes selection based on incomplete cost information
6. Completes application through chosen channel
7. Begins using account without behaviour-based optimization

**Information Gaps:**
- Transaction fees not easily comparable without usage simulation
- No personalized cost estimates based on expected behaviour
- Limited guidance on which account fits specific use cases
- No post-opening optimization recommendations

## Assumed

For flow modeling:

- Most customers select accounts during initial onboarding
- Account switching after opening is rare without proactive prompting
- Customers prioritize convenience over detailed cost analysis
- Branch staff provide recommendations based on stated needs, not data

## Proposed

**Current Flow Limitations:**

1. **Static Comparison:** Product pages show features, not personalized fit
2. **No Simulation:** Customers can't model their expected costs
3. **One-Time Decision:** Account selection happens once, rarely revisited
4. **Limited Guidance:** No data-driven recommendations

**Typical Customer Journey:**

```
Need Banking → Browse Products → Compare Features → Select Account → Open Account → Use Account
                                      ↑
                                 (Decision made here with limited data)
```

**What's Missing:**

```
Behaviour Analysis → Fee Simulation → Fit Scoring → Recommendation → Ongoing Optimization
```

## Current State: Silver PAYU Selection

**How customers currently choose Silver PAYU:**

1. **Income-based filtering:** Falls within 3000-50000 NAD range
2. **Fee visibility:** 30 NAD monthly fee is clear
3. **Feature checklist:** Transfers, payments, airtime, electricity, card management
4. **Channel preference:** Choose onboarding method (web, branch, call center)
5. **Application:** Complete KYC and eligibility verification

**What customers DON'T see:**

- Estimated transaction fees based on their behaviour
- Comparison with other accounts for their specific usage pattern
- Potential savings from alternative accounts
- Feature utilization predictions

## Pain Points in Current Flow

**For Customers:**
- Uncertainty about total cost of ownership
- Difficulty comparing transaction fee structures
- No confidence that selected account is optimal
- Post-opening optimization requires manual research

**For the Bank:**
- Customers may select suboptimal accounts
- Higher support burden from fee-related questions
- Missed opportunities for proactive account optimization
- Limited data on why customers choose specific accounts

## Opportunities for Improvement

1. **Pre-Opening:** Behaviour-based simulation and recommendations
2. **Post-Opening:** Ongoing optimization analysis
3. **Transparency:** Clear cost breakdowns and comparisons
4. **Automation:** Scalable intelligence vs. manual advice

## Related Documentation

- See `03_proposed_solution.md` for how we address these gaps
- See `04_system_architecture.md` for technical implementation
