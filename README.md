LogIA: Análisis Inteligente de Logs con Modelos de Lenguaje
===========================================================

Descripción del Proyecto
------------------------

LogIA es una herramienta desarrollada en dos versiones (1.0 y 2.0) para analizar alertas y eventos de logs usando modelos de lenguaje (LLMs). Permite transformar información técnica en descripciones comprensibles en lenguaje natural, así como evaluar las respuestas generadas por distintos modelos.

Estructura General
------------------

.
├── LogIA1.0              # Versión inicial del sistema
└── LogIA2.0              # Versión mejorada con evaluación temática

LogIA1.0
--------

Componentes principales:

- main.py: Script principal.
- lib/parseoalertas.py: Lógica de parseo de logs.
- src/dataset.py: Construcción del dataset para entrada a modelos.
- data/: Contiene archivos de eventos en CSV y logs parseados en JSON.
- respuesta_modelos/: Resultados de modelos como GPT-4 y Phi-4.
- requirements.txt: Lista de dependencias necesarias.

LogIA2.0
--------

Mejoras y nuevas funcionalidades:

- Clasificación por temas:
  - Tema 1: Eventos básicos
  - Tema 2: Resumen del contenido
  - Tema 3: Patrones, errores o anomalías
  - Tema 4: Conclusiones
  - Tema 5: Preguntas de opción múltiple
- Nuevos scripts:
  - generar_respuestas_modelos_menu.py: Generación interactiva.
  - generar_respuestas_todas_tematicas.py: Generación automática por temática.
  - evaluar_modelos.py: Evaluación automática.
- Evaluadores:
  - src/evaluador_openAI.py: Evalúa con la API de OpenAI.
  - src/evaluador_humano.py: Evalúa mediante anotación manual.
- eval/ground_truth.json: Respuestas esperadas para la evaluación.

Instalación
-----------

Requiere Python 3.12

cd LogIA2.0
pip install -r requirements.txt

Uso
---

1. Parsear los logs

   python lib/parseoalertas.py

2. Generar respuestas de los modelos

   python generar_respuestas_modelos_menu.py

3. Evaluar los resultados

   python evaluar_modelos.py

Modelos Utilizados
------------------

- GPT-4 (OpenAI)
- LLaMA 3.2
- DeepSeek R1 32B
- Phi-4

Datos
-----

- Entrada: Archivos CSV con eventos y alertas extraídos de wazuh.
- Salida: Archivos .json con las respuestas generadas por cada modelo para distintas temáticas.

Créditos
--------

Este proyecto ha sido desarrollado como parte de un Trabajo de Fin de Grado (TFG).

Autor: Fernando Jesús García Molina
Fecha: 2025
