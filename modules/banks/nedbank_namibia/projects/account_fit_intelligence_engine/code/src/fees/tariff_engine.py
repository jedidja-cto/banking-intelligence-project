"""
Tariff engine for variable fee calculation based on transaction history.

This module implements the Nedbank Namibia fee schedule with support for
multiple fee rule types: flat, per_step, and base_plus_step_cap.
"""

import math
from typing import Any, Dict, Optional, Tuple
import yaml
import pandas as pd


def ceil_div(amount: float, step_amount: float) -> int:
    """
    Calculate ceiling division for step-based fee calculations.
    
    Args:
        amount: Transaction amount
        step_amount: Step size for fee calculation
        
    Returns:
        Number of steps (rounded up)
        
    Example:
        >>> ceil_div(450, 300)
        2
        >>> ceil_div(300, 300)
        1
    """
    return math.ceil(amount / step_amount)


def fee_flat(value: float) -> float:
    """
    Calculate flat fee.
    
    Args:
        value: Flat fee amount
        
    Returns:
        Fee amount
    """
    return value


def fee_per_step(amount: float, step_amount: float, step_fee: float) -> float:
    """
    Calculate fee based on stepped amount.
    
    Fee = ceil(amount / step_amount) * step_fee
    
    Args:
        amount: Transaction amount
        step_amount: Step size
        step_fee: Fee per step
        
    Returns:
        Total fee
        
    Example:
        >>> fee_per_step(450, 300, 10.00)
        20.0
        >>> fee_per_step(300, 300, 10.00)
        10.0
    """
    steps = ceil_div(amount, step_amount)
    return steps * step_fee


def fee_base_plus_step_cap(
    amount: float,
    base_fee: float,
    step_amount: float,
    step_fee: float,
    cap: float
) -> float:
    """
    Calculate fee with base + stepped component, capped at maximum.
    
    Fee = min(base_fee + ceil(amount / step_amount) * step_fee, cap)
    
    Args:
        amount: Transaction amount
        base_fee: Base fee component
        step_amount: Step size
        step_fee: Fee per step
        cap: Maximum fee
        
    Returns:
        Total fee (capped)
        
    Example:
        >>> fee_base_plus_step_cap(1000, 7.20, 500, 13.70, 35.00)
        34.6
        >>> fee_base_plus_step_cap(2000, 7.20, 500, 13.70, 35.00)
        35.0
    """
    steps = ceil_div(amount, step_amount)
    uncapped_fee = base_fee + (steps * step_fee)
    return min(uncapped_fee, cap)


def load_fee_schedule(fee_schedule_path: str) -> Dict[str, Any]:
    """
    Load fee schedule from YAML file.
    
    Args:
        fee_schedule_path: Path to fee schedule YAML file
        
    Returns:
        Fee schedule dictionary
    """
    with open(fee_schedule_path, 'r') as f:
        return yaml.safe_load(f)


def compute_variable_fees(
    transactions_df: pd.DataFrame,
    fee_schedule: Dict[str, Any],
    account_class: str
) -> Dict[str, Dict[str, Any]]:
    """
    Compute variable fees for all customers based on transaction history.
    
    Args:
        transactions_df: DataFrame with columns: customer_id, type, amount, channel, 
                        atm_owner (for ATM), pos_scope (for POS)
        fee_schedule: Fee schedule dictionary from YAML
        account_class: Account classification ("current" or "savings") for POS fees
        
    Returns:
        Dictionary mapping customer_id to fee breakdown:
        {
            customer_id: {
                "variable_total": float,
                "by_type": {tx_type: float},
                "by_channel": {channel: float}
            }
        }
        
    Example:
        >>> fee_schedule = load_fee_schedule('configs/fee_schedules/nedbank_2026_27.yaml')
        >>> fees = compute_variable_fees(transactions, fee_schedule, "current")
        >>> print(fees['CUST_001']['variable_total'])
    """
    results = {}
    
    # Group by customer
    for customer_id in transactions_df['customer_id'].unique():
        customer_txns = transactions_df[transactions_df['customer_id'] == customer_id]
        
        by_type = {}
        by_channel = {}
        total = 0.0
        
        for _, txn in customer_txns.iterrows():
            fee = 0.0
            tx_type = txn['type']
            channel = txn.get('channel', '')
            amount = abs(txn['amount'])
            
            # Skip income transactions (no fee)
            if tx_type == 'income':
                continue
            
            # Online channel transactions
            if channel == 'online':
                if tx_type in fee_schedule.get('online', {}):
                    rule = fee_schedule['online'][tx_type]
                    if rule['rule_type'] == 'flat':
                        fee = fee_flat(rule['value'])
            
            # ATM channel transactions
            elif channel == 'atm' and tx_type == 'atm_withdrawal':
                atm_owner = txn.get('atm_owner', 'nedbank')
                
                if atm_owner == 'nedbank':
                    rule = fee_schedule['atm'].get('nedbank_atm_withdrawal', {})
                    if rule.get('rule_type') == 'per_step':
                        fee = fee_per_step(
                            amount,
                            rule['step_amount'],
                            rule['step_fee']
                        )
                elif atm_owner == 'other_bank':
                    rule = fee_schedule['atm'].get('other_bank_atm_withdrawal', {})
                    if rule.get('rule_type') == 'base_plus_step_cap':
                        fee = fee_base_plus_step_cap(
                            amount,
                            rule['base_fee'],
                            rule['step_amount'],
                            rule['step_fee'],
                            rule['cap']
                        )
            
            # POS channel transactions
            elif channel == 'pos' and tx_type == 'pos_purchase':
                pos_scope = txn.get('pos_scope', 'local')
                
                if pos_scope == 'local':
                    local_rules = fee_schedule['pos'].get('local', {})
                    if account_class in local_rules:
                        rule = local_rules[account_class]
                        if rule['rule_type'] == 'flat':
                            fee = fee_flat(rule['value'])
            
            # Accumulate fees
            if fee > 0:
                total += fee
                by_type[tx_type] = by_type.get(tx_type, 0.0) + fee
                by_channel[channel] = by_channel.get(channel, 0.0) + fee
        
        results[customer_id] = {
            'variable_total': round(total, 2),
            'by_type': {k: round(v, 2) for k, v in by_type.items()},
            'by_channel': {k: round(v, 2) for k, v in by_channel.items()}
        }
    
    return results


