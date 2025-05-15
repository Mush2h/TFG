import os
import json

class Dataset:
    def __init__(self, data_path: str):
        """
        Inicializa el dataset cargando las preguntas por temas y verificando la ruta de los archivos JSON.
        """
        self.__questions = {
            "Tema 1 - Eventos básicos": [
                "¿Cuántos eventos hay en el fichero de logs sumando el campo recuento?",
                "¿Cuántos agentes diferentes aparecen y cual es el nombre?",
                "¿Qué tipo de evento es el más crítico dime su según el nivel ?"
            ],
            "Tema 2 - Resumen del contenido": [
                "Resume en una línea qué está ocurriendo en el sistema."
            ],
            "Tema 3 - Patrones, errores o anomalías": [
                "¿Detectas algún comportamiento anómalo en estos logs?",
                "¿Hay intentos de acceso fallidos?¿Dime con que alerta?",
                "¿Hay ficheros que son problemáticos dime cuales?"
            ],
            "Tema 4 - Conclusiones": [
                "¿Qué podría estar causando los errores observados?",
                "Sugiere posibles soluciones para los errores detectados.",
                "¿Hay indicios de algún tipo de ataque, dime cual o cuales?",
                "¿Cuál sería tu diagnóstico general del estado del sistema según estos logs?"
            ],
            "Tema 5 - Preguntas de opción múltiple": [
                "¿Qué tipo de ataque se detecta en múltiples entradas del log?\nA) Escaneo de puertos\nB) Ataque de denegación de servicio (DoS)\nC) Fuerza bruta sobre SSH\nD) Inyección SQL",
                "¿Qué archivo fue identificado con múltiples reglas YARA maliciosas?\nA) /etc/passwd\nB) /home/mirai\nC) /var/log/auth.log\nD) /home/unknown",
                "¿Qué nivel de criticidad es la mayor de los eventos detectados por las reglas YARA?\nA) 3\nB) 12\nC) 7\nD) 10",
                "¿Cuál es el evento más crítico relacionado con sshd?\nA) Cambio de contraseña exitoso\nB) Acceso root autorizado\nC) Autenticación fallida por fuerza bruta\nD) Sesión cerrada",
                "¿Qué agente está registrando todos los eventos del log?\nA) agente-centos\nB) agente-debian\nC) agente-ubuntu\nD) agente-fedora",
                "¿Qué tipo de archivos fueron detectados como maliciosos por las reglas YARA?\nA) Archivos .docx\nB) Archivos .conf\nC) Archivos sospechosos en /home/\nD) Archivos ejecutables del sistema"
            ]
        }

        abs_path = os.path.join(os.getcwd(), data_path)

        if os.path.exists(abs_path):
            self.__data_path = abs_path
            self.__files = self.__get_json_files()
        else:
            raise Exception("La ruta no existe. Por favor, verifica la ruta de los archivos JSON.")

    def __get_json_files(self):
        return [
            os.path.join(self.__data_path, f)
            for f in os.listdir(self.__data_path)
            if f.endswith(".json")
        ]

    def load_logs(self, file_name: str) -> list:
        path = os.path.join(self.__data_path, file_name)
        with open(path, 'r') as f:
            return [json.loads(line) for line in f.readlines()]

    def get_questions_by_topic(self, topic: str):
        return self.__questions.get(topic, [])

    def __get_response_style(self, topic: str) -> str:
        estilos = {
            "Tema 1 - Eventos básicos": (
                "Responde de forma breve y directa. Usa el siguiente formato exclusivamente sin añadir extra:\n"
                "Hay X eventos.\n"
                "Hay Y agentes: nombre1, nombre2...\n"
                "El evento más crítico es DESCRIPCIÓN con nivel N.\n\n"
            ),
            "Tema 2 - Resumen del contenido": (
                "Se lo mas preciso posible no hagas introduccion\n"
            ),
            "Tema 3 - Patrones, errores o anomalías": (
                "Responde de forma breve y directa omitiendo caracteres innecesarios y en una linea sin introduccion. Usa el siguiente formato:\n"
                "Elegir Sí o No y en que consiste\n"
                "Elegir Sí o No decir que alerta\n"
                "Nombres ficheros problematicos\n\n"
            ),
            "Tema 4 - Conclusiones": (
                "Contesta con este formato de plantilla lo mas breve posible omitiendo caracteres innecesarios y en una linea sin introduccion:\n"
                "Posible causa de errores: ...\n"
                "Soluciones sugeridas: ...\n"
                "Indicios de ataque: Sí/No, tipo: ...\n"
                "Diagnóstico general: ...\n\n"
            ),
            "Tema 5 - Preguntas de opción múltiple": (
                "Responde exclusivamente con la letra para cada pregunta, sin justificar, omitiendo caracteres y numeros innecesarios directamente:\n"
                "1: A/B/C/D\n"
                "2: A/B/C/D\n"
                "3: A/B/C/D\n"
                "4: A/B/C/D\n"
                "5: A/B/C/D\n"
                "6: A/B/C/D\n"
            )
        }
        return estilos.get(topic, "")

    def generate_prompt(self, file_name: str, topic: str) -> str:
        logs = self.load_logs(file_name)
        sample = logs[:25]  # Tomamos solo una muestra

        estilo_respuesta = self.__get_response_style(topic)
        prompt = f"Contesta a las preguntas sin salirte de las plantilla contestando lo mas preciso posible.\n{json.dumps(sample, indent=2)}\n\n"
        prompt += estilo_respuesta
        prompt += "\n".join(self.get_questions_by_topic(topic))
        return prompt

    def show_formatted_answer(self, answer_file: str):
        path = answer_file

        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró el archivo: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print("\n📄 Información del archivo:")
        print(f"Modelo: {data.get('modelo', 'Desconocido')}")
        print(f"Archivo analizado: {data.get('archivo', 'Desconocido')}")
        print(f"Tema: {data.get('tema', 'Desconocido')}")
        print("\n📝 Preguntas y Respuestas:")

        respuesta = data.get("respuesta", "")
        if isinstance(respuesta, str):
            print("\n" + respuesta)
        else:
            print("\n(No se encontró una respuesta en formato texto.)")
