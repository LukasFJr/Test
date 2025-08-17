from __future__ import annotations

from pathlib import Path
from typing import Iterable

import click

SENSITIVE_EXTENSIONS = ["*.db", "*.parquet", "*.csv", "*.jsonl"]


def _sensitive_files(root: Path) -> Iterable[Path]:
    data_dir = root / "data"
    if not data_dir.exists():
        return []
    files: list[Path] = []
    for pattern in SENSITIVE_EXTENSIONS:
        files.extend(data_dir.rglob(pattern))
    return [p for p in files if p.is_file()]


def ensure_clean_repo(root: Path, override: bool = False) -> None:
    """Raise an error if sensitive files exist in a git repo.

    Parameters
    ----------
    root: Path
        Directory to scan (typically current working directory).
    override: bool
        If True, skip the guard.
    """
    if override:
        return
    if not (root / ".git").exists():
        return
    files = list(_sensitive_files(root))
    if files:
        joined = ", ".join(str(f) for f in files)
        raise click.ClickException(
            f"Sensitive files present in git repository: {joined}"
        )
