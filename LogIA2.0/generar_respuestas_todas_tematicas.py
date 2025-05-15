import os
import json
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI as LlamaOpenAI
from src.dataset import Dataset
from lib.parseoalertas import parsear_logs

load_dotenv()

OUTPUT_DIR = "respuestas_por_tematica"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODELOS = {
    "openai": "openai_gpt4",
    "phi4": "phi4",
    "deepseek-r1_32b": "deepseek-r1_32b",
    "llama3.2": "llama3.2"
}

# 🔧 Nueva función para estructurar la respuesta
def formatear_respuesta_modelo(modelo, archivo, tema, preguntas, respuesta_texto, timestamp):
    lineas = [line.strip("- ").strip() for line in respuesta_texto.strip().split("\n") if line.strip()]
    preguntas_respuestas = {}
    for i, pregunta in enumerate(preguntas):
        if i < len(lineas):
            preguntas_respuestas[pregunta] = lineas[i]
        else:
            preguntas_respuestas[pregunta] = "(Sin respuesta)"
    return {
        "modelo": modelo,
        "archivo": archivo,
        "tema": tema,
        "preguntas_respuestas": preguntas_respuestas,
        "timestamp": timestamp
    }

def build_openai_model():
    return LlamaOpenAI(
        model="gpt-4",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )

def query_openai(llm, prompt):
    return llm.complete(prompt).text

def query_ollama_api(prompt, model="phi4", base_url="http://localhost:11435"):
    url = f"{base_url}/api/generate"
    payload = {"model": model, "prompt": prompt, "temperature": 0.1, "stream": True}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=300)
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    obj = json.loads(line)
                    if "response" in obj:
                        full_response += obj["response"]
                except json.JSONDecodeError:
                    print(f"⚠️ Error decodificando línea: {line}")
        return full_response.strip()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error consultando Ollama API: {e}")
        return None

def guardar_respuesta(modelo, tema, filename, preguntas, respuesta, timestamp):
    tema_dir = os.path.join(OUTPUT_DIR, tema.replace(" ", "_").lower())
    os.makedirs(tema_dir, exist_ok=True)

    file_out = os.path.join(tema_dir, f"respuesta_{modelo}_{timestamp}.json")
    estructura = formatear_respuesta_modelo(
        modelo=modelo,
        archivo=filename,
        tema=tema,
        preguntas=preguntas,
        respuesta_texto=respuesta,
        timestamp=timestamp
    )

    with open(file_out, "w", encoding="utf-8") as f:
        json.dump(estructura, f, ensure_ascii=False, indent=2)

    print(f"✅ Guardado: {file_out}")

def seleccionar_tematica(tematicas):
    print("\n📚 Selecciona una temática para analizar:")
    for i, tema in enumerate(tematicas, 1):
        print(f"{i}. {tema}")
    print(f"{len(tematicas)+1}. TODAS las temáticas")

    opcion = input("👉 Ingresa el número de tu elección: ").strip()

    if opcion.isdigit():
        idx = int(opcion)
        if 1 <= idx <= len(tematicas):
            return [tematicas[idx - 1]]
        elif idx == len(tematicas) + 1:
            return tematicas
    print("❌ Opción inválida. Ejecutando TODAS las temáticas por defecto.")
    return tematicas

def main():
    ds = Dataset("data/")
    filename = "logs_parseados_por_rule_description_unica.json" # Cambiar si quieres evaular otro fichero

    print("🚀 Parseando logs de entrada...")
    parsear_logs("data/eventos_prueba.csv",
                 "data/logs_parseados_filtrados.json",
                 "data/logs_parseados_todos.json",
                 "data/logs_parseados_por_rule_description_unica.json")
    
    #imprimir el fichero de logs que se va a analizar
    print("\n📂 Fichero de logs a analizar:"
          f"\n{filename}")

    todas_las_tematicas = list(ds._Dataset__questions.keys())
    tematicas_seleccionadas = seleccionar_tematica(todas_las_tematicas)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for tema in tematicas_seleccionadas:
        print(f"\n📂 Tema seleccionado: {tema}")
        prompt = ds.generate_prompt(filename, tema)
        preguntas = ds.get_questions_by_topic(tema)

        for model_id, model_name in MODELOS.items():
            print(f"🤖 Consultando modelo: {model_name}")
            try:
                if model_id == "openai":
                    llm = build_openai_model()
                    respuesta = query_openai(llm, prompt)
                else:
                    respuesta = query_ollama_api(prompt, model=model_id.replace("_", ":"))

                if model_id == "deepseek-r1_32b":
                    respuesta = re.sub(r"<think>.*?</think>", "", respuesta, flags=re.DOTALL).strip()

                if respuesta:
                    guardar_respuesta(model_name, tema, filename, preguntas, respuesta, timestamp)
                else:
                    print(f"⚠️ No se recibió respuesta de {model_name}.")
            except Exception as e:
                print(f"❌ Error con modelo {model_name}: {e}")

    print("\n✅ Proceso completado.")

if __name__ == "__main__":
    main()
