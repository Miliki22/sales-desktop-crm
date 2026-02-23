from __future__ import annotations

import pandas as pd
import pytest

from app.core.repository import Repository

@pytest.fixture()
def repo(tmp_path, monkeypatch) -> Repository:
    """
    Repo aislado por test:
    - CRM_CLIENTES_FILE se redirige a un csv temporal
    """
    fake_clients_file = tmp_path / "clientes.csv"

    # OJO: hay que parchear el atributo DENTRO del módulo app.core.repository
    import app.core.repository as repo_module
    monkeypatch.setattr(repo_module, "CRM_CLIENTES_FILE", fake_clients_file)

    return Repository()

# =========================
# Ventas
# =========================

def test_get_summary_without_sales_returns_empty(repo: Repository):
    assert repo.get_summary() == {
    "total_ventas": 0.0,
    "ticket_promedio": 0.0,
    "cantidad_operaciones": 0,
    "clientes_unicos": 0,
}

def test_get_summary_with_sales_ok(repo: Repository):
    df = pd.DataFrame(
        {
            "importe": [100.0, 200.0, 300.0],
            "cliente": ["Juan", "Ana", "Juan"],
        }
    )
    repo.data = df

    summary = repo.get_summary()

    assert summary["total_ventas"] == 600.0
    assert summary["ticket_promedio"] == 200.0
    assert summary["cantidad_operaciones"] == 3
    assert summary["clientes_unicos"] == 2

# =========================
# CRM - clientes
# =========================

def test_load_clients_creates_file_if_missing(repo: Repository):
    df = repo.load_clients()

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["fecha_alta", "nombre", "email", "telefono", "estado", "nota"]
    # debe existir el archivo temporal
    import app.core.repository as repo_module
    assert repo_module.CRM_CLIENTES_FILE.exists()

def test_add_client_persists(repo: Repository):
    repo.load_clients()

    repo.add_client(
        {
            "fecha_alta": "2025-12-31",
            "nombre": "Cliente 1",
            "email": "c1@test.com",
            "telefono": "123",
            "estado": "Lead",
            "nota": "ok",
        }
    )

    df = repo.load_clients()
    assert len(df) == 1
    assert df.loc[0, "nombre"] == "Cliente 1"
    assert df.loc[0, "estado"] == "Lead"

def test_update_client_persists(repo: Repository):
    repo.load_clients()
    repo.add_client(
        {
            "fecha_alta": "2025-12-31",
            "nombre": "Cliente 1",
            "email": "c1@test.com",
            "telefono": "123",
            "estado": "Lead",
            "nota": "",
        }
    )

    repo.update_client(
        0,
        {
            "fecha_alta": "2025-12-31",
            "nombre": "Cliente 1 editado",
            "email": "edit@test.com",
            "telefono": "999",
            "estado": "En seguimiento",
            "nota": "nota edit",
        },
    )

    df = repo.load_clients()
    assert df.loc[0, "nombre"] == "Cliente 1 editado"
    assert df.loc[0, "estado"] == "En seguimiento"
    assert df.loc[0, "telefono"] == "999"

def test_update_client_invalid_index_raises(repo: Repository):
    repo.load_clients()
    with pytest.raises(IndexError):
        repo.update_client(99, {"nombre": "x"})

def test_delete_client_persists(repo: Repository):
    repo.load_clients()
    repo.add_client(
        {
            "fecha_alta": "2025-12-31",
            "nombre": "A",
            "email": "",
            "telefono": "",
            "estado": "Lead",
            "nota": "",
        }
    )
    repo.add_client(
        {
            "fecha_alta": "2025-12-31",
            "nombre": "B",
            "email": "",
            "telefono": "",
            "estado": "Lead",
            "nota": "",
        }
    )

    repo.delete_client(0)

    df = repo.load_clients()
    assert len(df) == 1
    assert df.loc[0, "nombre"] == "B"  # porque hace reset_index(drop=True)

def test_delete_client_invalid_index_raises(repo: Repository):
    repo.load_clients()
    with pytest.raises(IndexError):
        repo.delete_client(0)