import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import matplotlib.pyplot as plt


from utils import load_data, transformacion_df, calcular_NPS_Alexia, calcular_NPS_Modulo, calcular_CSAT

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

st.dataframe(df)

st.divider()
col1, col2, col3 = st.columns(3)
col1.metric(label="NPS Alexia", value=f"{calcular_NPS_Alexia(df):.2f}")
col2.metric(label="NPS Modulo", value=f"{calcular_NPS_Modulo(df):.2f}")
col3.metric(label="CSAT", value=f"{calcular_CSAT(df):.2f}")
st.divider()


st.plotly_chart(px.histogram(df, x="NPS_Recomendar", color="Cargo", title="Distribución de NPS x Cargo"))

st.plotly_chart(px.histogram(df, x="NPS_Recomendar", color="Modulo_Usado", title="Distribución de NPS x Modulo"))

st.plotly_chart(px.histogram(df, x="CS_Alexia", color="Modulo_Usado", title="Distribución de CS x Modulo"))

st.plotly_chart(px.histogram(df, x="Cargo", color="Modulo_Usado", title="Distribución x Cargo x Modulo"))

st.plotly_chart(px.histogram(df, x="NPS_Modulo", color="Antiguedad", title="Distribución por NPS Modulo y Antiguedad"))

# Selecciona las columnas numéricas que quieres comparar
cols = ["CS_Alexia", "NPS_Modulo", "NPS_Recomendar", "Satisf_Modulo"]  # ajusta según tus datos

st.markdown("### Matriz de Dispersión")
fig = ff.create_scatterplotmatrix(df[cols], diag='box',height=800, width=800)
st.plotly_chart(fig, use_container_width=True)



st.markdown("### Análisis de NPS por Variables")
# Supón que df es tu DataFrame ya cargado y transformado
variables = ["Cargo", "Antiguedad", "Centro", "Modulo_Usado"]  # agrega las variables que quieras analizar

opcion = st.selectbox("Selecciona una variable para analizar NPS_Recomendacion:", variables)

# Gráfico de distribución de NPS_Recomendacion según la variable seleccionada
fig = px.box(df, x=opcion, y="NPS_Recomendar", title=f"NPS_Recomendacion según {opcion}")
st.plotly_chart(fig)

fig = px.box(df, x=opcion, y="CS_Alexia", title=f"Satifaccion Alexia según {opcion}")
st.plotly_chart(fig)