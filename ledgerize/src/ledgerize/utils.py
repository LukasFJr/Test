from __future__ import annotations

import hashlib
import unicodedata
from datetime import datetime
from pathlib import Path

from charset_normalizer import from_path
from dateutil import parser  # type: ignore[import]


def detect_encoding(path: Path) -> str:
    result = from_path(str(path)).best()
    return result.encoding if result else "utf-8"


def parse_date(value: str) -> datetime:
    return parser.parse(value, dayfirst=True)


def parse_amount(value: str) -> float:
    value = value.replace(" ", "").replace(",", ".")
    return float(value)


def normalize_str(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(text.upper().split())


def sha1_hash(*parts: str) -> str:
    h = hashlib.sha1()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    previous_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current_row = [i]
        for j, cb in enumerate(b, 1):
            insertions = previous_row[j] + 1
            deletions = current_row[j - 1] + 1
            substitutions = previous_row[j - 1] + (ca != cb)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
