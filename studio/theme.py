
"""Wizualny język Atelier — tusz, papier i terakota."""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk


# ==========================================================
# PALETA KOLORÓW
# ==========================================================

INK = "#20293A"
INK_SOFT = "#303B50"
INK_LIGHT = "#46536A"

PAPER = "#F1ECE3"
PAPER_CARD = "#FFFCF6"
PAPER_DARK = "#E8DFD2"

LINE = "#DED4C6"

TERRACOTTA = "#C45C32"
TERRACOTTA_HOVER = "#A94926"
TERRACOTTA_LIGHT = "#F2D8C9"

TEAL = "#397A72"
TEAL_LIGHT = "#DCEBE5"

GOLD = "#BD913F"
GOLD_LIGHT = "#F4EAD1"

RED = "#B94D43"
RED_LIGHT = "#F5DEDA"

TEXT = "#252D3B"
MUTED = "#81776B"

ON_INK = "#FFF9F0"
ON_INK_MUTED = "#B8C1CF"

ROW_ALT = "#F7F1E8"
SELECT = "#EED4C3"
TREE_HEAD = "#303B50"


# ==========================================================
# FONT
# ==========================================================

def pick_font(root: tk.Tk) -> str:
    families = set(tkfont.families(root))

    for name in (
        "Avenir Next",
        "Avenir",
        "SF Pro Display",
        "Helvetica Neue",
        "Gill Sans",
        "Lucida Grande",
    ):
        if name in families:
            return name

    return "TkDefaultFont"


# ==========================================================
# MAIN THEME
# ==========================================================

