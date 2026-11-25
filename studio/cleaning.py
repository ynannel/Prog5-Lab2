from __future__ import annotations

from typing import Literal

import pandas as pd

MissingStrategy = Literal["drop_rows", "mean", "median", "mode"]
OutlierAction = Literal["flag", "drop", "clip", "keep"]
RangeAction = Literal["flag", "drop", "clip"]


def numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        raise ValueError(f"Brak kolumny '{column}'. Wybierz kolumnę z listy.")
    return pd.to_numeric(frame[column], errors="coerce")


def iqr_mask(frame: pd.DataFrame, column: str, factor: float = 1.5) -> pd.Series:
    values = numeric_series(frame, column)
    q1, q3 = values.quantile([0.25, 0.75])
    iqr = q3 - q1
    if pd.isna(iqr) or iqr == 0:
        return pd.Series(False, index=frame.index)
    return (values < q1 - factor * iqr) | (values > q3 + factor * iqr)


def range_mask(frame: pd.DataFrame, column: str, minimum: float, maximum: float) -> pd.Series:
    if minimum > maximum:
        raise ValueError("Minimum nie może być większe od maksimum. Popraw zakres.")
    values = numeric_series(frame, column)
    known = values.notna()
    return known & ((values < minimum) | (values > maximum))


def drop_exact_duplicates(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(frame)
    cleaned = frame.drop_duplicates(keep="first").copy()
    return cleaned, before - len(cleaned)


def handle_missing(
    frame: pd.DataFrame,
    columns: list[str],
    strategy: MissingStrategy,
) -> tuple[pd.DataFrame, int]:
    missing = frame[columns].isna().any(axis=1)
    affected = int(missing.sum())
    if affected == 0:
        return frame.copy(), 0

    result = frame.copy()
    if strategy == "drop_rows":
        return result.loc[~missing].copy(), affected

    for column in columns:
        if strategy in {"mean", "median"}:
            values = pd.to_numeric(result[column], errors="coerce")
            fill_value = values.mean() if strategy == "mean" else values.median()
            if pd.isna(fill_value):
                raise ValueError(
                    f"Kolumna '{column}' nie ma wartości liczbowych do imputacji. "
                    "Wybierz inną kolumnę albo strategię 'moda' / usunięcie wierszy."
                )
            result[column] = values.fillna(fill_value)
        elif strategy == "mode":
            mode = result[column].mode(dropna=True)
            if mode.empty:
                raise ValueError(
                    f"Kolumna '{column}' nie ma wartości do imputacji modą. "
                    "Usuń wiersze z brakami albo uzupełnij dane ręcznie."
                )
            result[column] = result[column].fillna(mode.iloc[0])
        else:
            raise ValueError("Nieznana strategia braków. Wybierz usunięcie, średnią, medianę albo modę.")
    return result, affected


def handle_invalid_numeric(frame: pd.DataFrame, column: str, drop: bool) -> tuple[pd.DataFrame, int]:
    if column not in frame.columns:
        raise ValueError(f"Brak kolumny '{column}'.")
    original = frame[column]
    coerced = pd.to_numeric(original, errors="coerce")
    invalid = original.notna() & coerced.isna()
    affected = int(invalid.sum())
    result = frame.copy()
    if drop:
        result = result.loc[~invalid].copy()
    else:
        result[column] = coerced
    return result, affected


def apply_range_rule(
    frame: pd.DataFrame,
    column: str,
    minimum: float,
    maximum: float,
    action: RangeAction,
) -> tuple[pd.DataFrame, int]:
    mask = range_mask(frame, column, minimum, maximum)
    affected = int(mask.sum())
    result = frame.copy()
    flag_col = f"{column}_out_of_range"
    if action == "flag":
        result[flag_col] = mask
    elif action == "drop":
        result = result.loc[~mask].copy()
        if flag_col in result.columns:
            result = result.drop(columns=[flag_col])
    elif action == "clip":
        values = numeric_series(result, column)
        result[column] = values.clip(lower=minimum, upper=maximum)
    else:
        raise ValueError("Nieznana akcja zakresu. Wybierz oznaczenie, usunięcie albo przycięcie.")
    return result, affected


def apply_outliers(
    frame: pd.DataFrame,
    column: str,
    factor: float,
    action: OutlierAction,
) -> tuple[pd.DataFrame, int]:
    if factor <= 0:
        raise ValueError("Współczynnik IQR musi być dodatni (typowo 1.5).")
    mask = iqr_mask(frame, column, factor=factor)
    affected = int(mask.sum())
    result = frame.copy()
    flag_col = f"{column}_is_outlier"
    if action == "keep":
        return result, affected
    if action == "flag":
        result[flag_col] = mask
    elif action == "drop":
        result = result.loc[~mask].copy()
    elif action == "clip":
        values = numeric_series(result, column)
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - factor * iqr, q3 + factor * iqr
        result[column] = values.clip(lower=lower, upper=upper)
    else:
        raise ValueError("Nieznana akcja outlierów. Wybierz oznaczenie, usunięcie, przycięcie albo pozostawienie.")
    return result, affected
