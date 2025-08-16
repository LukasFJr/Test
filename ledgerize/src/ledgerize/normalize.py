from __future__ import annotations

import pandas as pd

from .utils import normalize_str, sha1_hash


REQUIRED_COLUMNS = [
    "account",
    "date",
    "amount",
    "currency",
    "description",
    "norm_desc",
    "category",
]


def finalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["norm_desc"] = df["description"].map(normalize_str)
    df["id"] = df.apply(
        lambda r: sha1_hash(
            r["account"],
            str(r["date"]),
            f"{r['amount']:.2f}",
            r["currency"],
            r["norm_desc"],
        ),
        axis=1,
    )
    if "category" not in df:
        df["category"] = "Uncategorized"
    return df
