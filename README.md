# Studio jakości i wizualizacji danych

Aplikacja desktopowa (Python 3 + Tkinter) do pracy ze zbiorem CSV: wczytanie, profil jakości, konfigurowalne czyszczenie ze śladem zmian, wykresy i eksport. Użytkownik widzi, **ile rekordów** zmieniła każda operacja, i może wrócić do danych surowych bez ponownego uruchamiania programu.

Projekt realizuje wymagania *Programowanie V — Projekt 2* (laboratoria 6–9).

## Wymagania

- Python 3.10+
- Tkinter (w standardowej instalacji CPythona na macOS/Windows; na Linuxie pakiet `python3-tk`)
- pakiety z `requirements.txt`: pandas, matplotlib, seaborn, pytest, numpy

## Instalacja i uruchomienie

```bash
cd Prog5
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

W GUI: **Wczytaj CSV** → zakładka **Profil** → **Czyszczenie** (duplikaty, braki, zakres, IQR) → **Wizualizacja** → zapis CSV / PNG / PDF / SVG z menu **Plik**.

Powtarzalny pipeline bez GUI (generuje `outputs/`):

```bash
python scripts/generate_reference_data.py
PYTHONPATH=. python scripts/build_demo_outputs.py
python -m pytest -q
```

## Zbiór referencyjny

`data/california_housing_dirty.csv` — zmodyfikowana, mniejsza wersja schematu California Housing z celowo wprowadzonymi problemami:

| Problem | Gdzie |
| --- | --- |
| Braki liczbowe | `total_bedrooms`, `median_income` |
| Braki tekstowe | `ocean_proximity` |
| Pełne duplikaty | 3 skopiowane wiersze |
| Poza zakresem | `longitude` (-10, 2.5), `median_income` (48, -3.2) |
| Outliery | bardzo wysokie `median_house_value` |
| Wartości błędne | tekst w `population` i `households` |

Aplikacja przyjmuje **dowolny poprawny CSV** (separator przecinek albo średnik).

## Obsługiwane funkcje

**Wczytywanie:** autodetekcja `,` / `;`, próby kodowań UTF-8, CP1250, Latin-1; komunikat zamiast awarii przy wadliwym wierszu lub złym kodowaniu; podgląd w tabeli.

**Profil:** liczba rekordów i kolumn, typy, statystyki opisowe, liczba i % braków, pełne duplikaty, liczba unikalnych wartości.

**Czyszczenie (nie rusza kopii `raw`):**

- usuwanie **pełnych** duplikatów;
- braki: usunięcie wierszy **albo** imputacja średnią / medianą / modą;
- wartości nienumeryczne w kolumnie liczbowej → NaN albo usunięcie wiersza;
- reguła zakresu (oznacz / przytnij / usuń) — **bez automatycznego usuwania**;
- outliery metodą **IQR** (oznacz / pozostaw / przytnij / usuń).

**Ślad zmian:** znacznik czasu, parametry, liczba wierszy przed/po, liczba rekordów dotkniętych operacją. **Reset** przywraca dane surowe.

**Wykresy:** histogram, punktowy, pudełkowy, słupkowy oraz macierz korelacji Pearsona. Typ kolumny jest walidowany. Podpis osi i tytuł są ustawiane automatycznie. Osadzenie w oknie przez `FigureCanvasTkAgg`.

**Eksport:** `cleaned.csv`, raport TXT, wykres PNG oraz PDF/SVG.

## Strategia jakości (uzasadnienie)

Obserwacja odstająca **nie jest automatycznie błędem**. W nieruchomościach skrajne `median_house_value` mogą oznaczać dzielnice premium, a nietypowa długość geograficzna — literówkę. Domyślna akcja w GUI to **oznaczenie** (`flag`): powstaje kolumna `{nazwa}_is_outlier` albo `{nazwa}_out_of_range`, a rekord zostaje w zbiorze. Usunięcie albo przycięcie wymaga świadomej decyzji.

Korelacja na wykresie punktowym i heatmapie to miara **zależności liniowej**, nie przyczynowości (np. dochód i wartość domu rosną razem, ale przyczyną mogą być inne czynniki).

## Dane testowe

| Plik | Oczekiwany wynik |
| --- | --- |
| `tests/fixtures/comma.csv` | 3 kolumny, separator `,` |
| `tests/fixtures/semicolon.csv` | 4 wiersze, separator `;` |
| `tests/fixtures/quality_issues.csv` | 1 brak w `wiek`, wynik 999 poza zakresem 0–20, pełny duplikat |
| `tests/fixtures/mixed_types.csv` | 1 wartość nienumeryczna w `x` |

Automatyczne testy: `pytest -q`. Test GUI: dymny test odświeżania kontrolek (`tests/test_gui_smoke.py`). Test ponownego odczytu eksportu: `test_session_from_csv_roundtrip`. Krótki raport: `tests/TEST_REPORT.md`.

## Architektura

- `studio/session.py` — stan sesji (`raw` / `current` / `audit_log`), bez GUI
- `studio/csv_io.py`, `profiling.py`, `cleaning.py`, `plots.py` — czyste funkcje
- `studio/gui.py` — Tkinter/ttk; trzyma referencję do `DataSession`
- `main.py` — punkt wejścia

Brak ukrytych zmiennych globalnych z danymi; operacje pracują na kopiach.

## Znane ograniczenia

- Podgląd w tabeli pokazuje pierwsze 80 wierszy (pełny zbiór jest w sesji).
- Wykrywanie separatora opiera się na próbce nagłówka; egzotyczne TSV trzeba zapisać jako CSV.
- Imputacja średnią/medianą wymaga kolumny sprowadzalnej do liczb.

## Autorzy i narzędzia

- Autor: studentka/student Programowania V
- Biblioteki: pandas, matplotlib, seaborn, Tkinter
- Dokumentacje: pandas `read_csv`, Pandas User Guide, Matplotlib Embed in Tk, Seaborn tutorial
- Asystent AI (Cursor) użyty do szkicu struktury GUI i testów; logika czyszczenia i uzasadnienie outlierów zostały dopasowane do instrukcji projektowej

## Historia pracy

Patrz `HISTORIA.md` (dziennik zmian równoważny commitom, gdy repozytorium Git jest dodawane później).
