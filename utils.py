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

def calcular_CSAT(df):
    csat = (df["CS_Alexia"].isin([4, 5]).sum() / df["CS_Alexia"].count()) * 100
    return csat
    

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


def transformar_centros(df):
    df.loc[df["Centro"].str.contains("Craighouse", case=False), "Centro"] = "Craighouse School"
    df.loc[df["Centro"].str.contains("Nocedal", case=False), "Centro"] = "Colegio Nocedal"
    df.loc[df["Centro"].str.contains("everest", case=False), "Centro"] = "Colegio Everest"
    df.loc[df["Centro"].str.contains("Colegio Everedt", case=False), "Centro"] = "Colegio Everest"
    df.loc[df["Centro"].str.contains("Cumbres", case=False), "Centro"] = "Colegio Cumbres"
    df.loc[df["Centro"].str.contains("Colegio Cumbres\n", case=False), "Centro"] = "Colegio Cumbres"
    df.loc[df["Centro"].str.contains("San Gabriel", case=False), "Centro"] = "Colegio San Gabriel"
    df.loc[df["Centro"].str.contains("scuola italiana", case=False), "Centro"] = "Scuola Italiana"
    df.loc[df["Centro"].str.contains("Colegio Saint Gabriel school", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Dagoberto Godoy", case=False), "Centro"] = "Colegio Teniente Dagoberto Godoy"
    df.loc[df["Centro"].str.contains("Degoberto", case=False), "Centro"] = "Colegio Teniente Dagoberto Godoy"
    df.loc[df["Centro"].str.contains("Jorge Alessandri", case=False), "Centro"] = "Colegio Jorge Alessandri"
    df.loc[df["Centro"].str.contains("Jorge Alesandri", case=False), "Centro"] = "Colegio Jorge Alessandri"
    df.loc[df["Centro"].str.contains("Saint Gabriel`s School", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Saint Gabriel´s School", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Saint Gabriel's School", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Saint Gabriel School", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Colegio saint Gabriel's school", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Saint Gabriel ´s", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Colegio Saint Gabriel´s", case=False), "Centro"] = "Saint Gabriel´s School"
    df.loc[df["Centro"].str.contains("Colegio Instituto Hebreo", case=False), "Centro"] = "Instituto Hebreo"
    df.loc[df["Centro"].str.contains("Morus", case=False), "Centro"] = "DS Morus"
    df.loc[df["Centro"].str.contains("Morrus", case=False), "Centro"] = "DS Morus"
    df.loc[df["Centro"].str.contains("SIP", case=False), "Centro"] = "SIP"
    df.loc[df["Centro"].str.contains("AML", case=False), "Centro"] = "Arturo Matte Larrain"
    df.loc[df["Centro"].str.contains("Arturo Matte", case=False), "Centro"] = "Arturo Matte Larrain"
    df.loc[df["Centro"].str.contains("Sociedad de Instrucción Primaria", case=False), "Centro"] = "SIP"
    df.loc[df["Centro"].str.contains("Colegio San Nicolas Diacono", case=False), "Centro"] = "Colegio San Nicolás Diácono"
    df.loc[df["Centro"].str.contains("Colegio San Nicolás Diacono", case=False), "Centro"] = "Colegio San Nicolás Diácono"
    df.loc[df["Centro"].str.contains("Arturo toro amor", case=False), "Centro"] = "Colegio Arturo Toro Amor"
    df.loc[df["Centro"].str.contains("Eliodoro Matte Ossa", case=False), "Centro"] = "Eliodoro Matte Ossa"
    df.loc[df["Centro"].str.contains("EMO", case=False), "Centro"] = "Eliodoro Matte Ossa"
    df.loc[df["Centro"].str.contains("Colegio San Felipe diácono", case=False), "Centro"] = "Colegio San Felipe Diácono"
    df.loc[df["Centro"].str.contains("San Felipe Diácono", case=False), "Centro"] = "Colegio San Felipe Diácono"
    df.loc[df["Centro"].str.contains("San Felipe diacono", case=False), "Centro"] = "Colegio San Felipe Diácono"
    df.loc[df["Centro"].str.contains("San esteban diácono", case=False), "Centro"] = "Colegio San Esteban Diácono"
    df.loc[df["Centro"].str.contains("maitenes", case=False), "Centro"] = "Colegio Maitenes"
    df.loc[df["Centro"].str.contains("instituto hebreo", case=False), "Centro"] = "Instituto Hebreo"
    df.loc[df["Centro"].str.contains("San esteban diacono", case=False), "Centro"] = "Colegio San Esteban Diácono"
    df.loc[df["Centro"].str.contains("Colegio San Esteba Diacono", case=False), "Centro"] = "Colegio San Esteban Diácono"
    df.loc[df["Centro"].str.contains("San Nicolás Diácono", case=False), "Centro"] = "Colegio San Nicolás Diácono"
    df.loc[df["Centro"].str.contains("San Nicolas Diácono", case=False), "Centro"] = "Colegio San Nicolás Diácono"
    df.loc[df["Centro"].str.contains("San Nicolas Diacono", case=False), "Centro"] = "Colegio San Nicolás Diácono"
    df.loc[df["Centro"].str.contains("amazing grace peñuelas", case=False), "Centro"] = "Colegio Amazing Grace Peñuelas"
    df.loc[df["Centro"].str.contains("amazing grace", case=False), "Centro"] = "Colegio Amazing Grace Peñuelas"
    df.loc[df["Centro"].str.contains("Alicante del Valle", case=False), "Centro"] = "Alicante del Valle"
    df.loc[df["Centro"].str.contains("Alicante delo Valle", case=False), "Centro"] = "Alicante del Valle"
    df.loc[df["Centro"].str.contains("Colegio Alicante del Valle", case=False), "Centro"] = "Alicante del Valle"
    df.loc[df["Centro"].str.contains("Fundación Educacional Alicante Maipú", case=False), "Centro"] = "Alicante Maipú"
    df.loc[df["Centro"].str.contains("Alicante de maipu", case=False), "Centro"] = "Alicante Maipú"
    df.loc[df["Centro"].str.contains("Alicante maipu", case=False), "Centro"] = "Alicante Maipú"
    df.loc[df["Centro"].str.contains("Colegio Alicante maipú", case=False), "Centro"] = "Alicante Maipú"
    df.loc[df["Centro"].str.contains("Colegio Alicante de Maipú", case=False), "Centro"] = "Alicante Maipú"
    df.loc[df["Centro"].str.contains("Alicante de maipú", case=False), "Centro"] = "Alicante Maipú"
    df.loc[df["Centro"].str.contains("Alicante de la florida", case=False), "Centro"] = "Alicante Florida"
    df.loc[df["Centro"].str.contains("alicante la florida", case=False), "Centro"] = "Alicante Florida"
    df.loc[df["Centro"].str.contains("claudio matte", case=False), "Centro"] = "Claudio Matte"
    df.loc[df["Centro"].str.contains("colegio chuquicamata", case=False), "Centro"] = "Colegio Chuquicamata"
    df.loc[df["Centro"].str.contains("Coelcgio Chuquicamata", case=False), "Centro"] = "Colegio Chuquicamata"
    df.loc[df["Centro"].str.contains("colegio creacion osorno", case=False), "Centro"] = "Colegio Creación Osorno"
    df.loc[df["Centro"].str.contains("colegio creación osorno", case=False), "Centro"] = "Colegio Creación Osorno"
    df.loc[df["Centro"].str.contains("Sociedad Colegio Alemán de Temuco", case=False), "Centro"] = "Colegio Alemán de Temuco"
    df.loc[df["Centro"].str.contains("Colegio puente maipo", case=False), "Centro"] = "Colegio Puente Maipo"
    df.loc[df["Centro"].str.contains("Puentemaipo", case=False), "Centro"] = "Colegio Puente Maipo"
    df.loc[df["Centro"].str.contains("Colegio Puentemaipo", case=False), "Centro"] = "Colegio Puente Maipo"
    df.loc[df["Centro"].str.contains("Colegio Púentemaipo", case=False), "Centro"] = "Colegio Puente Maipo"
    df.loc[df["Centro"].str.contains("Colegio La Fontaine", case=False), "Centro"] = "Colegio La Fontaine"
    df.loc[df["Centro"].str.contains("Colegio la cruz", case=False), "Centro"] = "Colegio La Cruz"
    df.loc[df["Centro"].str.contains("Colegio La cruz.", case=False), "Centro"] = "Colegio La Cruz"
    df.loc[df["Centro"].str.contains("Alicante del Sol", case=False), "Centro"] = "Alicante del Sol"
    df.loc[df["Centro"].str.contains("Alicante del sol, Puente Alto", case=False), "Centro"] = "Alicante del Sol"
    df.loc[df["Centro"].str.contains("Colegio Alcántara de Cordillera.", case=False), "Centro"] = "Alcantara de Cordillera"
    df.loc[df["Centro"].str.contains("Colegio Alcántara de la Cordillera", case=False), "Centro"] = "Alcantara de Cordillera"
    df.loc[df["Centro"].str.contains("Colegio alemán de valparaisoñr", case=False), "Centro"] = "Colegio Alemán de Valparaíso"
    df.loc[df["Centro"].str.contains("Colegio Alemán de Valparaíso", case=False), "Centro"] = "Colegio Alemán de Valparaíso"
    df.loc[df["Centro"].str.contains("valparaiso", case=False), "Centro"] = "Colegio Alemán de Valparaíso"
    df.loc[df["Centro"].str.contains("Creacion concepcion", case=False), "Centro"] = "Colegio Creación Concepción"
    df.loc[df["Centro"].str.contains("concepcion", case=False), "Centro"] = "Colegio Creación Concepción"
    df.loc[df["Centro"].str.contains("Liceo Industrial Temuco", case=False), "Centro"] = "Liceo Industrial Temuco"
    df.loc[df["Centro"].str.contains("Temuco", case=False), "Centro"] = "Liceo Industrial Temuco"
    df.loc[df["Centro"].str.contains("Temuco/", case=False), "Centro"] = "Liceo Industrial Temuco"
    df.loc[df["Centro"].str.contains("LICEO POLITECNICO DE CURACAUTIN", case=False), "Centro"] = "Liceo Politécnico de Curacautín"
    df.loc[df["Centro"].str.contains("LICEO POLITÉCNICO DE CURACAUTIN", case=False), "Centro"] = "Liceo Politécnico de Curacautín"
    df.loc[df["Centro"].str.contains("Liceo Politécnico Curacautín", case=False), "Centro"] = "Liceo Politécnico de Curacautín"
    df.loc[df["Centro"].str.contains("Liceo San José", case=False), "Centro"] = "Liceo San José"
    df.loc[df["Centro"].str.contains("Liceo San Jose", case=False), "Centro"] = "Liceo San José"
    df.loc[df["Centro"].str.contains("liceo bicentenario italia", case=False), "Centro"] = "Liceo Bicentenario Italia"
    df.loc[df["Centro"].str.contains("Vista Hermosa", case=False), "Centro"] = "Liceo Bicentenario Agrícola Vista Hermosa"
    df.loc[df["Centro"].str.contains("de la Patagonia", case=False), "Centro"] = "Liceo Bicentenario de la Patagonia"
    df.loc[df["Centro"].str.contains("Werner Grob", case=False), "Centro"] = "Liceo Bicentenario Agrícola Tecnológico Werner Grob"
    df.loc[df["Centro"].str.contains("Chillán", case=False), "Centro"] = "Liceo Bicentenario de excelencia Agrícola de Chillán"
    df.loc[df["Centro"].str.contains("Chillan", case=False), "Centro"] = "Liceo Bicentenario de excelencia Agrícola de Chillán"
    df.loc[df["Centro"].str.contains("AGROTEC", case=False), "Centro"] = "Liceo Agrotec"
    df.loc[df["Centro"].str.contains("Fenner Ruedi", case=False), "Centro"] = "Liceo Bicentenario Industrial Ricardo Fenner Ruedi"
    df.loc[df["Centro"].str.contains("huerton", case=False), "Centro"] = "Liceo Agricola de Excelencia Tecnológica El Huertón"
    df.loc[df["Centro"].str.contains("huertón", case=False), "Centro"] = "Liceo Agricola de Excelencia Tecnológica El Huertón"
    df.loc[df["Centro"].str.contains("Lira Infante", case=False), "Centro"] = "Liceo Obispo Rafael Lira Infante de Quilpué"
    df.loc[df["Centro"].str.contains("carmen", case=False), "Centro"] = "Liceo Agrícola El Carmen de San Fernando"
    df.loc[df["Centro"].str.contains("Villarrica", case=False), "Centro"] = "Colegio Alemán de  Villarica"
    df.loc[df["Centro"].str.contains("Puerto Varas", case=False), "Centro"] = "Colegio Alemán de Puerto Varas"
    df.loc[df["Centro"].str.contains("Juan Pablo", case=False), "Centro"] = "Colegio Juan Pablo II"
    df.loc[df["Centro"].str.contains("Lizardi", case=False), "Centro"] = "Colegio Rafaél Sanhueza Lizardi"
    df.loc[df["Centro"].str.contains("sanhueza", case=False), "Centro"] = "Colegio Rafaél Sanhueza Lizardi"
    df.loc[df["Centro"].str.contains("dsv", case=False), "Centro"] = "Colegio Alemán de Valparaíso"
    df.loc[df["Centro"].str.contains("Cruz", case=False), "Centro"] = "Colegio La Cruz"
    df.loc[df["Centro"].str.contains("Rosa Elvira Matte", case=False), "Centro"] = "Colegio Rosa Elvira Matte"
    df.loc[df["Centro"].str.contains("Francisco Arriaran", case=False), "Centro"] = "Colegio Francisco Arriarán"
    df.loc[df["Centro"].str.contains("Francisco Arriarán", case=False), "Centro"] = "Colegio Francisco Arriarán"
    df.loc[df["Centro"].str.contains("nogales", case=False), "Centro"] = "Colegio Los Nogales"  
    df.loc[df["Centro"].str.contains("san isidro", case=False), "Centro"] = "Colegio San Isidro"
    df.loc[df["Centro"].str.contains("isisdro", case=False), "Centro"] = "Colegio San Isidro"
    df.loc[df["Centro"].str.contains("zan Isidro", case=False), "Centro"] = "Colegio San Isidro"
    df.loc[df["Centro"].str.contains("Müller", case=False), "Centro"] = "Complejo Educacional Ernesto Müller López"
    df.loc[df["Centro"].str.contains("Muller", case=False), "Centro"] = "Complejo Educacional Ernesto Müller López"
    df.loc[df["Centro"].str.contains("molina", case=False), "Centro"] = "Escuela Bicentenario Agrícola Superior de Molina"
    df.loc[df["Centro"].str.contains("paine", case=False), "Centro"] = "Colegio Bicentenario Santa Maria de Paine"
    df.loc[df["Centro"].str.contains("agustin alfonso", case=False), "Centro"] = "Colegio José Agustín Alfonso"
    df.loc[df["Centro"].str.contains("jar", case=False), "Centro"] = "Colegio Jorge Alessandri Rodriguez"
    df.loc[df["Centro"].str.contains("jorge alessandri", case=False), "Centro"] = "Colegio Jorge Alessandri Rodriguez"
    df.loc[df["Centro"].str.contains("Elvira Hurtado de Matte", case=False), "Centro"] = "Colegio Bicentenario Elvira Hurtado de Matte"
    df.loc[df["Centro"].str.contains("Punta arenas", case=False), "Centro"] = "Colegio Alemán de Punta Arenas"
    df.loc[df["Centro"].str.contains("Peñalolen", case=False), "Centro"] = "Colegio Alcántara de Peñalolén"
    df.loc[df["Centro"].str.contains("Peñalolén", case=False), "Centro"] = "Colegio Alcántara de Peñalolén"
    df.loc[df["Centro"].str.contains("Fontaine", case=False), "Centro"] = "Colegio La Fontaine"
    df.loc[df["Centro"].str.contains("la florida", case=False), "Centro"] = "Colegio Santiago La Florida"
    df.loc[df["Centro"].str.contains("agrícola san felipe", case=False), "Centro"] = "Colegio Agrícola San Felipe"
    df.loc[df["Centro"].str.contains("agrícola de san felipe", case=False), "Centro"] = "Colegio Agrícola San Felipe"
    df.loc[df["Centro"].str.contains("creación puerto montt", case=False), "Centro"] = "Colegio Creación Puerto Montt"
    df.loc[df["Centro"].str.contains("creación concepción", case=False), "Centro"] = "Colegio Creación Concepción"
    df.loc[df["Centro"].str.contains("andres olea", case=False), "Centro"] = "Colegio Francisco Andres Olea"
    df.loc[df["Centro"].str.contains("andrés olea", case=False), "Centro"] = "Colegio Francisco Andres Olea"
    df.loc[df["Centro"].str.contains("ándres olea", case=False), "Centro"] = "Colegio Francisco Andres Olea"
    df.loc[df["Centro"].str.contains("oléa", case=False), "Centro"] = "Colegio Francisco Andres Olea"
    df.loc[df["Centro"].str.contains("highlands", case=False), "Centro"] = "Colegio Highlands"
    df.loc[df["Centro"].str.contains("Presidente Alessandri", case=False), "Centro"] = "Colegio Presidente Alessandri"
    df.loc[df["Centro"].str.contains("Presidente Alessandrí", case=False), "Centro"] = "Colegio Presidente Alessandri"
    df.loc[df["Centro"].str.contains("javiera carrera", case=False), "Centro"] = "Colegio Javiera Carrera"
    df.loc[df["Centro"].str.contains("javieracarrera", case=False), "Centro"] = "Colegio Javiera Carrera"
    df.loc[df["Centro"].str.contains("LBI", case=False), "Centro"] = "Liceo Bicentenario Italia"
    df.loc[df["Centro"].str.contains("guillermo matta", case=False), "Centro"] = "Guillermo Matta"
    df.loc[df["Centro"].str.contains("INSTITUTO HNOS. MATTE", case=False), "Centro"] = "Instituto Hermanos Matte"
    df.loc[df["Centro"].str.contains("IHM", case=False), "Centro"] = "Instituto Hermanos Matte"
    df.loc[df["Centro"].str.contains("hermanos matte", case=False), "Centro"] = "Instituto Hermanos Matte"
    df.loc[df["Centro"].str.contains("trigales del maipo", case=False), "Centro"] = "Colegio Trigales del Maipo"
    df.loc[df["Centro"].str.contains("pudahuel", case=False), "Centro"] = "Colegio Santiago de Pudahuel"
    df.loc[df["Centro"].str.contains("talagante", case=False), "Centro"] = "Colegio Sagrado Corazón de Talagante"
    df.loc[df["Centro"].str.contains("sagrado corazón", case=False), "Centro"] = "Colegio Sagrado Corazón de Talagante"
    df.loc[df["Centro"].str.contains("quilicura", case=False), "Centro"] = "Colegio Santiago Quilicura"
    df.loc[df["Centro"].str.contains("jjprieto", case=False), "Centro"] = "Colegio José Joaquín Prieto"
    df.loc[df["Centro"].str.contains("prieto", case=False), "Centro"] = "Colegio José Joaquín Prieto"
    df.loc[df["Centro"].str.contains("c-dar", case=False), "Centro"] = "Colegio C-DAR"
    df.loc[df["Centro"].str.contains("cdar", case=False), "Centro"] = "Colegio C-DAR"
    df.loc[df["Centro"].str.contains("cambridge", case=False), "Centro"] = "Cambridge College"
    df.loc[df["Centro"].str.contains("linares", case=False), "Centro"] = "Colegio Concepción Linares"
    df.loc[df["Centro"].str.contains("montaner", case=False), "Centro"] = "Colegio Montaner de Hualpén"
    df.loc[df["Centro"].str.contains("cecilia", case=False), "Centro"] = "Colegio Santa Cecilia"
    df.loc[df["Centro"].str.contains("elidoro", case=False), "Centro"] = "Colegio Eliodoro Matte Ossa"
    df.loc[df["Centro"].str.contains("eleodoro", case=False), "Centro"] = "Colegio Eliodoro Matte Ossa"
    df.loc[df["Centro"].str.contains("eliodoro matte", case=False), "Centro"] = "Colegio Eliodoro Matte Ossa"
    df.loc[df["Centro"].str.contains("agustín alfonso", case=False), "Centro"] = "Colegio José Agustín Alfonso"
    df.loc[df["Centro"].str.contains("perry", case=False), "Centro"] = "Liceo Agrícola Tadeo Perry Barnes"
    df.loc[df["Centro"].str.contains("vittorio", case=False), "Centro"] = "Scuola Italiana Vittorio Montiglio"
    df.loc[df["Centro"].str.contains("engintel", case=False), "Centro"] = "Engintel"
    df.loc[df["Centro"].str.contains("alcantara de la cordillera", case=False), "Centro"] = "Alcantara de Cordillera"


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


