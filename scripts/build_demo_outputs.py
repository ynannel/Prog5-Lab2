"""Powtarzalny pipeline: profil → czyszczenie → cleaned.csv, raport i wykresy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")

from studio.plots import bar_figure, boxplot_figure, histogram_figure, save_figure, scatter_figure
from studio.session import DataSession
SRC = ROOT / "data" / "california_housing_dirty.csv"
OUT = ROOT / "outputs"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    session = DataSession.from_csv(SRC)

    session.drop_exact_duplicates()
    session.coerce_invalid_numeric("population", drop=False)
    session.coerce_invalid_numeric("households", drop=False)
    session.fill_or_drop_missing(["total_bedrooms"], "median")
    session.fill_or_drop_missing(["median_income"], "median")
    session.fill_or_drop_missing(["ocean_proximity"], "mode")
    session.fill_or_drop_missing(["population", "households"], "median")
    session.apply_range("median_income", 0.0, 15.0, action="flag")
    session.apply_range("longitude", -125.0, -114.0, action="flag")
    session.apply_outliers("median_house_value", factor=1.5, action="flag")

    session.export_cleaned(OUT / "cleaned.csv")
    session.export_audit(OUT / "raport_zmian.txt")

    frame = session.current
    save_figure(histogram_figure(frame, "median_house_value"), str(OUT / "histogram_median_house_value.png"))
    save_figure(
        scatter_figure(frame, "median_income", "median_house_value", hue="ocean_proximity"),
        str(OUT / "scatter_income_value.png"),
    )
    save_figure(
        scatter_figure(frame, "median_income", "median_house_value", hue="ocean_proximity"),
        str(OUT / "scatter_income_value.pdf"),
    )
    save_figure(boxplot_figure(frame, "median_house_value", by="ocean_proximity"), str(OUT / "box_value_by_ocean.svg"))
    save_figure(bar_figure(frame, "ocean_proximity"), str(OUT / "bar_ocean_proximity.png"))
    print("Zapisano wyniki w", OUT)


if __name__ == "__main__":
    main()
