from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd


class BaseParser:
    def __init__(self, accounts: List[dict], currency: str) -> None:
        self.accounts = accounts
        self.currency = currency

    def parse(self, path: Path) -> pd.DataFrame:
        raise NotImplementedError

    def map_account(self, account: str) -> str:
        for acc in self.accounts:
            if acc["match"] in account:
                return acc["name"]
        return account
