"""Safely execute external CLI commands with subcommand validation."""

from __future__ import annotations

import logging
import os
import re
import subprocess
from subprocess import CompletedProcess
from typing import Iterable, Sequence, Set

from .cli_aliases import ALIASES

logger = logging.getLogger(__name__)


def _run_help(binary: str) -> str:
    """Return the combined stdout/stderr of ``binary --help``."""
    try:
        cp = subprocess.run(
            [binary, "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - handled by caller
        raise RuntimeError(f"Command not found: {binary}") from exc
    return (cp.stdout or "") + "\n" + (cp.stderr or "")


def _iter_command_blocks(text: str) -> Iterable[Sequence[str]]:
    """Yield blocks of indented lines that likely contain subcommands."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        lower = line.lower()
        if "command" in lower and line.strip().endswith(":"):
            # classic "Commands:"/"Subcommands:" block
            start = idx + 1
        elif (
            line.strip().endswith(":")
            and "option" not in lower
            and idx + 1 < len(lines)
        ):
            # heuristic: any colon line (except options) followed by indented lines
            start = idx + 1
        else:
            continue

        block: list[str] = []
        for line_ in lines[start:]:
            if not line_.strip():
                if block:
                    break
                continue
            if re.match(r"^\s{2,}\S", line_):
                block.append(line_)
            elif block:
                break
        if block:
            yield block


def list_subcommands(binary: str) -> Set[str]:
    """Return the set of available subcommands for ``binary``."""
    help_text = _run_help(binary)
    subcommands: Set[str] = set()
    pattern = re.compile(r"^\s{2,}([\w-]+)(\s{2,}|$)")
    for block in _iter_command_blocks(help_text):
        for line in block:
            match = pattern.match(line)
            if match:
                subcommands.add(match.group(1))
        if subcommands:
            break
    return subcommands


def _levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein distance between two strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(
                min(
                    prev[j] + 1,
                    cur[j - 1] + 1,
                    prev[j - 1] + cost,
                )
            )
        prev = cur
    return prev[-1]


def ensure_subcommand(binary: str, subcmd: str) -> None:
    """Ensure that ``subcmd`` exists for ``binary`` or raise ``ValueError``."""
    subcommands = list_subcommands(binary)
    if subcmd in subcommands:
        return
    suggestions = sorted([c for c in subcommands if _levenshtein(subcmd, c) <= 2])
    msg = (
        f"Commande inconnue: {subcmd}\n"
        "Sous-commandes disponibles pour {binary}: "
        f"{', '.join(sorted(subcommands))}"
    )
    if suggestions:
        msg += f"\nAstuce: avez-vous voulu dire '{suggestions[0]}' ?"
    raise ValueError(msg)


def run_cli(
    binary: str, args: Sequence[str] | None = None, *, dry_run: bool = False
) -> CompletedProcess[str]:
    """Run ``binary`` with ``args`` after validating the subcommand.

    Parameters
    ----------
    binary: str
        The executable to run.
    args: Sequence[str]
        Command arguments; the first element is treated as subcommand.
    dry_run: bool
        If True, the command is only logged and not executed.
    """
    if args is None:
        args = []
    args = list(args)
    if args:
        subcmd = args[0]
        subcmd = ALIASES.get(binary, {}).get(subcmd, subcmd)
        ensure_subcommand(binary, subcmd)
        args[0] = subcmd
    cmd = [binary] + args
    logger.info("Executing: %s", " ".join(cmd))
    if dry_run:
        print(" ".join(cmd))
        return CompletedProcess(cmd, 0, "", "")
    try:
        cp = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=True,
            timeout=5,
        )
    except subprocess.CalledProcessError as exc:
        msg = (
            f"Command {' '.join(cmd)} failed with code {exc.returncode}\n"
            f"stdout: {exc.stdout}\n"
            f"stderr: {exc.stderr}"
        )
        raise RuntimeError(msg) from exc
    return cp


def get_secret(service: str, user: str) -> str:
    """Retrieve a secret from keyring or environment variables.

    Environment variable fallback is ``{SERVICE}_{USER}_TOKEN`` with both parts
    upper‑cased.
    """
    secret = None
    try:
        import keyring  # type: ignore

        secret = keyring.get_password(service, user)
    except Exception:  # pragma: no cover - keyring may be missing
        secret = None
    if secret:
        return secret
    env_key = f"{service}_{user}_TOKEN".upper().replace("-", "_")
    secret = os.environ.get(env_key)
    if secret:
        return secret
    raise RuntimeError(
        "Aucun secret trouvé pour le service '{service}' et l'utilisateur '{user}'. "
        f"Installez 'keyring' ou définissez la variable d'environnement {env_key}."
    )
