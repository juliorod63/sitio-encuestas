import streamlit as st
import pandas as pd
import plotly.express as px


from utils import ENCUESTAS, load_data, transformacion_df, calcular_NPS_Alexia, calcular_NPS_Modulo, calcular_CSAT, transformar_centros, calcular_CSAT_Capacitacion

#nlp = spacy.load("es_core_news_sm")


def calcular_metricas_basicas(datos):
    return {
        "Respuestas": datos.shape[0],
        "NPS Alexia": calcular_NPS_Alexia(datos),
        "NPS Modulo": calcular_NPS_Modulo(datos),
        "CSAT Alexia": calcular_CSAT(datos),
        "CSAT Capacitación": calcular_CSAT_Capacitacion(datos),
    }


def mostrar_metrica(columna, etiqueta, valor, comparativa_2025=None, ayuda=None):
    if etiqueta == "Respuestas":
        columna.metric(label=etiqueta, value=f"{valor}", help=ayuda)
        if comparativa_2025 is not None:
            columna.markdown(
                f'<span style="color:#6b7280; font-size:0.95rem;">2025: <strong>{comparativa_2025}</strong></span>',
                unsafe_allow_html=True,
            )
        return

    columna.metric(label=etiqueta, value=f"{valor:.2f}", help=ayuda)
    if comparativa_2025 is None:
        columna.markdown(
            '<span style="color:#6b7280; font-size:0.95rem;">2025: <strong>sin comparativa</strong></span>',
            unsafe_allow_html=True,
        )
    else:
        columna.markdown(
            f'<span style="color:#6b7280; font-size:0.95rem;">2025: <strong>{comparativa_2025:.2f}</strong></span>',
            unsafe_allow_html=True,
        )

st.set_page_config(
    page_title="Resultados Encuesta Satisfacción Clientes Chile",
    page_icon=":bar_chart:",
    layout="wide"
)

st.sidebar.image("flag_chile.png")


st.title("Resultados Encuesta Satisfacción Clientes Chile")
st.write("Bienvenido a la aplicación de Resultados Encuesta Satisfacción Clientes Chile.")

password_guess = st.text_input("Ingrese la contraseña para acceder a los resultados:", type="password")

