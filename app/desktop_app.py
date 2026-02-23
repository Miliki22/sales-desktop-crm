from __future__ import annotations
from app.core.repository import Repository
from config import APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, LOGO_PATH

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Type
from app.views.base_view import BaseView

from PIL import Image, ImageTk

from app.views.dashboard_view import DashboardView
from app.views.importar_datos_view import ImportarDatosView
from app.views import VentasView
from app.views.estadisticas_view import EstadisticasView

class DesktopApp(tk.Tk):
    """Aplicación principal del Analizador de Ventas Sales Desktop CRM."""

    def __init__(self) -> None:
        super().__init__()

        # Repositorio central de datos
        self.repository = Repository()

        # Estado interno de vistas
        self._views: Dict[str, BaseView] = {}
        self._current_view: Optional[BaseView] = None

        # Cargar logo e icono
        self._load_logo()

        # Al inicio ocultamos la ventana principal y mostramos un splash
        self.withdraw()
        self._show_splash()

    ######  Inicialización visual. ######

    def _load_logo(self) -> None:
        """Carga las imágenes de logo para icono y splash."""
        logo_path = str(LOGO_PATH)

        # Icono pequeño de la aplicación
        logo_image_small = Image.open(logo_path)
        logo_image_small = logo_image_small.resize((40, 40))
        self.logo_icon = ImageTk.PhotoImage(logo_image_small)

        # Logo más grande para splash
        logo_image_big = Image.open(logo_path)
        logo_image_big = logo_image_big.resize((120, 120))
        self.logo_splash = ImageTk.PhotoImage(logo_image_big)

        # Asignar icono a la app (dock / barra de tareas)
        self.iconphoto(False, self.logo_icon)

    def _show_splash(self) -> None:
        """Muestra una ventana splash antes de cargar la UI principal."""

        splash = tk.Toplevel(self)
        splash.overrideredirect(True)  # sin bordes/controles
        splash.configure(bg="black")

        # Centrar splash en pantalla
        splash.update_idletasks()
        w, h = 320, 260
        sw = splash.winfo_screenwidth()
        sh = splash.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        splash.geometry(f"{w}x{h}+{x}+{y}")

        # Contenido del splash
        logo_label = tk.Label(splash, image=self.logo_splash, bg="black")
        logo_label.pack(pady=20)

        title_label = tk.Label(
            splash,
            text="Demo Company",
            fg="white",
            bg="black",
            font=("Segoe UI", 14, "bold"),
        )
        title_label.pack(pady=5)

        self._splash_status = tk.StringVar(value="Cargando aplicación…")
        status_label = tk.Label(
            splash,
            textvariable=self._splash_status,
            fg="white",
            bg="black",
            font=("Segoe UI", 10),
        )
        status_label.pack(pady=10)

        # Pequeña animación de puntos "…"
        def animate_dots(step: int = 0) -> None:
            dots = "." * ((step % 3) + 1)
            self._splash_status.set(f"Cargando aplicación{dots}")
            splash.after(400, animate_dots, step + 1)

        animate_dots()

        # Tras 2,5 segundos destruimos el splash y cargamos la app
        def finish_splash() -> None:
            splash.destroy()
            self._init_main_window()

        splash.after(2500, finish_splash)

    def _init_main_window(self) -> None:
        """Configura y muestra la ventana principal después del splash."""

        # Título y tamaño mínimo
        self.title(APP_NAME)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Layout base
        self._configure_style()
        self._build_layout()
        self._build_menu()
        self._register_views()

        # Mostrar primera vista
        self.show_view("dashboard")

        # Mostrar la ventana principal (estaba withdraw)
        self.deiconify()

    ########  Construcción de layout / menús ########
    
    def _configure_style(self) -> None:
        """Configura tema y estilos generales de la UI."""
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))

    def _build_layout(self) -> None:
        """Crea contenedor principal y barra de estado."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.content = ttk.Frame(self)
        self.content.grid(row=0, column=0, sticky="nsew")

        self.status_bar = ttk.Label(self, relief=tk.SUNKEN, anchor="w", padding=(10, 5))
        self.status_bar.grid(row=1, column=0, sticky="ew")

    def _register_views(self) -> None:
        """Registra todas las pantallas de la aplicación."""
        self._install_view("dashboard", DashboardView)
        self._install_view("importar", ImportarDatosView)
        self._install_view("ventas", VentasView)
        self._install_view("estadisticas", EstadisticasView)

    def _install_view(self, key: str, view_cls: Type[BaseView]) -> None:
        frame = view_cls(self.content, self)
        self._views[key] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def _build_menu(self) -> None:
        """Construye la barra de menús principal."""
        menubar = tk.Menu(self)

        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        # Menú Vistas
        menu_vistas = tk.Menu(menubar, tearoff=0)
        menu_vistas.add_command(label="Dashboard", command=lambda: self.show_view("dashboard"))
        menu_vistas.add_command(label="Importar datos", command=lambda: self.show_view("importar"))
        menu_vistas.add_command(label="Ventas", command=lambda: self.show_view("ventas"))
        menu_vistas.add_command(label="Estadísticas", command=lambda: self.show_view("estadisticas"))
        menubar.add_cascade(label="Vistas", menu=menu_vistas)

        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menu_ayuda.add_command(label="Acerca de…", command=self._mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.config(menu=menubar)

    ########  Navegación / Estado ########

    def show_view(self, key: str) -> None:
        """Muestra la vista indicada por su clave."""
        next_view = self._views.get(key)
        if not next_view:
            self.set_status(f"Vista '{key}' no registrada.")
            return

        if self._current_view is next_view:
            return

        if self._current_view:
            self._current_view.on_hide()

        next_view.tkraise()
        next_view.on_show()
        self._current_view = next_view
        self.set_status(f"Vista actual: {key.title()}")
    
    def get_view(self, key: str):
        """Devuelve una vista registrada por su clave (o None si no existe)."""
        return self._views.get(key)

    def set_status(self, message: str) -> None:
        """Actualiza el texto de la barra de estado."""
        self.status_bar.config(text=message)

    #######  Ventana "Acerca de…" #######

    def _mostrar_acerca_de(self) -> None:
        """Muestra una ventana modal con información de la app."""
        ventana = tk.Toplevel(self)
        ventana.title("Acerca de Sales Desktop CRM")
        ventana.iconphoto(False, self.logo_icon)
        ventana.resizable(False, False)

        # Tamaño y centrado
        w, h = 380, 260
        ventana.update_idletasks()
        sw = ventana.winfo_screenwidth()
        sh = ventana.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        ventana.geometry(f"{w}x{h}+{x}+{y}")

        frame = ttk.Frame(ventana, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, image=self.logo_icon).pack(pady=(0, 10))

        ttk.Label(
            frame,
            text="Demo Company",
            font=("Segoe UI", 14, "bold"),
        ).pack()

        ttk.Label(
            frame,
            text="Analizador de Ventas y CRM básico\nVersión 1.0 (Desktop)",
            justify="center",
        ).pack(pady=10)

        ttk.Label(
            frame,
            text="Proyecto técnico Sales Desktop CRM (Portfolio)",
            font=("Segoe UI", 9, "italic"),
        ).pack(pady=(0, 15))

        ttk.Button(frame, text="Cerrar", command=ventana.destroy).pack()