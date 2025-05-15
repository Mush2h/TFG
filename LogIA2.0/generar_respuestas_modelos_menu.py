import os
import json
import requests
import re


from datetime import datetime
from lib.parseoalertas import parsear_logs

from dotenv import load_dotenv

# LlamaIndex imports para OpenAI
from llama_index.llms.openai import OpenAI as LlamaOpenAI


# Importar tu Dataset
from src.dataset import Dataset

# 📁 Cargar variables de entorno
load_dotenv()

# 📂 Crear directorio de salida
output_dir = "respuesta_modelos"
os.makedirs(output_dir, exist_ok=True)

def build_openai_model():
    """Inicializa el modelo de OpenAI."""
    return LlamaOpenAI(
        model="gpt-4",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY")
    )

def query_openai(llm, prompt):
    """Consulta a OpenAI usando LlamaIndex."""
    response = llm.complete(prompt)
    return response.text

def query_ollama_api(prompt, model="phi4", base_url="http://localhost:11435"):
    """Consulta a Ollama manualmente como curl, procesando línea a línea."""
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": 0.3,
        "stream": True
    }

    headers = {
        "Content-Type": "application/json"
    }

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
                    print(f"⚠️ No se pudo decodificar una línea: {line}")

        return full_response.strip()

    except requests.exceptions.RequestException as e:
        print(f"❌ Error consultando Ollama API: {e}")
        return None

def seleccionar_modelos():
    print("\n📌 Selecciona el modelo que deseas usar para evaluar las preguntas:")
    print("1. Todos los modelos")
    print("2. Solo OpenAI GPT-4")
    print("3. Solo Ollama - phi4")
    print("4. Solo Ollama - deepseek-r1_32b")
    print("5. Solo Ollama - llama3.2")

    opcion = input("Ingresa el número de tu elección: ").strip()

    if opcion == "1":
        return ["openai", "phi4", "deepseek-r1_32b", "llama3.2"]
    elif opcion == "2":
        return ["openai"]
    elif opcion == "3":
        return ["phi4"]
    elif opcion == "4":
        return ["deepseek-r1_32b"]
    elif opcion == "5":
        return ["llama3.2"]
    else:
        print("❌ Opción inválida. Usando todos los modelos por defecto.")
        return ["openai", "phi4", "deepseek-r1_32b", "llama3.2"]

def main():
    ds = Dataset("data/")
    topic = "Tema 1 - Eventos básicos"
    filename = "logs_parseados_por_rule_description_unica.json"

    parsear_logs("data/eventos_prueba.csv", "data/logs_parseados_filtrados.json",
                 "data/logs_parseados_todos.json", "data/logs_parseados_por_rule_description_unica.json")

    prompt = ds.generate_prompt(filename, topic)
    print("\n📝 Prompt generado:\n")
    print(prompt)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    respuestas_generadas = {}

    modelos_a_usar = seleccionar_modelos()

    if "openai" in modelos_a_usar:
        print("\n🤖 Consultando modelo: OpenAI GPT-4...\n")
        try:
            llm_openai = build_openai_model()
            answer_openai = query_openai(llm_openai, prompt)

            output_path_openai = os.path.join(output_dir, f"respuesta_openai_gpt4_{timestamp}.json")
            with open(output_path_openai, "w", encoding="utf-8") as f:
                json.dump({
                    "modelo": "openai_gpt4",
                    "archivo": filename,
                    "tema": topic,
                    "prompt": prompt,
                    "respuesta": answer_openai
                }, f, ensure_ascii=False, indent=2)

            print(f"✅ Respuesta OpenAI guardada en: {output_path_openai}")
            respuestas_generadas["1"] = output_path_openai

        except Exception as e:
            print(f"⚠️ Error consultando OpenAI: {e}")

    ollama_models = ["phi4", "deepseek-r1_32b", "llama3.2"]
    idx = 2
    for ollama_model in ollama_models:
        if ollama_model in modelos_a_usar:
            print(f"\n🤖 Consultando modelo Ollama: {ollama_model}...\n")
            model_api_name = ollama_model.replace('_', ':').replace('_', '.')
            answer_ollama = query_ollama_api(prompt, model=model_api_name)

            if answer_ollama:
                if ollama_model == "deepseek-r1_32b":
                    answer_ollama = re.sub(r"<think>.*?</think>", "", answer_ollama, flags=re.DOTALL).strip()

                output_path_ollama = os.path.join(output_dir, f"respuesta_{ollama_model}_{timestamp}.json")
                with open(output_path_ollama, "w", encoding="utf-8") as f:
                    json.dump({
                        "modelo": ollama_model,
                        "archivo": filename,
                        "tema": topic,
                        "prompt": prompt,
                        "respuesta": answer_ollama
                    }, f, ensure_ascii=False, indent=2)

                print(f"✅ Respuesta {ollama_model} guardada en: {output_path_ollama}")
                respuestas_generadas[str(idx)] = output_path_ollama
            else:
                print(f"⚠️ No se pudo obtener respuesta de {ollama_model}")
            idx += 1

    while True:
        print("\n📋 Respuestas disponibles:")
        for option, filepath in respuestas_generadas.items():
            model_name = os.path.basename(filepath).replace("respuesta_", "").replace(".json", "")
            print(f"{option}. {model_name}")

        print("0. Salir")

        choice = input("\nSelecciona una opción para mostrar la respuesta: ")

        if choice == "0":
            print("👋 Saliendo del menú.")
            break
        elif choice in respuestas_generadas:
            ds.show_formatted_answer(respuestas_generadas[choice])
        else:
            print("❌ Opción inválida, intenta de nuevo.")

if __name__ == "__main__":
    main()
