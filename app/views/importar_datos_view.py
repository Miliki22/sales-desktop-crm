from __future__ import annotations
from config import PREVIEW_ROWS
import pandas as pd
from pathlib import Path
from .data_table_dialog import show_data_table_dialog

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .base_view import BaseView
from app.core.data_loader import DataLoaderError
from .preview_dialog import show_preview_dialog


class ImportarDatosView(BaseView):
    """Pantalla para importar datos de ventas desde CSV / Excel / etc."""

    def _build(self) -> None:
        layout = ttk.LabelFrame(self, text="Importar datos a Sales Desktop CRM")
        layout.pack(fill="both", expand=True)

        # Ruta de archivo
        ttk.Label(layout, text="Archivo origen").grid(
            row=0, column=0, sticky="w", pady=10, padx=10
        )
        self.entry_path = ttk.Entry(layout, width=40)
        self.entry_path.grid(row=0, column=1, sticky="ew", pady=10, padx=10)
        ttk.Button(
            layout,
            text="Buscar",
            command=self._seleccionar_archivo,
        ).grid(row=0, column=2, padx=10)

        # Formato
        ttk.Label(layout, text="Formato").grid(row=1, column=0, sticky="w", padx=10)
        self.combo_formato = ttk.Combobox(
            layout,
            values=["CSV", "XLSX"],
            state="readonly",
        )
        self.combo_formato.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.combo_formato.set("CSV")

        # Botones de acción
        ttk.Button(
            layout,
            text="Previsualizar",
            command=self._previsualizar,
        ).grid(row=2, column=0, columnspan=1, pady=(20, 0), padx=10, sticky="w")

        ttk.Button(
           layout,
           text="Ver datos (tabla)",
           command=self._ver_datos,
        ).grid(row=2, column=1, pady=(20, 0), padx=10, sticky="w")

        ttk.Button(
            layout,
            text="Cargar demo",
            command=self._cargar_demo,
        ).grid(row=2, column=1, pady=(20, 0), padx=10)

        ttk.Button(
            layout,
            text="Importar a base de datos",
            command=self._importar,
        ).grid(row=2, column=2, pady=(20, 0), padx=10, sticky="e")

        layout.columnconfigure(1, weight=1)

    # ---------- Acciones ----------

    def _seleccionar_archivo(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de ventas",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls")],
        )
        if filepath:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, filepath)
            self.app.set_status(f"Archivo seleccionado: {filepath}")

    def _cargar_demo(self) -> None:
        """Carga rápida: setea en el input el CSV demo del repo."""
        demo_path = Path(__file__).resolve().parents[2] / "data" / "sample" / "ventas_demo.csv"

        if not demo_path.exists():
            messagebox.showerror(
                "Demo no encontrada",
                f"No se encontró el archivo demo en:\n{demo_path}",
            )
            self.app.set_status("No se encontró ventas_demo.csv")
            return

        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(0, str(demo_path))
        self.app.set_status("Demo cargada: ventas_demo.csv")

        # Opcional PRO: abrir preview automático
        # self._previsualizar()

    def _previsualizar(self) -> None:
        """Carga el archivo y muestra las primeras filas SIN tocar la base interna."""
        path = self.entry_path.get().strip()
        if not path:
            messagebox.showwarning("Archivo requerido", "Selecciona un archivo primero.")
            return

        try:
            # Usamos directamente el loader, NO guardamos en self.app.repository.data
            df = self.app.repository.loader.load(path)

            if df.empty:
                messagebox.showinfo(
                    "Previsualización de datos",
                    "El archivo se cargó correctamente pero no contiene filas.",
                )
                return

            total_rows = len(df)
            preview_rows = min(PREVIEW_ROWS, total_rows)

            # Solo tomamos las primeras N filas para mostrar
            df_preview = df.head(preview_rows).copy()

            # Abrimos el diálogo “premium”
            show_preview_dialog(self, df_preview, total_rows)

            self.app.set_status(
                f"Previsualización correcta: {total_rows} registros encontrados."
            )

        except DataLoaderError as e:
            messagebox.showerror(
                "Error al previsualizar",
                f"No se pudo leer el archivo:\n\n{e}",
            )
            self.app.set_status("Error al previsualizar datos.")
        except Exception as e:
            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un error no esperado al previsualizar:\n\n{e}",
            )
            self.app.set_status("Error inesperado al previsualizar datos.")
        
    def _importar(self) -> None:
        """Carga el archivo y ACTUALIZA la base de datos interna."""
        path = self.entry_path.get().strip()
        if not path:
            messagebox.showwarning("Archivo requerido", "Selecciona un archivo primero.")
            return

        try:
            # Aquí sí actualizamos el repositorio central
            df = self.app.repository.load_sales(path)

            messagebox.showinfo(
                "Importación completa",
                f"Los datos de ventas se importaron correctamente.\n"
                f"Total de registros: {len(df)}",
            )
            self.app.set_status(
                f"Importación correcta: {len(df)} registros disponibles para análisis."
            )

            # Si existe la vista de dashboard, la refrescamos
            dashboard_view = self.app.get_view("dashboard")
            if dashboard_view:
                dashboard_view.refresh()

        except DataLoaderError as e:
            messagebox.showerror(
                "Error al importar datos",
                f"No se pudo importar el archivo:\n\n{e}",
            )
            self.app.set_status("Error al importar datos.")
        except Exception as e:
            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un error no esperado al importar:\n\n{e}",
            )
            self.app.set_status("Error inesperado al importar datos.")

    def _ver_datos(self) -> None:
        """Muestra una tabla con TODO el dataset cargado en memoria."""
        df = self.app.repository.get_all_sales()

        if df is None or df.empty:
            messagebox.showwarning(
                "Sin datos",
                "Todavía no hay datos cargados.\n\nPrimero importá un CSV o usá 'Cargar demo'.",
            )
            return

        show_data_table_dialog(self, df, title="Ventas importadas (tabla completa)")
    
