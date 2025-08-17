from __future__ import annotations

import base64
import io
import json
import os
import tarfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import keyring

SERVICE = "ledgerize"
KEY_NAME = "master_key"
MAGIC = b"LZV1"


def init_vault() -> str:
    """Generate and store a master key in the system keyring.

    Returns the base64 encoded key."""
    key = os.urandom(32)
    b64 = base64.b64encode(key).decode()
    keyring.set_password(SERVICE, KEY_NAME, b64)
    return b64


def _load_key() -> bytes:
    b64 = keyring.get_password(SERVICE, KEY_NAME)
    if not b64:
        raise RuntimeError("master key not initialized")
    return base64.b64decode(b64)


@dataclass
class Manifest:
    version: str
    created: str
    files: List[Dict[str, str]]
    nonce: str

    def to_json(self) -> bytes:
        return json.dumps(self.__dict__).encode()


def lock(data_dir: Path, vault_file: Path, key: Optional[bytes] = None) -> None:
    key = key or _load_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for path in data_dir.rglob("*"):
            if path.is_file():
                tar.add(path, arcname=path.relative_to(data_dir))
    payload = buf.getvalue()
    manifest = Manifest(
        version="1",
        created=datetime.utcnow().isoformat(),
        files=[{"path": str(p.relative_to(data_dir)), "size": p.stat().st_size}
               for p in data_dir.rglob("*") if p.is_file()],
        nonce=base64.b64encode(nonce).decode(),
    )
    aad = MAGIC + manifest.to_json()
    ct = aesgcm.encrypt(nonce, payload, aad)
    with open(vault_file, "wb") as f:
        f.write(MAGIC)
        m = manifest.to_json()
        f.write(len(m).to_bytes(4, "big"))
        f.write(m)
        f.write(nonce)
        f.write(ct)


def unlock(vault_file: Path, out_dir: Path, key: Optional[bytes] = None) -> None:
    key = key or _load_key()
    data = vault_file.read_bytes()
    if not data.startswith(MAGIC):
        raise ValueError("invalid vault file")
    idx = len(MAGIC)
    mlen = int.from_bytes(data[idx:idx + 4], "big")
    idx += 4
    mbytes = data[idx:idx + mlen]
    idx += mlen
    manifest = json.loads(mbytes)
    nonce = data[idx:idx + 12]
    idx += 12
    ct = data[idx:]
    aesgcm = AESGCM(key)
    payload = aesgcm.decrypt(nonce, ct, MAGIC + mbytes)
    out_dir.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO(payload)
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        tar.extractall(out_dir)
