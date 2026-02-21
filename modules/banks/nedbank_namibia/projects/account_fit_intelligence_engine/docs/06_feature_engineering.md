# Feature Engineering

## Purpose

This document describes the behaviour features extracted from customer transaction data to support account fit analysis.

## Scope

Feature engineering approach for v0.2.1, focusing on transaction-based behaviour patterns for Silver PAYU account analysis. Includes deposit fee eligibility as a derived feature.

## Observed

Standard banking behaviour indicators:
- Transaction frequency and volume
- Channel usage patterns (ATM, POS, online)
- Payment type preferences
- Income regularity

## Inferred

Relevant features for account fit:
- Transaction diversity indicates feature utilization
- Frequency patterns predict future fee exposure
- Amount distributions suggest income level alignment
- Temporal patterns reveal banking habits

## Assumed

For feature design:
- Historical behaviour predicts future behaviour
- 3-6 months of data sufficient for pattern detection
- Aggregated features capture meaningful signals
- Simple features adequate for v0.1 (complex ML features in v1.0)

## Proposed

### Feature Categories

#### 1. Transaction Frequency Features

**Purpose:** Measure how often customers use different banking services

| Feature | Calculation | Interpretation |
|---------|-------------|----------------|
| txn_count_monthly | COUNT(transactions) / months | Overall banking activity level |
| pos_purchase_freq | COUNT(type=pos_purchase) / months | Card usage frequency |
| atm_withdrawal_freq | COUNT(type=atm_withdrawal) / months | Cash withdrawal habits |
| airtime_purchase_freq | COUNT(type=airtime_purchase) / months | Airtime top-up frequency |
| electricity_purchase_freq | COUNT(type=electricity_purchase) / months | Utility payment frequency |
| eft_transfer_freq | COUNT(type=eft_transfer) / months | Transfer usage |
| third_party_payment_freq | COUNT(type=third_party_payment) / months | Third-party payment usage |
| income_freq | COUNT(type=income) / months | Income regularity |

**Use Case:**
- High transaction frequency → Higher potential transaction fees
- Low frequency → Fixed monthly fee may be disproportionate
- Specific type frequency → Feature utilization alignment

#### 2. Transaction Amount Features

**Purpose:** Measure transaction size patterns

| Feature | Calculation | Interpretation |
|---------|-------------|----------------|
| txn_amount_monthly_avg | SUM(amount) / months | Monthly cash flow volume |
| avg_transaction_amount | AVG(amount WHERE amount > 0) | Typical transaction size |
| max_transaction_amount | MAX(amount) | Largest transaction (capacity needs) |
| min_transaction_amount | MIN(amount WHERE amount > 0) | Smallest transaction |
| amount_std_dev | STDDEV(amount WHERE amount > 0) | Transaction size variability |

**Use Case:**
- High volume → May benefit from accounts with volume discounts
- Large transactions → May need higher limits
- High variability → Needs flexible account features

#### 3. Behaviour Diversity Features

**Purpose:** Measure breadth of banking service usage

| Feature | Calculation | Interpretation |
|---------|-------------|----------------|
| transaction_diversity | COUNT(DISTINCT type) | Number of different services used |
| channel_diversity | COUNT(DISTINCT channel) | Number of channels used (future) |
| merchant_diversity | COUNT(DISTINCT merchant) | Shopping pattern diversity |

**Use Case:**
- High diversity → Needs full-featured account
- Low diversity → May be over-paying for unused features
- Specific patterns → Targeted account recommendations

#### 5. Deposit Fee Eligibility Feature (v0.2.1)

**Purpose:** Classify each customer's cash deposit fee eligibility status based on segment and annual turnover. Feeds directly into fee calculation.

**Feature name:** `deposit_fee_eligibility_status`

| Value | Condition | Deposit Fee |
|-------|-----------|-------------|
| `individual` | `customer_segment == 'individual'` | N$0 (always exempt) |
| `sme_below_threshold` | segment is sme/business AND `annual_turnover ≤ N$1,300,000` | N$0 (SME concession) |
| `sme_above_threshold` | segment is sme/business AND `annual_turnover > N$1,300,000` | N$25 × deposit_count |
| `unknown` | segment is sme/business AND `annual_turnover is None` | N$0 + flagged |

**Computation:**
```python
# Single source of logic — no duplication
from fees.tariff_engine import resolve_deposit_eligibility

status = resolve_deposit_eligibility(
    customer_segment='sme',
    annual_turnover=1_500_000,
    turnover_threshold=1_300_000
)  # returns 'sme_above_threshold'
```

**Key Design Decisions:**
- Logic lives in `tariff_engine.resolve_deposit_eligibility` (shared helper)
- `build_features.py` imports from tariff_engine — zero duplicated logic
- `account_fit.py` also imports `compute_cash_deposit_fee` from tariff_engine
- **No phantom fees:** deposit fee is only charged if `cash_deposit` transactions exist
- Missing turnover → conservative default (do not charge, flag for review)

#### 4. Temporal Features (Future)

**Purpose:** Capture time-based patterns

