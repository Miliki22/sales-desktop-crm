from __future__ import annotations

from typing import Optional, Dict, Any

import pandas as pd

from .data_loader import DataLoader, DataLoaderError
from .analytics import Analytics
from config import CRM_CLIENTES_FILE


class Repository:
    """Capa de acceso a datos para la aplicación Sales Desktop CRM."""

    def __init__(self) -> None:
        # Loader y análisis de ventas
        self.loader = DataLoader()
        self.analytics = Analytics()
        self.data: Optional[pd.DataFrame] = None  # dataset de ventas

        # 🔹 Dataset de clientes CRM
        self.clients: Optional[pd.DataFrame] = None

    # ========= VENTAS =========

    def load_sales(self, file_path: str) -> pd.DataFrame:
        """Carga y almacena ventas desde un CSV/XLSX."""
        try:
            df = self.loader.load(file_path)
            self.data = df
            return df
        except DataLoaderError as e:
            raise e

    def get_all_sales(self) -> Optional[pd.DataFrame]:
        """Devuelve el dataset completo cargado."""
        return self.data

    def get_summary(self) -> dict:
        """Devuelve métricas de ventas listas para el dashboard."""
        return self.analytics.summary(self.data)

    # ========= CRM – CLIENTES =========

    def load_clients(self) -> pd.DataFrame:
        """Carga clientes del CRM desde CSV; si no existe, crea uno vacío estándar."""
        CRM_CLIENTES_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not CRM_CLIENTES_FILE.exists():
            df = pd.DataFrame(
                columns=["fecha_alta", "nombre", "email", "telefono", "estado", "nota"]
            )
            df.to_csv(CRM_CLIENTES_FILE, index=False)
        else:
            # keep_default_na=False evita que las celdas vacías sean 'NaN'
            df = pd.read_csv(CRM_CLIENTES_FILE, keep_default_na=False, dtype=str)

        self.clients = df
        return df

    def get_all_clients(self) -> Optional[pd.DataFrame]:
        """Devuelve el DataFrame de clientes en memoria (si se ha cargado)."""
        return self.clients

    def _ensure_clients_df(self) -> pd.DataFrame:
        """Garantiza que tenemos un DataFrame de clientes listo para usar."""
        if self.clients is None:
            self.load_clients()
        if self.clients is None:
            self.clients = pd.DataFrame(
                columns=["fecha_alta", "nombre", "email", "telefono", "estado", "nota"]
            )
        return self.clients

    def add_client(self, data: Dict[str, Any]) -> None:
        """Añade un cliente al CRM y persiste en CSV."""
        df = self._ensure_clients_df().copy()

        df.loc[len(df)] = data

        CRM_CLIENTES_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CRM_CLIENTES_FILE, index=False)

        self.clients = df

    def update_client(self, index: int, data: Dict[str, Any]) -> None:
        """Actualiza un cliente existente y persiste en CSV."""
        if self.clients is None:
            self.load_clients()

        if self.clients is None:
            raise RuntimeError("No hay dataset de clientes cargado.")

        df = self.clients

        if index not in df.index:
            raise IndexError(f"No existe cliente con índice {index}.")

        for key, value in data.items():
            if key in df.columns:
                df.at[index, key] = value

        # Guardamos en disco
        CRM_CLIENTES_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CRM_CLIENTES_FILE, index=False)

        # Actualizamos caché
        self.clients = df

    def delete_client(self, index: int) -> None:
        """Elimina un cliente del CRM y actualiza CSV."""
        if self.clients is None:
            self.load_clients()

        if self.clients is None:
            raise RuntimeError("No hay dataset de clientes cargado.")

        df = self.clients

        if index not in df.index:
            raise IndexError(f"No existe cliente con índice {index}.")

        df = df.drop(index)
        df = df.reset_index(drop=True)

        CRM_CLIENTES_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CRM_CLIENTES_FILE, index=False)

        self.clients = df