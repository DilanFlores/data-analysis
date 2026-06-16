# Estadísticas Empresariales de Costa Rica (2005–2024)

App en Python para subir el Excel de estadísticas empresariales y explorar
sus gráficos de forma interactiva. El código está organizado por
responsabilidades, no en una sola clase.

## Estructura

```
estadisticas_empresariales/
├── app.py                      # Punto de entrada (streamlit run app.py)
├── requirements.txt
└── src/estadisticas/
    ├── config.py               # Hojas, columnas, unidades, constantes
    ├── data/
    │   └── loader.py           # Carga y limpieza del Excel
    ├── charts/
    │   └── builders.py         # Una función por tipo de gráfico
    └── ui/
        └── app.py              # Interfaz Streamlit (subir archivo + mostrar)
```

Cada capa hace una sola cosa:

- **`config`** — el "qué" del archivo: qué hojas existen y cómo leerlas.
- **`data/loader`** — convierte el Excel crudo en DataFrames limpios
  (trata `"x"` y `"nd"` como faltantes, convierte tipos, normaliza columnas).
- **`charts/builders`** — recibe un DataFrame y devuelve figuras de Plotly.
  Funciones puras: fáciles de probar y reutilizar fuera de la UI.
- **`ui/app`** — solo orquesta: sube el archivo, elige hoja, pinta gráficos.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en el navegador. En la barra lateral:

1. **Cargar datos** → subí `Estadisticas_empresariales_2005_2024.xlsx`.
2. **Elegir hoja** → C1 a C4.
3. Elegí la métrica y explorá los gráficos.

## Gráficos disponibles

- 📈 Serie temporal (evolución 2005–2024, una línea por tamaño).
- 📊 Barras por categoría para un año seleccionable.
- 🥧 Pastel de participación por categoría.
- 🗂️ Área apilada (composición en el tiempo).
- 🌎 Exportaciones vs importaciones.

## Hojas soportadas

C1–C4 (encabezado simple). Las hojas C5 usan encabezados de varios
niveles y quedan fuera del lector automático; se pueden agregar
extendiendo `config.HOJAS` y `data/loader.py`.