| Feature | Calculation | Interpretation |
|---------|-------------|----------------|
| weekend_txn_ratio | COUNT(weekend) / COUNT(all) | Weekend banking habits |
| business_hours_ratio | COUNT(9am-5pm) / COUNT(all) | Business hours usage |
| month_end_spike | AVG(last_week) / AVG(other_weeks) | Month-end activity pattern |

**Use Case:**
- Temporal patterns may indicate lifestyle/work patterns
- Could inform personalized banking advice (future)

### Feature Engineering Pipeline

```
Raw Transactions
    ↓
1. Data Validation
   - Schema check
   - Quality validation
   - Outlier detection
    ↓
2. Aggregation
   - Group by customer
   - Calculate frequencies
   - Compute statistics
    ↓
3. Feature Calculation
   - Apply formulas
   - Handle edge cases
   - Normalize if needed
    ↓
4. Feature Validation
   - Check for NaN/Inf
   - Validate ranges
   - Log warnings
    ↓
Behaviour Features
```

### Implementation Approach

**Function Signature:**
```python
def build_features(customer_data, transaction_data, time_period_months):
    """
    Extract behaviour features from customer transaction history.
    
    Args:
        customer_data: DataFrame with customer information
        transaction_data: DataFrame with transaction history
        time_period_months: Number of months in observation period
        
    Returns:
        DataFrame with customer_id and behaviour features
    """
```

**Processing Steps:**

1. **Validate Inputs**
   - Check schemas
   - Verify data quality
   - Handle missing values

2. **Calculate Frequencies**
   - Group transactions by customer and type
   - Count occurrences
   - Normalize by time period

3. **Calculate Amounts**
   - Aggregate transaction amounts
   - Compute statistics (mean, max, std)
   - Handle negative values (income)

4. **Calculate Diversity**
   - Count distinct values
   - Compute ratios

5. **Validate Outputs**
   - Check for invalid values
   - Log warnings for edge cases
   - Return clean feature set

### Edge Case Handling

**No Transactions:**
- Set all frequency features to 0
- Set amount features to 0 or null
- Flag customer for review

**Single Transaction Type:**
- Diversity = 1
- Type-specific frequency > 0, others = 0
- Valid but may indicate limited usage

**Extreme Values:**
- Cap maximum transaction amounts at reasonable threshold
- Log outliers for investigation
- Don't exclude (may be legitimate)

**Short History:**
- Normalize by actual months observed
- Flag if < 3 months (insufficient data)
- Adjust confidence in features

### Feature Validation Rules

**Frequency Features:**
- Must be >= 0
- Should be < 100 (sanity check: 100 txns/month is high)
- Warn if total frequency < 1 (very low activity)

**Amount Features:**
- Must be >= 0 (for debit transactions)
- Should be < 1,000,000 (sanity check)
- Warn if avg < 10 (very small transactions)

**Diversity Features:**
- Must be integer
- Must be between 0 and number of transaction types
- Warn if = 1 (single service usage)

### Feature Importance (Future)

**For Account Fit Scoring (v0.3+):**

High importance:
- txn_count_monthly (fee exposure)
- transaction_diversity (feature utilization)
- txn_amount_monthly_avg (income alignment)

Medium importance:
- Specific type frequencies (feature-specific fit)
- avg_transaction_amount (transaction size needs)

Low importance (v0.1):
- Temporal patterns (not yet used)
- Merchant diversity (not yet used)

### Feature Evolution Roadmap

**v0.1: Basic Aggregations**
- Frequency counts
- Amount statistics
- Simple diversity metrics

**v0.2.1: Deposit Eligibility (Done)**
- `deposit_fee_eligibility_status` derived feature
- `cash_deposit_count` transaction counter
- Shared `resolve_deposit_eligibility` helper

**v0.3: Enhanced Features (Planned)**
- Temporal patterns
- Channel preferences
- Merchant categories

**v0.3: Derived Features**
- Ratios and combinations
- Trend indicators
- Anomaly scores

**v1.0: ML Features**
- Embeddings
- Clustering-based features
- Predictive features

### Testing Strategy

**Unit Tests:**
- Test each feature calculation independently
- Verify edge case handling
- Check output ranges

**Integration Tests:**
- Test full pipeline with synthetic data
- Verify feature consistency
- Check performance

**Validation Tests:**
- Compare features against expected patterns
- Visual inspection in notebooks
- Statistical validation

### Performance Considerations

**v0.1 Scale:**
- 100-500 customers
- 10,000-100,000 transactions
- Pandas operations sufficient
- Sub-second processing expected

**Optimization (if needed):**
- Vectorized operations (avoid loops)
- Efficient groupby operations
- Caching for repeated calculations

### Documentation Requirements

**In Code:**
- Docstrings for all functions
- Comments for complex calculations
- Type hints for clarity

**In Notebooks:**
- Feature distribution visualizations
- Correlation analysis
- Example calculations

## Related Documentation

- See `05_data_model.md` for input data schemas
- See `04_system_architecture.md` for pipeline integration
- See `code/src/features/build_features.py` for implementation
