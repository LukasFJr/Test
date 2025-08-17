from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import pandas as pd

from .config import load_accounts, load_rules
from .db import Database
from .guard import ensure_clean_repo
from .logging import configure_logging
from .parsers import parse_file, preview_file
from .report import build_report
from .rules import apply_rules, explain_transaction
from . import vault


@click.group()
@click.option("--verbose", is_flag=True, help="Enable debug logging")
@click.option("--i-know-what-im-doing", is_flag=True, help="Bypass safety checks")
def main(verbose: bool = False, i_know_what_im_doing: bool = False) -> None:
    """Ledgerize CLI."""
    configure_logging(debug=verbose)
    ensure_clean_repo(Path.cwd(), override=i_know_what_im_doing)


@main.command(name="import")
@click.argument("input_dir", type=click.Path(path_type=Path))
@click.option("--rules", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--accounts", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--since", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option("--out", type=click.Path(path_type=Path), required=True)
@click.option("--currency", default="EUR")
@click.option("--merge", is_flag=True, help="Merge with existing database if present")
@click.option("--secure", is_flag=True, help="Encrypt output into a vault")
@click.option("--vault-dir", type=click.Path(path_type=Path))
def import_(
    input_dir: Path,
    rules: Path,
    accounts: Path,
    since: Optional[pd.Timestamp],
    out: Path,
    currency: str,
    merge: bool,
    secure: bool,
    vault_dir: Optional[Path],
) -> None:
    """Import CSV files into a SQLite database."""
    out.mkdir(parents=True, exist_ok=True)
    rule_cfg = load_rules(rules)
    acc_cfg = load_accounts(accounts)
    db = Database(out / "ledgerize.db", merge=merge)
    txns = []
    for path in input_dir.rglob("*.csv"):
        df = parse_file(path, acc_cfg, currency=currency)
        if since is not None:
            df = df[df["date"] >= since.date()]
        df = apply_rules(df, rule_cfg)
        txns.append(df)
    if txns:
        all_df = pd.concat(txns, ignore_index=True)
        db.ingest_dataframe(all_df)
        db.export(all_df, out)
        log_path = out / "import_log.json"
        log_path.write_text(json.dumps({"rows": len(all_df)}))
        if secure:
            vdir = vault_dir or (out.parent / "vault")
            vdir.mkdir(parents=True, exist_ok=True)
            vault_file = vdir / f"{out.name}.lzvault"
            vault.lock(out, vault_file)
            for p in out.rglob("*"):
                if p.is_file():
                    p.unlink()


@main.command()
@click.argument("csv_file", type=click.Path(exists=True, path_type=Path))
@click.option("--rules", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--accounts", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--n", default=20)
def preview(csv_file: Path, rules: Path, accounts: Path, n: int) -> None:
    """Preview the first N normalized rows of a CSV file."""
    rule_cfg = load_rules(rules)
    acc_cfg = load_accounts(accounts)
    df = preview_file(csv_file, acc_cfg, n)
    df = apply_rules(df, rule_cfg)
    click.echo(df.head(n).to_string())


@main.command()
@click.option("--db", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--html", type=click.Path(path_type=Path), required=True)
@click.option("--months", default=12)
def report(db: Path, html: Path, months: int) -> None:
    """Generate an offline HTML report."""
    database = Database(db)
    df = database.read_transactions(months)
    build_report(df, html)


@main.command()
@click.option("--db", type=click.Path(exists=True, path_type=Path), required=True)
@click.argument("query")
def explain(db: Path, query: str) -> None:
    """Explain the rule applied to the transaction matching query."""
    database = Database(db)
    tx = database.find_transaction(query)
    if tx is None:
        click.echo("Transaction not found")
        return
    rule = explain_transaction(tx)
    click.echo(json.dumps({"transaction": tx, "rule": rule}, default=str, indent=2))


@main.group()
def vault_cmd() -> None:
    """Vault operations."""


@vault_cmd.command(name="init")
def vault_init() -> None:
    vault.init_vault()
    click.echo("vault initialized")


@vault_cmd.command(name="lock")
@click.argument("data_dir", type=click.Path(exists=True, path_type=Path))
@click.argument("vault_file", type=click.Path(path_type=Path))
def vault_lock(data_dir: Path, vault_file: Path) -> None:
    """Encrypt a data directory into a vault file."""
    vault.lock(data_dir, vault_file)


@vault_cmd.command(name="unlock")
@click.argument("vault_file", type=click.Path(exists=True, path_type=Path))
@click.argument("out_dir", type=click.Path(path_type=Path))
def vault_unlock(vault_file: Path, out_dir: Path) -> None:
    """Decrypt a vault file into OUT_DIR."""
    vault.unlock(vault_file, out_dir)
