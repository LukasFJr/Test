# Ledgerize specification

This project normalizes heterogeneous bank statement CSV files into a unified schema. It supports loading declarative categorization rules in YAML and mapping account identifiers to logical names. Transactions are deduplicated using a stable hash and approximate matching on normalized descriptions. Data is stored in SQLite and can be exported to Parquet/CSV/JSONL. A Plotly-based offline report summarizes spending.

Main modules:
- `parsers`: bank specific CSV parsers and a generic parser.
- `normalize`: utilities to clean strings, parse dates and amounts.
- `rules`: evaluation of YAML rules and explanations.
- `dedupe`: generation of transaction ids and duplicate removal.
- `db`: SQLite persistence and exports.
- `report`: HTML report generation using Jinja2 templates.

## Security model

Ledgerize optionally stores sensitive datasets inside encrypted `.lzvault`
containers. AES‑256‑GCM protects the archives and keys are kept in the user's
system keyring. This mitigates risks when laptops are lost or when repositories
are shared publicly.

The design does **not** provide forward secrecy and decrypted data may briefly
exist on disk when reports are generated. No hardware security modules are
used.
