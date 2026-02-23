from app.desktop_app import DesktopApp


def main() -> None:
    """Punto de entrada de la aplicación de escritorio Sales Desktop CRM."""
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()