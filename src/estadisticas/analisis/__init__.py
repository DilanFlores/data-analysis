"""Métodos cuantitativos aplicados a las estadísticas empresariales."""

from estadisticas.analisis.control_estadistico import grafico_imr
from estadisticas.analisis.markov import proyectar_markov
from estadisticas.analisis.programacion_lineal import optimizar_asignacion
from estadisticas.analisis.pronosticos import pronosticar

__all__ = [
    "grafico_imr",
    "optimizar_asignacion",
    "pronosticar",
    "proyectar_markov",
]
