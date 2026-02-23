from __future__ import annotations

# Estados del CRM
ESTADOS_CRM = ["Lead", "En seguimiento", "Cerrado", "Perdido"]

# Tabla (Treeview)
CRM_COLUMNS = ("fecha_alta", "nombre", "email", "telefono", "estado", "nota")

CRM_HEADINGS: dict[str, str] = {
    "fecha_alta": "Fecha alta",
    "nombre": "Nombre",
    "email": "Email",
    "telefono": "Teléfono",
    "estado": "Estado",
    "nota": "Nota",
}

# Tags por estado (colores del texto)
CRM_STATE_TAGS: dict[str, str] = {
    "Lead": "estado_Lead",
    "En seguimiento": "estado_En_seguimiento",
    "Cerrado": "estado_Cerrado",
    "Perdido": "estado_Perdido",
}

# Colores por estado (texto del Treeview)
CRM_STATE_COLORS: dict[str, str] = {
    "Lead": "#2563eb",            # azul
    "En seguimiento": "#d97706",  # ámbar
    "Cerrado": "#15803d",         # verde
    "Perdido": "#b91c1c",         # rojo
}

def estado_to_tag(estado: str) -> str:
    """Convierte un estado a tag de Treeview (compatible con espacios)."""
    estado = (estado or "").strip()
    if not estado:
        return ""
    # Si existe mapeo exacto, lo usamos; si no, caemos al replace de espacios.
    return CRM_STATE_TAGS.get(estado, f"estado_{estado.replace(' ', '_')}")