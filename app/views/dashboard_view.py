from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .base_view import BaseView
from config import CURRENCY_SYMBOL, LOGO_PATH


class DashboardView(BaseView):
    """Vista de resumen ejecutivo de ventas."""

    def __init__(self, parent, app) -> None:
        self._cards: dict[str, ttk.Label] = {}

        # Logo responsive
        self._logo_base = None
        self._logo_img: tk.PhotoImage | None = None
        self._logo_label: ttk.Label | None = None
        self._logo_after_id: str | None = None

        super().__init__(parent, app)
        self.refresh()

    # ========= Construcción de UI =========

    def _build(self) -> None:
        style = ttk.Style(self)
        self._configure_styles(style)

        # --------- Layout principal ----------
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        # Usamos GRID para ordenar verticalmente (más control del spacing)
        container.columnconfigure(0, weight=1)

        # ====== HEADER ======
        header = ttk.Frame(container, padding=10)
        header.grid(row=0, column=0, sticky="ew", pady=(10, 20))
        header.columnconfigure(0, weight=1)

        # Logo (con PIL si está disponible)
        self._logo_label = ttk.Label(header)
        self._logo_label.grid(row=0, column=0, pady=(0, 10))

        self._load_logo(LOGO_PATH)
        self._set_logo_size(180)

        # Títulos
        ttk.Label(
            header,
            text="Demo Company",
            font=("TkDefaultFont", 20, "bold"),
        ).grid(row=1, column=0, pady=(0, 2))

        ttk.Label(
            header,
            text="Resumen Ejecutivo",
            font=("TkDefaultFont", 16, "bold"),
        ).grid(row=2, column=0, pady=(0, 6))

        ttk.Label(
            header,
            text="Visión rápida de ventas, ticket promedio, operaciones y clientes únicos.",
            font=("TkDefaultFont", 11),
        ).grid(row=3, column=0)

        # Separator (UNO solo)
        sep = ttk.Separator(container, orient="horizontal", style="SoftLine.TSeparator")
        sep.grid(row=1, column=0, sticky="ew", pady=(10, 20))

        # ====== CARDS ======
        cards_frame = ttk.Frame(container)
        cards_frame.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        for col in range(4):
            cards_frame.columnconfigure(col, weight=1)

        self._create_card(cards_frame, 0, "total_ventas", "Ventas totales")
        self._create_card(cards_frame, 1, "ticket_promedio", "Ticket promedio")
        self._create_card(cards_frame, 2, "cantidad_operaciones", "Operaciones")
        self._create_card(cards_frame, 3, "clientes_unicos", "Clientes únicos")

        # ====== AYUDA ======
        ttk.Label(
            container,
            text=(
                "Usa el menú para ir a importación de datos, análisis de ventas y estadísticas.\n"
                "Cuando vuelvas a importar nuevos datos, este resumen se actualizará automáticamente."
            ),
            style="DashboardSubtitle.TLabel",
            wraplength=820,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(0, 0))

        # Logo responsive: escuchamos el resize del toplevel (más fiable)
        self.winfo_toplevel().bind("<Configure>", self._on_window_resize)

    # ========= Logo responsive =========

    def _load_logo(self, path: str) -> None:
        """Carga imagen base (PIL) si está disponible, sino deja el texto [Logo]."""
        if not self._logo_label:
            return

        try:
            from PIL import Image, ImageTk  # type: ignore

            self._PIL_Image = Image
            self._PIL_ImageTk = ImageTk

            self._logo_base = self._PIL_Image.open(path)
        except Exception:
            self._logo_base = None
            self._logo_label.configure(text="[Logo]")

    def _set_logo_size(self, size: int) -> None:
        """Redimensiona el logo a `size`x`size` y actualiza el label manteniendo la referencia."""
        if not self._logo_base or not self._logo_label:
            return

        img = self._logo_base.copy().resize((size, size))
        self._logo_img = self._PIL_ImageTk.PhotoImage(img)  # mantener referencia
        self._logo_label.configure(image=self._logo_img, text="")

    def _on_window_resize(self, event: tk.Event) -> None:
        """Throttle para no redimensionar el logo demasiadas veces por segundo."""
        if not self._logo_base or not self._logo_label:
            return

        if self._logo_after_id:
            self.after_cancel(self._logo_after_id)

        def do_resize() -> None:
            # Ajuste en función del ancho (con límites)
            w = max(420, self.winfo_width())
            size = int(w * 0.18)
            size = max(110, min(size, 190))
            self._set_logo_size(size)

        self._logo_after_id = self.after(90, do_resize)

    # ========= Cards =========

    def _create_card(self, parent: ttk.Frame, grid_col: int, key: str, title: str) -> None:
        """Crea una tarjeta KPI y guarda la referencia del label de valor en `self._cards[key]`."""
        card = ttk.Frame(parent, style="DashboardCard.TFrame", padding=12)
        card.grid(row=0, column=grid_col, padx=10, sticky="nsew")

        title_label = ttk.Label(card, text=title, style="DashboardCardTitle.TLabel")
        title_label.pack(anchor="w", pady=(0, 6))

        value_label = ttk.Label(card, text="—", style="DashboardCardValue.TLabel")
        value_label.pack(anchor="center", pady=(10, 0))

        self._cards[key] = value_label

        # Hover: cambiamos estilo del frame y de los labels (para evitar “sombras”/bloques raros)
        def set_hover(on: bool) -> None:
            card.configure(style="DashboardCardHover.TFrame" if on else "DashboardCard.TFrame")
            title_label.configure(style="DashboardCardTitleHover.TLabel" if on else "DashboardCardTitle.TLabel")
            value_label.configure(style="DashboardCardValueHover.TLabel" if on else "DashboardCardValue.TLabel")

        for w in (card, title_label, value_label):
            w.bind("<Enter>", lambda e: set_hover(True))
            w.bind("<Leave>", lambda e: set_hover(False))

    # ========= API pública =========

    def refresh(self) -> None:
        """Actualiza las métricas del dashboard a partir del repositorio."""
        if not self._cards:
            return

        try:
            summary = self.app.repository.get_summary()
        except Exception:
            summary = None

        if not isinstance(summary, dict) or not summary:
            for label in self._cards.values():
                label.config(text="–")
            self.app.set_status("Sin datos de ventas todavía. Importa un archivo desde 'Importar datos'.")
            return

        def to_float(v, default=0.0) -> float:
            try:
                return default if v is None else float(v)
            except Exception:
                return default

        def to_int(v, default=0) -> int:
            try:
                return default if v is None else int(float(v))
            except Exception:
                return default

        total = to_float(summary.get("total_ventas"))
        ticket = to_float(summary.get("ticket_promedio"))
        ops = to_int(summary.get("cantidad_operaciones"))
        clientes = to_int(summary.get("clientes_unicos"))

        self._cards["total_ventas"].config(text=f"{total:,.2f} {CURRENCY_SYMBOL}".replace(",", " "))
        self._cards["ticket_promedio"].config(text=f"{ticket:,.2f} {CURRENCY_SYMBOL}".replace(",", " "))
        self._cards["cantidad_operaciones"].config(text=f"{ops:,}".replace(",", "."))
        self._cards["clientes_unicos"].config(text=f"{clientes:,}".replace(",", "."))

        self.app.set_status("Dashboard actualizado con las últimas métricas de ventas.")
    
    # ========= Estilos =========
    def _configure_styles(self, style: ttk.Style) -> None:  
        """Configura los estilos del dashboard (tarjetas, subtítulos, separadores)."""
        # --------- Estilos generales ----------
        style.configure("DashboardSubtitle.TLabel", font=("TkDefaultFont", 10), foreground="#555555")
        
        # Tarjetas (normal / hover)
        style.configure("DashboardCard.TFrame", background="#F9FAFB", relief="solid", borderwidth=1)
        style.configure("DashboardCardHover.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)
        
        # Labels dentro de tarjetas (normal / hover)
        style.configure("DashboardCardTitle.TLabel", background="#F9FAFB", foreground="#111827", font=("TkDefaultFont", 12, "bold"))
        style.configure("DashboardCardValue.TLabel", background="#F9FAFB", foreground="#111827", font=("TkDefaultFont", 22, "bold"))

        style.configure("DashboardCardTitleHover.TLabel", background="#FFFFFF", foreground="#111827", font=("TkDefaultFont", 12, "bold"))
        style.configure("DashboardCardValueHover.TLabel", background="#FFFFFF", foreground="#111827", font=("TkDefaultFont", 22, "bold"))