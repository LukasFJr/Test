from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class Transaction(BaseModel):
    id: str
    account: str
    date: date
    amount: float
    currency: str
    description: str
    norm_desc: str
    category: str
    counterparty: Optional[str] = None
    type: Optional[str] = None
    balance: Optional[float] = None
    raw_source: Optional[str] = None
    raw_rownum: Optional[int] = None
    rule_id: Optional[str] = None
    created_at: Optional[str] = None
