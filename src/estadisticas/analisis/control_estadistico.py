"""Control estadístico de procesos: gráfico I-MR para observaciones anuales.

Gráfico de individuales (I) y de rango móvil (MR) con límites a ±3 sigma,
marcando los puntos fuera de control.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from estadisticas.analisis._utiles import serie_total

# Constantes de las cartas I-MR para n=2 (rango móvil de dos observaciones).
D2 = 1.128
E2 = 2.66    # 3 / d2, factor de los límites del gráfico de individuales
D4 = 3.267   # factor del límite superior del rango móvil


def _puntos_fuera(valores: np.ndarray, lci: float, lcs: float) -> list[int]:
    """Índices de los puntos que caen fuera de los límites de control."""
    return [i for i, v in enumerate(valores) if v > lcs or v < lci]


def grafico_imr(df: pd.DataFrame, metrica: str) -> go.Figure:
    """Carta I-MR de la serie total de `metrica`.

    Devuelve una figura con dos paneles: individuales (arriba) y rango móvil.
    """
    serie = serie_total(df, metrica)
    anios = serie.index.tolist()
    valores = serie.to_numpy(dtype=float)

    rango_movil = np.abs(np.diff(valores))
    mr_medio = float(rango_movil.mean())
    media = float(valores.mean())

    lcs_i = media + E2 * mr_medio
    lci_i = media - E2 * mr_medio
    lcs_mr = D4 * mr_medio
    lci_mr = 0.0

    fuera_i = _puntos_fuera(valores, lci_i, lcs_i)
    fuera_mr = _puntos_fuera(rango_movil, lci_mr, lcs_mr)

    fig = make_subplots(
        rows=2, cols=1, vertical_spacing=0.12,
        subplot_titles=(f"Gráfico de individuales (I) — {metrica}",
                        "Gráfico de rango móvil (MR)"),
    )

    # --- Panel I ---
    fig.add_trace(
        go.Scatter(x=anios, y=valores, mode="lines+markers", name="Observación",
                   line=dict(color="#2980b9")),
        row=1, col=1,
    )
    if fuera_i:
        fig.add_trace(
            go.Scatter(x=[anios[i] for i in fuera_i],
                       y=[valores[i] for i in fuera_i],
                       mode="markers", name="Fuera de control",
                       marker=dict(color="red", size=12, symbol="x")),
            row=1, col=1,
        )
    _lineas_control(fig, media, lcs_i, lci_i, row=1)

    # --- Panel MR ---
    anios_mr = anios[1:]
    fig.add_trace(
        go.Scatter(x=anios_mr, y=rango_movil, mode="lines+markers",
                   name="Rango móvil", line=dict(color="#16a085")),
        row=2, col=1,
    )
    if fuera_mr:
        fig.add_trace(
            go.Scatter(x=[anios_mr[i] for i in fuera_mr],
                       y=[rango_movil[i] for i in fuera_mr],
                       mode="markers", name="MR fuera de control",
                       marker=dict(color="red", size=12, symbol="x")),
            row=2, col=1,
        )
    _lineas_control(fig, mr_medio, lcs_mr, lci_mr, row=2)

    fig.update_layout(title=f"Control estadístico de {metrica}",
                      hovermode="x unified", showlegend=False)
    return fig


def _lineas_control(fig: go.Figure, central: float, lcs: float, lci: float,
                    row: int) -> None:
    """Dibuja línea central, LCS y LCI como líneas horizontales en un panel."""
    fig.add_hline(y=central, line_dash="solid", line_color="green",
                  annotation_text="LC", row=row, col=1)
    fig.add_hline(y=lcs, line_dash="dash", line_color="red",
                  annotation_text="LCS", row=row, col=1)
    fig.add_hline(y=lci, line_dash="dash", line_color="red",
                  annotation_text="LCI", row=row, col=1)
