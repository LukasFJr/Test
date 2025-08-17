"""Simple wrapper to execute binaries through :func:`run_cli`."""

from __future__ import annotations

import argparse
from typing import Sequence

from .cli_safe import run_cli


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a CLI with validation")
    parser.add_argument("--dry-run", action="store_true", help="Only validate")
    parser.add_argument("binary", help="Executable to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments")
    ns = parser.parse_args(argv)
    run_cli(ns.binary, ns.args, dry_run=ns.dry_run)
