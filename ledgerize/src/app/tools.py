"""Miscellaneous helper tools for the application."""

from __future__ import annotations

import argparse
from typing import Sequence

from .cli_safe import list_subcommands


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    ps = sub.add_parser("print-subcommands", help="List subcommands of a binary")
    ps.add_argument("binary")
    ns = parser.parse_args(argv)
    if ns.cmd == "print-subcommands":
        for name in sorted(list_subcommands(ns.binary)):
            print(name)