if password_guess != st.secrets["password"]:
   
    st.write("Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()
else:
    st.sidebar.header("Resultados de la Encuesta")

    encuesta_seleccionada = st.sidebar.selectbox(
        "Selecciona la encuesta:",
        options=list(ENCUESTAS),
    )
    if "version_cache_datos" not in st.session_state:
        st.session_state["version_cache_datos"] = 0

    if st.sidebar.button("Actualizar datos desde GitHub"):
        st.session_state["version_cache_datos"] += 1
        load_data.clear()
        st.sidebar.success("Datos actualizados desde el origen.")

    st.sidebar.markdown("- [Resultados de la Encuesta](#resultados-de-la-encuesta)")
    st.sidebar.markdown("- [Métricas Clave](#metricas-clave)")
    st.sidebar.markdown("- [Evaluaciones adicionales](#evaluaciones-adicionales)")
    st.sidebar.markdown("- [Análisis de Respuestas por Centro](#analisis-de-respuestas-por-centro)")
    st.sidebar.markdown("- [Análisis de Respuestas por Grupo Educativo](#analisis-de-respuestas-por-grupo-educativo)")
    st.sidebar.markdown("- [Análisis Detallado por Centro](#analisis-detallado-por-centro)")
    st.sidebar.markdown("- [Matriz de Correlación de Centros Seleccionados](#matriz-de-correlacion-de-centros-seleccionados)")
    st.sidebar.markdown("- [Análisis de NPS por Variables](#analisis-de-nps-por-variables)")
    st.sidebar.markdown("- [Análisis NPS y CSAT por Rol](#analisis-nps-y-csat-por-rol)")
    
    st.success("Contraseña correcta. Acceso concedido.")

df = load_data(encuesta_seleccionada, st.session_state["version_cache_datos"])

st.markdown(f"### Resultados de la Encuesta {ENCUESTAS[encuesta_seleccionada]['anio']}")
st.write(" Respuestas: ", df.shape[0])


df = transformacion_df(df)

df = transformar_centros(df)

df_comparativa_2025 = None
if ENCUESTAS[encuesta_seleccionada]["anio"] == 2026:
    df_comparativa_2025 = load_data("Encuesta 2025", st.session_state["version_cache_datos"])
    df_comparativa_2025 = transformacion_df(df_comparativa_2025)
    df_comparativa_2025 = transformar_centros(df_comparativa_2025)

st.dataframe(df)
st.header("Métricas Clave")

modulos = sorted(df["Modulo_Usado"].dropna().unique())
modulo_seleccionado = st.selectbox(
    "Filtra las métricas por módulo:",
    options=["Todos los módulos", *modulos],
)
if modulo_seleccionado == "Todos los módulos":
    df_metricas = df
else:
    df_metricas = df[df["Modulo_Usado"] == modulo_seleccionado]
    if df_comparativa_2025 is not None:
        df_comparativa_2025 = df_comparativa_2025[df_comparativa_2025["Modulo_Usado"] == modulo_seleccionado]

grupos_educativos = sorted(df_metricas["Grupo_Educativo"].dropna().unique())
grupo_educativo_seleccionado = st.selectbox(
    "Filtra las métricas por grupo educativo:",
    options=["Todos los grupos educativos", *grupos_educativos],
)
if grupo_educativo_seleccionado != "Todos los grupos educativos":
    df_metricas = df_metricas[df_metricas["Grupo_Educativo"] == grupo_educativo_seleccionado]
    if df_comparativa_2025 is not None:
        df_comparativa_2025 = df_comparativa_2025[df_comparativa_2025["Grupo_Educativo"] == grupo_educativo_seleccionado]

roles = sorted(df_metricas["Cargo"].dropna().unique())
rol_seleccionado = st.selectbox(
    "Filtra las métricas por rol:",
    options=["Todos los roles", *roles],
)
if rol_seleccionado != "Todos los roles":
    df_metricas = df_metricas[df_metricas["Cargo"] == rol_seleccionado]
    if df_comparativa_2025 is not None:
        df_comparativa_2025 = df_comparativa_2025[df_comparativa_2025["Cargo"] == rol_seleccionado]

antiguedades = sorted(df_metricas["Antiguedad"].dropna().unique())
antiguedad_seleccionada = st.selectbox(
    "Filtra las métricas por antigüedad de uso:",
    options=["Todas las antigüedades", *antiguedades],
)
if antiguedad_seleccionada != "Todas las antigüedades":
    df_metricas = df_metricas[df_metricas["Antiguedad"] == antiguedad_seleccionada]
    if df_comparativa_2025 is not None:
        df_comparativa_2025 = df_comparativa_2025[df_comparativa_2025["Antiguedad"] == antiguedad_seleccionada]

if "Mejoras_Implementadas" in df_metricas.columns:
    df_metricas = df_metricas.copy()
    df_metricas["Grupo_Mejoras_Implementadas"] = df_metricas["Mejoras_Implementadas"].fillna("Sin respuesta")
    grupos_mejoras = sorted(df_metricas["Grupo_Mejoras_Implementadas"].unique())
    grupos_mejoras_seleccionados = st.multiselect(
        "Filtra las métricas por evaluación de mejoras implementadas:",
        options=["Todas las evaluaciones", *grupos_mejoras],
        default=["Todas las evaluaciones"],
    )
    if grupos_mejoras_seleccionados and "Todas las evaluaciones" not in grupos_mejoras_seleccionados:
        df_metricas = df_metricas[df_metricas["Grupo_Mejoras_Implementadas"].isin(grupos_mejoras_seleccionados)]
        if df_comparativa_2025 is not None:
            if "Mejoras_Implementadas" in df_comparativa_2025.columns:
                df_comparativa_2025 = df_comparativa_2025[df_comparativa_2025["Mejoras_Implementadas"].isin(grupos_mejoras_seleccionados)]
            else:
                df_comparativa_2025 = None

st.divider()
with st.expander("¿Cómo calculamos el NPS y el CSAT?"):

    st.markdown("""
    El NPS (Net Promoter Score) se calcula restando el porcentaje de detractores del porcentaje de promotores.\n
    **Fórmula:**
    ```python
    NPS = (Promotores - Detractores) / Total de respuestas × 100
    promoters = df[df["NPS_Recomendar"] >= 9].shape[0]
    detractors = df[df["NPS_Recomendar"] <= 6].shape[0]
    total = df["NPS_Recomendar"].shape[0]
    nps = ((promoters - detractors) / total) * 100
   

    """)
    st.markdown("""
    El CSAT (Customer Satisfaction Score) se calcula como el porcentaje de respuestas positivas sobre el total de respuestas.\n
    **Fórmula:**
    ```python
    CSAT = (Respuestas positivas / Total de respuestas) × 100
    csat = (df["CS_Alexia"].isin([4, 5]).sum() / df["CS_Alexia"].count()) * 100
    """)

    st.markdown("""
    **Error Muestral: 0,0295 %**\n
    Se calcula utilizando la fórmula del error estándar para proporciones:\n
    **Fórmula:**
    - Error Muestral= ± Z * s / √(n)
    - Donde:
      - Z es el valor crítico (1.96 para un nivel de confianza del 95%)
      - s es la desviación estándar de las respuestas (calculo en base a la proporción de respuestas del NPS)
      - n es el tamaño de la muestra
    """)

metricas_actuales = calcular_metricas_basicas(df_metricas)
metricas_2025 = None
if df_comparativa_2025 is not None and not df_comparativa_2025.empty:
    metricas_2025 = calcular_metricas_basicas(df_comparativa_2025)

col1, col2, col3, col4, col5 = st.columns(5)
mostrar_metrica(col1, "Respuestas", metricas_actuales["Respuestas"], metricas_2025["Respuestas"] if metricas_2025 else None, "Cantidad de respuestas incluidas en los filtros de métricas")
mostrar_metrica(col2, "NPS Alexia", metricas_actuales["NPS Alexia"], metricas_2025["NPS Alexia"] if metricas_2025 else None, "NPS basado en la pregunta de recomendar Alexia")
mostrar_metrica(col3, "NPS Modulo", metricas_actuales["NPS Modulo"], metricas_2025["NPS Modulo"] if metricas_2025 else None, "NPS basado en la pregunta de recomendar el Módulo")
mostrar_metrica(col4, "CSAT Alexia", metricas_actuales["CSAT Alexia"], metricas_2025["CSAT Alexia"] if metricas_2025 else None, "CSAT basado en la satisfacción general con Alexia")
mostrar_metrica(col5, "CSAT Capacitación", metricas_actuales["CSAT Capacitación"], metricas_2025["CSAT Capacitación"] if metricas_2025 else None, "CSAT basado en la satisfacción con la Capacitación")

df_metricas = df_metricas.copy()
df_metricas["Segmento_NPS"] = pd.cut(
    df_metricas["NPS_Recomendar"],
    bins=[-1, 6, 8, 10],
    labels=["Detractores (0-6)", "Pasivos (7-8)", "Promotores (9-10)"],
)
distribucion_nps = df_metricas["Segmento_NPS"].value_counts().reindex(
    ["Detractores (0-6)", "Pasivos (7-8)", "Promotores (9-10)"],
    fill_value=0,
).reset_index()
distribucion_nps.columns = ["Segmento NPS", "Respuestas"]
fig = px.bar(
    distribucion_nps,
    x="Segmento NPS",
    y="Respuestas",
    color="Segmento NPS",
    text="Respuestas",
    title="Distribución de NPS",
    color_discrete_map={
        "Detractores (0-6)": "#d62728",
        "Pasivos (7-8)": "#ffbf00",
        "Promotores (9-10)": "#2ca02c",
    },
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

fig = px.histogram(
    df_metricas,
    x="NPS_Recomendar",
    nbins=11,
    range_x=[0, 10],
    title="Histograma de NPS Recomendar",
)
fig.update_traces(marker_color="#38bdf8")
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Selecciona las columnas numéricas que quieres comparar
cols = ["CS_Alexia", "NPS_Modulo", "NPS_Recomendar", "Satisf_Modulo", "Funcionalidad_Alexia", "Amigable_Alexia", "Capacitacion"]  # ajusta según tus datos

columnas_adicionales = ["Soporte_Tecnico", "Centro_Ayuda", "Mejoras_Implementadas"]
if any(columna in df.columns for columna in columnas_adicionales):
    st.markdown("### Evaluaciones adicionales")

    if "Soporte_Tecnico" in df.columns:
        st.plotly_chart(
            px.histogram(
                df,
                x="Soporte_Tecnico",
                title="Evaluación del soporte técnico",
            ),
            use_container_width=True,
        )

    if "Centro_Ayuda" in df.columns:
        centro_ayuda = df["Centro_Ayuda"].value_counts().reset_index()
        centro_ayuda.columns = ["Evaluación", "Respuestas"]
        st.plotly_chart(
            px.bar(
                centro_ayuda,
                x="Evaluación",
                y="Respuestas",
                title="Evaluación del centro de ayuda",
            ),
            use_container_width=True,
        )

    if "Mejoras_Implementadas" in df.columns:
        mejoras_implementadas = df["Mejoras_Implementadas"].value_counts().reset_index()
        mejoras_implementadas.columns = ["Evaluación", "Respuestas"]
        st.plotly_chart(
            px.bar(
                mejoras_implementadas,
                x="Evaluación",
                y="Respuestas",
                title="Evaluación de mejoras implementadas",
            ),
            use_container_width=True,
        )

st.markdown("### Análisis de Respuestas por Centro")

centros_count = df["Centro"].value_counts().reset_index()
centros_count.columns = ["Centro", "Respuestas"]

st.metric(label="Centros", value=f"{centros_count.shape[0]}")

fig = px.bar(centros_count, x="Centro", y="Respuestas", title="Cantidad de respuestas por Centro")
st.plotly_chart(fig)

# calcular_NPS_Alexia recibe un DataFrame y calcula el NPS
tabla_nps = df.groupby("Centro", group_keys=False).apply(calcular_NPS_Alexia).reset_index()
tabla_nps.columns = ["Centro", "NPS_Alexia"]


fig = px.bar(tabla_nps, x="Centro", y="NPS_Alexia", title="NPS Alexia por Centro")
st.plotly_chart(fig)

tabla_nps["Clasificación NPS"] = pd.cut(
    tabla_nps["NPS_Alexia"],
    bins=[-101, -0.0001, 0.0001, 100],
    labels=["Negativo", "Neutro", "Positivo"],
)
resumen_nps_centros = tabla_nps["Clasificación NPS"].value_counts().reindex(
    ["Positivo", "Neutro", "Negativo"],
    fill_value=0,
).reset_index()
resumen_nps_centros.columns = ["Clasificación NPS", "Centros"]
fig = px.bar(
    resumen_nps_centros,
    x="Clasificación NPS",
    y="Centros",
    color="Clasificación NPS",
    text="Centros",
    title="Cantidad de centros por clasificación NPS",
    color_discrete_map={
        "Positivo": "#2ca02c",
        "Neutro": "#ffbf00",
        "Negativo": "#d62728",
    },
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Análisis de Respuestas por Grupo Educativo")
st.info("Sección preparada para incorporar el análisis por grupo educativo.")

st.markdown("### Análisis Detallado por Centro")
# Selector de centro
centros_ordenados = sorted(df["Centro"].unique())
centros_seleccionados = st.multiselect(
    "Selecciona uno o más centros:",
    centros_ordenados,
)
if not centros_seleccionados:
    centros_seleccionados = centros_ordenados
    st.info("Sin centros seleccionados: se muestran todos los centros.")

# Filtra el DataFrame por los centros seleccionados
df_filtrado = df[df["Centro"].isin(centros_seleccionados)]
st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(label="Respuestas", value=f"{df_filtrado.shape[0]}")
col2.metric(label="NPS Recomendar", value=f"{calcular_NPS_Alexia(df_filtrado):.2f}")
col3.metric(label="NPS Modulo", value=f"{calcular_NPS_Modulo(df_filtrado):.2f}")
col4.metric(label="CSAT Alexia", value=f"{calcular_CSAT(df_filtrado):.2f}")
col5.metric(label="CSAT Capacitación", value=f"{calcular_CSAT_Capacitacion(df_filtrado):.2f}")

import plotly.graph_objects as go

# Supón que df_filtrado es tu DataFrame filtrado
categorias = ["CS_Alexia", "NPS_Modulo", "NPS_Recomendar", "Satisf_Modulo", "Funcionalidad_Alexia", "Amigable_Alexia", "Capacitacion"]
valores = [df_filtrado[c].mean() for c in categorias]

fig = go.Figure(
    data=[
        go.Scatterpolar(
            r=valores,
            theta=categorias,
            fill='toself',
            name='Promedio'
        )
    ]
)
fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10]),
        domain=dict(x=[0.05, 0.95], y=[0.05, 0.95])
    ),
    height=700,
    margin=dict(l=80, r=80, t=80, b=80),
    showlegend=False,
    title="Radar de Métricas Clave"
)

