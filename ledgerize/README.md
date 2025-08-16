## 🧾 Ledgerize

Ledgerize is a CLI tool that helps you consolidate bank statement CSVs from multiple providers into a single, normalized ledger. It can:

- 🧹 Clean and deduplicate transactions
- 🏷️ Categorize entries based on user‑defined YAML rules
- 💾 Store data in SQLite
- 📊 Export reports, including a fully offline HTML dashboard

## 🛠️ Installation

Prerequisites:

- [Python](https://www.python.org/) 3.11+
- [Poetry](https://python-poetry.org/) for dependency management

Steps:

```bash
git clone <repo-url>
cd ledgerize
poetry install
```

## 🚀 Quick start

Preview, import and report on transactions using the sample data:

```bash
# Peek at the first 5 transactions from an N26 export
poetry run ledgerize preview samples/n26_2025-06.csv \
    --rules samples/rules.yml --accounts samples/accounts.yml --n 5

# Import all sample statements into an SQLite database
poetry run ledgerize import samples \
    --rules samples/rules.yml --accounts samples/accounts.yml \
    --since 2024-01-01 --out data/

# Generate a 12‑month HTML report from the database
poetry run ledgerize report --db data/ledgerize.db \
    --html report/index.html --months 12
```

`rules.yml` and `accounts.yml` are YAML configuration files that control how transactions are categorized and which accounts they belong to. Consult the examples in the `samples/` directory to craft your own.

## ✅ Development checks

Run formatting, type checking and tests before submitting changes:

```bash
poetry run ruff src tests
poetry run black --check src tests
poetry run mypy src
poetry run pytest
```
