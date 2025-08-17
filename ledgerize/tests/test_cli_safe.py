import subprocess
import shutil

import pytest

from app.cli_safe import list_subcommands, ensure_subcommand, run_cli

CLICK_HELP = """Usage: prog [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  import   Import data
  report   Generate report
  preview  Preview data
"""

TYPER_HELP = """Usage: prog [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion
  --help                Show this message and exit.

Commands:
  import   Import data
  report   Generate report
  preview  Preview data
"""

ARGPARSE_HELP = """usage: prog [-h] {import,report,preview} ...

positional arguments:
  {import,report,preview}
    import   Import data
    report   Generate report
    preview  Preview data
"""


@pytest.mark.parametrize("output", [CLICK_HELP, TYPER_HELP, ARGPARSE_HELP])
def test_list_subcommands_parsing(monkeypatch, output):
    def fake_run(cmd, capture_output, text, timeout, check):
        return subprocess.CompletedProcess(cmd, 0, output, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert list_subcommands("prog") == {"import", "report", "preview"}


def test_ensure_subcommand_suggestion(monkeypatch):
    monkeypatch.setattr(
        "app.cli_safe.list_subcommands", lambda binary: {"import", "report", "preview"}
    )
    with pytest.raises(ValueError) as exc:
        ensure_subcommand("prog", "improt")
    assert "import" in str(exc.value)


def test_run_cli_exec(monkeypatch):
    monkeypatch.setattr("app.cli_safe.list_subcommands", lambda binary: {"import"})

    calls = {}

    def fake_run(cmd, text, capture_output, check, timeout):
        calls["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, "ok", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    cp = run_cli("prog", ["import"])
    assert cp.stdout == "ok"
    assert calls["cmd"] == ["prog", "import"]


@pytest.mark.xfail(shutil.which("ledgerize") is None, reason="ledgerize missing")
def test_integration_ledgerize():
    cmds = list_subcommands("ledgerize")
    assert cmds
    ensure_subcommand("ledgerize", "import")
