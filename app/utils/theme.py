from tkinter import ttk

COLORS = {
    "bg_main": "#0F1438",
    "bg_card": "#1A214F",
    "bg_input": "#232C66",
    "border": "#323E8A",
    "primary": "#0066EB",
    "primary_hover": "#1A78F5",
    "accent": "#D9269D",
    "text_primary": "#FFFFFF",
    "text_secondary": "#C5CEE8",
    "text_muted": "#8F9BC2",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 10),
    "section": ("Segoe UI", 13, "bold"),
    "label": ("Segoe UI", 10),
    "label_bold": ("Segoe UI", 10, "bold"),
    "button": ("Segoe UI", 10, "bold"),
    "tree_heading": ("Segoe UI", 10, "bold"),
    "tree_cell": ("Segoe UI", 10),
}


def apply_theme(root):
    root.configure(bg=COLORS["bg_main"])
    style = ttk.Style(root)
    style.theme_use("clam")

    # Frames e Containers
    style.configure("Main.TFrame", background=COLORS["bg_main"])
    style.configure("Card.TFrame", background=COLORS["bg_card"])

    # LabelFrame
    style.configure(
        "Card.TLabelframe",
        background=COLORS["bg_card"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        font=FONTS["section"],
    )

    # Labels
    style.configure(
        "Title.TLabel",
        background=COLORS["bg_main"],
        foreground=COLORS["text_primary"],
        font=FONTS["title"],
    )
    style.configure(
        "CardTitle.TLabel",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        font=FONTS["title"],
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["bg_main"],
        foreground=COLORS["text_secondary"],
        font=FONTS["subtitle"],
    )
    style.configure(
        "CardSubtitle.TLabel",
        background=COLORS["bg_card"],
        foreground=COLORS["text_secondary"],
        font=FONTS["subtitle"],
    )
    style.configure(
        "Section.TLabel",
        background=COLORS["bg_main"],
        foreground=COLORS["text_primary"],
        font=FONTS["section"],
    )
    style.configure(
        "Field.TLabel",
        background=COLORS["bg_card"],
        foreground=COLORS["text_secondary"],
        font=FONTS["label"],
    )
    style.configure(
        "FieldBold.TLabel",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        font=FONTS["label_bold"],
    )
    style.configure(
        "Value.TLabel",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        font=FONTS["label"],
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["bg_card"],
        foreground=COLORS["text_muted"],
        font=FONTS["subtitle"],
    )

    # Inputs (Entry & Combobox)
    style.configure(
        "App.TEntry",
        fieldbackground=COLORS["bg_input"],
        foreground=COLORS["text_primary"],
        insertcolor=COLORS["text_primary"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        padding=6,
    )
    style.configure(
        "App.TCombobox",
        fieldbackground=COLORS["bg_input"],
        foreground=COLORS["text_primary"],
        selectbackground=COLORS["primary"],
        selectforeground=COLORS["text_primary"],
        bordercolor=COLORS["border"],
        padding=5,
    )

    # Botão Primário
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground=COLORS["text_primary"],
        font=FONTS["button"],
        bordercolor=COLORS["primary"],
        padding=(12, 8),
    )
    style.map(
        "Primary.TButton",
        background=[
            ("active", COLORS["primary_hover"]),
            ("disabled", "#2A3366"),
        ],
        foreground=[("disabled", "#7C88B5")],
    )

    # Botão Secundário / Neutro
    style.configure(
        "Secondary.TButton",
        background=COLORS["bg_input"],
        foreground=COLORS["text_primary"],
        font=FONTS["button"],
        bordercolor=COLORS["border"],
        padding=(10, 7),
    )
    style.map(
        "Secondary.TButton",
        background=[
            ("active", COLORS["border"]),
            ("disabled", "#171D45"),
        ],
        foreground=[("disabled", "#6E79A3")],
    )

    # Treeview (Tabela)
    style.configure(
        "App.Treeview",
        background=COLORS["bg_card"],
        fieldbackground=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        bordercolor=COLORS["border"],
        rowheight=28,
        font=FONTS["tree_cell"],
    )
    style.configure(
        "App.Treeview.Heading",
        background=COLORS["bg_input"],
        foreground=COLORS["text_primary"],
        bordercolor=COLORS["border"],
        font=FONTS["tree_heading"],
        padding=6,
    )
    style.map(
        "App.Treeview",
        background=[("selected", COLORS["primary"])],
        foreground=[("selected", COLORS["text_primary"])],
    )