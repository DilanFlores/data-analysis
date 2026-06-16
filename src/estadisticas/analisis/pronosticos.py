"""Pronósticos de series anuales: PM3, suavización exponencial y Holt.

Compara tres modelos por MAPE, elige el mejor y proyecta 3 años.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.holtwinters import Holt, SimpleExpSmoothing

from estadisticas.analisis._utiles import serie_total

PASOS = 3  # años a proyectar (2025, 2026, 2027)


def _mape(real: np.ndarray, pred: np.ndarray) -> float:
    """Error porcentual absoluto medio, ignorando valores reales nulos o cero."""
    real = np.asarray(real, dtype=float)
    pred = np.asarray(pred, dtype=float)
    valido = np.isfinite(real) & np.isfinite(pred) & (real != 0)
    if not valido.any():
        return float("nan")
    return float(np.mean(np.abs((real[valido] - pred[valido]) / real[valido])) * 100)


def _pm3(valores: np.ndarray) -> tuple[np.ndarray, list[float]]:
    """Promedio móvil de 3 períodos: ajuste histórico y proyección."""
    ajuste = np.full(len(valores), np.nan)
    for i in range(3, len(valores)):
        ajuste[i] = valores[i - 3:i].mean()

    historico = list(valores)
    pronostico = []
    for _ in range(PASOS):
        siguiente = float(np.mean(historico[-3:]))
        pronostico.append(siguiente)
        historico.append(siguiente)
    return ajuste, pronostico


def _exponencial(valores: np.ndarray, doble: bool) -> tuple[np.ndarray, list[float]]:
    """Ajusta SES (doble=False) o Holt (doble=True) y proyecta PASOS períodos."""
    serie = pd.Series(valores, dtype=float)
    Modelo = Holt if doble else SimpleExpSmoothing
    ajustado = Modelo(serie, initialization_method="estimated").fit()
    ajuste = ajustado.fittedvalues.to_numpy()
    pronostico = ajustado.forecast(PASOS).tolist()
    return ajuste, pronostico


def pronosticar(df: pd.DataFrame, metrica: str) -> go.Figure:
    """Compara PM3, SES y Holt sobre la serie total de `metrica`.

    Devuelve una figura con las curvas, los pronósticos y una tabla de MAPE.
    """
    serie = serie_total(df, metrica)
    anios = serie.index.tolist()
    valores = serie.to_numpy(dtype=float)
    futuros = [anios[-1] + k for k in range(1, PASOS + 1)]

    aj_pm3, pr_pm3 = _pm3(valores)
    aj_ses, pr_ses = _exponencial(valores, doble=False)
    aj_holt, pr_holt = _exponencial(valores, doble=True)

    modelos = {
        "Promedio Móvil (3)": (aj_pm3, pr_pm3),
        "Suavización Exponencial": (aj_ses, pr_ses),
        "Holt (doble exponencial)": (aj_holt, pr_holt),
    }
    errores = {nom: _mape(valores, aj) for nom, (aj, _) in modelos.items()}
    mejor = min(errores, key=lambda n: errores[n])

    fig = make_subplots(
        rows=2, cols=1, row_heights=[0.72, 0.28], vertical_spacing=0.08,
        specs=[[{"type": "xy"}], [{"type": "table"}]],
    )

    fig.add_trace(
        go.Scatter(x=anios, y=valores, mode="lines+markers", name="Real",
                   line=dict(color="#222", width=3)),
        row=1, col=1,
    )
    for nombre, (ajuste, pronostico) in modelos.items():
        destacado = nombre == mejor
        # Curva histórica (ajuste) + pronóstico encadenado al último real.
        x_curva = anios + futuros
        y_curva = list(ajuste) + list(pronostico)
        fig.add_trace(
            go.Scatter(
                x=x_curva, y=y_curva, mode="lines+markers",
                name=f"{nombre}{' ★' if destacado else ''}",
                line=dict(width=3 if destacado else 1.5,
                          dash="solid" if destacado else "dot"),
            ),
            row=1, col=1,
        )

    fig.add_vline(x=anios[-1] + 0.5, line_dash="dash", line_color="gray",
                  row=1, col=1)

    fig.add_trace(
        go.Table(
            header=dict(values=["Modelo", "MAPE (%)"] + [str(a) for a in futuros],
                        fill_color="#2c3e50", font=dict(color="white"),
                        align="left"),
            cells=dict(
                values=[
                    list(modelos.keys()),
                    [f"{errores[n]:.2f}" for n in modelos],
                    *[[f"{pr:,.0f}" for pr in
                       [modelos[n][1][k] for n in modelos]] for k in range(PASOS)],
                ],
                align="left",
                fill_color=[["#eafaf1" if n == mejor else "white"
                             for n in modelos]],
            ),
        ),
        row=2, col=1,
    )

    fig.update_layout(
        title=f"Pronóstico de {metrica} — mejor modelo: {mejor} "
              f"(MAPE {errores[mejor]:.2f}%)",
        hovermode="x unified", legend_title_text="Serie",
    )
    return fig
