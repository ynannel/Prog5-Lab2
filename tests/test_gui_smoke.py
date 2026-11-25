import tkinter as tk

import pytest

from studio.gui import StudioApp
from studio.session import DataSession


def test_gui_refresh_after_load(tmp_path) -> None:
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Brak środowiska graficznego Tk")
    root.withdraw()
    try:
        app = StudioApp(root)
        csv_path = tmp_path / "mini.csv"
        csv_path.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
        app.session = DataSession.from_csv(csv_path)
        app.refresh_all()
        assert "Wiersze: 2" in app.data_info.get()
        assert app.plot_x_combo["values"]
    finally:
        root.destroy()
