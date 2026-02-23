from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from ..base_view import BaseView
from .ventas_dialogs import open_client_dialog, delete_selected_client
from .ventas_constants import ESTADOS_CRM, CRM_COLUMNS, CRM_HEADINGS, CRM_STATE_TAGS, CRM_STATE_COLORS, estado_to_tag

class VentasView(BaseView):
    """Vista de CRM: clientes potenciales y oportunidades de venta."""

    def __init__(self, parent, app) -> None:
        # Atributos propios de la vista
        self._tree: ttk.Treeview | None = None
        self._hover_iid: str | None = None
        self._estado_var: tk.StringVar | None = None
        self._headings: dict[str, str] = {}
        self._sort_state: dict[str, bool] = {}  # col -> descending?

        # BaseView llamará internamente a _build()
        super().__init__(parent, app)

        # Cargamos datos
        self.refresh()

    # ========= Construcción de UI =========

    def _build(self) -> None:
        # ====== Estilos específicos del CRM ======
        style = ttk.Style(self)

        # Font general moderna (un poco más grande)
        base_font = ("Segoe UI", 11)
        header_font = ("Segoe UI", 11, "bold")

        # Botones del CRM (tono oscuro Sales Desktop CRM)
        style.configure("CRM.TButton", padding=(10, 4), font=base_font)

        # Treeview del CRM
        style.configure("CRM.Treeview",font=base_font, rowheight=26)
        style.configure("CRM.Treeview.Heading",font=header_font)

        # Cabecera
        header = ttk.Label(self, text="CRM de clientes", style="Header.TLabel")
        header.pack(anchor="w", pady=(10, 0), padx=10)

        # Barra de acciones
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        # --- Botones de la barra ---
        buttons = [
            ("Nuevo cliente", self._open_new_client_dialog),
            ("Refrescar", self.refresh),
            ("Editar", self._edit_selected_client),
            ("Eliminar", self._delete_selected_client),
            ("Exportar CSV", self._export_csv),
        ]

        for idx, (text, cmd) in enumerate(buttons):
            padx = (0, 0)
            # Separamos un poco "Editar" del bloque Nuevo/Refrescar
            if text == "Editar":
                padx = (15, 0)
            elif text in ("Refrescar", "Eliminar"):
                padx = (5, 0)

            ttk.Button(
                toolbar,
                text=text,
                style="CRM.TButton",
                command=cmd,
            ).pack(side="left", padx=padx)

        # Filtro por estado
        ttk.Label(toolbar, text="Estado:").pack(side="left", padx=(20, 5))
        self._estado_var = tk.StringVar(value="Todos")
        combo_estado = ttk.Combobox(
            toolbar,
            textvariable=self._estado_var,
            state="readonly",
            values=["Todos", *ESTADOS_CRM],
            width=15,
        )
        combo_estado.pack(side="left")
        combo_estado.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Frame que contiene la tabla + scroll
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Tabla principal (Treeview)
        columns = CRM_COLUMNS
        tree = ttk.Treeview(tree_frame, columns=columns,show="headings", style="CRM.Treeview")
        self._tree = tree

        # Tag para hover sobre filas
        tree.tag_configure("hover", background="#e3f2fd")

        # Eventos de ratón para sombrear fila al pasar por encima
        tree.bind("<Motion>", self._on_tree_motion)
        tree.bind("<Leave>", self._on_tree_leave)

        self._headings = CRM_HEADINGS

        for col in columns:
            # Cabecera clicable para ordenar
            tree.heading(col, text=self._headings[col], command=lambda c=col: self._sort_by(c))
            
            # Anchuras razonables
            if col == "nota":
                width = 220
            elif col == "nombre":
                width = 160
            else:
                width = 120

            anchor = "center" if col == "estado" else "w"
            tree.column(col, width=width, anchor=anchor)

        # Scroll vertical
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Colores por estado (solo texto, para mantenerlo elegante)
        for estado, tag in CRM_STATE_TAGS.items():
            color = CRM_STATE_COLORS.get(estado)
            if color:
                tree.tag_configure(tag, foreground=color)
                
        # Texto guía
        ttk.Label(
            self,
            text=(
                "Gestiona clientes potenciales y oportunidades de venta.\n"
                "Usa 'Nuevo cliente' para añadir leads y 'Refrescar' para actualizar la tabla."
            ),
        ).pack(anchor="w", padx=10, pady=(0, 10))

    # ========= API pública de la vista =========

    def refresh(self) -> None:
        """Recarga los datos del CRM en la tabla, aplicando filtros."""
        if self._tree is None:
            return

        # Intentamos usar lo que haya en memoria; si no, leemos de disco
        df = self.app.repository.get_all_clients()
        if df is None:
            df = self.app.repository.load_clients()

        # Aplicamos filtro por estado (si corresponde)
        estado_filtro = self._estado_var.get() if self._estado_var else "Todos"
        if df is None or df.empty:
            self._populate_tree(None)
            self.app.set_status("Sin clientes todavía. Usa 'Nuevo cliente' para dar de alta el primero.")
            return

        if estado_filtro and estado_filtro != "Todos":
            df_filtrado = df[df["estado"] == estado_filtro].copy()
        else:
            df_filtrado = df.copy()

        self._populate_tree(df_filtrado)
        self.app.set_status(
            f"CRM cargado: {len(df_filtrado)} cliente(s) visible(s) con los filtros actuales."
        )

    def _export_csv(self) -> None:
        """Exporta el CRM filtrado o completo a un CSV."""
        from tkinter import filedialog

        df = self.app.repository.get_all_clients()
        if df is None or df.empty:
            messagebox.showinfo("Exportar CSV", "No hay datos para exportar.")
            return

        # Aplicamos filtro activo
        estado_filtro = self._estado_var.get()
        if estado_filtro != "Todos":
            df = df[df["estado"] == estado_filtro].copy()

        # Selecciona ubicación
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Guardar CRM como CSV"
        )

        if not file_path:
            return

        # Guardar CSV
        df.to_csv(file_path, index=False)

        messagebox.showinfo("Exportación completa", f"CRM exportado correctamente a:\n{file_path}")

    # ========= Utilidades internas =========

    def _populate_tree(self, df) -> None:
        """Vuelca un DataFrame en la tabla con zebra stripes y colores por estado."""
        tree = self._tree
        if tree is None:
            return

        tree.delete(*tree.get_children())

        if df is None or df.empty:
            return

        for visual_idx, (df_index, row) in enumerate(df.iterrows()):
            estado = str(row.get("estado", ""))
            estado_tag = estado_to_tag(estado)

            values = [
                row.get("fecha_alta", ""),
                row.get("nombre", ""),
                row.get("email", ""),
                row.get("telefono", ""),
                estado,
                row.get("nota", ""),
            ]

            # zebra + posible color por estado
            tags = []
            if visual_idx % 2:
                tags.append("odd")
            if estado_tag:
                tags.append(estado_tag)

            tree.insert(
                "",
                "end",
                iid=str(df_index),
                values=values,
                tags=tuple(tags),
            )

    def _sort_by(self, col: str) -> None:
        """Ordena la tabla por la columna dada, alternando asc/desc."""
        tree = self._tree
        if tree is None:
            return

        items = list(tree.get_children())
        if not items:
            return

        # Estado actual de orden para esa columna
        descending = self._sort_state.get(col, False)

        def _key(item_id: str):
            idx = tree["columns"].index(col)
            value = tree.item(item_id, "values")[idx]
            return value

        items_sorted = sorted(items, key=_key, reverse=descending)

        for pos, item_id in enumerate(items_sorted):
            tree.move(item_id, "", pos)

        # Alternamos el estado para la próxima vez
        self._sort_state[col] = not descending

    def _get_selected_iid(self) -> str | None:
        """Devuelve el iid seleccionado en la tabla (índice del DataFrame)."""
        tree = self._tree
        if tree is None:
            return None

        selection = tree.selection()
        if not selection:
            messagebox.showinfo(
                "Seleccionar cliente",
                "Selecciona primero un cliente de la tabla.",
            )
            return None

        return selection[0]

    # ========= Diálogo: nuevo cliente =========

    def _open_new_client_dialog(self) -> None:
        """Abre un diálogo modal para crear un nuevo cliente/oportunidad."""
        open_client_dialog(self, mode="new")
    
    # ========= Acciones de edición / borrado =========

    def _edit_selected_client(self) -> None:
        """Edita el cliente seleccionado en la tabla."""
        open_client_dialog(self, mode="edit")

    def _delete_selected_client(self) -> None:
        """Elimina el cliente seleccionado del CRM (con confirmación)."""
        delete_selected_client(self)

    # ========= Hover sobre filas =========

    def _on_tree_motion(self, event: tk.Event) -> None:
        """Sombrea la fila por la que pasa el ratón."""
        if self._tree is None:
            return

        row_id = self._tree.identify_row(event.y)

        # Si ya estamos sobre la misma fila, no hacemos nada
        if row_id == self._hover_iid:
            return

        # Quitamos hover anterior sin romper otros tags
        if self._hover_iid:
            old_tags = list(self._tree.item(self._hover_iid, "tags"))
            if "hover" in old_tags:
                old_tags.remove("hover")
                self._tree.item(self._hover_iid, tags=tuple(old_tags))
        
        self._hover_iid = row_id or None

        # Aplicamos hover nuevo
        if row_id:
            new_tags = list(self._tree.item(row_id, "tags"))
            if "hover" not in new_tags:
                new_tags.append("hover")
                self._tree.item(row_id, tags=tuple(new_tags))

    def _on_tree_leave(self, event: tk.Event) -> None:
        """Limpia el hover cuando el ratón sale del Treeview."""
        if self._tree is None or self._hover_iid is None:
            return

        old_tags = list(self._tree.item(self._hover_iid, "tags"))
        if "hover" in old_tags:
            old_tags.remove("hover")
        self._tree.item(self._hover_iid, tags=tuple(old_tags))

        self._hover_iid = None