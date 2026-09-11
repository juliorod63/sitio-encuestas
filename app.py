import json

import streamlit as st
import pandas as pd
import plotly.express as px


from utils import ENCUESTAS, load_data, transformacion_df, calcular_NPS_Alexia, calcular_NPS_Modulo, calcular_CSAT, transformar_centros, calcular_CSAT_Capacitacion, generar_analisis_inteligente_openrouter

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


PUNTAJES_NPS = list(range(0, 11))
PUNTAJES_CSAT = list(range(1, 6))


def preparar_distribucion_puntajes(datos, columna, puntajes, grupo=None):
    base = datos.copy()
    base[columna] = pd.to_numeric(base[columna], errors="coerce")
    base = base[base[columna].isin(puntajes)].copy()
    base["Puntaje"] = base[columna].astype(int)

    if grupo is None:
        return base["Puntaje"].value_counts().reindex(puntajes, fill_value=0).rename_axis("Puntaje").reset_index(name="Respuestas")

    base[grupo] = base[grupo].fillna("Sin dato")
    grupos = sorted(base[grupo].unique())
    indice = pd.MultiIndex.from_product([puntajes, grupos], names=["Puntaje", grupo])
    return base.groupby(["Puntaje", grupo]).size().reindex(indice, fill_value=0).reset_index(name="Respuestas")


def grafico_distribucion_puntajes(datos, columna, titulo, puntajes, grupo=None, color=None):
    distribucion = preparar_distribucion_puntajes(datos, columna, puntajes, grupo)
    grafico = px.bar(
        distribucion,
        x="Puntaje",
        y="Respuestas",
        color=grupo,
        text="Respuestas",
        title=titulo,
    )
    if grupo is None and color:
        grafico.update_traces(marker_color=color)
    grafico.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=puntajes,
        tickmode="array",
        tickvals=puntajes,
    )
    return grafico


def grafico_distribucion_puntajes_nps(datos, columna, titulo, grupo=None):
    return grafico_distribucion_puntajes(datos, columna, titulo, PUNTAJES_NPS, grupo, "#38bdf8")


def grafico_distribucion_puntajes_csat(datos, columna, titulo, grupo=None):
    return grafico_distribucion_puntajes(datos, columna, titulo, PUNTAJES_CSAT, grupo, "#38bdf8")


def resumen_segmentos_nps(datos):
    segmentos = pd.cut(
        datos["NPS_Recomendar"],
        bins=[-1, 6, 8, 10],
        labels=["Detractores", "Pasivos", "Promotores"],
    )
    return segmentos.value_counts().reindex(["Detractores", "Pasivos", "Promotores"], fill_value=0).astype(int).to_dict()


def resumen_puntajes(datos, columna, puntajes):
    valores = pd.to_numeric(datos[columna], errors="coerce")
    return valores[valores.isin(puntajes)].astype(int).value_counts().reindex(puntajes, fill_value=0).astype(int).to_dict()


def construir_payload_analisis_inteligente(
    grupo_educativo,
    filtros,
    metricas_actuales,
    metricas_2025,
    df_metricas,
    df_comparativa_2025,
    centros_grupo_educativo,
):
    return {
        "contexto": {
            "encuesta_actual": 2026,
            "comparativa": 2025,
            "grupo_educativo": grupo_educativo,
            "filtros": filtros,
            "comparativa_2025_disponible": metricas_2025 is not None,
        },
        "metricas_2026": metricas_actuales,
        "metricas_2025": metricas_2025 or "sin comparativa",
        "distribucion_nps_2026": resumen_segmentos_nps(df_metricas),
        "distribucion_nps_2025": resumen_segmentos_nps(df_comparativa_2025) if df_comparativa_2025 is not None and not df_comparativa_2025.empty else "sin comparativa",
        "puntajes_nps_2026": resumen_puntajes(df_metricas, "NPS_Recomendar", PUNTAJES_NPS),
        "puntajes_csat_alexia_2026": resumen_puntajes(df_metricas, "CS_Alexia", PUNTAJES_CSAT),
        "centros_incluidos": centros_grupo_educativo.to_dict(orient="records") if centros_grupo_educativo is not None else [],
    }


