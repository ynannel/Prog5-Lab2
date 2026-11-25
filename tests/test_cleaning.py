import pandas as pd
import pytest

from studio.session import DataSession


def _session() -> DataSession:
    frame = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 4],
            "wiek": [20.0, 21.0, None, 19.0, 19.0],
            "wynik": [10.0, 12.0, 11.0, 999.0, 999.0],
            "grupa": ["A", "A", "B", "B", "B"],
        }
    )
    return DataSession(frame)


def test_drop_exact_duplicates_only() -> None:
    session = _session()
    removed = session.drop_exact_duplicates()
    assert removed == 1
    assert len(session.current) == 4
    assert len(session.raw) == 5


def test_missing_drop_and_impute() -> None:
    drop_session = _session()
    affected = drop_session.fill_or_drop_missing(["wiek"], "drop_rows")
    assert affected == 1
    assert drop_session.current["wiek"].isna().sum() == 0
    assert len(drop_session.current) == 4

    impute = _session()
    impute.drop_exact_duplicates()
    affected = impute.fill_or_drop_missing(["wiek"], "median")
    assert affected == 1
    assert impute.current["wiek"].isna().sum() == 0
    assert impute.current.loc[impute.current["id"] == 3, "wiek"].notna().all()


def test_range_rule_flags_without_deleting() -> None:
    session = _session()
    affected = session.apply_range("wynik", 0, 20, action="flag")
    assert affected == 2
    assert len(session.current) == len(session.raw)
    assert "wynik_out_of_range" in session.current.columns
    assert int(session.current["wynik_out_of_range"].sum()) == 2


def test_range_drop_is_explicit() -> None:
    session = _session()
    affected = session.apply_range("wynik", 0, 20, action="drop")
    assert affected == 2
    assert len(session.current) == 3


def test_outliers_iqr_flag() -> None:
    frame = pd.DataFrame({"x": [10, 11, 12, 10, 11, 12, 10, 11, 12, 500]})
    session = DataSession(frame)
    affected = session.apply_outliers("x", factor=1.5, action="flag")
    assert affected == 1
    assert session.current["x_is_outlier"].sum() == 1
    assert len(session.current) == 10


def test_invalid_range_parameters() -> None:
    session = _session()
    with pytest.raises(ValueError, match="Minimum"):
        session.apply_range("wynik", 20, 0, action="flag")


def test_reset_restores_raw() -> None:
    session = _session()
    session.drop_exact_duplicates()
    session.fill_or_drop_missing(["wiek"], "drop_rows")
    session.reset()
    pd.testing.assert_frame_equal(session.current, session.raw)
    assert any("Przywrócono" in entry.operation for entry in session.audit_log)


def test_invalid_numeric() -> None:
    session = DataSession(pd.DataFrame({"x": [1, "oops", 3], "y": [1, 2, 3]}))
    affected = session.coerce_invalid_numeric("x", drop=False)
    assert affected == 1
    assert pd.isna(session.current.loc[1, "x"])
