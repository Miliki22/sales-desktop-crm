from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from .ventas_constants import ESTADOS_CRM

def open_client_dialog(view, mode: str = "new") -> None:
    """Abre un diálogo modal para crear o editar un cliente.

    Args:
        view: instancia de VentasView (necesita view.app, view.refresh y view._get_selected_iid()).
        mode: "new" para alta, "edit" para editar seleccionado.
    """
    editing = mode == "edit"
    initial_data = {
        "fecha_alta": "",
        "nombre": "",
        "email": "",
        "telefono": "",
        "estado": ESTADOS_CRM[0],
        "nota": "",
    }
    row_index: int | None = None

    if editing:
        iid = view._get_selected_iid()
        if iid is None:
            return
        row_index = int(iid)

        df = view.app.repository.get_all_clients()
        if df is None or row_index not in df.index:
            messagebox.showerror(
                "Error",
                "No se pudo encontrar el cliente seleccionado.",
            )
            return

        row = df.loc[row_index]
        initial_data = {
            "fecha_alta": str(row.get("fecha_alta", "")),
            "nombre": str(row.get("nombre", "")),
            "email": str(row.get("email", "")),
            "telefono": str(row.get("telefono", "")),
            "estado": str(row.get("estado", ESTADOS_CRM[0])),
            "nota": str(row.get("nota", "")),
        }

    win = tk.Toplevel(view)
    win.title("Editar cliente" if editing else "Nuevo cliente / oportunidad")
    win.transient(view.winfo_toplevel())
    win.grab_set()
    win.resizable(False, False)

    frame = ttk.Frame(win, padding=10)
    frame.pack(fill="both", expand=True)

    entries: dict[str, tk.Widget] = {}

    def add_row(
        label_text: str,
        key: str,
        widget_type: str = "entry",
        **kwargs,
    ) -> None:
        row_frame = ttk.Frame(frame)
        row_frame.pack(fill="x", pady=3)

        ttk.Label(row_frame, text=label_text, width=15).pack(side="left")

        if widget_type == "entry":
            widget: tk.Widget = ttk.Entry(row_frame)
            widget.insert(0, initial_data.get(key, ""))
        elif widget_type == "combo":
            widget = ttk.Combobox(
                row_frame,
                state="readonly",
                values=kwargs.get("values", ESTADOS_CRM),
            )
            values = widget["values"]
            current_value = initial_data.get(key, ESTADOS_CRM[0])
            try:
                widget.current(values.index(current_value))
            except ValueError:
                widget.current(0)
        else:
            widget = ttk.Entry(row_frame)

        widget.pack(side="left", fill="x", expand=True)
        entries[key] = widget

    add_row("Nombre", "nombre")
    add_row("Email", "email")
    add_row("Teléfono", "telefono")
    add_row(
        "Estado",
        "estado",
        widget_type="combo",
        values=ESTADOS_CRM,
    )
    add_row("Nota", "nota")

    # Botones
    buttons = ttk.Frame(frame)
    buttons.pack(fill="x", pady=(10, 0))

    def on_save() -> None:
        nombre = entries["nombre"].get().strip()
        if not nombre:
            messagebox.showwarning(
                "Datos incompletos",
                "El nombre del cliente es obligatorio.",
            )
            return
        
        fecha_alta = (
                initial_data.get("fecha_alta") if editing and initial_data.get("fecha_alta")
                else date.today().strftime("%Y-%m-%d")
        )
        data = {
            "fecha_alta": fecha_alta,
            "nombre": nombre,
            "email": entries["email"].get().strip(),
            "telefono": entries["telefono"].get().strip(),
            "estado": entries["estado"].get().strip(),
            "nota": entries["nota"].get().strip(),
        }

        try:
            if editing and row_index is not None:
                view.app.repository.update_client(row_index, data)
            else:
                view.app.repository.add_client(data)
        except Exception as e:  # defensivo
            messagebox.showerror(
                "Error al guardar",
                f"Ocurrió un error al guardar el cliente:\n\n{e}",
            )
            return

        view.refresh()
        win.destroy()

    ttk.Button(buttons, text="Guardar", command=on_save).pack(side="right")
    ttk.Button(buttons, text="Cancelar", command=win.destroy).pack(
        side="right", padx=(0, 5)
    )

def delete_selected_client(view) -> None:
    """Elimina el cliente seleccionado del CRM (con confirmación)."""
    iid = view._get_selected_iid()
    if iid is None:
        return

    row_index = int(iid)

    resp = messagebox.askyesno(
        "Confirmar eliminación",
        "¿Seguro que quieres eliminar este cliente del CRM?",
    )
    if not resp:
        return

    try:
        view.app.repository.delete_client(row_index)
    except Exception as e:  # defensivo
        messagebox.showerror(
            "Error al eliminar",
            f"Ocurrió un error al eliminar el cliente:\n\n{e}",
        )
        return

    view.refresh()