def apply_theme(root: tk.Tk) -> str:
    family = pick_font(root)

    root.configure(bg=PAPER)
    root.option_add("*tearOff", False)

    style = ttk.Style(root)

    if "clam" in style.theme_names():
        style.theme_use("clam")

    # ------------------------------------------------------
    # GLOBAL
    # ------------------------------------------------------

    style.configure(
        ".",
        background=PAPER,
        foreground=TEXT,
        font=(family, 10),
    )

    style.configure("TFrame", background=PAPER)
    style.configure("Card.TFrame", background=PAPER_CARD)
    style.configure("Ink.TFrame", background=INK)
    style.configure("Soft.TFrame", background=PAPER_DARK)
    style.configure("Accent.TFrame", background=TERRACOTTA)

    # ------------------------------------------------------
    # LABELS
    # ------------------------------------------------------

    style.configure(
        "TLabel",
        background=PAPER,
        foreground=TEXT,
        font=(family, 10),
    )

    style.configure(
        "Title.TLabel",
        background=PAPER,
        foreground=INK,
        font=(family, 24, "bold"),
    )

    style.configure(
        "Subtitle.TLabel",
        background=PAPER,
        foreground=MUTED,
        font=(family, 10),
    )

    style.configure(
        "Header.TLabel",
        background=PAPER,
        foreground=INK,
        font=(family, 14, "bold"),
    )

    style.configure(
        "Section.TLabel",
        background=PAPER,
        foreground=TERRACOTTA,
        font=(family, 9, "bold"),
    )

    style.configure(
        "Muted.TLabel",
        background=PAPER,
        foreground=MUTED,
        font=(family, 9),
    )

    style.configure(
        "Card.TLabel",
        background=PAPER_CARD,
        foreground=TEXT,
        font=(family, 10),
    )

    style.configure(
        "CardTitle.TLabel",
        background=PAPER_CARD,
        foreground=INK,
        font=(family, 12, "bold"),
    )

    style.configure(
        "CardMuted.TLabel",
        background=PAPER_CARD,
        foreground=MUTED,
        font=(family, 9),
    )

    # ------------------------------------------------------
    # DARK PANEL
    # ------------------------------------------------------

    style.configure(
        "Ink.TLabel",
        background=INK,
        foreground=ON_INK,
        font=(family, 10),
    )

    style.configure(
        "InkTitle.TLabel",
        background=INK,
        foreground=ON_INK,
        font=(family, 20, "bold"),
    )

    style.configure(
        "InkMuted.TLabel",
        background=INK,
        foreground=ON_INK_MUTED,
        font=(family, 9),
    )

    style.configure(
        "InkSection.TLabel",
        background=INK,
        foreground="#E39A70",
        font=(family, 9, "bold"),
    )

    # ------------------------------------------------------
    # STATISTIC CARDS
    # ------------------------------------------------------

    style.configure(
        "Stat.TFrame",
        background=INK_SOFT,
        relief="flat",
    )

    style.configure(
        "StatValue.TLabel",
        background=INK_SOFT,
        foreground=ON_INK,
        font=(family, 23, "bold"),
    )

    style.configure(
        "StatCaption.TLabel",
        background=INK_SOFT,
        foreground=ON_INK_MUTED,
        font=(family, 9),
    )

    style.configure(
        "StatAccent.TLabel",
        background=INK_SOFT,
        foreground="#E99A72",
        font=(family, 9, "bold"),
    )

    # ------------------------------------------------------
    # BUTTONS
    # ------------------------------------------------------

    style.configure(
        "TButton",
        background=PAPER_CARD,
        foreground=INK,
        bordercolor=LINE,
        lightcolor=PAPER_CARD,
        darkcolor=LINE,
        padding=(14, 9),
        font=(family, 10, "bold"),
        relief="flat",
        borderwidth=1,
    )

    style.map(
        "TButton",
        background=[
            ("disabled", PAPER_DARK),
            ("pressed", SELECT),
            ("active", PAPER_DARK),
        ],
        foreground=[
            ("disabled", MUTED),
            ("active", INK),
        ],
    )

    # Primary button
    style.configure(
        "Primary.TButton",
        background=TERRACOTTA,
        foreground="#FFFFFF",
        bordercolor=TERRACOTTA,
        lightcolor=TERRACOTTA,
        darkcolor=TERRACOTTA_HOVER,
        padding=(17, 10),
        font=(family, 10, "bold"),
        relief="flat",
    )

    style.map(
        "Primary.TButton",
        background=[
            ("disabled", PAPER_DARK),
            ("pressed", "#8D3F20"),
            ("active", TERRACOTTA_HOVER),
        ],
        foreground=[
            ("disabled", MUTED),
            ("!disabled", "#FFFFFF"),
        ],
    )

    # Secondary button
    style.configure(
        "Secondary.TButton",
        background=TEAL,
        foreground="#FFFFFF",
        bordercolor=TEAL,
        lightcolor=TEAL,
        darkcolor="#285D57",
        padding=(15, 9),
        font=(family, 10, "bold"),
    )

    style.map(
        "Secondary.TButton",
        background=[
            ("pressed", "#285D57"),
            ("active", "#326B64"),
        ],
    )

    # Dark button
    style.configure(
        "Ghost.TButton",
        background=INK_SOFT,
        foreground=ON_INK,
        bordercolor=INK_SOFT,
        lightcolor=INK_SOFT,
        darkcolor=INK,
        padding=(15, 9),
        font=(family, 10, "bold"),
    )

    style.map(
        "Ghost.TButton",
        background=[
            ("pressed", INK),
            ("active", INK_LIGHT),
        ],
    )

    # ------------------------------------------------------
    # NOTEBOOK / TABS
    # ------------------------------------------------------

    style.configure(
        "TNotebook",
        background=PAPER,
        borderwidth=0,
        tabmargins=(5, 8, 5, 0),
    )

    style.configure(
        "TNotebook.Tab",
        background=PAPER_DARK,
        foreground=MUTED,
        padding=(18, 11),
        font=(family, 10, "bold"),
        borderwidth=0,
    )

    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", PAPER_CARD),
            ("active", TERRACOTTA_LIGHT),
        ],
        foreground=[
            ("selected", TERRACOTTA),
            ("active", INK),
        ],
    )

    # ------------------------------------------------------
    # LABEL FRAMES
    # ------------------------------------------------------

    style.configure(
        "TLabelframe",
        background=PAPER_CARD,
        foreground=INK,
        bordercolor=LINE,
        relief="solid",
        borderwidth=1,
        padding=14,
    )

    style.configure(
        "TLabelframe.Label",
        background=PAPER_CARD,
        foreground=TERRACOTTA,
        font=(family, 10, "bold"),
    )

    # ------------------------------------------------------
    # INPUTS
    # ------------------------------------------------------

    style.configure(
        "TEntry",
        fieldbackground=PAPER_CARD,
        foreground=TEXT,
        insertcolor=TERRACOTTA,
        bordercolor=LINE,
        lightcolor=LINE,
        darkcolor=LINE,
        padding=(9, 8),
        relief="flat",
    )

    style.map(
        "TEntry",
        bordercolor=[
            ("focus", TERRACOTTA),
        ],
        lightcolor=[
            ("focus", TERRACOTTA),
        ],
    )

    style.configure(
        "TCombobox",
        fieldbackground=PAPER_CARD,
        background=PAPER_CARD,
        foreground=TEXT,
        arrowcolor=TERRACOTTA,
        bordercolor=LINE,
        lightcolor=LINE,
        darkcolor=LINE,
        padding=(9, 7),
    )

    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", PAPER_CARD),
        ],
        foreground=[
            ("readonly", TEXT),
        ],
        bordercolor=[
            ("focus", TERRACOTTA),
        ],
    )

    style.configure(
        "TSpinbox",
        fieldbackground=PAPER_CARD,
        foreground=TEXT,
        arrowcolor=TERRACOTTA,
        padding=7,
    )

    # ------------------------------------------------------
    # CHECKBOXES AND RADIO BUTTONS
    # ------------------------------------------------------

    style.configure(
        "TCheckbutton",
        background=PAPER,
        foreground=TEXT,
        font=(family, 10),
        padding=5,
    )

    style.map(
        "TCheckbutton",
        background=[("active", PAPER)],
        foreground=[("disabled", MUTED)],
    )

    style.configure(
        "TRadiobutton",
        background=PAPER,
        foreground=TEXT,
        font=(family, 10),
        padding=5,
    )

    style.map(
        "TRadiobutton",
        background=[("active", PAPER)],
    )

    # ------------------------------------------------------
    # TABLES
    # ------------------------------------------------------

    style.configure(
        "Treeview",
        background=PAPER_CARD,
        fieldbackground=PAPER_CARD,
        foreground=TEXT,
        rowheight=34,
        font=(family, 10),
        bordercolor=LINE,
        borderwidth=0,
        relief="flat",
    )

    style.configure(
        "Treeview.Heading",
        background=TREE_HEAD,
        foreground=ON_INK,
        font=(family, 9, "bold"),
        relief="flat",
        padding=(10, 11),
        borderwidth=0,
    )

    style.map(
        "Treeview",
        background=[
            ("selected", SELECT),
        ],
        foreground=[
            ("selected", INK),
        ],
    )

    style.map(
        "Treeview.Heading",
        background=[
            ("active", INK_LIGHT),
        ],
        foreground=[
            ("active", ON_INK),
        ],
    )

    # ------------------------------------------------------
    # SCROLLBARS
    # ------------------------------------------------------

    for orientation in ("Vertical", "Horizontal"):
        style.configure(
            f"{orientation}.TScrollbar",
            background=PAPER_DARK,
            troughcolor=PAPER,
            bordercolor=PAPER,
            arrowcolor=MUTED,
            gripcount=0,
            relief="flat",
        )

        style.map(
            f"{orientation}.TScrollbar",
            background=[
                ("active", TERRACOTTA),
            ],
        )

    # ------------------------------------------------------
    # PROGRESS BAR
    # ------------------------------------------------------

    style.configure(
        "Horizontal.TProgressbar",
        background=TERRACOTTA,
        troughcolor=PAPER_DARK,
        bordercolor=PAPER_DARK,
        lightcolor=TERRACOTTA,
        darkcolor=TERRACOTTA,
        thickness=9,
    )

    # ------------------------------------------------------
    # SEPARATORS
    # ------------------------------------------------------

    style.configure(
        "TSeparator",
        background=LINE,
    )

    return family


