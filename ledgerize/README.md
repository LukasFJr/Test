# Ledgerize

Ledgerize is a CLI tool to aggregate bank statement CSV files from multiple banks, normalize them into a unified schema, categorize transactions using YAML rules, deduplicate entries, store them in SQLite and export various formats. It can also generate an offline HTML report.

## Installation

```bash
poetry install
```

## Quick start

```
poetry run ledgerize preview samples/n26_2025-06.csv --rules samples/rules.yml --accounts samples/accounts.yml --n 5
poetry run ledgerize import samples --rules samples/rules.yml --accounts samples/accounts.yml --since 2024-01-01 --out data/
poetry run ledgerize report --db data/ledgerize.db --html report/index.html --months 12
```

Rules and accounts files are YAML documents. See `samples/rules.yml` and `samples/accounts.yml` for examples.
