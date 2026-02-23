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

        # Mensaje guía (arriba, antes de los charts)
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

        # Grid para 2 gráficos lado a lado
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.columnconfigure(1, weight=1)
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
        fig = Figure(figsize=(5, 3), dpi=100)
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
        - Soporta números o strings ya formateados
        """

        if y_values is None:
            return

        # Convertimos a lista sin romper si viene np.array / pd.Series
        values = list(y_values)

        if len(values) == 0:
            return

        # Detectar valores numéricos reales para calcular límites
        numeric_vals = []
        for v in values:
            try:
                numeric_vals.append(float(v))
            except Exception:
                numeric_vals.append(0.0)
        
        ymax = max(numeric_vals) if numeric_vals else 0.0
        ylim_max = max(ymax * 1.20, 1.0)
        ax.set_ylim(0, ylim_max)

        offset = ylim_max * 0.03

        def format_number(v: float) -> str:
            formatted = f"{int(round(v)):,}".replace(",", ".")
            return f"{CURRENCY_SYMBOL}{formatted}"

        for bar, raw_val in zip(bars, values):
            height = bar.get_height()

            if isinstance(raw_val, str):
                label = raw_val
            else:
                try:
                    label = format_number(float(raw_val))
                except Exception:
                    label = str(raw_val)
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + offset,
                label,
                ha="center",
                va="bottom",
                fontsize=9,
                clip_on=True,
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
                "No se encontraron las columnas necesarias "
                "('fecha', 'producto', 'importe') en el dataset.",
            )
            return

        # Aseguramos tipos
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

        # ====== Layout: 2 charts lado a lado ======
        left = ttk.LabelFrame(self.charts_frame, text="Ventas por día")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        right = ttk.LabelFrame(self.charts_frame, text="Cursos trading - Total ventas")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        # ========== Gráfico 1: Ventas por día (barras) ==========
        try:
            df_fechas = df.copy()
            df_fechas["fecha"] = pd.to_datetime(df_fechas["fecha"], errors="coerce")
            df_fechas = df_fechas.dropna(subset=["fecha"])
            df_fechas["fecha_dia"] = df_fechas["fecha"].dt.date

            series_por_dia = df_fechas.groupby("fecha_dia")["importe"].sum().sort_index()
            if series_por_dia.empty:
                messagebox.showinfo("No hay fechas válidas para graficar por día.")
                return

            canvas_fecha, ax_fecha = self._add_chart(left, "Ventas por día")

            x = list(range(len(series_por_dia)))
            y = series_por_dia.values

            bars = ax_fecha.bar(x, y)
            labels = [pd.to_datetime(d).strftime("%d-%m-%Y") for d in series_por_dia.index]

            ax_fecha.set_xticks(x)
            ax_fecha.set_xticklabels(labels, rotation=30, ha="right")
            ax_fecha.set_xlabel("Fecha")
            ax_fecha.set_ylabel("Importe")
            ax_fecha.grid(axis="y", linestyle="--", alpha=0.4)

            self._annotate_bars(ax_fecha, bars, y)

            canvas_fecha.figure.tight_layout()
            canvas_fecha.draw()

        except Exception as e:
            messagebox.showerror(
                "Error al generar gráfica de fechas",
                f"Ocurrió un error al generar la gráfica por fechas:\n\n{e}",
            )
            return

        # ========== Gráfico 2: Ventas por producto (Top N) ==========
        try:
            df_prod = df.copy()
            df_prod["producto"] = df_prod["producto"].astype(str).str.strip()

            series_por_producto = (
                df_prod.groupby("producto")["importe"]
                .sum()
                .sort_values(ascending=False)
            )

            if series_por_producto.empty:
                canvas_prod, ax_prod = self._add_chart(right, "Total ventas por producto")
                ax_prod.text(
                    0.5, 0.5, "Sin datos de producto para graficar",
                    ha="center", va="center", transform=ax_prod.transAxes
                )
                ax_prod.set_axis_off()
                canvas_prod.draw()
            else:
                TOP_N = 10  # ajustable
                series_top = series_por_producto.head(TOP_N)

                canvas_prod, ax_prod = self._add_chart(right, "Total ventas por producto (Top 10)")

                x = list(range(len(series_top)))
                y = series_top.values
                bars = ax_prod.bar(x, y)

                ax_prod.set_xticks(x)
                ax_prod.set_xticklabels(series_top.index.tolist(), rotation=25, ha="right")
                ax_prod.set_xlabel("Producto")
                ax_prod.set_ylabel("Importe")
                ax_prod.grid(axis="y", linestyle="--", alpha=0.4)

                # Etiquetas más lindas (15.000 en vez de 15000)
                y_labels = [f"{int(v):,}".replace(",", ".") for v in y]
                self._annotate_bars(ax_prod, bars, y_labels)

                canvas_prod.figure.tight_layout()
                canvas_prod.draw()

        except Exception as e:
            messagebox.showerror(
                "Error al generar gráfica de productos",
                f"Ocurrió un error al generar la gráfica por productos:\n\n{e}",
          )
            return