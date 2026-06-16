"""Programación lineal: asignación óptima de recursos por tamaño de empresa.

Maximiza el ingreso potencial repartiendo una proporción de recursos entre
Micro, Pequeña, Mediana y Grande, sujeto a restricciones de equidad.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pulp
from plotly.subplots import make_subplots

from estadisticas.analisis._utiles import TAMANIOS, buscar_columna
from estadisticas.data import columna_categoria

# Restricciones del modelo (proporción de recursos por tamaño).
MIN_CADA = 0.05    # piso para todos los tamaños
MIN_MICRO = 0.20   # restricción social: prioriza microempresas
MAX_GRANDE = 0.50  # techo para empresas grandes


def _ingreso_por_uj(df: pd.DataFrame) -> dict[str, float]:
    """Ingreso promedio por unidad jurídica de cada tamaño en el último año."""
    cat = columna_categoria(df)
    col_ing = buscar_columna(df, "Ingresos")
    col_uj = buscar_columna(df, "Cantidad UJ", "Unidades jurídicas")

    anio = int(df["Año"].dropna().max())
    datos = df[(df["Año"] == anio) & (df[cat].astype(str).isin(TAMANIOS))]
    datos = datos.set_index(datos[cat].astype(str))

    ingresos = {}
    for tam in TAMANIOS:
        if tam in datos.index:
            uj = datos.loc[tam, col_uj]
            ing = datos.loc[tam, col_ing]
            ingresos[tam] = float(ing / uj) if uj and uj > 0 else 0.0
        else:
            ingresos[tam] = 0.0
    return ingresos


def optimizar_asignacion(df: pd.DataFrame) -> go.Figure:
    """Resuelve el modelo de asignación y devuelve figura con barras y tabla."""
    ingreso = _ingreso_por_uj(df)

    modelo = pulp.LpProblem("asignacion_recursos", pulp.LpMaximize)
    x = {tam: pulp.LpVariable(f"x_{tam}", lowBound=0) for tam in TAMANIOS}

    modelo += pulp.lpSum(x[tam] * ingreso[tam] for tam in TAMANIOS)

    modelo += pulp.lpSum(x.values()) == 1
    for tam in TAMANIOS:
        modelo += x[tam] >= MIN_CADA
    modelo += x["Micro"] >= MIN_MICRO
    modelo += x["Grande"] <= MAX_GRANDE

    modelo.solve(pulp.PULP_CBC_CMD(msg=False))

    asignacion = {tam: x[tam].value() for tam in TAMANIOS}
    aporte = {tam: asignacion[tam] * ingreso[tam] for tam in TAMANIOS}
    total = pulp.value(modelo.objective)

    fig = make_subplots(
        rows=1, cols=2, column_widths=[0.55, 0.45],
        specs=[[{"type": "xy"}, {"type": "table"}]],
        subplot_titles=("Asignación óptima de recursos", "Detalle del modelo"),
    )

    fig.add_trace(
        go.Bar(x=TAMANIOS, y=[asignacion[t] for t in TAMANIOS],
               text=[f"{asignacion[t]:.0%}" for t in TAMANIOS],
               textposition="outside", marker_color="#2980b9",
               name="Proporción"),
        row=1, col=1,
    )

    fig.add_trace(
        go.Table(
            header=dict(
                values=["Tamaño", "Ingreso/UJ (₡)", "Asignación", "Aporte (₡)"],
                fill_color="#2c3e50", font=dict(color="white"), align="left"),
            cells=dict(
                values=[
                    TAMANIOS,
                    [f"{ingreso[t]:,.0f}" for t in TAMANIOS],
                    [f"{asignacion[t]:.0%}" for t in TAMANIOS],
                    [f"{aporte[t]:,.0f}" for t in TAMANIOS],
                ],
                align="left"),
        ),
        row=1, col=2,
    )

    fig.update_yaxes(tickformat=".0%", title_text="Proporción", row=1, col=1)
    fig.update_layout(
        title=f"Ingreso potencial total maximizado: ₡{total:,.0f} por UJ",
        showlegend=False,
    )
    return fig
