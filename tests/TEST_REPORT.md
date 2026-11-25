# Raport testów

Data: 2025-11-25  
Polecenie: `python3 -m pytest -q`  
Wynik: **20 passed**

## Macierz z instrukcji

| Przypadek | Test / dowód | Rezultat |
| --- | --- | --- |
| CSV z przecinkiem i średnikiem | `test_csv_io.py` + `comma.csv`, `semicolon.csv` | OK — poprawna liczba kolumn |
| Braki liczbowe i tekstowe | `test_missing_drop_and_impute` | OK — drop i mediana, raport `affected` |
| Duplikaty | `test_drop_exact_duplicates_only` | OK — tylko pełne duplikaty |
| Wartość poza zakresem | `test_range_rule_flags_without_deleting` | OK — flaga, bez usuwania |
| Stała / nienumeryczna kolumna | `test_histogram_rejects_*` | OK — `ValueError` z komunikatem |
| Eksport CSV ponownie wczytywalny | `test_session_from_csv_roundtrip` | OK |
| GUI | `test_gui_smoke.py` | OK — odświeżenie list kolumn |
| PNG/PDF/SVG | `outputs/*.png`, `scatter_income_value.pdf`, `box_value_by_ocean.svg` | Pliki otwieralne |

## GUI / eksport (udokumentowane)

1. `python main.py`
2. Wczytaj `data/california_housing_dirty.csv`
3. Błędny plik (np. pusty) → dialog błędu, aplikacja zostaje.
4. Menu Plik → zapis CSV i wykresu PNG oraz PDF lub SVG.
