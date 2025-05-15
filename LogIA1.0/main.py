import os
import json
from datetime import datetime
import subprocess
from openai import OpenAI
from src.dataset import Dataset
from dotenv import load_dotenv  # << AÑADIR ESTO

# ⚡ Cargar el archivo .env
load_dotenv()

# Cliente con tu API key (leída del .env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Ruta donde se guardarán las respuestas
output_dir = "respuesta_modelos"
os.makedirs(output_dir, exist_ok=True)

def query_openai(prompt):
    """Consulta a OpenAI GPT-4."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un analista de seguridad. Ayuda a entender los eventos del sistema."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

def query_ollama_phi4_with_curl(prompt):
    """Consulta al modelo phi4 usando CURL real y procesa correctamente el streaming de respuestas."""
    curl_command = [
        "curl",
        "http://localhost:11434/api/generate",
        "-s",  
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": "phi4",
            "prompt": prompt,
            "temperature": 0.3
        })
    ]

    try:
        # Ejecutar el comando curl
        result = subprocess.run(
            curl_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Procesar línea a línea para juntar todos los fragmentos de respuesta
        lines = result.stdout.strip().split('\n')
        full_response = ""

        for line in lines:
            if line.strip():
                try:
                    obj = json.loads(line)
                    if "response" in obj:
                        full_response += obj["response"]
                except json.JSONDecodeError:
                    print(f"⚠️ No se pudo decodificar una línea: {line}")

        return full_response.strip()

    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando curl: {e.stderr}")
        raise

def main():
    ds = Dataset("data/")
    topic = "Tema 1 - Eventos básicos"
    filename = "logs_parseados_todos.json"

    # Generar prompt
    prompt = ds.generate_prompt(filename, topic)
    print("\n📝 Prompt generado:\n")
    print(prompt)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- 1. Consultar OpenAI ---
    print("\n🤖 Consultando OpenAI GPT-4...\n")
    try:
        answer_openai = query_openai(prompt)

        print("\n✅ Respuesta de OpenAI:\n")
        print(answer_openai)

        output_path_openai = os.path.join(output_dir, f"respuesta_openai_{timestamp}.json")
        with open(output_path_openai, "w", encoding="utf-8") as f:
            json.dump({
                "modelo": "gpt-4",
                "archivo": filename,
                "tema": topic,
                "prompt": prompt,
                "respuesta": answer_openai
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Respuesta OpenAI guardada en: {output_path_openai}")

    except Exception as e:
        print(f"⚠️ Error consultando OpenAI: {e}")

    # --- 2. Consultar Ollama phi4 usando curl ---
    print("\n🤖 Consultando modelo local Phi4 vía CURL + Ollama...\n")
    try:
        answer_ollama = query_ollama_phi4_with_curl(prompt)

        print("\n✅ Respuesta de Phi4 (Ollama):\n")
        print(answer_ollama)

        output_path_ollama = os.path.join(output_dir, f"respuesta_phi4_{timestamp}.json")
        with open(output_path_ollama, "w", encoding="utf-8") as f:
            json.dump({
                "modelo": "phi4",
                "archivo": filename,
                "tema": topic,
                "prompt": prompt,
                "respuesta": answer_ollama
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Respuesta Phi4 guardada en: {output_path_ollama}")

    except Exception as e:
        print(f"⚠️ Error consultando Phi4 (Ollama): {e}")

if __name__ == "__main__":
    main()
