"""Programación lineal: asignación óptima del apoyo institucional por sector.

Maximiza el aporte potencial al PIB del segmento Mipyme repartiendo un
presupuesto de recursos entre los cinco sectores económicos con mayor aporte.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pulp
from plotly.subplots import make_subplots

# Aporte de las micro empresas al PIB por sector (%, BCCR, año 2022).
# Coeficientes de la función objetivo (insumo externo a la hoja C1).
SECTORES = {
    "Enseñanza y salud": 5.55,
    "Act. inmobiliarias": 2.90,
    "Prof. y técnicas": 2.77,
    "Comercio": 1.35,
    "Construcción": 0.88,
}

PRESUPUESTO = 100   # unidades de recurso de apoyo a repartir
MAX_SECTOR = 40     # tope por sector para no concentrar los recursos
UNIFORME = PRESUPUESTO / len(SECTORES)  # asignación equitativa de referencia


def optimizar_asignacion(df: pd.DataFrame | None = None) -> go.Figure:
    """Resuelve el modelo de asignación y devuelve figura con barras y tabla.

    `df` no se utiliza: los coeficientes de aporte sectorial al PIB provienen
    del conjunto de datos del BCCR 2018-2022, externo al cuadro C1.
    """
    modelo = pulp.LpProblem("apoyo_mipyme", pulp.LpMaximize)
    x = {s: pulp.LpVariable(f"x_{i}", lowBound=0, upBound=MAX_SECTOR)
         for i, s in enumerate(SECTORES)}

    modelo += pulp.lpSum(SECTORES[s] * x[s] for s in SECTORES)
    modelo += pulp.lpSum(x.values()) <= PRESUPUESTO

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    asignacion = {s: x[s].value() for s in SECTORES}
    aporte = {s: asignacion[s] * SECTORES[s] for s in SECTORES}
    z_optimo = pulp.value(modelo.objective)
    z_uniforme = sum(SECTORES[s] * UNIFORME for s in SECTORES)
    mejora = (z_optimo - z_uniforme) / z_uniforme * 100

    fig = make_subplots(
        rows=1, cols=2, column_widths=[0.55, 0.45],
        specs=[[{"type": "xy"}, {"type": "table"}]],
        subplot_titles=("Asignación óptima de recursos", "Detalle del modelo"),
    )

    fig.add_trace(
        go.Bar(x=list(SECTORES), y=[asignacion[s] for s in SECTORES],
               text=[f"{asignacion[s]:.0f}" for s in SECTORES],
               textposition="outside", marker_color="#2980b9",
               name="Unidades"),
        row=1, col=1,
    )

    fig.add_trace(
        go.Table(
            header=dict(
                values=["Sector", "Aporte PIB (%)", "Asignación", "Aporte"],
                fill_color="#2c3e50", font=dict(color="white"), align="left"),
            cells=dict(
                values=[
                    list(SECTORES),
                    [f"{SECTORES[s]:.2f}" for s in SECTORES],
                    [f"{asignacion[s]:.0f}" for s in SECTORES],
                    [f"{aporte[s]:.1f}" for s in SECTORES],
                ],
                align="left"),
        ),
        row=1, col=2,
    )

    fig.update_yaxes(title_text="Unidades de recurso", row=1, col=1)
    fig.update_layout(
        title=f"Aporte potencial al PIB maximizado: Z = {z_optimo:.1f}  "
              f"(+{mejora:.1f}% sobre la distribución uniforme: {z_uniforme:.0f})",
        showlegend=False,
    )
    return fig
