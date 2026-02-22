"""
Account fit analysis engine — v0.3.1

This module orchestrates the account fit analysis process, combining
configuration loading, data processing, fee calculation, and behavioural
feature extraction to produce a comprehensive account fit report.

Supported account types (via --account argument):
  silver_payu    — v0.2.1 PAYU fee report (unchanged, frozen)
  basic_banking  — v0.3.1 Generic KPI Engine report with exec summary

Changes in v0.2.1:
- Loads customers_sample.csv and builds customer_map for fast lookup
- Integrates compute_cash_deposit_fee into per-customer variable fee pipeline
- Reads account_class from config (no hardcoding)
- Adds deposit eligibility line to per-customer output (only if relevant)
- Adds ASSUMPTIONS footer block flagging customers with missing turnover

Changes in v0.3.0:
- Adds generic KPI engine path (gated on kpi_profile key in account YAML)
- Loads KPI config and instantiates KPIEngine when kpi_profile is set
- Per-customer KPI summary block for Basic Banking (fee block still runs for PAYU)
- PAYU output identical to v0.2.1 — zero breaking changes
- Account type selected via DEFAULT_ACCOUNT constant (extensible to CLI args)

Changes in v0.3.1:
- Replaced DEFAULT_ACCOUNT constant with argparse --account (default: basic_banking)
- Version label: Basic Banking = v0.3.1; PAYU = v0.2.1 (frozen label)
- Basic Banking: per-customer EXEC SUMMARY block (max 59-char lines)
- compute_all() now receives account_config to enable benefit computation
- Footer rollups: count exceeding free ATM tier, cashout_shift_candidate count,
  payu_upgrade_candidate count
- PAYU customer blocks and footer UNCHANGED
"""

from pathlib import Path
import argparse
import sys
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import load_account_config
from ingest.load_data import load_transactions
from fees.tariff_engine import (
    load_fee_schedule,
    compute_variable_fees,
    compute_cash_deposit_fee,
)
from features.build_features import extract_behavioural_features
from utils.paths import find_project_root
from engine.kpi_engine import KPIEngine   # v0.3.0

import pandas as pd