SYSTEM_PROMPT_ANALISIS_INTELIGENTE = """
Eres un analista senior de customer success para software educativo en Chile.
Analiza métricas de satisfacción de clientes con lenguaje ejecutivo, claro y accionable.
No inventes datos. Si falta comparativa, dilo explícitamente.
Distingue hallazgos fuertes de señales exploratorias cuando el tamaño muestral sea bajo.
Prioriza lectura de NPS Alexia, NPS Módulo, CSAT Alexia, CSAT Capacitación y volumen de respuestas.
Entrega conclusiones breves y recomendaciones prácticas.
""".strip()


USER_PROMPT_ANALISIS_INTELIGENTE = """
Analiza las métricas del grupo educativo seleccionado comparando 2026 contra 2025 cuando exista información comparable.

Usa estos datos agregados:
{payload_json}

Entrega:
1. Resumen ejecutivo.
2. Principales cambios vs 2025.
3. Riesgos o señales de alerta.
4. Lectura por volumen de respuestas.
5. Recomendaciones concretas para seguimiento comercial o customer success.

No uses tablas largas. No inventes causas no presentes en los datos.
""".strip()

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
centros_grupo_educativo = None
if grupo_educativo_seleccionado != "Todos los grupos educativos":
    df_metricas = df_metricas[df_metricas["Grupo_Educativo"] == grupo_educativo_seleccionado]
    centros_grupo_educativo = df_metricas["Centro"].value_counts().reset_index()
    centros_grupo_educativo.columns = ["Centro", "Respuestas"]
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

grupos_mejoras_seleccionados = ["Todas las evaluaciones"]
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

fig = grafico_distribucion_puntajes_nps(df_metricas, "NPS_Recomendar", "Histograma de NPS Recomendar")
st.plotly_chart(fig, use_container_width=True)

if centros_grupo_educativo is not None:
    st.markdown(f"#### Centros incluidos en {grupo_educativo_seleccionado}")
    st.dataframe(centros_grupo_educativo, use_container_width=True)

st.markdown("#### Análisis Inteligente")
analisis_disponible = ENCUESTAS[encuesta_seleccionada]["anio"] == 2026 and grupo_educativo_seleccionado != "Todos los grupos educativos"
if not analisis_disponible:
    st.info("Selecciona la encuesta 2026 y un grupo educativo para generar el análisis inteligente.")
elif st.button("Generar análisis inteligente"):
    filtros_analisis = {
        "modulo": modulo_seleccionado,
        "grupo_educativo": grupo_educativo_seleccionado,
        "rol": rol_seleccionado,
        "antiguedad": antiguedad_seleccionada,
        "mejoras_implementadas": grupos_mejoras_seleccionados,
    }
    payload_analisis = construir_payload_analisis_inteligente(
        grupo_educativo_seleccionado,
        filtros_analisis,
        metricas_actuales,
        metricas_2025,
        df_metricas,
        df_comparativa_2025,
        centros_grupo_educativo,
    )
    user_prompt = USER_PROMPT_ANALISIS_INTELIGENTE.format(
        payload_json=json.dumps(payload_analisis, ensure_ascii=False, indent=2)
    )

    try:
        with st.spinner("Generando análisis inteligente..."):
            analisis_inteligente = generar_analisis_inteligente_openrouter(SYSTEM_PROMPT_ANALISIS_INTELIGENTE, user_prompt)
        st.markdown(analisis_inteligente)
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        st.error(f"No se pudo generar el análisis inteligente: {error}")

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
grupos_detalle = sorted(df["Grupo_Educativo"].dropna().unique())
grupo_detalle_seleccionado = st.selectbox(
    "Filtra el análisis detallado por grupo educativo:",
    options=["Todos los grupos educativos", *grupos_detalle],
)
if grupo_detalle_seleccionado == "Todos los grupos educativos":
    df_detalle = df
else:
    df_detalle = df[df["Grupo_Educativo"] == grupo_detalle_seleccionado]

# Selector de centro
centros_ordenados = sorted(df_detalle["Centro"].unique())
centros_seleccionados = st.multiselect(
    "Selecciona uno o más centros:",
    centros_ordenados,
)
if not centros_seleccionados:
    centros_seleccionados = centros_ordenados
    st.info("Sin centros seleccionados: se muestran todos los centros.")

