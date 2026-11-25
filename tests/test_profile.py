import pandas as pd

from studio.profiling import build_profile
from studio.session import DataSession


def test_profile_counts_missing_duplicates_unique() -> None:
    frame = pd.DataFrame(
        {
            "a": [1, 1, None, 2],
            "b": ["x", "z", "y", "y"],
        }
    )
    # pełny duplikat wiersza 0
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    profile = build_profile(frame)
    assert profile.n_rows == 5
    assert profile.n_columns == 2
    assert profile.duplicate_rows == 1
    missing_a = int(profile.column_table.loc[profile.column_table["kolumna"] == "a", "braki"].iloc[0])
    assert missing_a == 1


def test_unrelated_column_not_changed_by_income_range() -> None:
    frame = pd.DataFrame({"income": [1, 50, 2], "keep": [10, 20, 30]})
    session = DataSession(frame)
    original_keep = session.current["keep"].tolist()
    session.apply_range("income", 0, 10, action="flag")
    assert session.current["keep"].tolist() == original_keep
