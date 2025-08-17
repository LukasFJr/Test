from pathlib import Path
import os
from ledgerize import vault


def test_vault_roundtrip(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "a.txt").write_text("hello")
    key = os.urandom(32)
    vf = tmp_path / "test.lzvault"
    vault.lock(data, vf, key)
    out = tmp_path / "out"
    vault.unlock(vf, out, key)
    assert (out / "a.txt").read_text() == "hello"
