from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import pandas as pd


def show_data_table_dialog(parent: tk.Widget, df: pd.DataFrame, title: str = "Datos importados") -> None:
    """
    Abre una ventana con una tabla scrolleable para ver TODO el DataFrame.
    """
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("1100x650")
    win.transient(parent.winfo_toplevel())
    win.grab_set()

    container = ttk.Frame(win, padding=10)
    container.pack(fill="both", expand=True)

    # Info arriba
    info = ttk.Label(
        container,
        text=f"Registros: {len(df)} | Columnas: {len(df.columns)}",
        font=("Segoe UI", 10, "bold"),
    )
    info.pack(anchor="w", pady=(0, 8))

    # Frame para tree + scrollbars
    table_frame = ttk.Frame(container)
    table_frame.pack(fill="both", expand=True)

    cols = list(df.columns)

    tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    # Encabezados + ancho aproximado
    def sort_column(col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        data.sort(reverse=reverse)
        for index, (val, k) in enumerate(data):
            tree.move(k, "", index)
        tree.heading(col, command=lambda: sort_column(col, not reverse))

    for c in cols:
        tree.heading(c, text=c, command=lambda _c=c: sort_column(_c, False))
        tree.column(c, width=140, anchor="w", stretch=True)

    df_display = df.copy()

    # Formatear fecha si es datetime
    if "fecha" in df_display.columns:
        df_display["fecha"] = df_display["fecha"].dt.strftime("%d-%m-%Y")

    # Formatear importe como moneda
    if "importe" in df_display.columns:
        df_display["importe"] = df_display["importe"].map(lambda x: f"${x:,.0f}")

    for row in df_display.itertuples(index=False, name=None):
        tree.insert("", "end", values=row)
    
    # Botón cerrar
    btns = ttk.Frame(container)
    btns.pack(fill="x", pady=(10, 0))
    ttk.Button(btns, text="Cerrar", command=win.destroy).pack(side="right")