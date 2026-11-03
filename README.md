### Aplicación para Visualizar Encuestas Satisfacción de Clientes de CL. ![Python](https://img.shields.io/badge/python-3.12%2B-blue) 

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sitio-encuestas-alexia-cl.streamlit.app/) 



Aplicación para Visualizar y Analizar detalladamente los resultado Encuestas Satisfacción de Clientes de CL.

Los filtros de **Métricas Clave** se aplican también al conteo de **Centros**,
al listado de centros de los grupos educativos seleccionados y al **Análisis
de Respuestas por Centro** (cantidad de respuestas, NPS y clasificación NPS).
El conteo incluye solo centros distintos con respuestas que cumplen todos los
filtros seleccionados. El **Análisis Detallado por Centro** mantiene sus propios
filtros independientes.

Al consultar la encuesta 2026, las cinco métricas del **Análisis Detallado por
Centro** muestran el valor de 2025 y la variación respecto a ese año. La
comparativa utiliza los mismos centros y el grupo educativo seleccionados en
esta sección, independientemente de los filtros de Métricas Clave. Cada año
utiliza sus respuestas disponibles; si no hay respuestas de 2025 para la
selección, se informa que no hay comparativa.

El botón **Generar análisis inteligente de centros seleccionados**, disponible
en la encuesta 2026, analiza solo las respuestas de la selección del detalle y
su comparativa de 2025. Mantiene las mismas siete secciones del análisis
inteligente general, incluyendo comentarios abiertos y adopción de nuevas
funcionalidades, con la misma anonimización. No hereda los filtros de Métricas
Clave. Requiere seleccionar explícitamente al menos un centro; sin selección,
el botón queda deshabilitado, aunque las métricas y los gráficos sigan mostrando
todos los centros disponibles. El informe conjunto identifica la selección con
alias anónimos y no atribuye métricas agregadas a centros individuales. La
correspondencia entre alias y nombres reales se muestra solo en la aplicación.
Requiere la configuración existente de OpenRouter.