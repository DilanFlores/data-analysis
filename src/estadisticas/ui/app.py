"""Interfaz Streamlit: subir el Excel y explorar los gráficos."""

from __future__ import annotations

import streamlit as st

from estadisticas import analisis, charts
from estadisticas.config import HOJAS
from estadisticas.data import (
    cargar_hoja,
    columna_categoria,
    columnas_numericas,
    listar_hojas_disponibles,
)

# Variables de la hoja C1 sobre las que operan los métodos cuantitativos.
VAR_UJ = "Cantidad UJ"
VAR_TRABAJADORES = "Número de trabajadores"


def _sidebar_carga():
    """Widget para subir el archivo. Devuelve el buffer o None."""
    st.sidebar.header("1. Cargar datos")
    return st.sidebar.file_uploader(
        "Subí el Excel de estadísticas empresariales",
        type=["xlsx", "xlsm"],
    )


def _mostrar_graficos(df, hoja: str):
    """Renderiza todos los gráficos aplicables a la hoja seleccionada."""
    metricas = columnas_numericas(df)
    categoria = columna_categoria(df)

    if not metricas:
        st.warning("No se encontraron columnas numéricas para graficar.")
        return

    st.subheader("Configuración del gráfico")
    metrica = st.selectbox("Métrica a visualizar", metricas)

    # --- Serie temporal ---
    if "Año" in df.columns:
        st.markdown("### Evolución en el tiempo")
        st.plotly_chart(
            charts.serie_temporal(df, metrica, categoria),
            use_container_width=True,
        )

    # --- Gráficos por categoría ---
    if categoria:
        anios = sorted(df["Año"].dropna().unique()) if "Año" in df.columns else []
        anio = st.select_slider("Año", options=anios, value=anios[-1]) if anios else None

        st.markdown("### Comparación por categoría")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                charts.barras_por_categoria(df, metrica, categoria, anio),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                charts.participacion_pastel(df, metrica, categoria, anio),
                use_container_width=True,
            )

        if "Año" in df.columns:
            st.markdown("### Composición a lo largo del tiempo")
            st.plotly_chart(
                charts.composicion_apilada(df, metrica, categoria),
                use_container_width=True,
            )

    # --- Comercio exterior ---
    fig_comercio = charts.comparar_comercio(df)
    if fig_comercio is not None:
        st.markdown("### Comercio exterior")
        st.plotly_chart(fig_comercio, use_container_width=True)


def _mostrar_metodos(df):
    """Cuatro pestañas con los métodos cuantitativos sobre la hoja C1."""
    st.markdown("---")
    st.header(" Métodos Cuantitativos")
    st.caption("Análisis aplicados sobre el cuadro C1 (tamaño empresarial).")

    tab_pron, tab_pl, tab_cep, tab_mk = st.tabs(
        [" Pronósticos", " Programación lineal",
         " Control estadístico", " Cadenas de Markov"]
    )

    with tab_pron:
        st.markdown("Modelos PM3, suavización exponencial y Holt; se elige el "
                    "de menor MAPE y se proyectan 2025–2027.")
        for variable in (VAR_UJ, VAR_TRABAJADORES):
            st.plotly_chart(analisis.pronosticar(df, variable),
                            use_container_width=True)

    with tab_pl:
        st.markdown("Asignación óptima de recursos por tamaño para maximizar el "
                    "ingreso potencial total (PuLP).")
        st.plotly_chart(analisis.optimizar_asignacion(df),
                        use_container_width=True)

    with tab_cep:
        st.markdown("Cartas I-MR (individuales y rango móvil) con límites a "
                    "±3σ; los puntos en rojo están fuera de control.")
        for variable in (VAR_TRABAJADORES, "Ingresos (₡)"):
            st.plotly_chart(analisis.grafico_imr(df, variable),
                            use_container_width=True)

    with tab_mk:
        st.markdown("Matriz de transición entre tamaños y proyección de la "
                    "composición empresarial a 5, 10 y 20 años.")
        st.plotly_chart(analisis.proyectar_markov(df, VAR_UJ),
                        use_container_width=True)


def main():
    st.set_page_config(page_title="Estadísticas Empresariales CR",
                       page_icon="📊", layout="wide")
    st.title(" Estadísticas Empresariales de Costa Rica (2005–2024)")

    archivo = _sidebar_carga()
    if archivo is None:
        st.info(" Subí el archivo Excel en la barra lateral para comenzar.")
        return

    hojas = listar_hojas_disponibles(archivo)
    if not hojas:
        st.error("El archivo no contiene hojas reconocidas (C1–C4).")
        return

    st.sidebar.header("2. Elegir hoja")
    hoja = st.sidebar.selectbox(
        "Cuadro a explorar",
        hojas,
        format_func=lambda h: f"{h} — {HOJAS[h].titulo}",
    )

    df = cargar_hoja(archivo, hoja)
    st.caption(HOJAS[hoja].titulo)

    with st.expander("Ver datos (tabla)"):
        st.dataframe(df, use_container_width=True)

    _mostrar_graficos(df, hoja)

    # Métodos cuantitativos: siempre sobre la hoja C1, independientemente de la
    # hoja que se esté explorando arriba.
    if "C1" in hojas:
        df_c1 = df if hoja == "C1" else cargar_hoja(archivo, "C1")
        _mostrar_metodos(df_c1)


if __name__ == "__main__":
    main()
