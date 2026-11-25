from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from studio.audit import AuditEntry, now_stamp
from studio.cleaning import (
    MissingStrategy,
    OutlierAction,
    RangeAction,
    apply_outliers,
    apply_range_rule,
    drop_exact_duplicates,
    handle_invalid_numeric,
    handle_missing,
    iqr_mask,
)
from studio.csv_io import LoadResult, load_csv, save_csv
from studio.profiling import DataProfile, build_profile


@dataclass
class DataSession:
    raw: pd.DataFrame
    current: pd.DataFrame = field(init=False)
    audit_log: list[AuditEntry] = field(default_factory=list)
    source: LoadResult | None = None

    def __post_init__(self) -> None:
        self.current = self.raw.copy(deep=True)

    @classmethod
    def from_csv(cls, path: Path, encoding: str | None = None) -> "DataSession":
        loaded = load_csv(Path(path), encoding=encoding)
        session = cls(loaded.frame)
        session.source = loaded
        note = f"kodowanie={loaded.encoding}, separator={loaded.separator!r}"
        if loaded.skipped_bad_lines:
            note += f", pominięto wadliwych wierszy={loaded.skipped_bad_lines}"
        session._record(
            "Wczytano CSV",
            affected=len(loaded.frame),
            rows_before=0,
            parameters={"ścieżka": str(path)},
            note=note,
        )
        return session

    def profile(self) -> DataProfile:
        return build_profile(self.current)

    def reset(self) -> None:
        before = len(self.current)
        self.current = self.raw.copy(deep=True)
        self._record("Przywrócono dane surowe", affected=len(self.current), rows_before=before)

    def drop_exact_duplicates(self) -> int:
        before = len(self.current)
        self.current, removed = drop_exact_duplicates(self.current)
        self._record("Usunięto pełne duplikaty", affected=removed, rows_before=before)
        return removed

    def fill_or_drop_missing(self, columns: list[str], strategy: MissingStrategy) -> int:
        if not columns:
            raise ValueError("Wskaż co najmniej jedną kolumnę z brakami.")
        missing = [col for col in columns if col not in self.current.columns]
        if missing:
            raise ValueError(f"Nieznane kolumny: {', '.join(missing)}")
        before = len(self.current)
        self.current, affected = handle_missing(self.current, columns, strategy)
        self._record(
            "Obsłużono braki",
            affected=affected,
            rows_before=before,
            parameters={"kolumny": columns, "strategia": strategy},
        )
        return affected

    def coerce_invalid_numeric(self, column: str, drop: bool = False) -> int:
        before = len(self.current)
        self.current, affected = handle_invalid_numeric(self.current, column, drop=drop)
        action = "usunięto wiersze" if drop else "zamieniono na NaN / liczbę"
        self._record(
            "Obsłużono wartości nienumeryczne",
            affected=affected,
            rows_before=before,
            parameters={"kolumna": column, "akcja": action},
        )
        return affected

    def apply_range(
        self,
        column: str,
        minimum: float,
        maximum: float,
        action: RangeAction,
    ) -> int:
        before = len(self.current)
        self.current, affected = apply_range_rule(self.current, column, minimum, maximum, action)
        self._record(
            "Reguła zakresu",
            affected=affected,
            rows_before=before,
            parameters={
                "kolumna": column,
                "min": minimum,
                "max": maximum,
                "akcja": action,
            },
            note="Wartość poza zakresem nie jest usuwana, dopóki użytkownik nie wybierze akcji.",
        )
        return affected

    def apply_outliers(self, column: str, factor: float = 1.5, action: OutlierAction = "flag") -> int:
        before = len(self.current)
        self.current, affected = apply_outliers(self.current, column, factor, action)
        self._record(
            "Outliery IQR",
            affected=affected,
            rows_before=before,
            parameters={"kolumna": column, "współczynnik": factor, "akcja": action},
            note=(
                "Obserwacja odstająca nie zawsze jest błędem "
                "(np. drogie nieruchomości albo rzadkie lokalizacje)."
            ),
        )
        return affected

    def iqr_mask(self, column: str, factor: float = 1.5) -> pd.Series:
        return iqr_mask(self.current, column, factor)

    def export_cleaned(self, path: Path) -> Path:
        return save_csv(self.current, Path(path))

    def export_audit(self, path: Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = ["Raport śladu zmian — Studio jakości danych", ""]
        lines.extend(entry.as_line() for entry in self.audit_log)
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return target

    def _record(
        self,
        operation: str,
        affected: int,
        rows_before: int,
        parameters: dict[str, Any] | None = None,
        note: str = "",
    ) -> None:
        self.audit_log.append(
            AuditEntry(
                timestamp=now_stamp(),
                operation=operation,
                parameters=parameters or {},
                rows_before=rows_before,
                rows_after=len(self.current),
                affected=affected,
                note=note,
            )
        )
