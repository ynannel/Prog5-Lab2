from pathlib import Path

import pandas as pd
import pytest

from studio.csv_io import load_csv
from studio.session import DataSession

FIXTURES = Path(__file__).parent / "fixtures"


def test_comma_csv_has_expected_columns() -> None:
    loaded = load_csv(FIXTURES / "comma.csv")
    assert list(loaded.frame.columns) == ["id", "wartosc", "kategoria"]
    assert len(loaded.frame) == 3
    assert loaded.separator == ","


def test_semicolon_csv_has_expected_columns() -> None:
    loaded = load_csv(FIXTURES / "semicolon.csv")
    assert list(loaded.frame.columns) == ["id", "miasto", "temperatura"]
    assert len(loaded.frame) == 4
    assert loaded.separator == ";"


def test_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_csv(FIXTURES / "does_not_exist.csv")


def test_empty_file_raises(tmp_path: Path) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="pusty"):
        load_csv(empty)


def test_session_from_csv_roundtrip(tmp_path: Path) -> None:
    session = DataSession.from_csv(FIXTURES / "comma.csv")
    target = tmp_path / "out.csv"
    session.export_cleaned(target)
    again = pd.read_csv(target)
    pd.testing.assert_frame_equal(again, session.current.reset_index(drop=True))
