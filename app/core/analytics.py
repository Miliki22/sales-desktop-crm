from __future__ import annotations

from typing import Dict, Any
import pandas as pd

class Analytics:
    """Cálculos de métricas de ventas."""

    def summary(self, df: pd.DataFrame | None) -> Dict[str, Any]:
        if df is None or df.empty:
            return {
                "total_ventas": 0.0,
                "ticket_promedio": 0.0,
                "cantidad_operaciones": 0,
                "clientes_unicos": 0,
            }

        total_ventas = float(df["importe"].sum())
        ticket_promedio = float(df["importe"].mean())
        cantidad_operaciones = int(df.shape[0])
        clientes_unicos = int(df["cliente"].nunique())

        return {
            "total_ventas": total_ventas,
            "ticket_promedio": ticket_promedio,
            "cantidad_operaciones": cantidad_operaciones,
            "clientes_unicos": clientes_unicos,
        }