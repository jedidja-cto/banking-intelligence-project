# Demo and Usage Guide

## Prerequisites

- Python 3.8 or higher
- Required Python packages:
  - pyyaml
  - pandas

## Installation

Install the required dependencies:

```bash
pip install pyyaml pandas
```

## Running the Account Fit Intelligence Engine

From the repository root, run:

```bash
python modules/banks/nedbank_namibia/projects/account_fit_intelligence_engine/code/src/engine/account_fit.py
```

The script can be executed from any directory - it will automatically locate the project root.

## Expected Output

The engine produces a multi-customer intelligence report with the following information for each customer:

### Report Fields

- **Customer ID**: Unique customer identifier
- **Txns**: Total number of transactions
- **Digital%**: Percentage of digital (non-ATM) transactions
- **Behaviour**: Behavioural classification tag
  - `digital_first`: High digital usage (≥70%)
  - `cash_heavy`: High ATM usage (≥40%)
  - `utilities_focused`: Frequent utility payments (≥3)
  - `mixed_usage`: Balanced usage pattern
  - `no_activity`: No transactions
- **Inflow**: Total income/deposits (NAD)
- **Outflow**: Total expenses/withdrawals (NAD)
- **Est.Fee**: Estimated monthly account fee (NAD)

### Sample Output

```
================================================================================
Silver PAYU Multi-Customer Intelligence Report
================================================================================

Account Type: silver_payu
Total Customers: 3

--------------------------------------------------------------------------------
Customer ID  Txns   Digital%   Behaviour          Inflow       Outflow      Est.Fee   
--------------------------------------------------------------------------------
CUST_001     5      60.0       mixed_usage        N$12000.00   N$980.50      N$30.00    
CUST_002     5      60.0       mixed_usage        N$8500.00    N$970.75      N$30.00    
CUST_003     5      60.0       mixed_usage        N$25000.00   N$1955.00     N$30.00    
================================================================================
```

## Data Requirements

The engine expects the following data files in the project:

- `configs/account_types/silver_payu.yaml` - Account configuration
- `data/synthetic/customers_sample.csv` - Customer profiles
- `data/synthetic/transactions_sample.csv` - Transaction history

## Notes

- Transaction fees are not yet captured in the current version
- Fee estimates only include the fixed monthly fee (N$30)
- Variable PAYU pricing is pending and will be added in future versions
