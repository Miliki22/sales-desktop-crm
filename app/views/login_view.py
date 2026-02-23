from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .base_view import BaseView

class LoginView(BaseView):
    """Pantalla de inicio de sesión reutilizable.
    
    Diseñada para desacoplar la interfaz de usuario
    del mecanismo de autenticación, permitiendo
    su reutilización en otras aplicaciones de la empresa.
    """
    def _build(self) -> None:
        # Card principal
        card = ttk.LabelFrame(self, text="Inicio de sesión")
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Usuario
        ttk.Label(card, text="Usuario").grid(
            row=0, column=0, sticky="w", pady=5, padx=10
        )
        self.user_entry = ttk.Entry(card, width=30)
        self.user_entry.grid(row=0, column=1, pady=5, padx=10)

        # Contraseña
        ttk.Label(card, text="Contraseña").grid(
            row=1, column=0, sticky="w", pady=5, padx=10
        )
        self.password_entry = ttk.Entry(card, show="•", width=30)
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)

        # Fila de botones
        button_row = ttk.Frame(card)
        button_row.grid(row=2, column=0, columnspan=2, pady=(15, 0))

        ttk.Button(
            button_row,
            text="Ingresar",
            command=lambda: self.app.show_view("dashboard"),
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_row,
            text="Limpiar",
            command=self._clear_fields,
        ).pack(side=tk.RIGHT, padx=5)

    def _clear_fields(self) -> None:
        """Limpia los campos del formulario."""
        self.user_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def on_show(self) -> None:
        """Cuando se muestra la vista, poner el foco en usuario."""
        self.user_entry.focus_set()