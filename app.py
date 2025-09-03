import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import matplotlib.pyplot as plt


from utils import load_data, transformacion_df, calcular_NPS_Alexia, calcular_NPS_Modulo, calcular_CSAT, transformar_centros, calcular_CSAT_Capacitacion

#nlp = spacy.load("es_core_news_sm")

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

    st.sidebar.markdown("- [Resultados de la Encuesta](#resultados-de-la-encuesta)")
    st.sidebar.markdown("- [Métricas Clave](#metricas-clave)")
    st.sidebar.markdown("- [Matriz de Dispersión](#matriz-de-dispersion)")
    st.sidebar.markdown("- [Análisis de NPS por Variables](#analisis-de-nps-por-variables)")
    st.sidebar.markdown("- [Análisis de Respuestas por Centro](#analisis-de-respuestas-por-centro)")
    st.sidebar.markdown("- [Análisis Detallado NPS por Centro](#analisis-detallado-nps-por-centro)")
    st.sidebar.markdown("- [Análisis NPS y CSAT por Rol](#analisis-nps-y-csat-por-rol)")
    st.success("Contraseña correcta. Acceso concedido.")

#url del archivo
file_path = "https://raw.githubusercontent.com/juliorod63/DATASETS/refs/heads/main/CL_Encuesta.csv"
df = load_data(file_path)

st.markdown("### Resultados de la Encuesta")
st.write(" Respuestas: ", df.shape[0])


df = transformacion_df(df)

df = transformar_centros(df)

st.dataframe(df)
st.header("Métricas Clave")

st.divider()
with st.expander("¿Cómo calculamos el NPS y el CSAT?"):

    st.markdown("""
    El NPS (Net Promoter Score) se calcula restando el porcentaje de detractores del porcentaje de promotores.
    **Fórmula:**
    ```python
    NPS = (Promotores - Detractores) / Total de respuestas × 100
    promoters = df[df["NPS_Recomendar"] >= 9].shape[0]
    detractors = df[df["NPS_Recomendar"] <= 6].shape[0]
    total = df["NPS_Recomendar"].shape[0]
    nps = ((promoters - detractors) / total) * 100
   

    """)
    st.markdown("""
    El CSAT (Customer Satisfaction Score) se calcula como el porcentaje de respuestas positivas sobre el total de respuestas.
    **Fórmula:**
    ```python
    CSAT = (Respuestas positivas / Total de respuestas) × 100
    csat = (df["CS_Alexia"].isin([4, 5]).sum() / df["CS_Alexia"].count()) * 100
    """)

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="NPS Alexia", value=f"{calcular_NPS_Alexia(df):.2f}", help="NPS basado en la pregunta de recomendar Alexia")
col2.metric(label="NPS Modulo", value=f"{calcular_NPS_Modulo(df):.2f}", help="NPS basado en la pregunta de recomendar el Módulo")
col3.metric(label="CSAT", value=f"{calcular_CSAT(df):.2f}", help="CSAT basado en la satisfacción con Alexia")
col4.metric(label="CSAT Capacitación", value=f"{calcular_CSAT_Capacitacion(df):.2f}", help="CSAT basado en la satisfacción con la Capacitación")

st.divider()


st.plotly_chart(px.histogram(df, x="NPS_Recomendar", color="Cargo", title="Distribución de NPS x Cargo"))

st.plotly_chart(px.histogram(df, x="NPS_Recomendar", color="Modulo_Usado", title="Distribución de NPS x Modulo"))

st.plotly_chart(px.histogram(df, x="CS_Alexia", color="Modulo_Usado", title="Distribución de CS x Modulo"))

st.plotly_chart(px.histogram(df, x="Cargo", color="Modulo_Usado", title="Distribución x Cargo x Modulo"))

st.plotly_chart(px.histogram(df, x="NPS_Modulo", color="Antiguedad", title="Distribución por NPS Modulo y Antiguedad"))

st.plotly_chart(px.histogram(df, x="Funcionalidad_Alexia", color="Cargo", title="Distribución por Funcionalidad y Cargo"))

st.plotly_chart(px.histogram(df, x="Amigable_Alexia", color="Cargo", title="Distribución por Amigable y Cargo"))

# Selecciona las columnas numéricas que quieres comparar
cols = ["CS_Alexia", "NPS_Modulo", "NPS_Recomendar", "Satisf_Modulo", "Funcionalidad_Alexia", "Amigable_Alexia", "Capacitacion"]  # ajusta según tus datos

st.markdown("### Matriz de Dispersión")
fig = ff.create_scatterplotmatrix(df[cols], diag='box',height=800, width=800)
st.plotly_chart(fig, use_container_width=True)



st.markdown("### Análisis de NPS por Variables")
# Supón que df es tu DataFrame ya cargado y transformado
variables = ["Cargo", "Antiguedad", "Centro", "Modulo_Usado"]  # agrega las variables que quieras analizar

opcion = st.selectbox("Selecciona una variable para analizar NPS_Recomendacion:", variables)

# Gráfico de distribución de NPS_Recomendacion según la variable seleccionada
fig = px.violin(df, x=opcion, y="NPS_Recomendar", title=f"NPS_Recomendacion según {opcion}")
st.plotly_chart(fig)

fig = px.violin(df, x=opcion, y="CS_Alexia", title=f"Satifaccion Alexia según {opcion}")
st.plotly_chart(fig)

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

st.markdown("### Análisis Detallado NPS por Centro")
# Selector de centro
centros_ordenados = sorted(df["Centro"].unique())
centro_seleccionado = st.selectbox("Selecciona un centro:", centros_ordenados)

# Filtra el DataFrame por el centro seleccionado
df_filtrado = df[df["Centro"] == centro_seleccionado]
st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric(label="Respuestas", value=f"{df_filtrado.shape[0]}")
col2.metric(label="NPS Recomendar", value=f"{calcular_NPS_Alexia(df_filtrado):.2f}")
col3.metric(label="CSAT", value=f"{calcular_CSAT(df_filtrado):.2f}")
col4.metric(label="CSAT Capacitación", value=f"{calcular_CSAT_Capacitacion(df_filtrado):.2f}")

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
        radialaxis=dict(visible=True, range=[0, 10])
    ),
    showlegend=False,
    title="Radar de Métricas Clave"
)

st.plotly_chart(fig)

# Grafica la distribución de NPS_Alexia para ese centro
fig = px.histogram(df_filtrado, x="NPS_Recomendar", color="Cargo", nbins=10, range_x=[1,10],title=f"Distribución de NPS_Recomendar en {centro_seleccionado}")
st.plotly_chart(fig)

fig = px.histogram(df_filtrado, x="CS_Alexia", color="Cargo", nbins=10, range_x=[1,5], title=f"Distribución de CSAT en {centro_seleccionado}")
st.plotly_chart(fig)


st.markdown("### NPS_Alexia por Centro")
st.dataframe(tabla_nps)

st.markdown("### Análisis NPS y CSAT por Rol"  )
tabla_nps_rol = df.groupby("Cargo", group_keys=False).apply(calcular_NPS_Alexia).reset_index()
tabla_nps_rol.columns = ["Cargo", "NPS_Alexia"]

fig = px.bar(tabla_nps_rol, x="Cargo", y="NPS_Alexia", title="NPS Alexia por Cargo")
st.plotly_chart(fig)

tabla_csat_rol = df.groupby("Cargo", group_keys=False).apply(calcular_CSAT).reset_index()
tabla_csat_rol.columns = ["Cargo", "CSAT"]

fig = px.bar(tabla_csat_rol, x="Cargo", y="CSAT", title="CSAT por Cargo")
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