# Filtra el DataFrame por los centros seleccionados
df_filtrado = df_detalle[df_detalle["Centro"].isin(centros_seleccionados)]
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
fig = grafico_distribucion_puntajes_nps(df_filtrado, "NPS_Recomendar", "Distribución de NPS_Recomendar en centros seleccionados", "Cargo")
st.plotly_chart(fig)

fig = grafico_distribucion_puntajes_csat(df_filtrado, "CS_Alexia", "Distribución de CSAT Alexia en centros seleccionados", "Cargo")
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


st.plotly_chart(grafico_distribucion_puntajes_nps(df_filtrado, "NPS_Recomendar", "Distribución de NPS x Cargo en centros seleccionados", "Cargo"))

st.plotly_chart(grafico_distribucion_puntajes_nps(df_filtrado, "NPS_Recomendar", "Distribución de NPS x Modulo en centros seleccionados", "Modulo_Usado"))

st.plotly_chart(grafico_distribucion_puntajes_csat(df_filtrado, "CS_Alexia", "Distribución de CSAT Alexia x Modulo en centros seleccionados", "Modulo_Usado"))

st.plotly_chart(px.histogram(df_filtrado, x="Cargo", color="Modulo_Usado", title="Distribución x Cargo x Modulo en centros seleccionados"))

st.plotly_chart(grafico_distribucion_puntajes_nps(df_filtrado, "NPS_Modulo", "Distribución por NPS Modulo y Antiguedad en centros seleccionados", "Antiguedad"))

st.plotly_chart(grafico_distribucion_puntajes_csat(df_filtrado, "Funcionalidad_Alexia", "Distribución por Funcionalidad y Cargo en centros seleccionados", "Cargo"))

st.plotly_chart(grafico_distribucion_puntajes_csat(df_filtrado, "Amigable_Alexia", "Distribución por Amigable y Cargo en centros seleccionados", "Cargo"))


st.markdown("### Análisis de NPS por Variables")
# Supón que df es tu DataFrame ya cargado y transformado
variables = ["Cargo", "Antiguedad", "Centro", "Modulo_Usado"]  # agrega las variables que quieras analizar

opcion = st.selectbox("Selecciona una variable para analizar NPS_Recomendacion:", variables)

# Gráfico de distribución de NPS_Recomendacion según la variable seleccionada
fig = px.violin(df_filtrado, x=opcion, y="NPS_Recomendar", title=f"NPS_Recomendacion según {opcion} en centros seleccionados")
st.plotly_chart(fig)

fig = px.violin(df_filtrado, x=opcion, y="CS_Alexia", title=f"Satifaccion Alexia según {opcion} en centros seleccionados")
st.plotly_chart(fig)

st.markdown("### NPS_Alexia por Centro")
tabla_nps_seleccionados = df_filtrado.groupby("Centro", group_keys=False).apply(calcular_NPS_Alexia).reset_index()
tabla_nps_seleccionados.columns = ["Centro", "NPS_Alexia"]
st.dataframe(tabla_nps_seleccionados)

st.markdown("### Análisis NPS y CSAT por Rol"  )
tabla_nps_rol = df_filtrado.groupby("Cargo", group_keys=False).apply(calcular_NPS_Alexia).reset_index()
tabla_nps_rol.columns = ["Cargo", "NPS_Alexia"]

fig = px.bar(tabla_nps_rol, x="Cargo", y="NPS_Alexia", title="NPS Alexia por Cargo")
st.plotly_chart(fig)

tabla_csat_rol = df_filtrado.groupby("Cargo", group_keys=False).apply(calcular_CSAT).reset_index()
tabla_csat_rol.columns = ["Cargo", "CSAT_Alexia"]

fig = px.bar(tabla_csat_rol, x="Cargo", y="CSAT_Alexia", title="CSAT Alexia por Cargo")
st.plotly_chart(fig)

# Agrupar y calcular promedio CSAT
df_burbujas = df_filtrado.groupby(['Cargo', 'Antiguedad'], as_index=False)['CS_Alexia'].mean()
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

