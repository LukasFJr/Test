from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy import create_engine, text

from .dedupe import dedupe


class Database:
    def __init__(self, path: Path, merge: bool = True) -> None:
        self.path = path
        self.engine = create_engine(f"sqlite:///{path}")
        if not merge and path.exists():
            path.unlink()

    def ingest_dataframe(self, df: pd.DataFrame) -> None:
        df = dedupe(df)
        df.to_sql("transactions", self.engine, if_exists="append", index=False)

    def export(self, df: pd.DataFrame, out: Path) -> None:
        try:
            df.to_parquet(out / "normalized.parquet", index=False)
        except Exception:
            pass
        df.to_csv(out / "normalized.csv", index=False)
        df.to_json(out / "normalized.jsonl", orient="records", lines=True)

    def read_transactions(self, months: int) -> pd.DataFrame:
        query = "SELECT * FROM transactions ORDER BY date DESC LIMIT 5000"
        return pd.read_sql_query(query, self.engine, parse_dates=["date"])

    def find_transaction(self, query_str: str) -> Optional[Dict[str, Any]]:
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT * FROM transactions WHERE id = :q OR description LIKE :like LIMIT 1"
                ),
                {"q": query_str, "like": f"%{query_str}%"},
            )
            row = result.mappings().first()
            return dict(row) if row else None
