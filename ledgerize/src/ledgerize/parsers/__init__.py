from __future__ import annotations

from pathlib import Path
from typing import Dict, Type

import pandas as pd

from .base import BaseParser
from .generic import GenericParser
from .n26 import N26Parser

PARSERS: Dict[str, Type[BaseParser]] = {
    "n26": N26Parser,
}


def choose_parser(path: Path) -> Type[BaseParser]:
    name = path.stem.lower()
    for key, parser in PARSERS.items():
        if key in name:
            return parser
    return GenericParser


def parse_file(path: Path, accounts, currency: str) -> pd.DataFrame:
    parser = choose_parser(path)(accounts, currency)
    return parser.parse(path)


def preview_file(path: Path, accounts, n: int) -> pd.DataFrame:
    parser = choose_parser(path)(accounts, "EUR")
    df = parser.parse(path)
    return df.head(n)