st.plotly_chart(fig, use_container_width=True)

# Grafica la distribución de NPS_Alexia para ese centro
fig = px.histogram(df_filtrado, x="NPS_Recomendar", color="Cargo", nbins=10, range_x=[1,10],title="Distribución de NPS_Recomendar en centros seleccionados")
st.plotly_chart(fig)

fig = px.histogram(df_filtrado, x="CS_Alexia", color="Cargo", nbins=10, range_x=[1,5], title="Distribución de CSAT Alexia en centros seleccionados")
st.plotly_chart(fig)

st.markdown("### Matriz de Correlación de Centros Seleccionados")
min_respuestas_correlacion = 3
columnas_correlacion = [
    columna
    for columna in cols
    if df_filtrado[columna].count() >= min_respuestas_correlacion and df_filtrado[columna].nunique(dropna=True) > 1
]
if df_filtrado.shape[0] < min_respuestas_correlacion:
    st.warning(
        f"La matriz de correlación necesita al menos {min_respuestas_correlacion} respuestas. "
        f"La selección actual tiene {df_filtrado.shape[0]}."
    )
elif len(columnas_correlacion) < 2:
    st.warning("La selección actual no tiene suficiente variación en al menos dos métricas para calcular la correlación.")
else:
    if df_filtrado.shape[0] < 10:
        st.info("La selección tiene menos de 10 respuestas; interpreta la correlación como una señal exploratoria.")
    correlation_matrix = df_filtrado[columnas_correlacion].corr()
    fig = px.imshow(correlation_matrix, text_auto=True, title="Matriz de Correlación de Centros Seleccionados")
    fig.update_layout(height=750)
    st.plotly_chart(fig, use_container_width=True)


