"""Configuración central: nombres de hojas, columnas y metadatos del Excel."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HojaConfig:
    """Describe cómo leer una hoja del Excel."""

    nombre: str
    titulo: str
    fila_encabezado: int  # índice (0-based) de la fila con los nombres de columna


# Hojas "limpias" (un solo nivel de encabezado) que la app sabe graficar.
HOJAS = {
    "C1": HojaConfig(
        nombre="C1",
        titulo="Unidades jurídicas, trabajadores e ingresos según tamaño",
        fila_encabezado=1,
    ),
    "C2": HojaConfig(
        nombre="C2",
        titulo="Mipymes: detalle por tamaño, actividad, provincia y cantón",
        fila_encabezado=1,
    ),
    "C3": HojaConfig(
        nombre="C3",
        titulo="UJ grandes: detalle por sección, provincia y cantón",
        fila_encabezado=1,
    ),
    "C4": HojaConfig(
        nombre="C4",
        titulo="Representatividad de los datos publicados (%)",
        fila_encabezado=1,
    ),
}

# Columnas numéricas típicas y su unidad, para formateo de ejes.
UNIDADES = {
    "Cantidad UJ": "unidades",
    "Número de trabajadores": "personas",
    "Masa salarial (₡)": "₡",
    "Ingresos (₡)": "₡",
    "Exportaciones ($)": "$",
    "Importaciones ($)": "$",
}

# Marcadores de dato faltante / confidencial usados en el archivo original.
VALORES_NULOS = {"x", "X", "nd", "ND", "n.d.", ""}

ORDEN_TAMANIO = ["Micro", "Pequeña", "Mediana", "Grande", "nd", "Total"]
