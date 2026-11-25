from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ENCODINGS = ("utf-8", "utf-8-sig", "cp1250", "iso-8859-2", "latin-1")


@dataclass(frozen=True)
class LoadResult:
    frame: pd.DataFrame
    encoding: str
    separator: str
    path: Path
    skipped_bad_lines: int = 0


def _detect_separator(sample: str) -> str:
    comma = sample.count(",")
    semicolon = sample.count(";")
    if semicolon > comma:
        return ";"
    return ","


def load_csv(path: Path, encoding: str | None = None) -> LoadResult:
    """Wczytaj CSV z obsługą przecinka/średnika i błędów kodowania."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {file_path}")
    if file_path.stat().st_size == 0:
        raise ValueError("Plik jest pusty. Wybierz CSV z nagłówkiem i danymi.")

    encodings = (encoding,) if encoding else ENCODINGS
    last_decode_error: Exception | None = None

    for enc in encodings:
        try:
            raw_text = file_path.read_text(encoding=enc)
        except UnicodeDecodeError as exc:
            last_decode_error = exc
            continue

        sample = "\n".join(raw_text.splitlines()[:5])
        separator = _detect_separator(sample)
        skipped = 0

        try:
            frame = pd.read_csv(
                file_path,
                sep=separator,
                encoding=enc,
                engine="python",
                on_bad_lines="error",
            )
        except pd.errors.ParserError as exc:
            # Kontrolowany odczyt wadliwych wierszy: pomiń i zaraportuj.
            skipped_holder: list[int] = []

            def _skip_bad(bad_line: list[str]) -> None:
                skipped_holder.append(1)
                return None

            try:
                frame = pd.read_csv(
                    file_path,
                    sep=separator,
                    encoding=enc,
                    engine="python",
                    on_bad_lines=_skip_bad,
                )
                skipped = len(skipped_holder)
            except (TypeError, ValueError):
                raise ValueError(
                    "Wadliwy wiersz uniemożliwia odczyt. "
                    "Sprawdź, czy każdy wiersz ma tę samą liczbę kolumn i separator "
                    "(przecinek albo średnik)."
                ) from exc

            if skipped == 0:
                raise ValueError(
                    f"Nie udało się sparsować CSV ({exc}). "
                    "Sprawdź separator, cudzysłowy i liczbę kolumn."
                ) from exc

        if frame.empty:
            raise ValueError("Plik nie zawiera rekordów po odczycie nagłówka.")

        if frame.shape[1] == 1 and separator == "," and ";" in str(frame.columns[0]):
            frame = pd.read_csv(
                file_path,
                sep=";",
                encoding=enc,
                engine="python",
                on_bad_lines="skip",
            )
            separator = ";"

        return LoadResult(
            frame=frame,
            encoding=enc,
            separator=separator,
            path=file_path,
            skipped_bad_lines=skipped,
        )

    hint = f" Ostatni błąd: {last_decode_error}" if last_decode_error else ""
    raise ValueError(
        "Nie udało się odczytać kodowania pliku. Zapisz CSV w UTF-8 i spróbuj ponownie."
        + hint
    )


def save_csv(frame: pd.DataFrame, path: Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        frame.to_csv(target, index=False, encoding="utf-8")
    except OSError as exc:
        raise OSError(
            f"Nie udało się zapisać CSV do {target}. "
            "Sprawdź uprawnienia i czy plik nie jest otwarty w innym programie."
        ) from exc
    return target
