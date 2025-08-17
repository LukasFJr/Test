"""Entry point to dispatch submodules via ``python -m app``."""

from __future__ import annotations

import sys
from typing import List

from . import main as main_module
from . import tools as tools_module


def _usage() -> None:
    print("Usage: python -m app <main|tools> ...", file=sys.stderr)


def main(argv: List[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        _usage()
        sys.exit(1)
    cmd, rest = args[0], args[1:]
    if cmd == "main":
        main_module.main(rest)
    elif cmd == "tools":
        tools_module.main(rest)
    else:
        _usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
