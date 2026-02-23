import pandas as pd
from pathlib import Path
from typing import Optional

REQUIRED_COLUMNS = ["id", "fecha", "hora", "producto", "cliente", "importe"]

class DataLoaderError(Exception):
    """Error personalizado para manejo de cargas de datos."""
    pass

class DataLoader:
    """Servicio central de carga y validación de archivos CSV/XLSX."""

    def __init__(self):
        self.data: Optional[pd.DataFrame] = None

    def load(self, file_path: str) -> pd.DataFrame:
        """Carga un archivo CSV o XLSX y valida columnas."""
        path = Path(file_path)

        if not path.exists():
            raise DataLoaderError(f"Archivo no encontrado: {file_path}")

        # Detectar tipo
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(path)
        else:
            raise DataLoaderError("Formato no soportado. Use CSV o XLSX.")

        # Validar columnas
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise DataLoaderError(f"Faltan columnas obligatorias: {missing}")

        # Normalización
        df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
        df["hora"] = pd.to_datetime(df["hora"], format="%H:%M:%S", errors="coerce").dt.time
        df["importe"] = (
            df["importe"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            )
        df["importe"] = pd.to_numeric(df["importe"], errors="coerce").fillna(0.0)

        self.data = df
        return df

    def get_data(self) -> pd.DataFrame:
        """Devuelve el DataFrame cargado."""
        if self.data is None:
            raise DataLoaderError("No hay datos cargados aún.")
        return self.data