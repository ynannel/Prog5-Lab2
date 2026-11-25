# Historia pracy

Dziennik równoważny historii Git (punktacja: proces).

## 2026-11-25 — rdzeń sesji (zakres Lab. 6)

- Model `DataSession` z kopią `raw` / `current` i dziennikiem `AuditEntry`.
- Wczytywanie CSV (przecinek i średnik, kodowanie, wadliwy wiersz).
- Profil: rozmiar, typy, braki, duplikaty, unikalność, `describe`.
- Pipeline czyszczenia: duplikaty, dwie strategie braków, zakres, IQR, reset.
- Zbiór `california_housing_dirty.csv` z kontrolowanymi defektami.

## 2026-11-25 — wykresy (zakres Lab. 7)

- Histogram, scatter, box, bar (Seaborn + Matplotlib `Figure`).
- Macierz korelacji i podpis, że korelacja ≠ przyczynowość.
- Walidacja typu kolumny (w tym kolumna stała).

## 2026-11-25 — GUI (zakres Lab. 8)

- Tkinter/ttk, zakładki Dane / Profil / Czyszczenie / Wizualizacja / Ślad.
- Dynamiczne listy kolumn po zmianie zbioru.
- Błędny plik pokazuje dialog i nie zamyka aplikacji.

## 2026-11-25 — eksport, testy, dokumentacja (zakres Lab. 9)

- Osadzenie `FigureCanvasTkAgg`, usuwanie poprzedniego canvas.
- Eksport CSV, PNG, PDF, SVG oraz raportu zmian.
- Testy pytest na małych ramkach + dymny test GUI.
- `outputs/` z przykładowym `cleaned.csv` i wykresami.
