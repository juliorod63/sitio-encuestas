import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
#import spacy
from wordcloud import WordCloud
import matplotlib.pyplot as plt

#nlp = spacy.load("es_core_news_sm")

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df


def calcular_NPS_Modulo(df):
    promoters = df[df["NPS_Modulo"] >= 9].shape[0]
    detractors = df[df["NPS_Modulo"] <= 6].shape[0]
    total_responses = df["NPS_Modulo"].shape[0]
    if total_responses == 0:
        return 0
    return (promoters - detractors) / total_responses * 100

def calcular_NPS_Alexia(df):
    promoters = df[df["NPS_Recomendar"] >= 9].shape[0]
    detractors = df[df["NPS_Recomendar"] <= 6].shape[0]
    total = df["NPS_Recomendar"].shape[0]
    print (total, promoters, detractors)
    nps = ((promoters - detractors) / total) * 100
    print(nps)
    if total == 0:
        return 0
    return nps

def transformacion_df(df):

    df.rename(columns={df.columns[1]: "email", df.columns[2]:"Nombre", df.columns[3]:"Centro", df.columns[4]:"Cargo", df.columns[5]:"Antiguedad", df.columns[6]:"Modulo_Usado",df.columns[7]:"Satisf_Modulo",df.columns[8]:"NPS_Modulo",df.columns[9]:"Capacitacion",df.columns[10]:"CS_Alexia", df.columns[11]:"Funcionalidad_Alexia", df.columns[12]:"Amigable_Alexia",df.columns[13]:"NPS_Recomendar", df.columns[14]:"Mejoras"}, inplace=True)
    df = df.drop(columns=[df.columns[0]])

    df["Cargo"] = df["Cargo"].str.lower().replace({
    "profesor": "Docente",
    "profesor ": "Docente",
    "profesora ": "Docente",
    "profrsora": "Docente",
    "docente ": "Docente",
    "profesora": "Docente",
    "maestro": "Docente",
    "maestra": "Docente",
    "docente artes visuales": "Docente",
    "profesora de química y biología": "Docente",
    "profesor y apoderado": "Docente",
    "coeducadora 1° basico": "Docente",
    "educador": "Docente",
    "educadora": "Docente",
    "educadora diferencial": "Docente",
    "educadora de párvulos": "Docente",
    "educadora basica": "Docente",
    "educadora básica": "Docente"
    # Agrega aquí más variantes según lo que observes en los datos
    })
    df.loc[df["Cargo"].str.contains("jefe"), "Cargo"] = "Jefe/a"
    df.loc[df["Cargo"].str.contains("jefa"), "Cargo"] = "Jefe/a"
    df.loc[df["Cargo"].str.contains("coordinador"), "Cargo"] = "Coordinador/a"
    df.loc[df["Cargo"].str.contains("coordinación"), "Cargo"] = "Coordinador/a"
    df.loc[df["Cargo"].str.contains("asistente"), "Cargo"] = "Asistente"
    df.loc[df["Cargo"].str.contains("secretaría"), "Cargo"] = "Secretaria"
    df.loc[df["Cargo"].str.contains("secretaria"), "Cargo"] = "Secretaria"
    df.loc[df["Cargo"].str.contains("encargado"), "Cargo"] = "Encargado"
    df.loc[df["Cargo"].str.contains("encargada"), "Cargo"] = "Encargado"
    df.loc[df["Cargo"].str.contains("administrativo"), "Cargo"] = "Administrativo"
    df.loc[df["Cargo"].str.contains("administrativa"), "Cargo"] = "Administrativo"
    df.loc[df["Cargo"].str.contains("psicologo"), "Cargo"] = "Psicologo/a"
    df.loc[df["Cargo"].str.contains("psicólogo"), "Cargo"] = "Psicologo/a"
    df.loc[df["Cargo"].str.contains("psicologa"), "Cargo"] = "Psicologo/a"
    df.loc[df["Cargo"].str.contains("psicóloga"), "Cargo"] = "Psicologo/a"
    df.loc[df["Cargo"].str.contains("psicopedagoga"), "Cargo"] = "Psicopedagogo/a"
    df.loc[df["Cargo"].str.contains("psicopedagogo"), "Cargo"] = "Psicopedagogo/a"
    df.loc[df["Cargo"].str.contains("orientador"), "Cargo"] = "Orientador/a"
    df.loc[df["Cargo"].str.contains("orientadora"), "Cargo"] = "Orientador/a"
    df.loc[df["Cargo"].str.contains("profesor jefe"), "Cargo"] = "Jefe/a"
    df.loc[df["Cargo"].str.contains("inspector"), "Cargo"] = "Inspector/a"
    df.loc[df["Cargo"].str.contains("inspectora"), "Cargo"] = "Inspector/a"
    df.loc[df["Cargo"].str.contains("profesional de apoyo"), "Cargo"] = "Profesional de Apoyo"
    df.loc[df["Cargo"].str.contains("docente"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("profesor de"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("profesora de"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("profesor"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("monitor"), "Cargo"] = "Inspector"
    df.loc[df["Cargo"].str.contains("monitora"), "Cargo"] = "Inspector"
    df.loc[df["Cargo"].str.contains("gerente"), "Cargo"] = "Gerente"
    df.loc[df["Cargo"].str.contains("directora"), "Cargo"] = "Director/a"
    df.loc[df["Cargo"].str.contains("director"), "Cargo"] = "Director/a"
    df.loc[df["Cargo"].str.contains("dirección"), "Cargo"] = "Director/a"
    df.loc[df["Cargo"].str.contains("encargada de convivencia escolar"), "Cargo"] = "Encargado"
    df.loc[df["Cargo"].str.contains("encargada de convivencia escolar"), "Cargo"] = "Encargado"
    df.loc[df["Cargo"].str.contains("encargado de convivencia escolar"), "Cargo"] = "Encargado"
    df.loc[df["Cargo"].str.contains("subdirector"), "Cargo"] = "Director/a"
    df.loc[df["Cargo"].str.contains("subdirectora"), "Cargo"] = "Director/a"
    df.loc[df["Cargo"].str.contains("encargada de biblioteca"), "Cargo"] = "Bibliotecario/a"
    df.loc[df["Cargo"].str.contains("encargado de biblioteca"), "Cargo"] = "Bibliotecario/a"
    df.loc[df["Cargo"].str.contains("bibliotecaria"), "Cargo"] = "Bibliotecario/a"
    df.loc[df["Cargo"].str.contains("bibliotecario"), "Cargo"] = "Bibliotecario/a"
    df.loc[df["Cargo"].str.contains("técnico"), "Cargo"] = "Técnico/a"
    df.loc[df["Cargo"].str.contains("técnica"), "Cargo"] = "Técnico/a"
    df.loc[df["Cargo"].str.contains("convivencia"), "Cargo"] = "Convivencia"
    df.loc[df["Cargo"].str.contains("consejero"), "Cargo"] = "Consejero/a"
    df.loc[df["Cargo"].str.contains("consejera"), "Cargo"] = "Consejero/a"
    df.loc[df["Cargo"].str.contains("encargada de recursos"), "Cargo"] = "Encargado"
    df.loc[df["Cargo"].str.contains("educador"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("enfermer"), "Cargo"] = "Enfermero/a"
    df.loc[df["Cargo"].str.contains("apoderad"), "Cargo"] = "Apoderado/a"
    df.loc[df["Cargo"].str.contains("teacher"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("utp"), "Cargo"] = "Coordinador/a"
    df.loc[df["Cargo"].str.contains("asesor"), "Cargo"] = "Asesor/a"
    df.loc[df["Cargo"].str.contains("maestra"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("subdirección"), "Cargo"] = "Director/a"
    df.loc[df["Cargo"].str.contains("jede"), "Cargo"] = "Jefe/a"
    df.loc[df["Cargo"].str.contains("jefe de"), "Cargo"] = "Jefe/a"
    df.loc[df["Cargo"].str.contains("ed."), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("recretaria"), "Cargo"] = "Secretaria"
    df.loc[df["Cargo"].str.contains("soporte"), "Cargo"] = "Soporte Sistemas"
    df.loc[df["Cargo"].str.contains("porter"), "Cargo"] = "Mantenimiento"
    df.loc[df["Cargo"].str.contains("mantencion"), "Cargo"] = "Mantenimiento"
    df.loc[df["Cargo"].str.contains("mantenimiento"), "Cargo"] = "Mantenimiento"
    df.loc[df["Cargo"].str.contains("prof de"), "Cargo"] = "Docente"
    df.loc[df["Cargo"].str.contains("eca"), "Cargo"] = "Encargado/a"
    counts = (df["Cargo"].value_counts())

    # Reemplaza los valores que aparecen solo una vez por "Otros"
    df["Cargo"] = df["Cargo"].apply(lambda x: x if counts[x] >  2 else "Otros")
    return df


def transformacion_df_comentarios(df):
    df_comentarios = df[df["Mejoras"].notna() & (df["Mejoras"] != "")]
    df_comentarios = df_comentarios["Mejoras"]
    df_comentarios = df_comentarios.str.lower().str.replace("[-_ . , ]", " ", regex=True)
    return df_comentarios

""" def tokenizar(df_comentarios):
    nlp = spacy.load("es_core_news_sm")
    doc = nlp(" ".join(df_comentarios))
    return [token.text for token in doc if not token.is_stop and not token.is_punct] """


# Función para limpiar texto: tokenizar y eliminar stop words y signos de puntuación
def limpiar_texto(texto):
    doc = nlp(texto)
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

