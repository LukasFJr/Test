from __future__ import annotations

import logging
from typing import Dict, Tuple

import pandas as pd

from .utils import levenshtein

logger = logging.getLogger(__name__)


def dedupe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["id"])
    seen: Dict[Tuple[str, str, float], str] = {}
    rows = []
    for _, row in df.iterrows():
        key = (row["account"], str(row["date"]), float(row["amount"]))
        norm = row["norm_desc"]
        if key in seen and levenshtein(seen[key], norm) <= 2:
            logger.debug("Dropping near duplicate: %s", row["description"])
            continue
        seen[key] = norm
        rows.append(row)
    return pd.DataFrame(rows)
