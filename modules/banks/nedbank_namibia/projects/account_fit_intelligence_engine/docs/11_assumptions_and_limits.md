# Assumptions and Limitations

## Purpose

This document explicitly lists all assumptions made in v0.1 and limitations of the current implementation.

## Scope

Comprehensive documentation of what we know, what we assume, and what we cannot do in v0.1.

## Critical Principle

**Never present assumptions as facts.** This document ensures transparency about the boundaries of our knowledge and capabilities.

## Known Facts (Observed)

These are directly observed from Nedbank Namibia's public information:

1. Silver PAYU monthly fee: 30 NAD
2. Eligibility: Namibian residents, age 18+, income 3000-50000 NAD
3. Onboarding channels: web callback, Facebook Identity, branch, call center
4. Core capabilities: transfers, payments, airtime, electricity, card management, withdrawals
5. Cross-sell products: overdraft, credit card, personal loan, home loan, insurance
6. Account category: Personal → Accounts → Everyday banking

## Assumptions

### Data Assumptions

**1. Synthetic Data Represents Reality**
- **Assumption:** Generated transaction patterns reflect real customer behaviour
- **Reality:** Unknown until validated with real data
- **Impact:** Feature engineering and fee estimates may not generalize
- **Mitigation:** Use diverse patterns, validate against industry benchmarks

**2. Transaction Type Distribution**
- **Assumption:** POS (40%), ATM (15%), Airtime (15%), Electricity (10%), EFT (10%), Third-party (5%), Income (5%)
- **Reality:** Actual distribution unknown
- **Impact:** Synthetic data may not match real patterns
- **Mitigation:** Document assumption, adjust when real data available

**3. Transaction Frequency**
- **Assumption:** Average 15 transactions/month (Poisson distribution)
- **Reality:** Actual frequency unknown
- **Impact:** May over/underestimate typical usage
- **Mitigation:** Test with range of frequencies (5-30/month)

**4. Transaction Amounts**
- **Assumption:** Log-normal distribution, mean 200 NAD, std 150 NAD
- **Reality:** Actual distribution unknown
- **Impact:** May not reflect real spending patterns
- **Mitigation:** Validate against published banking statistics

### Fee Structure Assumptions

**5. Transaction Fees Unknown**
- **Assumption:** Using placeholder value of 0 NAD
- **Reality:** Actual per-transaction fees not publicly available
- **Impact:** Total cost estimates are incomplete and likely underestimated
- **Mitigation:** Clearly document in all outputs, update when information available

**6. No Volume Discounts**
- **Assumption:** No fee reductions for high transaction volumes
- **Reality:** Unknown if volume discounts exist
- **Impact:** May overestimate costs for high-volume users
- **Mitigation:** Document assumption, add logic when structure known

**7. No Conditional Fees**
- **Assumption:** Fees don't vary by transaction amount, time, or other factors
- **Reality:** Unknown if conditional pricing exists
- **Impact:** Simplified fee model may miss important cost factors
- **Mitigation:** Design extensible fee model for future complexity

### Behaviour Assumptions

**8. Historical Behaviour Predicts Future**
- **Assumption:** Past 3-6 months predict next 3-6 months
- **Reality:** Behaviour may change due to life events, economic factors
- **Impact:** Recommendations may become outdated
- **Mitigation:** Recommend periodic re-analysis

**9. Feature Importance**
- **Assumption:** Transaction frequency and diversity are key fit indicators
- **Reality:** Unknown which features actually matter for account fit
- **Impact:** Fit scoring may prioritize wrong factors
- **Mitigation:** Validate with customer feedback in production

**10. Eligibility is Binary**
- **Assumption:** Customers either meet all criteria or don't
- **Reality:** May be exceptions, special cases, or conditional eligibility
- **Impact:** May incorrectly classify edge cases
- **Mitigation:** Document edge cases, add flexibility for exceptions

### Technical Assumptions

**11. Single Account Per Customer**
- **Assumption:** Each customer has one primary everyday account
- **Reality:** Customers may have multiple accounts
- **Impact:** Analysis doesn't account for multi-account strategies
- **Mitigation:** Note limitation, address in future versions

**12. No Account Switching Costs**
- **Assumption:** Customers can switch accounts freely
- **Reality:** May be fees, effort, or restrictions on switching
- **Impact:** Recommendations may not account for switching friction
- **Mitigation:** Document assumption, add switching cost analysis (future)

**13. Static Product Definitions**
- **Assumption:** Account features and fees don't change
- **Reality:** Banks update products regularly
- **Impact:** Configurations may become outdated
- **Mitigation:** Version control configs, document update process

## Limitations

### v0.1 Limitations

