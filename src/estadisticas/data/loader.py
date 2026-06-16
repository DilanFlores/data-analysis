"""Carga y limpieza del Excel de estadísticas empresariales."""

from __future__ import annotations

import pandas as pd

from estadisticas.config import HOJAS, VALORES_NULOS


def listar_hojas_disponibles(fuente) -> list[str]:
    """Devuelve las hojas del Excel que la app sabe procesar."""
    todas = pd.ExcelFile(fuente).sheet_names
    return [h for h in HOJAS if h in todas]


def _a_numerico(serie: pd.Series) -> pd.Series:
    """Convierte una columna a numérico tratando 'x' y 'nd' como NaN."""
    limpia = serie.replace(list(VALORES_NULOS), pd.NA)
    return pd.to_numeric(limpia, errors="coerce")


def cargar_hoja(fuente, nombre_hoja: str) -> pd.DataFrame:
    """Lee una hoja y la devuelve limpia, con tipos correctos.

    `fuente` puede ser una ruta o un buffer (p. ej. el archivo subido en la UI).
    """
    if nombre_hoja not in HOJAS:
        raise ValueError(f"Hoja no soportada: {nombre_hoja}")

    cfg = HOJAS[nombre_hoja]
    df = pd.read_excel(fuente, sheet_name=nombre_hoja, header=cfg.fila_encabezado)

    # Normaliza nombres de columna (quita saltos de línea y espacios extra).
    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    df = df.dropna(how="all").reset_index(drop=True)

    # Año a entero cuando exista.
    if "Año" in df.columns:
        df["Año"] = _a_numerico(df["Año"]).astype("Int64")

    # Convierte a numérico todas las columnas que no sean claramente categóricas.
    categoricas = {"Tamaño", "Tamaño 1/", "Seccion", "Sección", "Clase CIIU",
                   "Provincia", "Cantón"}
    for col in df.columns:
        if col not in categoricas and col != "Año":
            df[col] = _a_numerico(df[col])

    return df


def columnas_numericas(df: pd.DataFrame) -> list[str]:
    """Columnas numéricas graficables (excluye el Año)."""
    cols = df.select_dtypes(include="number").columns.tolist()
    return [c for c in cols if c != "Año"]


def columna_categoria(df: pd.DataFrame) -> str | None:
    """Detecta la columna de categoría principal (Tamaño / Sección)."""
    for candidato in ("Tamaño 1/", "Tamaño", "Sección", "Seccion"):
        if candidato in df.columns:
            return candidato
    return None