# ---------------------------------------------------------------------------
# Account type registry
# ---------------------------------------------------------------------------
_ACCOUNT_CONFIG_MAP = {
    "silver_payu": "silver_payu.yaml",
    "basic_banking": "basic_banking.yaml",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_customers(customers_path: str) -> pd.DataFrame:
    """Load customers CSV and return as DataFrame."""
    return pd.read_csv(customers_path)


def build_customer_map(customers_df: pd.DataFrame) -> dict:
    """
    Build a fast-lookup dict: customer_id -> {segment, annual_turnover}.

    Args:
        customers_df: Customers DataFrame (must have customer_id, customer_segment,
                      and annual_turnover columns)

    Returns:
        Dict keyed on customer_id
    """
    customer_map = {}
    for _, row in customers_df.iterrows():
        turnover_val = row.get('annual_turnover', None)
        if pd.isna(turnover_val):
            turnover_val = None
        customer_map[row['customer_id']] = {
            'customer_segment': str(row.get('customer_segment', 'individual')),
            'annual_turnover': turnover_val,
        }
    return customer_map


def load_kpi_config_for_account(
    account_config: dict,
    project_root: Path,
) -> dict | None:
    """
    Load KPI YAML config if the account config declares a kpi_profile. (v0.3.0)

    Args:
        account_config: Loaded account YAML dict.
        project_root:   Project root Path.

    Returns:
        Loaded KPI config dict, or None if kpi_profile is absent/null.
    """
    kpi_profile = account_config.get("kpi_profile")
    if not kpi_profile:
        return None
    kpi_config_path = project_root / "configs" / "kpis" / f"{kpi_profile}_kpis.yaml"
    if not kpi_config_path.exists():
        raise FileNotFoundError(
            f"KPI config not found for profile '{kpi_profile}': {kpi_config_path}"
        )
    with open(kpi_config_path, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Exec Summary formatter (v0.3.1 — Basic Banking only)
# Max line width: 59 chars (content area).
# ---------------------------------------------------------------------------

_EXEC_WIDTH = 59   # max line width including leading spaces

def _exec_line(content: str) -> str:
    """Return a left-padded exec summary line, truncated to _EXEC_WIDTH."""
    line = f"  {content}"
    return line[:_EXEC_WIDTH]


def _fmt_money(amount: float) -> str:
    """Format a NAD monetary value: N$XX.XX"""
    return f"N${amount:.2f}"


def _fmt_yn(value: int) -> str:
    """Format 0/1 as yes/no."""
    return "yes" if value else "no"


def print_exec_summary(customer_id: str, kpi_results: dict, account_config: dict) -> None:
    """
    Print a compact EXEC SUMMARY block for a Basic Banking customer.
    All lines are guaranteed <= _EXEC_WIDTH (59) chars.

    Args:
        customer_id:   The customer identifier.
        kpi_results:   Output of kpi_engine.compute_all().
        account_config: Loaded account YAML (for free tier values).
    """
    kr = kpi_results
    kpis = kr["kpis"]
    signals = kr["migration_signals"]
    insights = kr.get("insights", [])
    benefits = kr.get("benefits", {})

    fit_score = int(round(kr["account_fit_score"]))
    digi = kpis.get("digital_ratio", 0.0) or 0.0
    paid_rail = kpis.get("paid_rail_dependency_ratio", 0.0) or 0.0

    free_atm = account_config.get("free_tier", {}).get("free_nedbank_atm_withdrawals", 3)
    atm_total = kpis.get("free_atm_utilisation_ratio", 0.0) or 0.0
    # nedbank ATM count comes from features via kpis namespace
    # We derive atm_used from the ratio * free_atm (or just use features directly)
    atm_b = benefits.get("free_atm_withdrawals", {})
    atm_used = atm_b.get("usage", 0)
    excess_atm = max(atm_used - free_atm, 0)
    excess_cost = kpis.get("excess_atm_cost", 0.0) or 0.0

    # CashOut, EFT->Ned, OnlineSub from benefits where available, else 0
    eft_b = benefits.get("free_eft_to_nedbank", {})
    sub_b = benefits.get("free_online_subscription", {})

    # cashout_count is a KPI-adjacent feature value we need to surface
    # It's computed inside features and passed through the kpi namespace
    # We get it from kpis if it was passed through, or default 0
    cashout_val = int(kpis.get("cashout_adoption_ratio", 0) * max(
        int(atm_used) + int(eft_b.get("usage", 0)), 1
    ) + 0.5)  # approximation fallback
    # Better: cashout_count flows through to kpis from features via compute_kpis namespace
    # But it's not a formula KPI — we need it from the raw features dict.
    # We'll accept it via a separate "features" key in kpi_results if present.
    cashout_count_raw = kr.get("_features", {}).get("cashout_count", 0)
    eft_to_ned = eft_b.get("usage", 0)
    online_sub = sub_b.get("usage", 0)

    sigs_str = ", ".join(signals) if signals else "none"
    next_msg = insights[0][:40] if insights else "n/a"  # truncate long messages

    sep = "-" * (_EXEC_WIDTH - 2)
    print(_exec_line(f"-- {customer_id} BASIC BANKING \u2014 EXEC SUMMARY --"))
    print(_exec_line(sep))
    print(_exec_line(
        f"Fit: {fit_score}/100  Digi: {digi:.2f}  PaidRail: {paid_rail:.2f}"
    ))
    print(_exec_line(
        f"ATM: {atm_used} (Free {free_atm}, Excess {excess_atm})"
        f"  ExcessCost: {_fmt_money(excess_cost)}"
    ))
    print(_exec_line(
        f"CashOut: {cashout_count_raw}  EFT->Ned: {eft_to_ned}"
        f"  OnlineSub: {_fmt_yn(online_sub)}"
    ))
    print(_exec_line(f"Signals: {sigs_str}"))
    print(_exec_line(f"Next: {next_msg}"))
    print(_exec_line(sep))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Execute the account fit analysis pipeline for the configured account type."""

    # v0.3.1: argparse replaces DEFAULT_ACCOUNT constant
    parser = argparse.ArgumentParser(
        description="Account Fit Intelligence Engine — Nedbank Namibia"
    )
    parser.add_argument(
        "--account",
        default="basic_banking",
        choices=list(_ACCOUNT_CONFIG_MAP.keys()),
        help="Account type to analyse (default: basic_banking)"
    )
    args = parser.parse_args()
    account_type = args.account

    PROJECT_ROOT = find_project_root(Path(__file__).resolve())

    account_filename = _ACCOUNT_CONFIG_MAP[account_type]
    config_path = PROJECT_ROOT / "configs" / "account_types" / account_filename
    fee_schedule_path = PROJECT_ROOT / "configs" / "fee_schedules" / "nedbank_2026_27.yaml"
    customers_path = PROJECT_ROOT / "data" / "synthetic" / "customers_sample.csv"
    tx_path = PROJECT_ROOT / "data" / "synthetic" / "transactions_sample.csv"

    # Load configuration
    account_config = load_account_config(str(config_path))
    fee_schedule = load_fee_schedule(str(fee_schedule_path))

    # Get account class for POS fee determination — config-driven, never hardcoded
    account_class = account_config.get('account_class', 'current')

    # v0.3.0: Load KPI config if the account has a kpi_profile
    kpi_config = load_kpi_config_for_account(account_config, PROJECT_ROOT)
    kpi_engine = KPIEngine(kpi_config) if kpi_config else None

    # v0.3.1: version label — PAYU keeps v0.2.1 label exactly; Basic Banking is v0.3.1
    if account_type == "silver_payu":
        version_label = "v0.2.1"
    elif kpi_engine:
        version_label = "v0.3.1"
    else:
        version_label = "v0.3.0"

    # Load data
    transactions = load_transactions(str(tx_path))
    customers_df = load_customers(str(customers_path))
    customer_map = build_customer_map(customers_df)

    # Extract turnover threshold from fee schedule config
    turnover_threshold = (
        fee_schedule.get('cash_deposit', {}).get('turnover_threshold', 1_300_000)
    )

    # Compute variable fees for all customers (POS, ATM, online)
    variable_fees = compute_variable_fees(transactions, fee_schedule, account_class)

    # Get unique customers
    unique_customers = transactions["customer_id"].unique()

    results = []
    flagged_turnover_customers = []

    for customer_id in unique_customers:
        tx_customer = transactions[transactions["customer_id"] == customer_id]

        # Customer profile
        cust_info = customer_map.get(customer_id, {
            'customer_segment': 'individual',
            'annual_turnover': None,
        })
        customer_segment = cust_info['customer_segment']
        annual_turnover = cust_info['annual_turnover']

        # Get fixed fee from config
        fixed_fee = account_config.get('monthly_fee', 0.0)

        # Get variable fee (POS, ATM, online) from tariff engine
        customer_var_fees = variable_fees.get(customer_id, {})
        tx_variable_fee = customer_var_fees.get('variable_total', 0.0)
        by_type = customer_var_fees.get('by_type', {})

        # Cash deposit fee (v0.2.1)
        deposit_txn_count = int((tx_customer['type'] == 'cash_deposit').sum())
        deposit_result = compute_cash_deposit_fee(
            customer_segment, annual_turnover, deposit_txn_count, fee_schedule,
        )
        deposit_fee = deposit_result['fee']
        eligibility_status = deposit_result['eligibility_status']
        deposit_flags = deposit_result['flags']

        if deposit_flags.get('turnover_required_for_deposit_fee'):
            flagged_turnover_customers.append(customer_id)

        variable_fee = round(tx_variable_fee + deposit_fee, 2)
        total_fee = round(fixed_fee + variable_fee, 2)

        fee_drivers = dict(by_type)
        if deposit_fee > 0:
            fee_drivers['cash_deposit'] = fee_drivers.get('cash_deposit', 0.0) + deposit_fee
        top_drivers = sorted(fee_drivers.items(), key=lambda x: x[1], reverse=True)[:3]

        show_deposit_line = (deposit_txn_count > 0) or deposit_flags.get(
            'turnover_required_for_deposit_fee', False
        )

        # v0.3.0: extract features with fee_schedule for charged_txn_count
        features = extract_behavioural_features(
            tx_customer,
            customer_segment=customer_segment,
            annual_turnover=annual_turnover,
            turnover_threshold=turnover_threshold,
            fee_schedule=fee_schedule if kpi_engine else None,
            account_class=account_class,
        )

        # v0.3.0/v0.3.1: compute KPI results if engine exists
        kpi_results = None
        if kpi_engine is not None:
            kpi_results = kpi_engine.compute_all(
                features=features,
                customer_txns=tx_customer,
                fee_schedule=fee_schedule,
                account_config=account_config,  # v0.3.1: enables compute_benefits
            )
            # v0.3.1: stash raw features for exec summary access (cashout_count etc.)
            kpi_results["_features"] = features

        results.append({
            'customer_id': customer_id,
            'customer_segment': customer_segment,
            'txn_count': features['txn_count'],
            'digital_ratio': features['digital_ratio'],
            'behaviour_tag': features['behaviour_tag'],
            'total_inflow': features['total_inflow'],
            'total_outflow': features['total_outflow'],
            'fixed_fee': fixed_fee,
            'variable_fee': variable_fee,
            'total_fee': total_fee,
            'top_drivers': top_drivers,
            'deposit_fee': deposit_fee,
            'deposit_eligibility': eligibility_status,
            'deposit_txn_count': deposit_txn_count,
            'show_deposit_line': show_deposit_line,
            'kpi_results': kpi_results,  # v0.3.0: None for PAYU path
            'features': features,         # v0.3.1: raw features for footer rollups
        })

    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------
    account_type_id = account_config.get('account_type_id', account_type)
    account_name = account_config.get('account_name', account_type_id)

    print("\n" + "=" * 70)
    print(f"{account_name} Multi-Customer Intelligence Report  {version_label}")
    print("=" * 70)
    print(f"\nAccount Type: {account_type_id}")
    print(f"Account Class: {account_class}  (POS pricing path: {account_class})")
    print(f"Total Customers: {len(unique_customers)}")
    print("")

    for r in results:
        seg_label = r['customer_segment'].upper()[:3]
        line1 = (f"{r['customer_id']:<11} [{seg_label}] "
                 f"{r['txn_count']:>3}tx {r['digital_ratio']*100:>5.1f}% "
                 f"{r['behaviour_tag']:<17}")
        line2 = f"  In: N${r['total_inflow']:>10,.2f}  Out: N${r['total_outflow']:>10,.2f}"
        line3 = (f"  Fixed: N${r['fixed_fee']:>5.2f}  "
                 f"Var: N${r['variable_fee']:>6.2f}  "
                 f"Total: N${r['total_fee']:>6.2f}")

        print(line1)
        print(line2)
        print(line3)

        if r['show_deposit_line']:
            dep_fee_str = f"N${r['deposit_fee']:.2f}" if r['deposit_fee'] > 0 else "FREE"
            print(f"  Deposit: {r['deposit_eligibility']:<24}  {dep_fee_str} "
                  f"({r['deposit_txn_count']} events)")

        if r['top_drivers']:
            drivers_str = "  Top fees: " + ", ".join(
                [f"{tx_type} N${amt:.2f}" for tx_type, amt in r['top_drivers']]
            )
            print(drivers_str)

        # v0.3.1: EXEC SUMMARY block (Basic Banking only)
        if r['kpi_results'] is not None and kpi_engine is not None:
            kr = r['kpi_results']
            print_exec_summary(r['customer_id'], kr, account_config)

        print("")

    print("=" * 70)

    # -------------------------------------------------------------------------
    # Footer: behaviour distribution + assumptions
    # -------------------------------------------------------------------------
    print("\nBehaviour Distribution:")
    behaviour_counts: dict = {}
    for r in results:
        tag = r['behaviour_tag']
        behaviour_counts[tag] = behaviour_counts.get(tag, 0) + 1
    for tag, count in sorted(behaviour_counts.items()):
        print(f"  {tag:<17} {count:>3} customers")

    if not kpi_engine:
        # PAYU-specific deposit eligibility distribution (unchanged)
        print("\nDeposit Eligibility Distribution:")
        eligibility_counts: dict = {}
        for r in results:
            status = r['deposit_eligibility']
            eligibility_counts[status] = eligibility_counts.get(status, 0) + 1
        for status, count in sorted(eligibility_counts.items()):
            print(f"  {status:<28} {count:>3} customers")

    avg_digital_ratio = sum(r['digital_ratio'] for r in results) / len(results)
    avg_total_fee = sum(r['total_fee'] for r in results) / len(results)
    print(f"\nAverage Digital Ratio: {avg_digital_ratio:.1%}")
    print(f"Average Total Fee:     N${avg_total_fee:.2f}")

    if kpi_engine:
        kpi_scored = [r for r in results if r['kpi_results']]
        if kpi_scored:
            avg_fit = sum(
                r['kpi_results']['account_fit_score'] for r in kpi_scored
            ) / len(kpi_scored)
            n_signals = sum(
                len(r['kpi_results']['migration_signals']) > 0 for r in kpi_scored
            )
            print(f"Average Fit Score:     {avg_fit:.1f} / 100")
            print(f"Customers with signal: {n_signals} / {len(kpi_scored)}")

            # v0.3.1: Footer rollups (Basic Banking specific)
            free_atm_tier = account_config.get("free_tier", {}).get(
                "free_nedbank_atm_withdrawals", 3
            )
            n_atm_excess = sum(
                1 for r in kpi_scored
                if r['features'].get('nedbank_atm_withdrawal_count', 0) > free_atm_tier
            )
            n_cashout_shift = sum(
                1 for r in kpi_scored
                if 'cashout_shift_candidate' in r['kpi_results']['migration_signals']
            )
            n_payu_upgrade = sum(
                1 for r in kpi_scored
                if 'payu_upgrade_candidate' in r['kpi_results']['migration_signals']
            )
            print(f"\nBasic Banking Rollups:")
            print(f"  Exceeding free ATM tier ({free_atm_tier}): "
                  f"{n_atm_excess} / {len(kpi_scored)}")
            print(f"  cashout_shift_candidate:  "
                  f"{n_cashout_shift} / {len(kpi_scored)}")
            print(f"  payu_upgrade_candidate:   "
                  f"{n_payu_upgrade} / {len(kpi_scored)}")

    print("\n" + "-" * 70)
    print("ASSUMPTIONS:")
    n_flagged = len(flagged_turnover_customers)
    if n_flagged > 0:
        print(f"  * {n_flagged} customer(s) had missing annual_turnover with cash deposit activity")
        print(f"    -> cash deposit fee NOT charged (policy: do_not_charge_flag)")
        print(f"    -> flagged for manual turnover verification")
    else:
        print("  * No customers flagged for missing turnover")
    print("  * account_class read from YAML — no hardcoded values")
    print("  * Deposit fee value (N$25.00) is a placeholder pending Nedbank tariff publication")
    if kpi_engine:
        print("  * KPI engine formulas validated via AST SafeExpressionEvaluator — no unsafe eval")
        print("  * excess_atm_cost derived from real Nedbank ATM per_step fee rule (N$10/N$300)")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
