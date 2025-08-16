from __future__ import annotations

import re
from typing import Any, Dict

import pandas as pd


def _check(row: pd.Series, cond: Dict[str, Any]) -> bool:
    if "regex" in cond:
        return bool(re.search(cond["regex"], row["description"]))
    if "contains" in cond:
        return cond["contains"].upper() in row["description"].upper()
    if "amount_gt" in cond:
        return row["amount"] > float(cond["amount_gt"])
    if "amount_lt" in cond:
        return row["amount"] < float(cond["amount_lt"])
    return False


def _eval_when(row: pd.Series, when: Dict[str, Any]) -> bool:
    if "any" in when:
        return any(_check(row, c) for c in when["any"])
    if "all" in when:
        return all(_check(row, c) for c in when["all"])
    return _check(row, when)


def apply_rules(df: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
    df = df.copy()
    for rule in cfg.get("rules", []):
        mask = df.apply(lambda r: _eval_when(r, rule.get("when", {})), axis=1)
        for col, value in rule.get("set", {}).items():
            df.loc[mask, col] = value
        df.loc[mask, "rule_id"] = rule.get("id")
    if "default_category" in cfg:
        df["category"].fillna(cfg["default_category"], inplace=True)
    return df


def explain_transaction(tx: Dict[str, Any]) -> str:
    return tx.get("rule_id", "fallback")