# ---------------------------------------------------------------------------
# v0.2.1 — Cash Deposit Fee: shared helper + fee calculator
# ---------------------------------------------------------------------------

def resolve_deposit_eligibility(
    customer_segment: str,
    annual_turnover: Optional[float],
    turnover_threshold: float
) -> str:
    """
    Determine a customer's cash deposit fee eligibility status.

    This is the single source of logic shared by tariff_engine.compute_cash_deposit_fee
    and features.build_features.extract_behavioural_features to avoid duplication.

    Args:
        customer_segment: 'individual', 'sme', or 'business'
        annual_turnover:  Annual NAD turnover; None means unknown
        turnover_threshold: NAD threshold above which deposit fee applies

    Returns:
        One of: 'individual' | 'sme_below_threshold' | 'sme_above_threshold' | 'unknown'

    Example:
        >>> resolve_deposit_eligibility('individual', None, 1_300_000)
        'individual'
        >>> resolve_deposit_eligibility('sme', 500_000, 1_300_000)
        'sme_below_threshold'
        >>> resolve_deposit_eligibility('sme', None, 1_300_000)
        'unknown'
        >>> resolve_deposit_eligibility('business', 2_000_000, 1_300_000)
        'sme_above_threshold'
    """
    if customer_segment == 'individual':
        return 'individual'
    if annual_turnover is None:
        return 'unknown'
    if annual_turnover <= turnover_threshold:
        return 'sme_below_threshold'
    return 'sme_above_threshold'


def compute_cash_deposit_fee(
    customer_segment: str,
    annual_turnover: Optional[float],
    deposit_txn_count: int,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute cash deposit fees for a single customer.

    Rules (Nedbank Namibia 2026/27):
    - Individuals are ALWAYS exempt (fee = 0).
    - No cash_deposit transactions → fee = 0 regardless of segment/turnover.
    - Turnover unknown → fee = 0, customer flagged; charge_policy_when_turnover_missing
      in config must be 'do_not_charge_flag' (fail-safe default).
    - Turnover ≤ threshold → fee = 0 (SME concession).
    - Turnover > threshold → fee = flat_per_event value × deposit_txn_count.

    NO PHANTOM FEES: if deposit_txn_count == 0, fee is always 0.

    Args:
        customer_segment:  'individual', 'sme', or 'business'
        annual_turnover:   Annual NAD turnover; None means unknown
        deposit_txn_count: Number of cash_deposit transactions for this customer
        config:            The full fee_schedule dict (from nedbank_2026_27.yaml);
                           must contain a 'cash_deposit' block

    Returns:
        Dict with:
            'fee':               float   — total deposit fee (NAD)
            'eligibility_status': str   — see resolve_deposit_eligibility
            'flags':             Dict    — e.g. {'turnover_required_for_deposit_fee': True}

    Example:
        >>> fs = {'cash_deposit': {'turnover_threshold': 1300000,
        ...     'charge_policy_when_turnover_missing': 'do_not_charge_flag',
        ...     'fee_if_applicable': {'rule_type': 'flat_per_event', 'value': 25.0}}}
        >>> compute_cash_deposit_fee('sme', 2_000_000, 3, fs)
        {'fee': 75.0, 'eligibility_status': 'sme_above_threshold', 'flags': {}}
        >>> compute_cash_deposit_fee('sme', None, 3, fs)
        {'fee': 0.0, 'eligibility_status': 'unknown', 'flags': {'turnover_required_for_deposit_fee': True}}
        >>> compute_cash_deposit_fee('individual', None, 3, fs)
        {'fee': 0.0, 'eligibility_status': 'individual', 'flags': {}}
    """
    deposit_cfg = config.get('cash_deposit', {})
    turnover_threshold = deposit_cfg.get('turnover_threshold', 1_300_000)
    fee_rule = deposit_cfg.get('fee_if_applicable', {})
    per_event_fee = fee_rule.get('value', 0.0)

    eligibility_status = resolve_deposit_eligibility(
        customer_segment, annual_turnover, turnover_threshold
    )

    flags: Dict[str, Any] = {}

    # Individuals are always exempt
    if eligibility_status == 'individual':
        return {'fee': 0.0, 'eligibility_status': eligibility_status, 'flags': flags}

    # No phantom fees — if no deposit transactions exist, there's nothing to charge
    if deposit_txn_count == 0:
        return {'fee': 0.0, 'eligibility_status': eligibility_status, 'flags': flags}

    # Turnover unknown — do not charge; flag for manual review
    if eligibility_status == 'unknown':
        flags['turnover_required_for_deposit_fee'] = True
        return {'fee': 0.0, 'eligibility_status': eligibility_status, 'flags': flags}

    # SME/business below threshold — exempt
    if eligibility_status == 'sme_below_threshold':
        return {'fee': 0.0, 'eligibility_status': eligibility_status, 'flags': flags}

    # SME/business above threshold — charge per event
    fee = round(per_event_fee * deposit_txn_count, 2)
    return {'fee': fee, 'eligibility_status': eligibility_status, 'flags': flags}
