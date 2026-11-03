import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import plotly.express as px
from streamlit.testing.v1 import AppTest

import utils


class FiltrosCentrosTests(unittest.TestCase):
    def setUp(self):
        filas = []
        for i in range(12):
            filas.append({
                "Centro": f"Centro {i % 3}",
                "Cargo": "Docente" if i % 3 == 0 else "Director",
                "Grupo_Educativo": "Grupo A",
                "Tipo": "Colegio" if i % 3 == 0 else "Red",
                "Modulo_Usado": "Academico" if i % 3 == 0 else "Gestion",
                "Antiguedad": "1 ano" if i % 3 == 0 else "2 anos",
                "Mejoras_Implementadas": "Buenas" if i % 3 == 0 else "Regulares",
                "email": f"test{i}@example.test",
                "Nombre": "Prueba",
                "Mejoras": "Sin comentarios",
                "NPS_Recomendar": i % 11,
                "NPS_Modulo": i % 11,
                **{
                    columna: i % 5 + 1
                    for columna in (
                        "CS_Alexia", "Satisf_Modulo", "Funcionalidad_Alexia",
                        "Amigable_Alexia", "Capacitacion",
                    )
                },
            })
        self.datos = pd.DataFrame(filas)
        self.datos_2025 = self.datos.copy()
        for nombre, reemplazo in (
            ("load_data", lambda encuesta, *args: (
                self.datos_2025 if encuesta == "Encuesta 2025" else self.datos
            ).copy()),
            ("transformacion_df", lambda df: df),
            ("transformar_centros", lambda df: df),
            ("deduplicar_por_email", lambda df: (df, 0)),
        ):
            parche = patch.object(utils, nombre, side_effect=reemplazo)
            parche.start()
            self.addCleanup(parche.stop)
        parche_graficos = patch.object(px, "bar", wraps=px.bar)
        self.graficos = parche_graficos.start()
        self.addCleanup(parche_graficos.stop)
        self.app = AppTest.from_file(
            str(Path(__file__).with_name("app.py")), default_timeout=30,
        )
        self.app.secrets["password"] = "test-password"
        self.app.run()
        self.app.text_input[0].set_value("test-password").run()
        self.assertFalse(self.app.exception)

    def comprobar_centros(self, centros, respuestas):
        self.assertFalse(self.app.exception)
        contadores = [m.value for m in self.app.metric if m.label == "Centros"]
        self.assertEqual(contadores, [str(len(centros))] * 2)
        self.assertEqual(self.app.metric[0].value, str(respuestas))
        for titulo in ("Cantidad de respuestas por Centro", "NPS Alexia por Centro"):
            llamada = next(
                llamada for llamada in reversed(self.graficos.call_args_list)
                if llamada.kwargs.get("title") == titulo
            )
            tabla = llamada.args[0]
            self.assertEqual(set(tabla["Centro"]), centros)
            if "Respuestas" in tabla:
                self.assertEqual(tabla["Respuestas"].sum(), respuestas)
            else:
                for centro, nps in tabla[["Centro", "NPS_Alexia"]].itertuples(index=False, name=None):
                    esperado = utils.calcular_NPS_Alexia(
                        self.datos[self.datos["Centro"] == centro],
                    )
                    self.assertEqual(nps, esperado)
        clasificacion = next(
            llamada.args[0] for llamada in reversed(self.graficos.call_args_list)
            if llamada.kwargs.get("title") == "Cantidad de centros por clasificación NPS"
        )
        self.assertEqual(clasificacion["Centros"].sum(), len(centros))

    def test_rol_y_listado_de_grupo_respetan_la_seleccion(self):
        self.comprobar_centros({"Centro 0", "Centro 1", "Centro 2"}, 12)
        grupo = next(
            w for w in self.app.multiselect
            if w.label == "Filtra las métricas por grupo educativo:"
        )
        grupo.set_value(["Grupo A"]).run()
        rol = next(
            w for w in self.app.selectbox
            if w.label == "Filtra las métricas por rol:"
        )
        rol.select("Docente").run()
        self.comprobar_centros({"Centro 0"}, 4)
        listados = [
            tabla.value for tabla in self.app.dataframe
            if list(tabla.value.columns) == ["Centro", "Respuestas"]
        ]
        self.assertEqual(len(listados), 1)
        self.assertEqual(listados[0].to_dict("records"), [
            {"Centro": "Centro 0", "Respuestas": 4},
        ])
        rol = next(
            w for w in self.app.selectbox
            if w.label == "Filtra las métricas por rol:"
        )
        rol.select("Todos los roles").run()
        self.comprobar_centros({"Centro 0", "Centro 1", "Centro 2"}, 12)

    def test_otros_filtros_y_comparativa_2026(self):
        self.app.sidebar.selectbox[0].select("Encuesta 2026").run()
        for etiqueta, valor in (
            ("Filtra las métricas por módulo:", "Academico"),
            ("Filtra las métricas por tipo:", "Colegio"),
            ("Filtra las métricas por antigüedad de uso:", "1 ano"),
        ):
            selector = next(w for w in self.app.selectbox if w.label == etiqueta)
            selector.select(valor).run()
            self.comprobar_centros({"Centro 0"}, 4)
        mejoras = next(
            w for w in self.app.multiselect
            if w.label == "Filtra las métricas por evaluación de mejoras implementadas:"
        )
        mejoras.set_value(["Buenas"]).run()
        self.comprobar_centros({"Centro 0"}, 4)
        comparativas = [m.value for m in self.app.markdown if "2025:" in m.value]
        self.assertTrue(any("<strong>1</strong>" in m for m in comparativas))

    def markdown_detalle(self):
        contenidos = [m.value for m in self.app.markdown]
        inicio = contenidos.index("### Análisis Detallado por Centro")
        return contenidos[inicio + 1:]

    def test_comparativa_detalle_independiente_de_metricas_clave(self):
        self.datos_2025 = self.datos_2025.iloc[:6].copy()
        self.datos_2025["NPS_Recomendar"] = 10
        self.datos_2025["NPS_Modulo"] = 0
        self.datos_2025["CS_Alexia"] = 5
        self.datos_2025["Capacitacion"] = 1
        self.app.sidebar.selectbox[0].select("Encuesta 2026").run()
        next(w for w in self.app.selectbox if w.label == "Filtra las métricas por rol:").select("Docente").run()
        next(w for w in self.app.multiselect if w.label == "Selecciona uno o más centros:").set_value(["Centro 1", "Centro 2"]).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.metric[-5].value, "8")
        textos = self.markdown_detalle()
        for esperado in (
            "2025: <strong>4</strong>",
            "2025: <strong>100.00</strong>",
            "2025: <strong>-100.00</strong>",
            "2025: <strong>0.00</strong>",
            "<strong>+4</strong> vs. 2025",
        ):
            self.assertTrue(any(esperado in texto for texto in textos), esperado)
        self.assertEqual(sum("vs. 2025" in texto for texto in textos), 5)
        actuales = self.datos[self.datos["Centro"].isin(["Centro 1", "Centro 2"])]
        anteriores = self.datos_2025[self.datos_2025["Centro"].isin(["Centro 1", "Centro 2"])]
        for calcular in (
            utils.calcular_NPS_Alexia, utils.calcular_NPS_Modulo,
            utils.calcular_CSAT, utils.calcular_CSAT_Capacitacion,
        ):
            diferencia = calcular(actuales) - calcular(anteriores)
            esperado = f"<strong>{diferencia:+.2f}</strong> vs. 2025"
            self.assertTrue(any(esperado in texto for texto in textos), esperado)

    def test_comparativa_detalle_filtra_grupo_y_avisa_sin_historico(self):
        self.datos.loc[self.datos["Centro"] == "Centro 0", "Grupo_Educativo"] = "Grupo B"
        self.datos_2025.loc[self.datos_2025.index[:2], "Grupo_Educativo"] = "Grupo B"
        self.app.sidebar.selectbox[0].select("Encuesta 2026").run()
        next(w for w in self.app.selectbox if w.label == "Filtra el análisis detallado por grupo educativo:").select("Grupo B").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.metric[-5].value, "4")
        self.assertTrue(any("2025: <strong>1</strong>" in texto for texto in self.markdown_detalle()))
        self.datos_2025 = self.datos_2025[self.datos_2025["Centro"] != "Centro 0"]
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("No hay respuestas de 2025" in info.value for info in self.app.info))
        self.assertFalse(any("vs. 2025" in texto for texto in self.markdown_detalle()))
        self.assertEqual(sum("sin comparativa" in texto for texto in self.markdown_detalle()), 4)

    def test_detalle_2025_no_muestra_comparativa_con_el_mismo_anio(self):
        self.assertFalse(any("2025:" in texto for texto in self.markdown_detalle()))
        self.assertFalse(any("vs. 2025" in texto for texto in self.markdown_detalle()))


if __name__ == "__main__":
    unittest.main()
