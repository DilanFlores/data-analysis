"""Utilidades compartidas por los métodos cuantitativos.

Funciones puras para extraer series y proporciones del DataFrame limpio
(hoja C1). No dependen de Streamlit.
"""

from __future__ import annotations

import pandas as pd

from estadisticas.data import columna_categoria

# Tamaños empresariales en orden lógico (excluye "nd" y "Total").
TAMANIOS = ["Micro", "Pequeña", "Mediana", "Grande"]


def buscar_columna(df: pd.DataFrame, *fragmentos: str) -> str | None:
    """Devuelve la primera columna cuyo nombre contenga alguno de los fragmentos."""
    for frag in fragmentos:
        for col in df.columns:
            if frag.lower() in str(col).lower():
                return col
    return None


def serie_total(df: pd.DataFrame, metrica: str) -> pd.Series:
    """Serie anual (índice = Año) de una métrica para el agregado nacional.

    Usa la fila "Total" si existe; si no, suma todas las categorías por año.
    """
    datos = df.dropna(subset=[metrica, "Año"])
    cat = columna_categoria(df)
    if cat and (datos[cat].astype(str) == "Total").any():
        datos = datos[datos[cat].astype(str) == "Total"]
    serie = datos.groupby("Año")[metrica].sum(min_count=1).dropna()
    serie.index = serie.index.astype(int)
    return serie.sort_index()


def proporciones_anuales(df: pd.DataFrame, metrica: str) -> pd.DataFrame:
    """Tabla año × tamaño con la participación relativa de cada tamaño.

    Cada fila suma 1 (composición de la métrica entre Micro…Grande ese año).
    """
    cat = columna_categoria(df)
    datos = df.dropna(subset=[metrica, "Año"])
    datos = datos[datos[cat].astype(str).isin(TAMANIOS)]
    tabla = datos.pivot_table(index="Año", columns=cat, values=metrica,
                              aggfunc="sum")
    tabla = tabla.reindex(columns=TAMANIOS).dropna(how="any")
    tabla = tabla.div(tabla.sum(axis=1), axis=0)
    tabla.index = tabla.index.astype(int)
    return tabla.sort_index()
