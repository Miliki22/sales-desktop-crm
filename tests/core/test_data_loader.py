import pandas as pd
import pytest
from pathlib import Path

from app.core.data_loader import DataLoader, DataLoaderError


def test_load_csv_ok(tmp_path: Path):
    """Carga correcta de un CSV válido."""
    csv_file = tmp_path / "ventas.csv"

    df = pd.DataFrame({
        "id": [1, 2],
        "fecha": ["2024-01-01", "2024-01-02"],
        "hora": ["10:00:00", "11:00:00"],
        "producto": ["Curso básico", "Curso medio"],
        "cliente": ["Juan", "Ana"],
        "importe": [100.0, 200.0],
    })
    df.to_csv(csv_file, index=False)

    loader = DataLoader()
    result = loader.load(str(csv_file))

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert "importe" in result.columns


def test_load_file_not_found():
    """Error si el archivo no existe."""
    loader = DataLoader()

    with pytest.raises(DataLoaderError):
        loader.load("archivo_inexistente.csv")


def test_missing_required_columns(tmp_path: Path):
    """Error si faltan columnas obligatorias."""
    csv_file = tmp_path / "ventas_incompleto.csv"

    df = pd.DataFrame({
        "fecha": ["2024-01-01"],
        "importe": [100.0],
    })
    df.to_csv(csv_file, index=False)

    loader = DataLoader()

    with pytest.raises(DataLoaderError):
        loader.load(str(csv_file))