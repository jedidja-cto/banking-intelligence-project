"""
Portfolio Engine — v0.5.0

Core logic for batch customer analysis, portfolio aggregation, and targeting.
"""

import pandas as pd
from pathlib import Path
import yaml
from config import load_account_config

def run_portfolio(account_ids, txns_df, customers_df, project_root):
    """
    Run analysis for all customers across all accounts in the set.
    """
    from engine.account_fit import analyze_customer_for_account, generate_recommendation

    results = {}
    unique_customers = txns_df["customer_id"].unique()

    # Pre-load account configs
    account_configs = {}
    for acc_id in account_ids:
        cfg_path = project_root / "configs" / "account_types" / f"{acc_id}.yaml"
        account_configs[acc_id] = load_account_config(str(cfg_path))

    for customer_id in unique_customers:
        cust_txns = txns_df[txns_df["customer_id"] == customer_id]
        customer_row = customers_df[customers_df["customer_id"] == customer_id].iloc[0].to_dict()
        
        cust_results = {"accounts": {}}
        
        # Analyze each account
        for acc_id in account_ids:
            res = analyze_customer_for_account(
                account_configs[acc_id],
                cust_txns,
                customer_row,
                project_root
            )
            cust_results["accounts"][acc_id] = res
            
        # Recommendation (v0.5.0 specific for Basic vs PAYU)
        if "basic_banking" in cust_results["accounts"] and "silver_payu" in cust_results["accounts"]:
            rec = generate_recommendation(
                cust_results["accounts"]["basic_banking"],
                cust_results["accounts"]["silver_payu"]
            )
            cust_results["recommendation"] = rec
        else:
            cust_results["recommendation"] = {
                "recommended_account": "unknown",
                "reasons": ["missing required accounts for recommendation"],
                "alternative": None
            }
            
        results[customer_id] = cust_results

    # Aggregate & Rank
    aggregate = aggregate_portfolio(results)
    targets = rank_targets(results)

    return {
        "customers": results,
        "aggregate": aggregate,
        "targets": targets
    }

def aggregate_portfolio(portfolio_results):
    """
    Compute aggregate statistics for the portfolio.
    """
    count = len(portfolio_results)
    rec_counts = {"choose_basic_banking": 0, "choose_silver_payu": 0, "unknown": 0}
    signal_counts = {"payu_upgrade_candidate": 0, "cashout_shift_candidate": 0, "digital_shift_candidate": 0}
    atm_pressure_count = 0
    total_payu_cost = 0.0
    payu_cost_count = 0

    for cust_id, res in portfolio_results.items():
        # Recommendations
        rec = res.get("recommendation", {}).get("recommended_account", "unknown")
        if rec == "Basic Banking":
            rec_counts["choose_basic_banking"] += 1
        elif rec == "Silver PAYU":
            rec_counts["choose_silver_payu"] += 1
        else:
            rec_counts["unknown"] += 1
            
        # Signals & ATM pressure (from Basic Banking results)
        basic_res = res["accounts"].get("basic_banking", {})
        if basic_res:
            sigs = basic_res.get("migration_signals", [])
            for sig in signal_counts:
                if sig in sigs:
                    signal_counts[sig] += 1
            
            # ATM Pressure: excess_atm_withdrawals > 0
            # Derive from features: nedbank_atm_withdrawal_count > free_tier
            feat = basic_res.get("_features", {})
            atm_used = feat.get("nedbank_atm_withdrawal_count", 0)
            if atm_used > 3: # Constant for basic_banking (v0.5.0)
                atm_pressure_count += 1
                
        # PAYU fees
        payu_res = res["accounts"].get("silver_payu", {})
        if payu_res and payu_res.get("cost_available"):
            cost = payu_res.get("total_cost")
            if cost is not None:
                total_payu_cost += cost
                payu_cost_count += 1

    avg_payu_cost = total_payu_cost / payu_cost_count if payu_cost_count > 0 else 0.0

    return {
        "customer_count": count,
        "recommendation_counts": rec_counts,
        "signal_counts": signal_counts,
        "atm_pressure_count": atm_pressure_count,
        "fee_pain": {
            "total_payu_cost": total_payu_cost,
            "avg_payu_cost": avg_payu_cost
        }
    }

def rank_targets(portfolio_results, limit=10):
    """
    Rank customers into targeting lists.
    """
    from engine.account_fit import clamp59

    upgrade_list = []
    cashout_list = []
    digital_list = []

    for cust_id, res in portfolio_results.items():
        basic_res = res["accounts"].get("basic_banking", {})
        if not basic_res:
            continue
            
        feat = basic_res.get("_features", {})
        sigs = basic_res.get("migration_signals", [])
        kpis = basic_res.get("kpis", {})
        
        # 1. PAYU Upgrade Targets
        atm_used = feat.get("nedbank_atm_withdrawal_count", 0)
        excess_atm = max(atm_used - 3, 0)
        paid_rail = kpis.get("paid_rail_dependency_ratio", 0.0)
        
        upgrade_list.append({
            "customer_id": cust_id,
            "has_signal": "payu_upgrade_candidate" in sigs,
            "excess_atm": excess_atm,
            "paid_rail": paid_rail,
            "reason": clamp59(f"ATMex {int(excess_atm)} PaidRail {paid_rail:.2f}")
        })
        
        # 2. Cashout Shift Targets
        cashout_list.append({
            "customer_id": cust_id,
            "has_signal": "cashout_shift_candidate" in sigs,
            "atm_count": atm_used,
            "reason": clamp59(f"ATM Count {int(atm_used)}")
        })
        
        # 3. Digital Shift Targets
        digi_ratio = kpis.get("digital_ratio", 1.0)
        digital_list.append({
            "customer_id": cust_id,
            "has_signal": "digital_shift_candidate" in sigs,
            "digi_ratio": digi_ratio,
            "reason": clamp59(f"DigiRatio {digi_ratio:.2f}")
        })

    # Sorting
    # upgrade_list: signal desc, excess_atm desc, paid_rail desc
    upgrade_list.sort(key=lambda x: (x["has_signal"], x["excess_atm"], x["paid_rail"]), reverse=True)
    
    # cashout_list: signal desc, atm_count desc
    cashout_list.sort(key=lambda x: (x["has_signal"], x["atm_count"]), reverse=True)
    
    # digital_list: signal desc, digi_ratio asc
    digital_list.sort(key=lambda x: (x["has_signal"], -x["digi_ratio"]), reverse=True)

    return {
        "top_payu_upgrade_targets": upgrade_list[:limit],
        "top_cashout_shift_targets": cashout_list[:limit],
        "top_digital_shift_targets": digital_list[:limit]
    }
