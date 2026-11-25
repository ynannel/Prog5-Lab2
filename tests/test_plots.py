import pandas as pd
import pytest
from matplotlib.figure import Figure

from studio.plots import build_figure


def test_histogram_rejects_non_numeric() -> None:
    frame = pd.DataFrame({"miasto": ["A", "B", "A"]})
    with pytest.raises(ValueError):
        build_figure(frame, "histogram", x="miasto")


def test_histogram_rejects_constant_column() -> None:
    frame = pd.DataFrame({"x": [5, 5, 5, 5]})
    with pytest.raises(ValueError, match="stała"):
        build_figure(frame, "histogram", x="x")


def test_four_plot_types_return_figure() -> None:
    frame = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 5, 8, 9, 13],
            "g": ["a", "a", "b", "b", "a", "b"],
        }
    )
    assert isinstance(build_figure(frame, "histogram", x="x"), Figure)
    assert isinstance(build_figure(frame, "scatter", x="x", y="y"), Figure)
    assert isinstance(build_figure(frame, "box", y="y", hue="g"), Figure)
    assert isinstance(build_figure(frame, "bar", x="g"), Figure)


def test_scatter_requires_two_columns() -> None:
    frame = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    with pytest.raises(ValueError, match="dwóch"):
        build_figure(frame, "scatter", x="x")
