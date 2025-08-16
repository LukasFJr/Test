from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..normalize import finalize
from ..utils import parse_amount, parse_date
from .base import BaseParser


class GenericParser(BaseParser):
    def parse(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        df["date"] = df["date"].map(lambda x: parse_date(str(x)).date())
        df["amount"] = df["amount"].map(lambda x: parse_amount(str(x)))
        if "currency" not in df:
            df["currency"] = self.currency
        if "account" not in df:
            df["account"] = "UNKNOWN"
        df["account"] = df["account"].map(self.map_account)
        df["category"] = None
        df = finalize(df)
        df["raw_source"] = path.name
        return df
