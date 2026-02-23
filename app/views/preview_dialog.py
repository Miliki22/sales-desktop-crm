from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

import pandas as pd

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

from config import LOGO_PATH

def show_preview_dialog(parent: tk.Misc, df_preview: pd.DataFrame, total_rows: int) -> None:
    """Muestra un diálogo modal con una tabla para previsualizar filas.

    Incluye:
    - Tabla con scrollbar
    - Zebra stripes
    - Orden por columnas (toggle asc/desc)
    - Exportar CSV
    - Exportar PDF (reportlab)
    """
    win = tk.Toplevel(parent)
    win.title("Previsualización de datos")
    win.transient(parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent)
    win.grab_set()
    win.resizable(True, True)
    win.minsize(700, 400)

    # Centrar ventana
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"+{x}+{y}")

    # Texto superior
    info = ttk.Label(
        win,
        text=(
            f"Se cargaron {total_rows} filas. "
            f"Mostrando las primeras {len(df_preview)}:"
        ),
        anchor="w",
    )
    info.pack(fill="x", padx=10, pady=(10, 5))

    # Frame para la tabla + scroll
    frame = ttk.Frame(win, padding=10)
    frame.pack(fill="both", expand=True)

    columns = list(df_preview.columns)

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        height=min(len(df_preview) + 1, 25),
    )
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Auto-ajuste de columnas
    default_font = tkfont.nametofont("TkDefaultFont")

    # Zebra stripes
    tree.tag_configure("even", background="#F7F7F7")
    tree.tag_configure("odd", background="#FFFFFF")

    # Columnas ordenables
    sort_state: dict[str, bool] = {}

    def sort_by(col: str) -> None:
        """Ordena la tabla por la columna indicada (toggle asc/desc)."""
        descending = sort_state.get(col, False)
        sort_state[col] = not descending

        items = list(tree.get_children(""))
        if not items:
            return

        def try_num(value: str):
            try:
                return float(str(value).replace(",", "."))
            except Exception:
                return str(value)

        data = []
        for item in items:
            value = tree.set(item, col)
            data.append((try_num(value), item))

        data.sort(reverse=descending, key=lambda x: x[0])

        for index, (_, item) in enumerate(data):
            tree.move(item, "", index)

        # Reaplicamos zebra
        for idx, item in enumerate(tree.get_children("")):
            tag = "even" if idx % 2 == 0 else "odd"
            tree.item(item, tags=(tag,))

    # Configuración de cabeceras y anchuras
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_by(c))

        max_text = col
        for value in df_preview[col]:
            text = str(value)
            if len(text) > len(max_text):
                max_text = text

        width_px = default_font.measure(max_text + "   ")
        width_px = min(max(width_px, 80), 260)

        anchor = "e" if df_preview[col].dtype.kind in "if" else "w"
        tree.column(col, width=width_px, anchor=anchor, stretch=True)

    # Insertamos filas
    for idx, (_, row) in enumerate(df_preview.iterrows()):
        values = [row[col] for col in columns]
        tag = "even" if idx % 2 == 0 else "odd"
        tree.insert("", "end", values=values, tags=(tag,))

    # Botones inferiores
    btn_frame = ttk.Frame(win)
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))

    def export_csv() -> None:
        """Exporta SOLO las filas previsualizadas a CSV."""
        file_path = filedialog.asksaveasfilename(
            parent=win,
            title="Exportar previsualización a CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")],
        )
        if not file_path:
            return

        try:
            df_preview.to_csv(file_path, index=False)
            messagebox.showinfo(
                "Exportación completada",
                f"Se exportaron {len(df_preview)} filas a:\n{file_path}",
                parent=win,
            )
        except Exception as e:
            messagebox.showerror(
                "Error al exportar",
                f"No se pudo exportar el CSV:\n\n{e}",
                parent=win,
            )

    def export_pdf() -> None:
        """Exporta la previsualización a un PDF profesional."""
        file_path = filedialog.asksaveasfilename(
            parent=win,
            title="Exportar previsualización a PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not file_path:
            return

        try:
            pdf = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            elements = []

            # Logo (si falla, no rompe)
            try:
                img = Image(str(LOGO_PATH), width=60, height=60)
                img.hAlign = "CENTER"
                elements.append(img)
                elements.append(Paragraph("<br/>", styles["BodyText"]))
            except Exception:
                pass

            title = Paragraph(
                f"<b>Previsualización de datos</b><br/>"
                f"Total de filas: {total_rows} &nbsp;&nbsp;&nbsp; Mostrando: {len(df_preview)}",
                styles["Title"],
            )
            elements.append(title)
            elements.append(Paragraph("<br/>", styles["BodyText"]))

            data = [df_preview.columns.tolist()] + df_preview.values.tolist()

            table = Table(data)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                    ]
                )
            )

            elements.append(table)
            pdf.build(elements)

            messagebox.showinfo(
                "Exportación completada",
                f"PDF generado correctamente en:\n{file_path}",
                parent=win,
            )

        except Exception as e:
            messagebox.showerror(
                "Error al exportar PDF",
                f"No se pudo generar el PDF:\n\n{e}",
                parent=win,
            )

    ttk.Button(btn_frame, text="Exportar CSV", command=export_csv).pack(side="left")
    ttk.Button(btn_frame, text="Exportar PDF", command=export_pdf).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="OK", command=win.destroy).pack(side="right")

    win.update_idletasks()
    win.minsize(win.winfo_width(), win.winfo_height())