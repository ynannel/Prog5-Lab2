from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from studio.plots import build_figure, categorical_columns, numeric_columns, save_figure
from studio.session import DataSession

APP_TITLE = "Studio jakości i wizualizacji danych"
PREVIEW_ROWS = 80


class StudioApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=8)
        self.master = master
        self.session: DataSession | None = None
        self._canvas: FigureCanvasTkAgg | None = None
        self._toolbar: NavigationToolbar2Tk | None = None
        self._figure: Figure | None = None
        self.pack(fill=tk.BOTH, expand=True)
        self._build_style()
        self._build_menu()
        self._build_layout()
        self._set_status("Wczytaj plik CSV, aby rozpocząć analizę.")

    def _build_style(self) -> None:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=(12, 6))
        style.configure("Header.TLabel", font=("TkDefaultFont", 14, "bold"))
        style.configure("Muted.TLabel", foreground="#555555")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Otwórz CSV…", command=self.open_csv)
        file_menu.add_command(label="Zapisz oczyszczony CSV…", command=self.export_csv)
        file_menu.add_command(label="Zapisz raport zmian…", command=self.export_audit)
        file_menu.add_separator()
        file_menu.add_command(label="Eksport wykresu PNG…", command=lambda: self.export_plot("png"))
        file_menu.add_command(label="Eksport wykresu PDF…", command=lambda: self.export_plot("pdf"))
        file_menu.add_command(label="Eksport wykresu SVG…", command=lambda: self.export_plot("svg"))
        file_menu.add_separator()
        file_menu.add_command(label="Zakończ", command=self.master.destroy)
        menubar.add_cascade(label="Plik", menu=file_menu)

        session_menu = tk.Menu(menubar, tearoff=0)
        session_menu.add_command(label="Przywróć dane surowe", command=self.reset_session)
        menubar.add_cascade(label="Sesja", menu=session_menu)
        self.master.config(menu=menubar)

    def _build_layout(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text=APP_TITLE, style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header, text="Wczytaj CSV", command=self.open_csv).pack(side=tk.RIGHT, padx=4)
        ttk.Button(header, text="Reset do surowych", command=self.reset_session).pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_data = ttk.Frame(self.notebook, padding=8)
        self.tab_profile = ttk.Frame(self.notebook, padding=8)
        self.tab_clean = ttk.Frame(self.notebook, padding=8)
        self.tab_plot = ttk.Frame(self.notebook, padding=8)
        self.tab_audit = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_data, text="Dane")
        self.notebook.add(self.tab_profile, text="Profil")
        self.notebook.add(self.tab_clean, text="Czyszczenie")
        self.notebook.add(self.tab_plot, text="Wizualizacja")
        self.notebook.add(self.tab_audit, text="Ślad zmian")

        self._build_data_tab()
        self._build_profile_tab()
        self._build_clean_tab()
        self._build_plot_tab()
        self._build_audit_tab()

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, style="Muted.TLabel").pack(fill=tk.X, pady=(6, 0))

    def _build_data_tab(self) -> None:
        info = ttk.Frame(self.tab_data)
        info.pack(fill=tk.X)
        self.data_info = tk.StringVar(value="Brak wczytanych danych.")
        ttk.Label(info, textvariable=self.data_info, wraplength=900).pack(anchor=tk.W)
        ttk.Label(
            self.tab_data,
            text=f"Podgląd pierwszych {PREVIEW_ROWS} wierszy (pełny zbiór pozostaje w sesji).",
            style="Muted.TLabel",
        ).pack(anchor=tk.W, pady=(6, 4))

        container = ttk.Frame(self.tab_data)
        container.pack(fill=tk.BOTH, expand=True)
        self.preview = ttk.Treeview(container, show="headings")
        yscroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.preview.yview)
        xscroll = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.preview.xview)
        self.preview.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.preview.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

    def _build_profile_tab(self) -> None:
        self.profile_summary = tk.StringVar(value="Profil pojawi się po wczytaniu pliku.")
        ttk.Label(self.tab_profile, textvariable=self.profile_summary).pack(anchor=tk.W)
        ttk.Label(self.tab_profile, text="Kolumny, typy, braki i unikalność", style="Muted.TLabel").pack(
            anchor=tk.W, pady=(8, 4)
        )
        self.profile_tree = self._make_tree(self.tab_profile)
        ttk.Label(self.tab_profile, text="Statystyki opisowe (kolumny liczbowe)", style="Muted.TLabel").pack(
            anchor=tk.W, pady=(8, 4)
        )
        self.stats_tree = self._make_tree(self.tab_profile, height=8)

    def _build_clean_tab(self) -> None:
        left = ttk.Frame(self.tab_clean)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        right = ttk.Frame(self.tab_clean)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Operacje", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 8))

        dup = ttk.LabelFrame(left, text="Duplikaty", padding=8)
        dup.pack(fill=tk.X, pady=4)
        ttk.Button(dup, text="Usuń pełne duplikaty", command=self._drop_duplicates).pack(fill=tk.X)

        miss = ttk.LabelFrame(left, text="Braki danych", padding=8)
        miss.pack(fill=tk.X, pady=4)
        self.missing_col = tk.StringVar()
        self.missing_strategy = tk.StringVar(value="drop_rows")
        ttk.Label(miss, text="Kolumna").pack(anchor=tk.W)
        self.missing_combo = ttk.Combobox(miss, textvariable=self.missing_col, state="readonly")
        self.missing_combo.pack(fill=tk.X, pady=2)
        ttk.Label(miss, text="Strategia").pack(anchor=tk.W)
        ttk.Combobox(
            miss,
            textvariable=self.missing_strategy,
            state="readonly",
            values=("drop_rows", "mean", "median", "mode"),
        ).pack(fill=tk.X, pady=2)
        ttk.Label(
            miss,
            text="drop_rows = usuń wiersze; mean/median/mode = imputacja",
            style="Muted.TLabel",
            wraplength=280,
        ).pack(anchor=tk.W, pady=(0, 4))
        ttk.Button(miss, text="Zastosuj strategię braków", command=self._apply_missing).pack(fill=tk.X)

        invalid = ttk.LabelFrame(left, text="Wartości błędne (nienumeryczne)", padding=8)
        invalid.pack(fill=tk.X, pady=4)
        self.invalid_col = tk.StringVar()
        self.invalid_combo = ttk.Combobox(invalid, textvariable=self.invalid_col, state="readonly")
        self.invalid_combo.pack(fill=tk.X, pady=2)
        ttk.Button(invalid, text="Zamień na NaN / liczbę", command=lambda: self._apply_invalid(False)).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(invalid, text="Usuń wadliwe wiersze", command=lambda: self._apply_invalid(True)).pack(fill=tk.X)

        rng = ttk.LabelFrame(left, text="Reguła zakresu", padding=8)
        rng.pack(fill=tk.X, pady=4)
        self.range_col = tk.StringVar()
        self.range_min = tk.StringVar(value="0")
        self.range_max = tk.StringVar(value="15")
        self.range_action = tk.StringVar(value="flag")
        self.range_combo = ttk.Combobox(rng, textvariable=self.range_col, state="readonly")
        self.range_combo.pack(fill=tk.X, pady=2)
        minmax = ttk.Frame(rng)
        minmax.pack(fill=tk.X)
        ttk.Entry(minmax, textvariable=self.range_min, width=10).pack(side=tk.LEFT)
        ttk.Label(minmax, text="–").pack(side=tk.LEFT, padx=4)
        ttk.Entry(minmax, textvariable=self.range_max, width=10).pack(side=tk.LEFT)
        ttk.Combobox(
            rng,
            textvariable=self.range_action,
            state="readonly",
            values=("flag", "clip", "drop"),
        ).pack(fill=tk.X, pady=2)
        ttk.Label(
            rng,
            text="flag = oznacz kolumną *_out_of_range (domyślnie bez usuwania)",
            style="Muted.TLabel",
            wraplength=280,
        ).pack(anchor=tk.W)
        ttk.Button(rng, text="Zastosuj regułę zakresu", command=self._apply_range).pack(fill=tk.X, pady=(4, 0))

        out = ttk.LabelFrame(left, text="Outliery (IQR)", padding=8)
        out.pack(fill=tk.X, pady=4)
        self.out_col = tk.StringVar()
        self.out_factor = tk.StringVar(value="1.5")
        self.out_action = tk.StringVar(value="flag")
        self.out_combo = ttk.Combobox(out, textvariable=self.out_col, state="readonly")
        self.out_combo.pack(fill=tk.X, pady=2)
        ttk.Entry(out, textvariable=self.out_factor).pack(fill=tk.X, pady=2)
        ttk.Combobox(
            out,
            textvariable=self.out_action,
            state="readonly",
            values=("flag", "keep", "clip", "drop"),
        ).pack(fill=tk.X, pady=2)
        ttk.Label(
            out,
            text="Outlier ≠ automatyczny błąd. keep tylko zlicza; flag oznacza.",
            style="Muted.TLabel",
            wraplength=280,
        ).pack(anchor=tk.W)
        ttk.Button(out, text="Zastosuj IQR", command=self._apply_outliers).pack(fill=tk.X, pady=(4, 0))

        ttk.Label(right, text="Ostatnie operacje", style="Muted.TLabel").pack(anchor=tk.W)
        self.clean_log = tk.Text(right, height=20, wrap=tk.WORD)
        self.clean_log.pack(fill=tk.BOTH, expand=True, pady=4)

    def _build_plot_tab(self) -> None:
        controls = ttk.Frame(self.tab_plot)
        controls.pack(fill=tk.X)
        self.plot_kind = tk.StringVar(value="histogram")
        self.plot_x = tk.StringVar()
        self.plot_y = tk.StringVar()
        self.plot_hue = tk.StringVar()

        ttk.Label(controls, text="Typ").grid(row=0, column=0, sticky=tk.W, padx=2)
        ttk.Combobox(
            controls,
            textvariable=self.plot_kind,
            state="readonly",
            values=("histogram", "scatter", "box", "bar", "correlation"),
            width=16,
        ).grid(row=0, column=1, padx=2)
        ttk.Label(controls, text="X / kategoria").grid(row=0, column=2, sticky=tk.W, padx=2)
        self.plot_x_combo = ttk.Combobox(controls, textvariable=self.plot_x, state="readonly", width=22)
        self.plot_x_combo.grid(row=0, column=3, padx=2)
        ttk.Label(controls, text="Y / wartość").grid(row=0, column=4, sticky=tk.W, padx=2)
        self.plot_y_combo = ttk.Combobox(controls, textvariable=self.plot_y, state="readonly", width=22)
        self.plot_y_combo.grid(row=0, column=5, padx=2)
        ttk.Label(controls, text="Grupa / hue").grid(row=0, column=6, sticky=tk.W, padx=2)
        self.plot_hue_combo = ttk.Combobox(controls, textvariable=self.plot_hue, state="readonly", width=18)
        self.plot_hue_combo.grid(row=0, column=7, padx=2)
        ttk.Button(controls, text="Rysuj", command=self.draw_plot).grid(row=0, column=8, padx=8)
        ttk.Button(controls, text="PNG", command=lambda: self.export_plot("png")).grid(row=0, column=9)
        ttk.Button(controls, text="PDF", command=lambda: self.export_plot("pdf")).grid(row=0, column=10)
        ttk.Button(controls, text="SVG", command=lambda: self.export_plot("svg")).grid(row=0, column=11)

        hint = (
            "histogram/box: kolumna liczbowa; scatter: X i Y liczbowe; "
            "bar: kategoria (X), opcjonalnie średnia Y; correlation: wszystkie liczby. "
            "Korelacja opisuje zależność liniową, nie przyczynę."
        )
        ttk.Label(self.tab_plot, text=hint, style="Muted.TLabel", wraplength=1100).pack(anchor=tk.W, pady=6)
        self.plot_host = ttk.Frame(self.tab_plot)
        self.plot_host.pack(fill=tk.BOTH, expand=True)

    def _build_audit_tab(self) -> None:
        ttk.Button(self.tab_audit, text="Zapisz raport zmian…", command=self.export_audit).pack(anchor=tk.W)
        self.audit_text = tk.Text(self.tab_audit, wrap=tk.WORD)
        self.audit_text.pack(fill=tk.BOTH, expand=True, pady=6)

    def _make_tree(self, parent: ttk.Frame, height: int = 12) -> ttk.Treeview:
        box = ttk.Frame(parent)
        box.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(box, show="headings", height=height)
        scroll = ttk.Scrollbar(box, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    def _require_session(self) -> DataSession | None:
        if self.session is None:
            messagebox.showwarning(APP_TITLE, "Najpierw wczytaj plik CSV.")
            return None
        return self.session

    def open_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Wybierz plik CSV",
            filetypes=[("CSV", "*.csv"), ("Wszystkie pliki", "*.*")],
        )
        if not path:
            return
        try:
            self.session = DataSession.from_csv(Path(path))
        except Exception as exc:
            messagebox.showerror(
                APP_TITLE,
                f"Nie udało się wczytać pliku.\n\n{exc}\n\n"
                "Aplikacja pozostaje otwarta — popraw plik albo wybierz inny CSV.",
            )
            return
        self.refresh_all()
        self._set_status(f"Wczytano {path}")

    def reset_session(self) -> None:
        session = self._require_session()
        if not session:
            return
        session.reset()
        self.refresh_all()
        self._set_status("Przywrócono dane surowe bez ponownego wczytywania pliku.")

    def export_csv(self) -> None:
        session = self._require_session()
        if not session:
            return
        path = filedialog.asksaveasfilename(
            title="Zapisz oczyszczony CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="cleaned.csv",
        )
        if not path:
            return
        try:
            session.export_cleaned(Path(path))
        except OSError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self._set_status(f"Zapisano {path}")
        messagebox.showinfo(APP_TITLE, f"Zapisano oczyszczone dane:\n{path}")

    def export_audit(self) -> None:
        session = self._require_session()
        if not session:
            return
        path = filedialog.asksaveasfilename(
            title="Zapisz raport zmian",
            defaultextension=".txt",
            filetypes=[("Tekst", "*.txt")],
            initialfile="raport_zmian.txt",
        )
        if not path:
            return
        try:
            session.export_audit(Path(path))
        except OSError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self._set_status(f"Zapisano raport {path}")

    def export_plot(self, fmt: str) -> None:
        if self._figure is None:
            messagebox.showwarning(APP_TITLE, "Najpierw narysuj wykres.")
            return
        path = filedialog.asksaveasfilename(
            title=f"Zapisz wykres ({fmt.upper()})",
            defaultextension=f".{fmt}",
            filetypes=[(fmt.upper(), f"*.{fmt}")],
            initialfile=f"wykres.{fmt}",
        )
        if not path:
            return
        try:
            save_figure(self._figure, path)
        except OSError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self._set_status(f"Zapisano wykres {path}")

    def draw_plot(self) -> None:
        session = self._require_session()
        if not session:
            return
        kind = self.plot_kind.get()
        x = self.plot_x.get() or None
        y = self.plot_y.get() or None
        hue = self.plot_hue.get() or None
        if hue == "(brak)":
            hue = None
        if y == "(brak)":
            y = None
        try:
            fig = build_figure(session.current, kind=kind, x=x, y=y, hue=hue)  # type: ignore[arg-type]
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self._embed_figure(fig)

    def _embed_figure(self, fig: Figure) -> None:
        if self._toolbar is not None:
            self._toolbar.destroy()
            self._toolbar = None
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        self._figure = fig
        self._canvas = FigureCanvasTkAgg(fig, master=self.plot_host)
        self._canvas.draw()
        widget = self._canvas.get_tk_widget()
        widget.pack(fill=tk.BOTH, expand=True)
        self._toolbar = NavigationToolbar2Tk(self._canvas, self.plot_host)
        self._toolbar.update()

    def refresh_all(self) -> None:
        if self.session is None:
            return
        frame = self.session.current
        source = self.session.source
        extra = ""
        if source:
            extra = (
                f" | kodowanie {source.encoding}, separator {source.separator!r}"
                + (f", pominięte wadliwe wiersze: {source.skipped_bad_lines}" if source.skipped_bad_lines else "")
            )
        self.data_info.set(
            f"Wiersze: {len(frame)} | Kolumny: {frame.shape[1]} | "
            f"surowe wiersze: {len(self.session.raw)}{extra}"
        )
        self._fill_preview(frame)
        self._fill_profile()
        self._refresh_column_lists()
        self._fill_audit()

    def _fill_preview(self, frame) -> None:
        self.preview.delete(*self.preview.get_children())
        columns = list(frame.columns)
        self.preview["columns"] = columns
        for col in columns:
            self.preview.heading(col, text=col)
            self.preview.column(col, width=110, stretch=True)
        for _, row in frame.head(PREVIEW_ROWS).iterrows():
            values = ["" if value != value else value for value in row.tolist()]
            self.preview.insert("", tk.END, values=values)

    def _fill_profile(self) -> None:
        profile = self.session.profile()  # type: ignore[union-attr]
        self.profile_summary.set(profile.summary_text())
        self._load_dataframe_tree(self.profile_tree, profile.column_table)
        stats = profile.numeric_stats.reset_index().rename(columns={"index": "kolumna"})
        self._load_dataframe_tree(self.stats_tree, stats)

    def _load_dataframe_tree(self, tree: ttk.Treeview, frame) -> None:
        tree.delete(*tree.get_children())
        if frame is None or frame.empty:
            tree["columns"] = ("info",)
            tree.heading("info", text="Brak danych")
            return
        columns = list(frame.columns)
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=str(col))
            tree.column(col, width=110, stretch=True)
        for _, row in frame.iterrows():
            tree.insert("", tk.END, values=[row[col] for col in columns])

    def _refresh_column_lists(self) -> None:
        if self.session is None:
            return
        cols = list(self.session.current.columns)
        nums = numeric_columns(self.session.current)
        cats = categorical_columns(self.session.current)
        for combo, values in (
            (self.missing_combo, cols),
            (self.invalid_combo, cols),
            (self.range_combo, nums or cols),
            (self.out_combo, nums or cols),
            (self.plot_x_combo, cols),
            (self.plot_y_combo, ["(brak)", *cols]),
            (self.plot_hue_combo, ["(brak)", *cats, *nums]),
        ):
            combo["values"] = values
        if cols:
            self.missing_col.set(cols[0])
            self.invalid_col.set(cols[0])
            self.plot_x.set(nums[0] if nums else cols[0])
            self.plot_y.set("(brak)")
            self.plot_hue.set("(brak)")
        if nums:
            self.range_col.set(nums[0] if "median_income" not in nums else "median_income")
            self.out_col.set(nums[0] if "median_house_value" not in nums else "median_house_value")

    def _fill_audit(self) -> None:
        if self.session is None:
            return
        lines = [entry.as_line() for entry in self.session.audit_log]
        text = "\n".join(lines) if lines else "Brak operacji."
        for widget in (self.audit_text, self.clean_log):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", text)

    def _drop_duplicates(self) -> None:
        session = self._require_session()
        if not session:
            return
        removed = session.drop_exact_duplicates()
        self.refresh_all()
        self._set_status(f"Usunięto {removed} pełnych duplikatów.")

    def _apply_missing(self) -> None:
        session = self._require_session()
        if not session:
            return
        column = self.missing_col.get()
        if not column:
            messagebox.showwarning(APP_TITLE, "Wybierz kolumnę.")
            return
        try:
            affected = session.fill_or_drop_missing([column], self.missing_strategy.get())  # type: ignore[arg-type]
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self.refresh_all()
        self._set_status(f"Braki: dotknięto {affected} rekordów.")

    def _apply_invalid(self, drop: bool) -> None:
        session = self._require_session()
        if not session:
            return
        column = self.invalid_col.get()
        if not column:
            messagebox.showwarning(APP_TITLE, "Wybierz kolumnę.")
            return
        try:
            affected = session.coerce_invalid_numeric(column, drop=drop)
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self.refresh_all()
        self._set_status(f"Wartości błędne: {affected} rekordów.")

    def _apply_range(self) -> None:
        session = self._require_session()
        if not session:
            return
        try:
            minimum = float(self.range_min.get().replace(",", "."))
            maximum = float(self.range_max.get().replace(",", "."))
        except ValueError:
            messagebox.showerror(APP_TITLE, "Minimum i maksimum muszą być liczbami.")
            return
        try:
            affected = session.apply_range(
                self.range_col.get(),
                minimum,
                maximum,
                self.range_action.get(),  # type: ignore[arg-type]
            )
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self.refresh_all()
        self._set_status(f"Reguła zakresu: {affected} rekordów.")

    def _apply_outliers(self) -> None:
        session = self._require_session()
        if not session:
            return
        try:
            factor = float(self.out_factor.get().replace(",", "."))
        except ValueError:
            messagebox.showerror(APP_TITLE, "Współczynnik IQR musi być liczbą (np. 1.5).")
            return
        try:
            affected = session.apply_outliers(
                self.out_col.get(),
                factor=factor,
                action=self.out_action.get(),  # type: ignore[arg-type]
            )
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self.refresh_all()
        self._set_status(f"IQR: {affected} obserwacji odstających.")

    def _set_status(self, text: str) -> None:
        self.status.set(text)


def run_app() -> None:
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("1280x780")
    root.minsize(960, 600)
    StudioApp(root)
    root.mainloop()
