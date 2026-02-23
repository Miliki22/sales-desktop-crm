# PT App Sales Desktop CRM – Documentación Técnica

Aplicación de escritorio desarrollada en Python para la carga, análisis y gestión
de datos de ventas y clientes (CRM).

Este README funciona como **guía técnica rápida** para comprender la arquitectura,
ejecutar la aplicación y entender el alcance del testing del core.

---

## Stack Tecnológico

- **Python 3.13**
- **Tkinter** – interfaz gráfica de escritorio
- **Pandas** – manipulación y análisis de datos
- **Matplotlib** – generación de gráficas
- **Pytest** – testing del core
- **CSV / Excel** – fuentes de datos
- **Git** – control de versiones

---

## Estructura del Core

El núcleo de la aplicación se encuentra en:
app/core

Contiene tres componentes principales:

### 1. `data_loader.py`
Responsable de:
- Cargar archivos CSV y Excel
- Validar columnas obligatorias
- Normalizar tipos de datos (fechas, horas, importes)
- Centralizar errores de carga mediante `DataLoaderError`

### 2. `analytics.py`
Encargado de los cálculos de métricas de ventas:
- Total de ventas
- Ticket promedio
- Cantidad de operaciones
- Clientes únicos

Está diseñado para:
- Soportar DataFrames vacíos o inexistentes
- Devolver siempre resultados consistentes

### 3. `repository.py`
Actúa como **capa intermedia** entre:
- Los datos (ventas y clientes)
- La lógica de negocio
- Las vistas de la aplicación

---

## ¿Por qué existe `Repository`?

El `Repository` centraliza el acceso y la persistencia de datos para:

- Evitar que las vistas accedan directamente a DataFrames o archivos
- Unificar la lógica de ventas y CRM
- Facilitar el testing aislado del core
- Permitir cambios futuros (ej: base de datos real) sin romper la UI

Es el **punto único de verdad** del estado de la aplicación.

---

## Ejecución de la Aplicación

### 1. Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```bash
python main.py
```

## Testing del Core

Los tests están implementados con **pytest** y cubren exclusivamente la lógica del core.

### ¿Qué se testea?

- **DataLoader**
  - Carga correcta de CSV
  - Archivo inexistente
  - Columnas obligatorias faltantes

- **Analytics**
  - DataFrame vacío
  - DataFrame inexistente
  - Datos válidos
  - Casos de una o múltiples operaciones

- **Repository**
  - Resúmenes de ventas con y sin datos
  - Persistencia de clientes (alta, edición, eliminación)
  - Manejo de índices inválidos
  - Creación automática del archivo de clientes

---

## Cómo ejecutar los tests

Desde la raíz del proyecto:

```bash
python -m pytest
```

O para ejecutar solo los tests del core:

```bash
python -m pytest tests/core
```