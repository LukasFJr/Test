from pathlib import Path

import pandas as pd
from click.testing import CliRunner

from ledgerize.cli import main
from ledgerize.dedupe import dedupe

BASE = Path(__file__).resolve().parent.parent


def test_preview(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "preview",
            str(BASE / "samples/n26_2025-06.csv"),
            "--rules",
            str(BASE / "samples/rules.yml"),
            "--accounts",
            str(BASE / "samples/accounts.yml"),
            "--n",
            "2",
        ],
    )
    assert "CARREFOUR" in result.output


def test_import_report_explain(tmp_path: Path) -> None:
    runner = CliRunner()
    out_dir = tmp_path / "data"
    result = runner.invoke(
        main,
        [
            "import",
            str(BASE / "samples"),
            "--rules",
            str(BASE / "samples/rules.yml"),
            "--accounts",
            str(BASE / "samples/accounts.yml"),
            "--since",
            "2024-01-01",
            "--out",
            str(out_dir),
        ],
    )
    assert result.exit_code == 0
    db = out_dir / "ledgerize.db"
    assert db.exists()
    report_file = tmp_path / "report" / "index.html"
    result = runner.invoke(
        main, ["report", "--db", str(db), "--html", str(report_file)]
    )
    assert result.exit_code == 0
    assert report_file.exists()
    result = runner.invoke(main, ["explain", "--db", str(db), "CARREFOUR"])
    assert "groceries" in result.output


def test_dedupe() -> None:
    df = pd.DataFrame(
        {
            "id": ["a", "a"],
            "account": ["A", "A"],
            "date": ["2024-01-01", "2024-01-01"],
            "amount": [1.0, 1.0],
            "currency": ["EUR", "EUR"],
            "description": ["foo", "foo"],
            "norm_desc": ["FOO", "FOO"],
            "category": ["X", "X"],
        }
    )
    deduped = dedupe(df)
    assert len(deduped) == 1
