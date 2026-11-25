from __future__ import annotations

from typing import Literal

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

PlotKind = Literal["histogram", "scatter", "box", "bar", "correlation"]

NUMERIC_PLOTS = {"histogram", "scatter", "box", "correlation"}


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if pd.api.types.is_numeric_dtype(frame[col])]


def categorical_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if not pd.api.types.is_numeric_dtype(frame[col])]


def _numeric_data(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        raise ValueError(f"Brak kolumny '{column}'.")
    data = pd.to_numeric(frame[column], errors="coerce").dropna()
    if data.empty:
        raise ValueError(
            f"Kolumna '{column}' nie zawiera danych liczbowych. "
            "Wybierz kolumnę liczbową albo oczyść wartości tekstowe."
        )
    if data.nunique(dropna=True) <= 1:
        raise ValueError(
            f"Kolumna '{column}' jest stała — histogram/wykres rozrzutu nie ma sensu. "
            "Wybierz kolumnę o zróżnicowanych wartościach."
        )
    return data


def _new_figure() -> tuple[Figure, object]:
    sns.set_theme(style="whitegrid")
    fig = Figure(figsize=(7.2, 4.4), dpi=100)
    ax = fig.add_subplot()
    return fig, ax


def histogram_figure(frame: pd.DataFrame, column: str) -> Figure:
    data = _numeric_data(frame, column)
    fig, ax = _new_figure()
    sns.histplot(data, bins="auto", kde=True, ax=ax, color="#3b6d99", edgecolor="white")
    ax.set(title=f"Rozkład: {column}", xlabel=column, ylabel="Liczba rekordów")
    fig.tight_layout()
    return fig


def scatter_figure(frame: pd.DataFrame, x_column: str, y_column: str, hue: str | None = None) -> Figure:
    _numeric_data(frame, x_column)
    _numeric_data(frame, y_column)
    plot_df = pd.DataFrame(
        {
            x_column: pd.to_numeric(frame[x_column], errors="coerce"),
            y_column: pd.to_numeric(frame[y_column], errors="coerce"),
        }
    ).dropna()
    if hue and hue in frame.columns:
        plot_df[hue] = frame.loc[plot_df.index, hue]
    if plot_df.empty:
        raise ValueError("Brak wspólnych obserwacji liczbowych dla wykresu punktowego.")
    fig, ax = _new_figure()
    sns.scatterplot(
        data=plot_df,
        x=x_column,
        y=y_column,
        hue=hue if hue in plot_df.columns else None,
        ax=ax,
        alpha=0.7,
        s=28,
    )
    corr = plot_df[x_column].corr(plot_df[y_column])
    corr_txt = f" (Pearson r = {corr:.3f})" if pd.notna(corr) else ""
    ax.set(
        title=f"Zależność: {y_column} vs {x_column}{corr_txt}",
        xlabel=x_column,
        ylabel=y_column,
    )
    ax.text(
        0.02,
        0.02,
        "Korelacja ≠ przyczynowość.",
        transform=ax.transAxes,
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout()
    return fig


def boxplot_figure(frame: pd.DataFrame, column: str, by: str | None = None) -> Figure:
    y = pd.to_numeric(frame[column], errors="coerce")
    if y.dropna().empty:
        raise ValueError(f"Kolumna '{column}' nie jest liczbowa.")
    plot_df = frame.copy()
    plot_df[column] = y
    fig, ax = _new_figure()
    if by:
        if by not in frame.columns:
            raise ValueError(f"Brak kolumny grupującej '{by}'.")
        sns.boxplot(data=plot_df.dropna(subset=[column, by]), x=by, y=column, ax=ax)
        ax.set(title=f"Rozkład {column} wg {by}", xlabel=by, ylabel=column)
        ax.tick_params(axis="x", rotation=20)
    else:
        sns.boxplot(y=plot_df[column].dropna(), ax=ax, color="#7aa2c4")
        ax.set(title=f"Wykres pudełkowy: {column}", ylabel=column, xlabel="")
    fig.tight_layout()
    return fig


def bar_figure(frame: pd.DataFrame, category: str, value: str | None = None) -> Figure:
    if category not in frame.columns:
        raise ValueError(f"Brak kolumny '{category}'.")
    fig, ax = _new_figure()
    if value:
        if value not in frame.columns:
            raise ValueError(f"Brak kolumny '{value}'.")
        numeric = pd.to_numeric(frame[value], errors="coerce")
        plot_df = pd.DataFrame({category: frame[category], value: numeric}).dropna()
        if plot_df.empty:
            raise ValueError("Brak danych do średniej w grupach.")
        grouped = plot_df.groupby(category, dropna=False)[value].mean().sort_values(ascending=False)
        sns.barplot(x=grouped.index.astype(str), y=grouped.values, ax=ax, color="#4c8c6a")
        ax.set(title=f"Średnia {value} wg {category}", xlabel=category, ylabel=f"Średnia {value}")
    else:
        counts = frame[category].fillna("(brak)").astype(str).value_counts()
        if counts.empty:
            raise ValueError("Kolumna kategorialna jest pusta.")
        sns.barplot(x=counts.index, y=counts.values, ax=ax, color="#4c8c6a")
        ax.set(title=f"Liczebność: {category}", xlabel=category, ylabel="Liczba rekordów")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    return fig


def correlation_figure(frame: pd.DataFrame) -> Figure:
    numeric = frame.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        raise ValueError("Do macierzy korelacji potrzeba co najmniej dwóch kolumn liczbowych.")
    corr = numeric.corr(numeric_only=True)
    fig = Figure(figsize=(7.2, 5.2), dpi=100)
    ax = fig.add_subplot()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax, square=False)
    ax.set_title("Macierz korelacji (Pearson) — zależność liniowa, nie przyczynowość")
    fig.tight_layout()
    return fig


def build_figure(
    frame: pd.DataFrame,
    kind: PlotKind,
    x: str | None = None,
    y: str | None = None,
    hue: str | None = None,
) -> Figure:
    if kind == "histogram":
        if not x:
            raise ValueError("Wybierz kolumnę liczbową do histogramu.")
        return histogram_figure(frame, x)
    if kind == "scatter":
        if not x or not y:
            raise ValueError("Wykres punktowy wymaga dwóch kolumn liczbowych (X i Y).")
        return scatter_figure(frame, x, y, hue=hue)
    if kind == "box":
        if not y and not x:
            raise ValueError("Wybierz kolumnę liczbową do wykresu pudełkowego.")
        return boxplot_figure(frame, column=y or x, by=hue)
    if kind == "bar":
        if not x:
            raise ValueError("Wybierz kolumnę kategorialną do wykresu słupkowego.")
        return bar_figure(frame, category=x, value=y)
    if kind == "correlation":
        return correlation_figure(frame)
    raise ValueError(f"Nieobsługiwany typ wykresu: {kind}")


def save_figure(fig: Figure, path: str) -> None:
    try:
        fig.savefig(path, bbox_inches="tight")
    except OSError as exc:
        raise OSError(
            f"Nie udało się zapisać wykresu do {path}. Sprawdź uprawnienia i wolne miejsce."
        ) from exc
