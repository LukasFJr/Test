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

## 🔐 Vault security

Ledgerize can encrypt banking data into `.lzvault` files so nothing sensitive remains on disk.

### 1. Initialize a key

Run once per machine:

```bash
poetry run ledgerize vault init --label personal
```

This generates a 256‑bit master key and stores it in the system keyring under
`ledgerize`. If the keyring is unavailable, Ledgerize prompts for a passphrase
and derives the key with scrypt. The printed `vault_id` and `key_id` uniquely
identify the vault and the KDF parameters are written to
`.ledgerize/keys/<key_id>.json`.

### 2. Create a vault

**Secure import**

```bash
poetry run ledgerize import samples \
    --rules samples/rules.yml --accounts samples/accounts.yml \
    --out data/ --secure --vault-dir vault/
```

The import runs as normal, then `data/` is packaged, encrypted into
`vault/*.lzvault`, and all plaintext files (`.db`, `.parquet`, `.csv`, `.jsonl`)
are deleted.

**Lock an existing folder**

```bash
poetry run ledgerize vault lock --data data/ --out vault/bank.lzvault
```

### 3. Use a vault

Run reports or queries without extracting data yourself:

```bash
poetry run ledgerize report --from-vault vault/bank.lzvault --html report/index.html
poetry run ledgerize explain --from-vault vault/bank.lzvault "select * from transactions limit 5"
```

The vault is decrypted in a 0700 temporary directory that is wiped after the
command completes. To manually inspect files:

```bash
poetry run ledgerize vault unlock --vault vault/bank.lzvault --out .ledgerize/tmp-XXXXX
```

### 4. Rotate or share

Rotate the encryption key of an existing vault:

```bash
poetry run ledgerize vault rotate --vault vault/bank.lzvault [--keep-old]
```

To share your data, send only the `.lzvault` file. The recipient can unlock or
report from it and must either have the key stored in their keyring (same
`vault_id`) or know the passphrase you used.

### 5. Guard against plaintext

Ledgerize aborts if it detects unencrypted `data/*.db`, `*.csv`, `*.jsonl` inside
a Git repository. Install an optional pre-commit hook to block commits
containing those files:

```bash
poetry run ledgerize guard install-hook
```

## ✅ Development checks

Run formatting, type checking and tests before submitting changes:

```bash
poetry run ruff src tests
poetry run black --check src tests
poetry run mypy src
poetry run pytest
```
