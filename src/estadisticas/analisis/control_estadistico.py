"""Control estadístico de procesos: gráfico I-MR para observaciones anuales.

Gráfico de individuales (I) con línea central y límites a ±3σ, acompañado del
gráfico de rango móvil (MR). Marca los puntos fuera de control.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from estadisticas.analisis._utiles import serie_total

D4 = 3.267  # factor del límite superior del rango móvil (n=2)


def _puntos_fuera(valores: np.ndarray, lci: float, lcs: float) -> list[int]:
    """Índices de los puntos que caen fuera de los límites de control."""
    return [i for i, v in enumerate(valores) if v > lcs or v < lci]


def grafico_imr(df: pd.DataFrame, metrica: str) -> go.Figure:
    """Carta I-MR de la serie total de `metrica`.

    Los límites del gráfico de individuales se calculan como media ± 3σ
    (desviación estándar muestral). Devuelve una figura con dos paneles:
    individuales (arriba) y rango móvil (abajo).
    """
    serie = serie_total(df, metrica)
    anios = serie.index.tolist()
    valores = serie.to_numpy(dtype=float)

    media = float(valores.mean())
    sigma = float(valores.std(ddof=1))
    lcs_i = media + 3 * sigma
    lci_i = max(0.0, media - 3 * sigma)

    rango_movil = np.abs(np.diff(valores))
    mr_medio = float(rango_movil.mean())
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

    fig.update_layout(
        title=f"Control estadístico de {metrica} — "
              f"media {media:,.0f} · LCS {lcs_i:,.0f} · LCI {lci_i:,.0f}",
        hovermode="x unified", showlegend=False,
    )
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
