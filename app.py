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

st.title("Resultados Encuesta Satisfacción Clientes Chile")
st.write("Bienvenido a la aplicación de Resultados Encuesta Satisfacción Clientes Chile.")

password_guess = st.text_input("Ingrese la contraseña para acceder a los resultados:", type="password")

if password_guess != st.secrets["password"]:
    st.write("Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()
else:
    st.success("Contraseña correcta. Acceso concedido.")

#url del archivo
file_path = "https://raw.githubusercontent.com/juliorod63/DATASETS/refs/heads/main/CL_Encuesta.csv"
df = load_data(file_path)

st.markdown("### Resultados de la Encuesta")
st.write(" Respuestas: ", df.shape[0])

df = transformacion_df(df)

df = transformar_centros(df)

st.dataframe(df)
st.markdown("### Métricas Clave")
st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="NPS Alexia", value=f"{calcular_NPS_Alexia(df):.2f}")
col2.metric(label="NPS Modulo", value=f"{calcular_NPS_Modulo(df):.2f}")
col3.metric(label="CSAT", value=f"{calcular_CSAT(df):.2f}")
col4.metric(label="CSAT Capacitación", value=f"{calcular_CSAT_Capacitacion(df):.2f}")

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


st.markdown("### Análisis Detallado NPS Recomendar por Centro")
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

# Grafica la distribución de NPS_Alexia para ese centro
fig = px.histogram(df_filtrado, x="NPS_Recomendar", nbins=10, title=f"Distribución de NPS_Recomendar en {centro_seleccionado}")
st.plotly_chart(fig)

# calcular_NPS_Alexia recibe un DataFrame y calcula el NPS
tabla_nps = df.groupby("Centro", group_keys=False).apply(calcular_NPS_Alexia).reset_index()
tabla_nps.columns = ["Centro", "NPS_Alexia"]


fig = px.bar(tabla_nps, x="Centro", y="NPS_Alexia", title="NPS Alexia por Centro")
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

