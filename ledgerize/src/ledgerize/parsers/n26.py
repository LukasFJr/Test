from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..normalize import finalize
from ..utils import parse_amount, parse_date
from .base import BaseParser


class N26Parser(BaseParser):
    def parse(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path, sep=";", dtype=str)
        df = pd.DataFrame(
            {
                "date": df["Date"].map(lambda x: parse_date(str(x)).date()),
                "description": df["Payee"],
                "amount": df["Amount"].map(lambda x: parse_amount(str(x))),
                "currency": df["Currency"],
                "account": df["Account"].map(self.map_account),
            }
        )
        df["category"] = None
        df = finalize(df)
        df["raw_source"] = path.name
        return df
