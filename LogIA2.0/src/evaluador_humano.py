import os
import json

class EvaluadorGT:
    def __init__(self, respuestas_dict, ground_truth_dict):
        self.respuestas = respuestas_dict
        self.ground_truth = ground_truth_dict

    def evaluar_respuesta_modelo(self, modelo_data):
        tema = modelo_data.get("tema")
        respuestas_modelo = modelo_data.get("preguntas_respuestas", {})
        respuestas_esperadas = self.ground_truth.get(tema, {})

        aciertos = 0
        total = len(respuestas_esperadas)
        detalle = {}

        for pregunta, respuesta_correcta in respuestas_esperadas.items():
            respuesta_modelo = respuestas_modelo.get(pregunta, "").strip()

            if respuesta_modelo.lower() == respuesta_correcta.lower():
                #Muestra la respuesta tambien aunque sea correcta tanto del modelo como el esperado
                detalle[pregunta] = f"✅ Correcta\n    Esperado: {respuesta_correcta} \n    Modelo: {respuesta_modelo}"
                aciertos += 1
            else:
                detalle[pregunta] = f"❌ Incorrecta\n    Esperado: {respuesta_correcta}\n    Modelo: {respuesta_modelo}"

        score = round((aciertos / total) * 10, 2) if total > 0 else 0
        return {
            "tema": tema,
            "archivo": modelo_data.get("archivo"),
            "score": score,
            "aciertos": aciertos,
            "total": total,
            "detalle": detalle
        }

    def evaluar_todos_los_modelos(self):
        resultados = {}
        for modelo, datos in self.respuestas.items():
            print(f"📊 Evaluando modelo: {modelo}")
            resultados[modelo] = self.evaluar_respuesta_modelo(datos)
        return resultados
