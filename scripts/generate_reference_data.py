"""Generuje zmodyfikowany zbiór w stylu California Housing oraz małe pliki testowe."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
DATA = ROOT / "data"
FIXTURES = ROOT / "tests" / "fixtures"


def california_like(n: int = 420, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ocean = rng.choice(
        ["<1H OCEAN", "INLAND", "NEAR OCEAN", "NEAR BAY", "ISLAND"],
        size=n,
        p=[0.42, 0.32, 0.14, 0.11, 0.01],
    )
    longitude = rng.uniform(-124.3, -114.3, n)
    latitude = rng.uniform(32.5, 41.9, n)
    housing_median_age = rng.integers(1, 53, n)
    households = rng.integers(20, 1200, n)
    total_rooms = (households * rng.uniform(3.5, 7.5, n)).astype(int)
    total_bedrooms = (households * rng.uniform(0.8, 1.6, n)).astype(int)
    population = (households * rng.uniform(2.0, 4.2, n)).astype(int)
    median_income = rng.uniform(0.7, 12.5, n).round(4)
    median_house_value = (
        40_000
        + median_income * 28_000
        + np.where(ocean == "INLAND", -25_000, 15_000)
        + rng.normal(0, 18_000, n)
    ).clip(15_000, 500_001).round(0)

    frame = pd.DataFrame(
        {
            "longitude": longitude.round(4),
            "latitude": latitude.round(4),
            "housing_median_age": housing_median_age,
            "total_rooms": total_rooms,
            "total_bedrooms": total_bedrooms,
            "population": population,
            "households": households,
            "median_income": median_income,
            "median_house_value": median_house_value,
            "ocean_proximity": ocean,
        }
    )

    # Braki (liczbowe i tekstowe)
    frame.loc[frame.sample(28, random_state=1).index, "total_bedrooms"] = np.nan
    frame.loc[frame.sample(12, random_state=2).index, "median_income"] = np.nan
    frame.loc[frame.sample(8, random_state=3).index, "ocean_proximity"] = np.nan

    # Duplikaty pełne
    dup = frame.iloc[[10, 25, 40]].copy()
    frame = pd.concat([frame, dup], ignore_index=True)

    # Wartości poza zakresem (longitude Kalifornii, income)
    frame.loc[5, "longitude"] = -10.0
    frame.loc[6, "longitude"] = 2.5
    frame.loc[7, "median_income"] = 48.0
    frame.loc[8, "median_income"] = -3.2

    # Outliery IQR na median_house_value
    frame.loc[15, "median_house_value"] = 980_000
    frame.loc[16, "median_house_value"] = 1_200_000

    # Wartości błędne (tekst w kolumnie liczbowej)
    frame["population"] = frame["population"].astype(object)
    frame["households"] = frame["households"].astype(object)
    frame.loc[20, "population"] = "unknown"
    frame.loc[21, "households"] = "???"

    return frame


def write_all() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    FIXTURES.mkdir(parents=True, exist_ok=True)

    reference = california_like()
    reference.to_csv(DATA / "california_housing_dirty.csv", index=False)

    comma = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "wartosc": [10.5, 20.0, 30.25],
            "kategoria": ["a", "b", "a"],
        }
    )
    comma.to_csv(FIXTURES / "comma.csv", index=False)

    semicolon = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "miasto": ["Gdańsk", "Kraków", "Warszawa", "Poznań"],
            "temperatura": [12.1, 14.0, 11.5, 13.2],
        }
    )
    semicolon.to_csv(FIXTURES / "semicolon.csv", index=False, sep=";")

    issues = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 5],
            "wiek": [20, 21, np.nan, 19, 22, 22],
            "wynik": [10, 12, 11, 999, 13, 13],
            "grupa": ["A", "A", "B", "B", "A", "A"],
        }
    )
    # pełny duplikat ostatniego wiersza już jest (id 5 powtórzone z tymi samymi polami)
    issues.to_csv(FIXTURES / "quality_issues.csv", index=False)

    bad_numeric = pd.DataFrame({"x": [1, 2, "oops", 4], "y": [5, 6, 7, 8]})
    bad_numeric.to_csv(FIXTURES / "mixed_types.csv", index=False)

    print("Zapisano zbiory referencyjne i testowe.")


if __name__ == "__main__":
    write_all()
