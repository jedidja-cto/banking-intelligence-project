"""
Generic KPI Engine for Account Fit Intelligence Engine.

Reads KPI definitions from a YAML config dict and computes:
  - KPI values from behavioural features
  - Excess ATM cost via real tariff engine (not a placeholder scalar)
  - Account fit score (0-100) based on migration signal penalties
  - Migration signals (list of fired signal names)
  - Insight messages
  - Benefit utilisation (v0.3.1) — per-benefit usage/allowance/remaining

v0.3.0 — No product logic inside this module. All thresholds come from YAML.
v0.3.1 — Added compute_benefits(); updated compute_all() to accept account_config;
          evaluate_migration_signals() now supports both 'all:' and 'conditions:' keys.

SECURITY: formula strings are evaluated by SafeExpressionEvaluator which uses
ast.parse + an allow-list of safe AST node types. No bare eval(). No builtins other
than max() and min() are permitted.
"""

import ast
import math
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


# ---------------------------------------------------------------------------
# Safe Expression Evaluator
# ---------------------------------------------------------------------------

# AST node types that are permitted in formula strings.
# NOTE: Python's ast module uses:
#   ast.Mult (not ast.Mul), ast.FloorDiv, etc.
_SAFE_NODE_TYPES = (
    ast.Expression,
    ast.BoolOp, ast.And, ast.Or,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Constant,
    ast.Name,
    ast.Load,
    # Arithmetic operators (correct Python ast names)
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    # Unary operators
    ast.UAdd, ast.USub, ast.Not, ast.Invert,
    # Comparison operators
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    # Allow max() and min() calls only
    ast.Call,
    ast.keyword,
)


class SafeExpressionEvaluator:
    """
    AST-validated expression evaluator for KPI formula strings.

    Permitted constructs:
      - Arithmetic: +, -, *, /, //, %, **
      - Comparisons: ==, !=, <, <=, >, >=
      - Boolean ops: and, or, not
      - Name references (resolved from namespace)
      - Calls to max() and min() with positional args only

    Disallowed: attribute access, subscripting, comprehensions, lambda,
                imports, walrus operator, f-strings, starred expressions,
                any function call other than max/min.

    Raises:
        ValueError: If the formula contains disallowed AST nodes.
        NameError: If a referenced name is not in the evaluation namespace.
    """

    _ALLOWED_FUNCTIONS = {"max", "min"}

    def _check_node(self, node: ast.AST) -> None:
        """Recursively validate that all AST nodes are safe."""
        if not isinstance(node, _SAFE_NODE_TYPES):
            raise ValueError(
                f"Disallowed expression in formula: {type(node).__name__}. "
                "Only arithmetic, comparisons, boolean ops, name references, "
                "and max()/min() calls are permitted."
            )
        # Extra guard: function calls must be max() or min() only
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError(
                    "Only simple function calls (max, min) are permitted — "
                    f"got {ast.dump(node.func)}"
                )
            if node.func.id not in self._ALLOWED_FUNCTIONS:
                raise ValueError(
                    f"Function '{node.func.id}' is not allowed in formulas. "
                    f"Permitted: {self._ALLOWED_FUNCTIONS}"
                )
            if node.keywords:
                raise ValueError("Keyword arguments are not permitted in max()/min() calls.")
        for child in ast.iter_child_nodes(node):
            self._check_node(child)

    def evaluate(self, formula: str, namespace: Dict[str, Any]) -> Any:
        """
        Parse, validate, and evaluate a formula string.

        Args:
            formula:   Expression string, e.g. "atm_withdrawal_count / max(total_payments, 1)"
            namespace: Dict of variable names available in the expression.

        Returns:
            Evaluated result (typically float or bool).

        Raises:
            ValueError: If the formula contains disallowed constructs.
            NameError: If a name in the formula is not in namespace.
            ZeroDivisionError: Should not occur if formulas use max(..., 1); but
                               callers should still protect against it.
        """
        try:
            tree = ast.parse(formula, mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"Formula syntax error: '{formula}' — {exc}") from exc

        self._check_node(tree.body)

        # Build a safe eval namespace with only max/min builtins
        safe_namespace = {"max": max, "min": min, **namespace}
        # Compile and evaluate
        code = compile(tree, filename="<kpi_formula>", mode="eval")
        return eval(code, {"__builtins__": {}}, safe_namespace)  # noqa: S307 — builtins blanked