st.plotly_chart(px.histogram(df, x="NPS_Recomendar", color="Cargo", title="Distribución de NPS x Cargo"))

st.plotly_chart(px.histogram(df, x="NPS_Recomendar", color="Modulo_Usado", title="Distribución de NPS x Modulo"))

st.plotly_chart(px.histogram(df, x="CS_Alexia", color="Modulo_Usado", title="Distribución de CS x Modulo"))

st.plotly_chart(px.histogram(df, x="Cargo", color="Modulo_Usado", title="Distribución x Cargo x Modulo"))

st.plotly_chart(px.histogram(df, x="NPS_Modulo", color="Antiguedad", title="Distribución por NPS Modulo y Antiguedad"))

st.plotly_chart(px.histogram(df, x="Funcionalidad_Alexia", color="Cargo", title="Distribución por Funcionalidad y Cargo"))

st.plotly_chart(px.histogram(df, x="Amigable_Alexia", color="Cargo", title="Distribución por Amigable y Cargo"))


st.markdown("### Análisis de NPS por Variables")
# Supón que df es tu DataFrame ya cargado y transformado
variables = ["Cargo", "Antiguedad", "Centro", "Modulo_Usado"]  # agrega las variables que quieras analizar

opcion = st.selectbox("Selecciona una variable para analizar NPS_Recomendacion:", variables)

