from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.desktop_app import DesktopApp


class BaseView(ttk.Frame):
    """
    Vista base para todas las pantallas de la app.

    Proporciona:
      - Referencia al controlador principal (DesktopApp)
      - Hooks on_show / on_hide para ejecutar lógica al mostrar/ocultar
    """

    def __init__(self, master: tk.Widget, app: "DesktopApp", *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.app = app
        self.configure(padding=20)
        self._build()

    def _build(self) -> None:
        """Método que cada vista concreta debe implementar."""
        raise NotImplementedError

    def on_show(self) -> None:
        """Hook ejecutado cuando la vista pasa a ser visible."""
        pass

    def on_hide(self) -> None:
        """Hook ejecutado justo antes de ocultar la vista."""
        pass