# ==========================================================
# TABLE ROW STYLING
# ==========================================================

def style_tree(tree: ttk.Treeview) -> None:
    tree.tag_configure(
        "odd",
        background=PAPER_CARD,
        foreground=TEXT,
    )

    tree.tag_configure(
        "even",
        background=ROW_ALT,
        foreground=TEXT,
    )

    tree.tag_configure(
        "success",
        background=TEAL_LIGHT,
        foreground="#285D57",
    )

    tree.tag_configure(
        "warning",
        background=GOLD_LIGHT,
        foreground="#80601F",
    )

    tree.tag_configure(
        "danger",
        background=RED_LIGHT,
        foreground="#963D35",
    )


# ==========================================================
# LOG WINDOW
# ==========================================================

def style_log(widget: tk.Text, family: str) -> None:
    widget.configure(
        bg="#25211F",
        fg="#F4EBDD",
        insertbackground="#E99A72",
        selectbackground=TERRACOTTA,
        selectforeground="#FFFFFF",
        relief="flat",
        borderwidth=0,
        padx=16,
        pady=14,
        font=(family, 10),
        spacing1=4,
        spacing3=4,
        wrap="word",
        highlightthickness=1,
        highlightbackground=LINE,
        highlightcolor=TERRACOTTA,
    )

    # Log message colors
    widget.tag_configure(
        "success",
        foreground="#91C7A8",
    )

    widget.tag_configure(
        "warning",
        foreground="#E6BD71",
    )

    widget.tag_configure(
        "error",
        foreground="#E68B7F",
    )

    widget.tag_configure(
        "info",
        foreground="#AFC4DE",
    )

    widget.tag_configure(
        "timestamp",
        foreground="#A69A8C",
    )