# Gráfico de distribución de NPS_Recomendacion según la variable seleccionada
fig = px.violin(df, x=opcion, y="NPS_Recomendar", title=f"NPS_Recomendacion según {opcion}")
st.plotly_chart(fig)

fig = px.violin(df, x=opcion, y="CS_Alexia", title=f"Satifaccion Alexia según {opcion}")
st.plotly_chart(fig)

st.markdown("### NPS_Alexia por Centro")
st.dataframe(tabla_nps)

st.markdown("### Análisis NPS y CSAT por Rol"  )
tabla_nps_rol = df.groupby("Cargo", group_keys=False).apply(calcular_NPS_Alexia).reset_index()
tabla_nps_rol.columns = ["Cargo", "NPS_Alexia"]

fig = px.bar(tabla_nps_rol, x="Cargo", y="NPS_Alexia", title="NPS Alexia por Cargo")
st.plotly_chart(fig)

tabla_csat_rol = df.groupby("Cargo", group_keys=False).apply(calcular_CSAT).reset_index()
tabla_csat_rol.columns = ["Cargo", "CSAT_Alexia"]

fig = px.bar(tabla_csat_rol, x="Cargo", y="CSAT_Alexia", title="CSAT Alexia por Cargo")
st.plotly_chart(fig)

# Agrupar y calcular promedio CSAT
df_burbujas = df.groupby(['Cargo', 'Antiguedad'], as_index=False)['CS_Alexia'].mean()
df_burbujas.rename(columns={'CS_Alexia': 'CSAT_promedio'}, inplace=True)

fig = px.scatter(
    df_burbujas,
    x='Cargo',
    y='Antiguedad',
    size='CSAT_promedio',
    color='Cargo',
    title='CSAT promedio por Cargo y Antigüedad',
    size_max=40
)
fig.update_xaxes(type='category')
st.plotly_chart(fig)

