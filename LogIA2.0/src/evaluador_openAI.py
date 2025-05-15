import os
import json
from llama_index.llms.openai import OpenAI as LlamaOpenAI

class Evaluador:
    def __init__(self, respuestas_dict, openai_api_key, modelo_referencia=None, ground_truth=None):
        self.respuestas = respuestas_dict
        self.modelo_referencia = modelo_referencia
        self.llm = LlamaOpenAI(model="gpt-4", temperature=0.3, api_key=openai_api_key)

        self.respuesta_gold = None
        self.prompt_base = ""

        # Modo GPT vs GPT
        if modelo_referencia:
            if modelo_referencia not in respuestas_dict:
                raise ValueError(f"Respuesta del modelo de referencia '{modelo_referencia}' no encontrada.")
            self.respuesta_gold = self._extraer_respuesta(respuestas_dict[modelo_referencia])
            self.prompt_base = respuestas_dict[modelo_referencia].get("prompt", "")

        # Modo Ground Truth
        self.ground_truth = ground_truth

    def _extraer_respuesta(self, datos):
        """
        Devuelve la respuesta del modelo en formato de texto unificado.
        """
        if "respuesta" in datos:
            return datos["respuesta"]
        elif "preguntas_respuestas" in datos:
            pr = datos["preguntas_respuestas"]
            return "\n".join([f"- {r}" for r in pr.values()])
        else:
            return "(Sin respuesta disponible)"

    def _build_eval_prompt_gpt_vs_gpt(self, respuesta_modelo, nombre_modelo):
        prompt = f"""
Eres un experto en ciberseguridad y en evaluación de respuestas generadas por modelos de lenguaje.

Se te ha dado una serie de eventos de log y un conjunto de preguntas. GPT-4 ya ha generado una respuesta correcta de referencia (gold answer), y ahora se te pide que evalúes otra respuesta generada por el modelo **{nombre_modelo}** comparándola con la referencia.

Evalúa en qué medida la respuesta del modelo coincide con la correcta, señalando:
1. En qué acierta y por qué.
2. En qué se equivoca y por qué.
3. Si la respuesta es correcta o incorrecta.
4. Una calificación global del 0 al 10.

--- PROMPT ORIGINAL ---
{self.prompt_base}

--- RESPUESTA REFERENCIA (GPT-4) ---
{self.respuesta_gold}

--- RESPUESTA DEL MODELO {nombre_modelo} ---
{respuesta_modelo}

--- EVALUACIÓN (por GPT-4) ---
"""
        return prompt.strip()

    def _build_eval_prompt_vs_groundtruth(self, modelo_data):
        tema = modelo_data.get("tema")
        respuestas_modelo = modelo_data.get("preguntas_respuestas", {})
        respuestas_esperadas = self.ground_truth.get(tema, {})

        prompt = f"""
Eres un evaluador experto. A continuación se presenta un conjunto de preguntas, las respuestas correctas (ground truth) y las respuestas dadas por un modelo de lenguaje.

Tu tarea es comparar cada respuesta del modelo con la correcta y señalar:
1. Si es correcta o incorrecta.
2. Una breve explicación si es incorrecta.
3. Una calificación del 0 al 10 basada en el número de aciertos.

--- TEMA ---
{tema}

--- RESPUESTAS CORRECTAS ---
{json.dumps(respuestas_esperadas, indent=2, ensure_ascii=False)}

--- RESPUESTAS DEL MODELO ---
{json.dumps(respuestas_modelo, indent=2, ensure_ascii=False)}

--- EVALUACIÓN ---
"""
        return prompt.strip()

    def evaluar_modelos_con_openai(self):
        """GPT vs GPT-4"""
        resultados = {}
        for modelo, datos in self.respuestas.items():
            if modelo == self.modelo_referencia:
                continue

            respuesta_modelo = self._extraer_respuesta(datos)
            prompt = self._build_eval_prompt_gpt_vs_gpt(respuesta_modelo, modelo)
            print(f"🧠 Evaluando modelo: {modelo} con GPT-4...")

            try:
                evaluacion = self.llm.complete(prompt).text.strip()
                resultados[modelo] = {
                    "modelo": modelo,
                    "evaluacion": evaluacion,
                    "archivo": datos.get("archivo", ""),
                    "tema": datos.get("tema", "")
                }
            except Exception as e:
                print(f"❌ Error evaluando modelo {modelo}: {e}")
                resultados[modelo] = {
                    "modelo": modelo,
                    "error": str(e)
                }

        return resultados

    def evaluar_modelos_con_groundtruth_openai(self):
        """GPT evalúa vs ground truth"""
        if not self.ground_truth:
            raise ValueError("Debes proporcionar el ground_truth para esta evaluación.")

        resultados = {}
        for modelo, datos in self.respuestas.items():
            if not datos.get("preguntas_respuestas"):
                continue

            prompt = self._build_eval_prompt_vs_groundtruth(datos)
            print(f"🧠 Evaluando modelo: {modelo} con GPT-4 comparando contra ground truth...")

            try:
                evaluacion = self.llm.complete(prompt).text.strip()
                resultados[modelo] = {
                    "modelo": modelo,
                    "evaluacion": evaluacion,
                    "archivo": datos.get("archivo", ""),
                    "tema": datos.get("tema", "")
                }
            except Exception as e:
                print(f"❌ Error evaluando modelo {modelo}: {e}")
                resultados[modelo] = {
                    "modelo": modelo,
                    "error": str(e)
                }

        return resultados
