"""Constructores de gráficos con Plotly.

Cada función recibe un DataFrame ya limpio y devuelve una figura de Plotly.
Mantener cada gráfico en su propia función facilita probarlo y reutilizarlo.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from estadisticas.config import ORDEN_TAMANIO


def _ordenar_categoria(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Aplica el orden lógico de tamaños cuando corresponde."""
    if df[col].dropna().isin(ORDEN_TAMANIO).any():
        df = df.copy()
        df[col] = pd.Categorical(df[col], categories=ORDEN_TAMANIO, ordered=True)
        df = df.sort_values([c for c in ("Año", col) if c in df.columns])
    return df


def serie_temporal(df: pd.DataFrame, metrica: str,
                   categoria: str | None = None) -> go.Figure:
    """Evolución de una métrica a lo largo de los años.

    Si hay columna de categoría, dibuja una línea por categoría.
    """
    datos = df.dropna(subset=[metrica, "Año"])
    if categoria and categoria in datos.columns:
        datos = _ordenar_categoria(datos, categoria)
        fig = px.line(
            datos, x="Año", y=metrica, color=categoria, markers=True,
            title=f"Evolución de {metrica} (2005-2024)",
        )
    else:
        fig = px.line(datos, x="Año", y=metrica, markers=True,
                      title=f"Evolución de {metrica} (2005-2024)")
    fig.update_layout(hovermode="x unified", legend_title_text=categoria or "")
    return fig


def barras_por_categoria(df: pd.DataFrame, metrica: str, categoria: str,
                         anio: int | None = None) -> go.Figure:
    """Barras de una métrica por categoría, para un año dado (o el último)."""
    datos = df.dropna(subset=[metrica])
    if "Año" in datos.columns:
        anio = anio or int(datos["Año"].max())
        datos = datos[datos["Año"] == anio]
        titulo = f"{metrica} por {categoria} — {anio}"
    else:
        titulo = f"{metrica} por {categoria}"

    datos = _ordenar_categoria(datos, categoria)
    # Excluye el Total para no aplastar las demás barras.
    datos = datos[datos[categoria].astype(str) != "Total"]
    fig = px.bar(datos, x=categoria, y=metrica, color=categoria, title=titulo)
    fig.update_layout(showlegend=False)
    return fig


def composicion_apilada(df: pd.DataFrame, metrica: str,
                        categoria: str) -> go.Figure:
    """Área apilada que muestra la composición por categoría en el tiempo."""
    datos = df.dropna(subset=[metrica, "Año"])
    datos = datos[datos[categoria].astype(str) != "Total"]
    datos = _ordenar_categoria(datos, categoria)
    fig = px.area(datos, x="Año", y=metrica, color=categoria,
                  title=f"Composición de {metrica} por {categoria}")
    fig.update_layout(hovermode="x unified")
    return fig


def participacion_pastel(df: pd.DataFrame, metrica: str, categoria: str,
                         anio: int | None = None) -> go.Figure:
    """Pastel con la participación de cada categoría en el último año."""
    datos = df.dropna(subset=[metrica])
    if "Año" in datos.columns:
        anio = anio or int(datos["Año"].max())
        datos = datos[datos["Año"] == anio]
        titulo = f"Participación en {metrica} — {anio}"
    else:
        titulo = f"Participación en {metrica}"
    datos = datos[datos[categoria].astype(str) != "Total"]
    fig = px.pie(datos, names=categoria, values=metrica, title=titulo, hole=0.4)
    return fig


def comparar_comercio(df: pd.DataFrame) -> go.Figure | None:
    """Exportaciones vs importaciones en el tiempo (si existen las columnas)."""
    exp = next((c for c in df.columns if c.startswith("Exportaciones")), None)
    imp = next((c for c in df.columns if c.startswith("Importaciones")), None)
    if not exp or not imp or "Año" not in df.columns:
        return None

    agregado = df.groupby("Año")[[exp, imp]].sum(min_count=1).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=agregado["Año"], y=agregado[exp],
                             mode="lines+markers", name="Exportaciones"))
    fig.add_trace(go.Scatter(x=agregado["Año"], y=agregado[imp],
                             mode="lines+markers", name="Importaciones"))
    fig.update_layout(title="Exportaciones vs Importaciones ($)",
                      hovermode="x unified", yaxis_title="USD")
    return fig
