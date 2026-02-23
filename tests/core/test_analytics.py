import pandas as pd

from app.core.analytics import Analytics


def test_summary_with_none_dataframe():
    analytics = Analytics()

    result = analytics.summary(None)

    assert result["total_ventas"] == 0.0
    assert result["ticket_promedio"] == 0.0
    assert result["cantidad_operaciones"] == 0
    assert result["clientes_unicos"] == 0


def test_summary_with_empty_dataframe():
    analytics = Analytics()
    df = pd.DataFrame()

    result = analytics.summary(df)

    assert result["total_ventas"] == 0.0
    assert result["ticket_promedio"] == 0.0
    assert result["cantidad_operaciones"] == 0
    assert result["clientes_unicos"] == 0


def test_summary_with_valid_data():
    analytics = Analytics()
    df = pd.DataFrame({
        "importe": [100.0, 200.0, 300.0],
        "cliente": ["Juan", "Ana", "Juan"],
    })

    result = analytics.summary(df)

    assert result["total_ventas"] == 600.0
    assert result["ticket_promedio"] == 200.0
    assert result["cantidad_operaciones"] == 3
    assert result["clientes_unicos"] == 2


def test_summary_single_row():
    analytics = Analytics()
    df = pd.DataFrame({
        "importe": [150.0],
        "cliente": ["Pedro"],
    })

    result = analytics.summary(df)

    assert result["total_ventas"] == 150.0
    assert result["ticket_promedio"] == 150.0
    assert result["cantidad_operaciones"] == 1
    assert result["clientes_unicos"] == 1