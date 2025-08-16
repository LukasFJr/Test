from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    handler = RichHandler(console=Console(), show_time=False)
    logging.basicConfig(level=level, handlers=[handler], format="%(message)s")
