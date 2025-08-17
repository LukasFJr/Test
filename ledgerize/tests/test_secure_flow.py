from pathlib import Path
from click.testing import CliRunner
from ledgerize.cli import main
from ledgerize import vault
import os

BASE = Path(__file__).resolve().parent.parent


def test_secure_import(tmp_path: Path, monkeypatch) -> None:
    key = os.urandom(32)
    monkeypatch.setattr(vault, "_load_key", lambda: key)
    runner = CliRunner()
    out_dir = tmp_path / "data"
    vault_dir = tmp_path / "vault"
    result = runner.invoke(
        main,
        [
            "import",
            str(BASE / "samples"),
            "--rules",
            str(BASE / "samples/rules.yml"),
            "--accounts",
            str(BASE / "samples/accounts.yml"),
            "--out",
            str(out_dir),
            "--secure",
            "--vault-dir",
            str(vault_dir),
        ],
    )
    assert result.exit_code == 0
    vault_file = vault_dir / "data.lzvault"
    assert vault_file.exists()
    assert not (out_dir / "ledgerize.db").exists()