**1. Single Account Type**
- **Limitation:** Only Silver PAYU implemented
- **Impact:** Cannot compare accounts or recommend alternatives
- **Roadmap:** v0.2 adds more accounts

**2. Incomplete Fee Calculations**
- **Limitation:** Transaction fees unknown, using placeholders
- **Impact:** Cost estimates are incomplete
- **Roadmap:** Update when fee structure available

**3. Synthetic Data Only**
- **Limitation:** No real customer data
- **Impact:** Cannot validate accuracy with real patterns
- **Roadmap:** v1.0 may integrate real data (with privacy controls)

**4. No Recommendation Logic**
- **Limitation:** Analyzes fit but doesn't recommend alternatives
- **Impact:** Limited decision support
- **Roadmap:** v0.3 adds recommendation engine

**5. No Temporal Analysis**
- **Limitation:** Doesn't detect trends or seasonality
- **Impact:** May miss changing behaviour patterns
- **Roadmap:** v0.3 adds temporal features

**6. No Cross-Sell Analysis**
- **Limitation:** Doesn't consider other products (loans, insurance)
- **Impact:** Misses holistic customer value
- **Roadmap:** v1.0 adds cross-sell intelligence

**7. No Real-Time Processing**
- **Limitation:** Batch processing only
- **Impact:** Cannot provide instant recommendations
- **Roadmap:** v1.0 adds API for real-time analysis

**8. No User Interface**
- **Limitation:** Python code only, no GUI
- **Impact:** Not accessible to non-technical users
- **Roadmap:** v1.0 adds web interface

**9. No Production Infrastructure**
- **Limitation:** Local execution only
- **Impact:** Cannot serve customers at scale
- **Roadmap:** v1.0 adds production deployment

**10. No Compliance Implementation**
- **Limitation:** No privacy controls, audit logs, or regulatory features
- **Impact:** Not suitable for real customer data
- **Roadmap:** v1.0 adds full compliance framework

### Methodological Limitations

**11. Correlation vs. Causation**
- **Limitation:** Features correlate with behaviour but don't explain it
- **Impact:** May miss underlying drivers of account fit
- **Mitigation:** Combine with qualitative research

**12. No Customer Preferences**
- **Limitation:** Doesn't account for subjective preferences (brand, UX, etc.)
- **Impact:** Purely cost/feature-based recommendations
- **Mitigation:** Add preference inputs in future versions

**13. No Competitive Analysis**
- **Limitation:** Only analyzes Nedbank accounts, not competitors
- **Impact:** May recommend Nedbank account when competitor is better
- **Mitigation:** Future: add cross-bank comparison

**14. No Life Event Modeling**
- **Limitation:** Doesn't predict major life changes (job loss, marriage, etc.)
- **Impact:** Recommendations may not account for future changes
- **Mitigation:** Recommend periodic re-analysis

### Data Quality Limitations

**15. No Data Validation Against Reality**
- **Limitation:** Synthetic data not validated against real patterns
- **Impact:** Unknown accuracy of simulations
- **Mitigation:** Validate when real data available

**16. No Outlier Handling**
- **Limitation:** Extreme values may skew analysis
- **Impact:** Recommendations may be poor for unusual customers
- **Mitigation:** Add outlier detection and handling

**17. No Missing Data Handling**
- **Limitation:** Assumes complete transaction history
- **Impact:** May fail with incomplete data
- **Mitigation:** Add imputation or partial analysis logic

## Uncertainty Quantification

**High Confidence (>90%):**
- Silver PAYU monthly fee (30 NAD)
- Eligibility criteria
- Core account capabilities

**Medium Confidence (50-90%):**
- Synthetic data patterns
- Feature importance for account fit
- Behaviour prediction from history

**Low Confidence (<50%):**
- Transaction fee structure
- Actual customer behaviour distributions
- Optimal account for specific customers

**Unknown:**
- Competitive positioning vs. other banks
- Customer satisfaction with recommendations
- Long-term accuracy of predictions

## Documentation Requirements

**In All Outputs:**
- Clearly state when using placeholder values
- Note limitations of analysis
- Provide confidence levels where applicable
- Link to this document for full context

**Example Disclaimer:**
"This analysis uses a placeholder value of 0 NAD for transaction fees, as the actual fee structure is not publicly available. Total cost estimates are therefore incomplete and likely underestimated. See assumptions_and_limits.md for full details."

## Update Process

**When Assumptions Change:**
1. Update this document
2. Update affected code and configs
3. Re-run validation tests
4. Update documentation
5. Communicate changes to users

**When Limitations Are Addressed:**
1. Document in change_log.md
2. Update this document
3. Update version number
4. Communicate improvements

## Related Documentation

- See `12_change_log.md` for version history
- See `08_risk_and_compliance.md` for risk implications
- See `10_demo_and_usage.md` for practical impact of limitations
