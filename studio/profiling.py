from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DataProfile:
    n_rows: int
    n_columns: int
    duplicate_rows: int
    column_table: pd.DataFrame
    numeric_stats: pd.DataFrame
    categorical_stats: pd.DataFrame

    def summary_text(self) -> str:
        lines = [
            f"Rekordy: {self.n_rows}",
            f"Kolumny: {self.n_columns}",
            f"Pełne duplikaty (nadmiarowe kopie): {self.duplicate_rows}",
        ]
        return "\n".join(lines)


def build_profile(frame: pd.DataFrame) -> DataProfile:
    missing = frame.isna().sum()
    missing_pct = frame.isna().mean().mul(100).round(2)
    table = pd.DataFrame(
        {
            "kolumna": frame.columns,
            "typ": frame.dtypes.astype(str).values,
            "braki": missing.values,
            "braki_%": missing_pct.values,
            "unikalne": frame.nunique(dropna=True).values,
        }
    )
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        numeric_stats = pd.DataFrame()
    else:
        numeric_stats = numeric.describe().T.round(3)

    categorical = frame.select_dtypes(exclude="number")
    if categorical.empty:
        categorical_stats = pd.DataFrame()
    else:
        categorical_stats = pd.DataFrame(
            {
                "unikalne": categorical.nunique(dropna=True),
                "najczęstsza": [
                    (categorical[col].mode(dropna=True).iloc[0] if not categorical[col].mode(dropna=True).empty else "")
                    for col in categorical.columns
                ],
            }
        )

    extra_duplicates = int(frame.duplicated(keep="first").sum())
    return DataProfile(
        n_rows=len(frame),
        n_columns=frame.shape[1],
        duplicate_rows=extra_duplicates,
        column_table=table,
        numeric_stats=numeric_stats,
        categorical_stats=categorical_stats,
    )
