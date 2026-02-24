from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd

import matplotlib
matplotlib.use("TkAgg")  # <-- clave en Mac/Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .base_view import BaseView
from config import CURRENCY_SYMBOL


class EstadisticasView(BaseView):
    """Pantalla de estadísticas y gráficas de ventas."""

    def __init__(self, parent, app) -> None:
        self._canvases: list[FigureCanvasTkAgg] = []
        super().__init__(parent, app)

    def _build(self) -> None:
        # Cabecera
        header = ttk.Label(self, text="Estadísticas de ventas", style="Header.TLabel")
        header.pack(anchor="w", pady=(10, 5), padx=10)

        # Botón de actualización
        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(controls, text="Actualizar gráficas", command=self.refresh).pack(side="left")

        # Mensaje guía
        ttk.Label(
            self,
            text=(
                "Importa datos desde la pestaña 'Importar datos a Sales Desktop CRM' para ver "
                "las gráficas de evolución de ventas."
            ),
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # Contenedor principal de gráficos
        self.charts_frame = ttk.Frame(self)
        self.charts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Un solo gráfico (full width)
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)

        self.refresh()

    # ==== Utilidades internas ====

    def _clear_charts(self) -> None:
        """Destruye canvases y widgets de gráficos para reconstruirlos desde cero."""
        for canvas in self._canvases:
            canvas.get_tk_widget().destroy()
        self._canvases.clear()

        for w in self.charts_frame.winfo_children():
            w.destroy()

    def _add_chart(self, parent: tk.Widget, title: str) -> tuple[FigureCanvasTkAgg, any]:
        """Crea un Figure + Canvas Tkinter dentro de parent y devuelve (canvas, ax)."""
        # un poco más grande para que se vea “pro”
        fig = Figure(figsize=(7.5, 4.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(title)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

        self._canvases.append(canvas)
        return canvas, ax

    def _annotate_bars(self, ax, bars, y_values) -> None:
        """
        Anota valores arriba de las barras.
        - Formatea miles estilo AR (15.000)
        - Muestra moneda delante ($15.000)
        - Ajusta ylim dinámicamente
        - Robusto (no rompe si viene Series/np.array)
        """
        if y_values is None:
            return

        values = list(y_values)
        if not values:
            return

        # Convertimos a float defensivo para cálculos
        numeric_vals: list[float] = []
        for v in values:
            try:
                fv = float(v)
                if fv != fv:  # NaN
                    fv = 0.0
                numeric_vals.append(fv)
            except Exception:
                numeric_vals.append(0.0)

        ymax = max(numeric_vals) if numeric_vals else 0.0
        ylim_max = max(ymax * 1.20, 1.0)
        ax.set_ylim(0, ylim_max)

        offset = ylim_max * 0.03

        def format_number(v: float) -> str:
            # miles con punto y sin decimales
            formatted = f"{int(round(v)):,}".replace(",", ".")
            return f"{CURRENCY_SYMBOL}{formatted}"

        for bar, raw_val, valor in zip(bars, values, numeric_vals):
            if valor <= 0:
                continue

            # Si ya viene string, lo respetamos; si no, formateamos
            label = raw_val if isinstance(raw_val, str) else format_number(valor)

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                valor + offset,
                label,
                ha="center",
                va="bottom",
                fontsize=10,
                clip_on=False,
            )

    # ==== API pública ====

    def refresh(self) -> None:
        """Regenera las gráficas a partir de los datos de ventas cargados en el repositorio."""
        self._clear_charts()

        df = self.app.repository.get_all_sales()
        if df is None or df.empty:
            self.app.set_status("No hay datos cargados para mostrar estadísticas.")
            return

        required_cols = {"fecha", "producto", "importe"}
        if not required_cols.issubset(df.columns):
            messagebox.showerror(
                "Datos incompletos",
                "No se encontraron las columnas necesarias ('fecha', 'producto', 'importe') en el dataset.",
            )
            return

        # Tipos y limpieza
        df = df.copy()
        df["importe"] = pd.to_numeric(df["importe"], errors="coerce")
        df = df.dropna(subset=["importe"])

        if df.empty:
            messagebox.showinfo(
                "Sin datos válidos",
                "No hay datos válidos de ventas para generar las gráficas.",
            )
            self.app.set_status("No hay importes válidos para estadísticas.")
            return

        # ====== Layout: 1 chart (full width) ======
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)

        frame = ttk.LabelFrame(self.charts_frame, text="Total ventas por producto")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=0)

        try:
            series_por_producto = (
                df.groupby("producto")["importe"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            if series_por_producto.empty:
                self.app.set_status("No hay productos para graficar.")
                return

            canvas, ax = self._add_chart(frame, "Total ventas por producto (Top 10)")

            x = list(range(len(series_por_producto)))
            y = series_por_producto.values
            bars = ax.bar(x, y)

            etiquetas = [str(p) for p in series_por_producto.index]
            ax.set_xticks(x)
            ax.set_xticklabels(etiquetas, rotation=25, ha="right")

            ax.set_xlabel("Producto")
            ax.set_ylabel("Importe")
            ax.grid(axis="y", linestyle="--", alpha=0.4)

            self._annotate_bars(ax, bars, y)

            canvas.figure.tight_layout()
            canvas.draw()

            self.app.set_status("Gráfica de estadísticas actualizada.")

        except Exception as e:
            messagebox.showerror(
                "Error al generar gráfica de productos",
                f"Ocurrió un error al generar la gráfica por productos:\n\n{e}",
            )
            self.app.set_status("Error al generar gráfica.")
            return