# ---------------------------------------------------------------------------
# KPI Engine
# ---------------------------------------------------------------------------

class KPIEngine:
    """
    Generic, config-driven KPI computation engine.

    All product logic lives in YAML. Python has no hardcoded thresholds.

    Args:
        kpi_config: Loaded KPI YAML dict (e.g. from basic_banking_kpis.yaml).
    """

    def __init__(self, kpi_config: Dict[str, Any]) -> None:
        self._config = kpi_config
        self._free_tier: Dict[str, Any] = kpi_config.get("free_tier", {})
        self._kpis_def: Dict[str, Any] = kpi_config.get("kpis", {})
        self._signals_def: Dict[str, Any] = kpi_config.get("migration_signals", {})
        self._insights_def: Dict[str, Any] = kpi_config.get("insight_outputs", {})
        self._north_star: Dict[str, Any] = kpi_config.get("north_star", {})
        self._evaluator = SafeExpressionEvaluator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_all(
        self,
        features: Dict[str, Any],
        customer_txns: Optional[pd.DataFrame] = None,
        fee_schedule: Optional[Dict[str, Any]] = None,
        account_config: Optional[Dict[str, Any]] = None,  # v0.3.1
    ) -> Dict[str, Any]:
        """
        Run the full KPI pipeline for one customer.

        Args:
            features:      Output of extract_behavioural_features().
            customer_txns: Customer transaction DataFrame (needed for
                           excess_atm_cost computation via tariff engine).
            fee_schedule:  Loaded fee schedule dict (nedbank_2026_27.yaml).
            account_config: Loaded account YAML dict (needed for compute_benefits). (v0.3.1)

        Returns:
            {
              "kpis": {...},
              "account_fit_score": float,
              "migration_signals": [...],
              "insights": [...],
              "benefits": {...},  # only present when account_config provided (v0.3.1)
            }
        """
        kpis = self.compute_kpis(features)
        kpis["excess_atm_cost"] = self.compute_excess_atm_cost(
            features, customer_txns, fee_schedule
        )
        signals = self.evaluate_migration_signals(kpis)
        score = self.compute_account_fit_score(kpis, signals)
        kpis["account_fit_score"] = score
        insights = self.generate_insights(kpis, signals)

        result: Dict[str, Any] = {
            "kpis": kpis,
            "account_fit_score": score,
            "migration_signals": signals,
            "insights": insights,
        }

        # v0.3.1: include benefit utilisation when account_config is supplied
        if account_config is not None:
            result["benefits"] = self.compute_benefits(features, account_config)

        return result

    def compute_kpis(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate all formula-based KPIs from the YAML config.

        Skips KPIs marked `computed: true` (they are handled separately).

        Args:
            features: Feature dict from extract_behavioural_features().

        Returns:
            Dict mapping kpi_name -> computed value.
        """
        # Namespace = features dict + free_tier values (no name collision expected)
        namespace = {**features, **self._free_tier}

        results: Dict[str, Any] = {}
        for kpi_name, kpi_def in self._kpis_def.items():
            if kpi_def.get("computed", False):
                # Deferred to dedicated method (excess_atm_cost, account_fit_score)
                results[kpi_name] = None
                continue
            formula = kpi_def.get("formula", "")
            if not formula:
                results[kpi_name] = None
                continue
            try:
                value = self._evaluator.evaluate(formula, namespace)
                results[kpi_name] = float(value) if isinstance(value, (int, float)) else value
            except Exception as exc:
                # Surface the error with context rather than silently nulling
                raise RuntimeError(
                    f"KPI '{kpi_name}': failed to evaluate formula '{formula}' — {exc}"
                ) from exc

        return results

    def compute_excess_atm_cost(
        self,
        features: Dict[str, Any],
        customer_txns: Optional[pd.DataFrame],
        fee_schedule: Optional[Dict[str, Any]],
    ) -> float:
        """
        Compute actual monetary cost of excess Nedbank ATM withdrawals.

        Uses the REAL Nedbank ATM fee rule (per_step: N$10 per N$300 withdrawn)
        applied only to withdrawals beyond the free tier.

        Algorithm:
          1. Determine excess count = nedbank_atm_withdrawal_count - free_nedbank_atm_withdrawals
          2. If excess_count <= 0, cost = 0.
          3. Sort nedbank ATM withdrawals by amount (ascending).
          4. Apply per_step fee rule to the excess transactions only.

        Args:
            features:      Feature dict (must contain nedbank_atm_withdrawal_count).
            customer_txns: Raw transaction DataFrame for this customer.
                           If None or missing, returns 0.0.
            fee_schedule:  Loaded fee schedule YAML dict.
                           If None, returns 0.0.

        Returns:
            Excess ATM cost in NAD (float).
        """
        if customer_txns is None or fee_schedule is None:
            return 0.0

        free_tier_count: int = int(self._free_tier.get("free_nedbank_atm_withdrawals", 0))
        nedbank_atm_count: int = int(features.get("nedbank_atm_withdrawal_count", 0))
        excess_count = max(nedbank_atm_count - free_tier_count, 0)

        if excess_count == 0:
            return 0.0

        # Filter to Nedbank ATM withdrawal transactions only
        if "atm_owner" not in customer_txns.columns or "type" not in customer_txns.columns:
            return 0.0

        nedbank_atm_txns = customer_txns[
            (customer_txns["type"] == "atm_withdrawal") &
            (customer_txns["atm_owner"] == "nedbank")
        ]["amount"].abs().sort_values().tolist()

        if not nedbank_atm_txns:
            return 0.0

        # The free tier covers the first N withdrawals (cheapest first to be conservative).
        # "excess" = the withdrawals beyond the free tier count.
        excess_txns = nedbank_atm_txns[free_tier_count:]  # amounts for excess withdrawals

        # Apply real Nedbank ATM fee rule from fee schedule
        atm_rule = fee_schedule.get("atm", {}).get("nedbank_atm_withdrawal", {})
        rule_type = atm_rule.get("rule_type", "per_step")
        step_amount = atm_rule.get("step_amount", 300)
        step_fee = atm_rule.get("step_fee", 10.0)

        total_excess_cost = 0.0
        if rule_type == "per_step":
            for amount in excess_txns:
                steps = math.ceil(amount / step_amount)
                total_excess_cost += steps * step_fee
        else:
            # Fallback: flat per withdrawal (unknown rule type)
            total_excess_cost = float(len(excess_txns)) * step_fee

        return round(total_excess_cost, 2)

    def evaluate_migration_signals(self, kpis: Dict[str, Any]) -> List[str]:
        """
        Evaluate migration signals against computed KPI values.

        A signal fires only if ALL its conditions evaluate to True.

        Supports two YAML key styles (v0.3.1):
          - 'conditions: [...]' — legacy style (v0.3.0)
          - 'all: [...]'        — new style (v0.3.1)
        Both are equivalent: the signal fires only when every expression is True.

        Args:
            kpis: Dict of computed KPI values.

        Returns:
            List of signal names that fired.
        """
        fired: List[str] = []
        # Build namespace from kpis (skip None values — computed-but-not-yet-set)
        namespace = {k: v for k, v in kpis.items() if v is not None}

        for signal_name, signal_def in self._signals_def.items():
            # v0.3.1: accept both 'all:' and 'conditions:' key styles
            conditions: List[str] = signal_def.get("all", signal_def.get("conditions", []))
            if not conditions:
                continue
            try:
                all_true = all(
                    bool(self._evaluator.evaluate(cond, namespace))
                    for cond in conditions
                )
            except Exception:
                # If a condition can't be evaluated (e.g. missing KPI), skip silently
                all_true = False
            if all_true:
                fired.append(signal_name)

        return fired

    def compute_account_fit_score(
        self,
        kpis: Dict[str, Any],
        signals: List[str],
    ) -> float:
        """
        Compute account fit score (0–100).

        Starts at the north_star base (100). Deducts the configured penalty
        for each fired migration signal. Clamps result to [0, 100].

        Args:
            kpis:    Computed KPI dict (unused directly; signals already evaluated).
            signals: List of fired signal names.

        Returns:
            Account fit score as a float between 0 and 100.
        """
        base: float = float(self._north_star.get("base", 100))
        score = base

        for signal_name in signals:
            signal_def = self._signals_def.get(signal_name, {})
            penalty = float(signal_def.get("penalty", 10))
            score -= penalty

        return max(0.0, min(100.0, round(score, 1)))

    def generate_insights(
        self,
        kpis: Dict[str, Any],
        signals: List[str],
    ) -> List[str]:
        """
        Generate human-readable insight messages based on KPI results and signals.

        v0.3.1: insight_outputs are now signal-keyed — each key matches a signal name.
        The good_fit entry is always the no-signal fallback.

        Backward-compatible with the old 'signal:' / 'trigger:' key style.

        Args:
            kpis:    Computed KPI dict.
            signals: Fired migration signals.

        Returns:
            List of insight message strings (at least one — good_fit or signal-based).
        """
        messages: List[str] = []
        namespace = {k: v for k, v in kpis.items() if v is not None}

        for insight_key, insight_def in self._insights_def.items():
            if insight_key == "good_fit":
                continue  # handled as fallback below

            message = insight_def.get("message", "")
            if not message:
                continue

            fires = False
            # v0.3.1 signal-keyed style: the insight_key itself is a signal name
            if insight_key in signals:
                fires = True

            # Backward-compat: old 'signal:' / 'trigger:' keys still work
            if not fires:
                signal_match = insight_def.get("signal")
                if signal_match and signal_match in signals:
                    fires = True
            if not fires:
                trigger_expr = insight_def.get("trigger")
                if trigger_expr:
                    try:
                        fires = bool(self._evaluator.evaluate(trigger_expr, namespace))
                    except Exception:
                        fires = False

            if fires:
                messages.append(message)

        # Default good_fit message when nothing else fired
        if not messages:
            good_fit_def = self._insights_def.get("good_fit", {})
            gf_message = good_fit_def.get("message", "")
            if gf_message:
                messages.append(gf_message)

        return messages

    def compute_benefits(
        self,
        features: Dict[str, Any],
        account_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compute benefit utilisation for each benefit defined in the KPI YAML.

        Reads kpi_config["benefits"] for each benefit's allowance_key and
        usage_feature_key, then looks up allowance from account_config["free_tier"].

        Allowance interpretations:
          - bool True  -> remaining = "included"    (unconditional inclusion)
          - int        -> remaining = max(allowance - usage, 0)
          - list       -> remaining = "included"     (txn types; just report usage)

        Args:
            features:       Output of extract_behavioural_features().
            account_config: Loaded account YAML dict (e.g. basic_banking.yaml).

        Returns:
            Dict mapping benefit_name -> {"usage": ..., "allowance": ..., "remaining": ...}
        """
        benefits_def: Dict[str, Any] = self._config.get("benefits", {})
        free_tier: Dict[str, Any] = account_config.get("free_tier", {})
        results: Dict[str, Any] = {}

        for benefit_name, bdef in benefits_def.items():
            allowance_key: str = bdef.get("allowance_key", "")
            usage_feature_key: str = bdef.get("usage_feature_key", "")

            allowance = free_tier.get(allowance_key)
            usage = features.get(usage_feature_key, 0)

            if isinstance(allowance, bool):
                remaining = "included" if allowance else 0
            elif isinstance(allowance, list):
                # List of txn types — treat as "included"; just report usage
                remaining = "included"
            elif isinstance(allowance, int):
                remaining = max(allowance - int(usage), 0)
            elif isinstance(allowance, float):
                remaining = max(int(allowance) - int(usage), 0)
            else:
                remaining = "unknown"

            results[benefit_name] = {
                "usage": int(usage) if isinstance(usage, (int, float)) else usage,
                "allowance": allowance,
                "remaining": remaining,
            }

        return results
