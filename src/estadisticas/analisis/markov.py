"""Cadenas de Markov: dinámica de la composición empresarial por tamaño.

Estima una matriz de transición a partir de cómo cambia año a año el peso
relativo de cada tamaño, calcula la distribución estacionaria y proyecta la
composición futura.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from estadisticas.analisis._utiles import TAMANIOS, proporciones_anuales

HORIZONTES = [5, 10, 20]  # años a proyectar


def _matriz_transicion(props: np.ndarray) -> np.ndarray:
    """Estima la matriz estocástica P tal que p_{t+1} ≈ p_t · P.

    Resuelve por mínimos cuadrados y proyecta a una matriz válida (filas no
    negativas que suman 1).
    """
    origen, destino = props[:-1], props[1:]
    P, *_ = np.linalg.lstsq(origen, destino, rcond=None)
    P = np.clip(P, 0, None)
    sumas = P.sum(axis=1, keepdims=True)
    # Filas sin masa se reemplazan por permanencia (identidad).
    P = np.where(sumas > 0, P / np.where(sumas == 0, 1, sumas), np.eye(len(P)))
    return P


def _estacionaria(P: np.ndarray) -> np.ndarray:
    """Distribución estacionaria π (eigenvector izquierdo con autovalor 1)."""
    valores, vectores = np.linalg.eig(P.T)
    idx = int(np.argmin(np.abs(valores - 1.0)))
    pi = np.real(vectores[:, idx])
    return pi / pi.sum()


def proyectar_markov(df: pd.DataFrame, metrica: str = "Cantidad UJ") -> go.Figure:
    """Construye la cadena de Markov sobre la composición de `metrica`.

    Devuelve una figura con la matriz de transición (mapa de calor) y la
    proyección de la composición a 5, 10 y 20 años (barras apiladas).
    """
    tabla = proporciones_anuales(df, metrica)
    props = tabla.to_numpy(dtype=float)
    P = _matriz_transicion(props)
    pi = _estacionaria(P)

    actual = props[-1]
    proyecciones = {"Actual": actual}
    for h in HORIZONTES:
        proyecciones[f"+{h} años"] = actual @ np.linalg.matrix_power(P, h)
    proyecciones["Estacionaria"] = pi

    fig = make_subplots(
        rows=1, cols=2, column_widths=[0.45, 0.55],
        specs=[[{"type": "heatmap"}, {"type": "xy"}]],
        subplot_titles=("Matriz de transición (origen → destino)",
                        "Proyección de la composición empresarial"),
    )

    fig.add_trace(
        go.Heatmap(
            z=P, x=TAMANIOS, y=TAMANIOS, colorscale="Blues", zmin=0, zmax=1,
            text=[[f"{v:.2f}" for v in fila] for fila in P],
            texttemplate="%{text}", showscale=False),
        row=1, col=1,
    )
    fig.update_yaxes(autorange="reversed", row=1, col=1)

    escenarios = list(proyecciones.keys())
    for j, tam in enumerate(TAMANIOS):
        fig.add_trace(
            go.Bar(name=tam, x=escenarios,
                   y=[proyecciones[e][j] for e in escenarios],
                   text=[f"{proyecciones[e][j]:.0%}" for e in escenarios],
                   textposition="inside"),
            row=1, col=2,
        )

    fig.update_yaxes(tickformat=".0%", title_text="Participación", row=1, col=2)
    fig.update_layout(
        title=f"Dinámica de composición por tamaño ({metrica})",
        barmode="stack", legend_title_text="Tamaño",
    )
    return fig
