from pathlib import Path
import click
import pytest
from ledgerize.guard import ensure_clean_repo


def test_guard_detects(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / '.git').mkdir()
    data = repo / 'data'
    data.mkdir()
    (data / 'x.csv').write_text('a')
    with pytest.raises(click.ClickException):
        ensure_clean_repo(repo)
