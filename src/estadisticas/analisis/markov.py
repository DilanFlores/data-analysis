"""Cadenas de Markov: dinámica de la composición empresarial por tamaño.

Estima la transición de la composición a partir del cambio promedio anual de
las proporciones de cada tamaño y proyecta la distribución del año siguiente.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from estadisticas.analisis._utiles import TAMANIOS, proporciones_anuales


def _proyeccion_siguiente(props: np.ndarray) -> np.ndarray:
    """Proyecta un año aplicando el cambio promedio anual a la última distribución."""
    tendencia = np.diff(props, axis=0).mean(axis=0)
    siguiente = np.maximum(props[-1] + tendencia, 0)
    return siguiente / siguiente.sum()


def proyectar_markov(df: pd.DataFrame, metrica: str = "Cantidad UJ") -> go.Figure:
    """Modela la composición por tamaño (`metrica`) y proyecta el año siguiente.

    Devuelve una figura con la evolución histórica de las proporciones y una
    tabla comparativa entre los años de referencia y la proyección.
    """
    tabla = proporciones_anuales(df, metrica)
    anios = tabla.index.tolist()
    props = tabla.to_numpy(dtype=float)
    proyeccion = _proyeccion_siguiente(props)

    ini, fin = anios[0], anios[-1]
    anio_proy = fin + 1
    # Año de mayor concentración micro (referencia de la composición extrema).
    anio_pico = int(tabla["Micro"].idxmax())

    fig = make_subplots(
        rows=1, cols=2, column_widths=[0.58, 0.42],
        specs=[[{"type": "xy"}, {"type": "table"}]],
        subplot_titles=("Evolución de la composición por tamaño",
                        "Proporciones de referencia y proyección"),
    )

    for tam in TAMANIOS:
        fig.add_trace(
            go.Scatter(x=anios, y=tabla[tam] * 100, mode="lines+markers",
                       name=tam),
            row=1, col=1,
        )

    columnas = {
        f"{ini}": tabla.loc[ini].values,
        f"{anio_pico} (máx Micro)": tabla.loc[anio_pico].values,
        f"{fin}": tabla.loc[fin].values,
        f"Proy. {anio_proy}": proyeccion,
    }
    fig.add_trace(
        go.Table(
            header=dict(values=["Tamaño"] + list(columnas),
                        fill_color="#2c3e50", font=dict(color="white"),
                        align="left"),
            cells=dict(
                values=[TAMANIOS] +
                       [[f"{v * 100:.2f}%" for v in col] for col in columnas.values()],
                align="left"),
        ),
        row=1, col=2,
    )

    fig.update_yaxes(title_text="Proporción (%)", row=1, col=1)
    fig.update_layout(
        title=f"Dinámica de composición por tamaño ({metrica}) — "
              f"proyección {anio_proy}",
        hovermode="x unified", legend_title_text="Tamaño",
    )
    return fig
