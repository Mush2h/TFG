import os
import json
import pandas as pd
from lib.parseoalertas import parsear_logs

class Dataset:
    def __init__(self, data_path: str):
        """
        Inicializa el dataset cargando las preguntas por temas y verificando la ruta de los archivos JSON.
        """
        self.__questions = {
            "Tema 1 - Eventos básicos": [
                "¿Cuántos eventos únicos hay en el fichero de logs?",
                "¿Cuántos agentes diferentes aparecen?",
                "¿Cuál es el evento que ocurre con más frecuencia?",
                "¿Qué tipo de evento es el más crítico según el log?"
            ],
            "Tema 2 - Resumen del contenido": [
                "Resume en 3 líneas qué está ocurriendo en el sistema.",
                "Haz una tabla con los tipos de eventos y su frecuencia."
            ],
            "Tema 3 - Patrones, errores o anomalías": [
                "¿Detectas algún comportamiento anómalo en estos logs?",
                "¿Hay intentos de acceso fallidos? ¿Cuántos y desde qué IPs?",
                "¿Hay alguna IP o usuario que repita acciones inusuales?",
                "¿Se ha producido algún error recurrente en el sistema?"
            ],
            "Tema 4 - Conclusiones": [
                "¿Qué podría estar causando los errores observados?",
                "Sugiere posibles soluciones para los errores detectados.",
                "¿Hay indicios de un ataque (e.g., fuerza bruta, escaneo de puertos)?",
                "¿Cuál sería tu diagnóstico general del estado del sistema según estos logs?"
            ]
        }

        abs_path = os.path.join(os.getcwd(), data_path)

        # Verificar que la ruta existe
        if os.path.exists(abs_path):
            self.__data_path = abs_path
            self.__files = self.__get_json_files()
        else:
            raise Exception("La ruta no existe. Por favor, verifica la ruta de los archivos JSON.")

    def __get_json_files(self):
        """
        Retorna una lista de todos los archivos .json o .jsonl del directorio indicado.
        """
        return [
            os.path.join(self.__data_path, f)
            for f in os.listdir(self.__data_path)
            if f.endswith(".json") or f.endswith(".jsonl")
        ]

    def load_logs(self, file_name: str) -> list:
        """
        Carga un archivo de logs en formato JSONL o JSON.
        """
        path = os.path.join(self.__data_path, file_name)
        with open(path, 'r') as f:
            return [json.loads(line) for line in f.readlines()]

    def get_questions_by_topic(self, topic: str):
        """
        Devuelve las preguntas relacionadas con un tema específico.
        """
        return self.__questions.get(topic, [])

    def list_all_questions(self):
        """
        Devuelve una cadena con todas las preguntas agrupadas por tema.
        """
        all_qs = []
        for tema, preguntas in self.__questions.items():
            all_qs.append(f"### {tema}")
            all_qs.extend(preguntas)
        return "\n".join(all_qs)

    def generate_prompt(self, file_name: str, topic: str) -> str:
        """
        Genera un prompt con un subconjunto de eventos del archivo y preguntas de un tema para pasar al LLM.
        """
        logs = self.load_logs(file_name)
        sample = logs[:15]  # Tomamos solo una muestra para no saturar el prompt
        prompt = f"Estos son algunos eventos del sistema:\n{json.dumps(sample, indent=2)}\n\n"
        prompt += "\n".join(self.get_questions_by_topic(topic))
        return prompt
    




