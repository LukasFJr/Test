"""Optional mapping of deprecated subcommand aliases.

This allows migration of old CLI usages to the current canonical commands.
"""

from __future__ import annotations

from typing import Dict

# Map of binary -> {alias: canonical}
ALIASES: Dict[str, Dict[str, str]] = {
    # Example: historically ``ledgerize sync`` became ``ledgerize import``
    "ledgerize": {
        "sync": "import",
        "analyse": "report",
    }
}
