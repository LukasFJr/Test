from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text())


def load_rules(path: Path) -> Dict[str, Any]:
    return load_yaml(path)


def load_accounts(path: Path) -> List[Dict[str, str]]:
    data = load_yaml(path)
    return data.get("accounts", [])
