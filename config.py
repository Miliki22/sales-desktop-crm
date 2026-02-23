from __future__ import annotations

from pathlib import Path

# Directorio base del proyecto (donde está este archivo)
BASE_DIR = Path(__file__).resolve().parent

# --- Carpetas de datos ---
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# --- Documentos / reportes ---
DOCS_DIR = BASE_DIR / "docs"
CRM_EXPORTS_DIR = DOCS_DIR / "crm"

# --- Aplicación ---
APP_NAME = "Demo Company – Analizador de Ventas"
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

# --- Rutas de archivos ---
ASSETS_DIR = BASE_DIR / "assets"

LOGO_FILENAME = "logo.png"
LOGO_PATH = ASSETS_DIR / LOGO_FILENAME

# Archivo de datos por defecto (por si lo queremos usar luego)
DEFAULT_DATA_FILE = DATA_DIR / "ventas.csv"

# Archivo de clientes del CRM
CRM_CLIENTES_FILE = OUTPUT_DIR / "clientes.csv"

# --- Formato de negocio ---
CURRENCY_SYMBOL = "€"

# Número de filas a mostrar en la previsualización
PREVIEW_ROWS = 5