import os
import json
import datetime
from dotenv import load_dotenv

from src.evaluador_humano import EvaluadorGT
from src.evaluador_openAI import Evaluador

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 📁 Ruta del ground truth
ruta_ground_truth = "eval/ground_truth.json"

# 📁 Directorio de respuestas (ajústalo según tema a evaluar)

#directorio_respuestas = "respuestas_por_tematica/tema_1_-_eventos_básicos"
#directorio_respuestas = "respuestas_por_tematica/tema_2_-_resumen_del_contenido"
#directorio_respuestas = "respuestas_por_tematica/tema_3_-_patrones,_errores_o_anomalías"
#directorio_respuestas = "respuestas_por_tematica/tema_4_-_conclusiones"
directorio_respuestas = "respuestas_por_tematica/tema_5_-_preguntas_de_opción_múltiple"

def cargar_respuestas_desde_directorio(directorio):
    respuestas = {}
    for nombre_archivo in os.listdir(directorio):
        if not nombre_archivo.endswith(".json"):
            continue
        path = os.path.join(directorio, nombre_archivo)
        try:
            with open(path, encoding="utf-8") as f:
                contenido = json.load(f)
                modelo = contenido.get("modelo")
                if modelo:
                    respuestas[modelo] = contenido
        except Exception as e:
            print(f"❌ Error al cargar {nombre_archivo}: {e}")
    return respuestas

def cargar_ground_truth(path=ruta_ground_truth):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_resultados(resultados, nombre_archivo_base):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"resultados_{nombre_archivo_base}_{timestamp}.json"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"\n📝 Resultados guardados en: {nombre_archivo}")

def menu_evaluacion():
    print("\n🔎 ¿Cómo deseas evaluar las respuestas generadas?")
    print("1. Usar Ground Truth")
    print("2. Usar GPT-4 como referencia")
    print("3. Usar GPT-4 comparando con Ground Truth")
    opcion = input("👉 Ingresa el número de tu elección: ").strip()

    if opcion == "1":
        return "groundtruth"
    elif opcion == "2":
        return "gpt"
    elif opcion == "3":
        return "gpt_vs_groundtruth"
    else:
        print("❌ Opción no válida. Usando Ground Truth por defecto.")
        return "groundtruth"

def main():
    modo_evaluacion = menu_evaluacion()
    respuestas_dict = cargar_respuestas_desde_directorio(directorio_respuestas)

    if modo_evaluacion == "groundtruth":
        print("\n📊 Evaluación basada en respuestas correctas (Ground Truth)")
        ground_truth = cargar_ground_truth()
        evaluador = EvaluadorGT(respuestas_dict, ground_truth)
        resultados = evaluador.evaluar_todos_los_modelos()

        for modelo, resultado in resultados.items():
            print(f"\n🔍 Modelo: {modelo}")
            print(f"✅ Aciertos: {resultado['aciertos']}/{resultado['total']} | Puntuación: {resultado['score']}/10")
            for pregunta, detalle in resultado["detalle"].items():
                print(f"\n❓ {pregunta}\n{detalle}")

        guardar_resultados(resultados, "groundtruth")

    elif modo_evaluacion == "gpt":
        print("\n🤖 Evaluación basada en GPT-4 como referencia")
        modelo_referencia = next((m for m in respuestas_dict if "gpt4" in m.lower()), None)
        if not modelo_referencia:
            raise ValueError("❌ No se encontró ninguna respuesta de GPT-4 como referencia.")

        print(f"🎯 Usando '{modelo_referencia}' como modelo de referencia.")
        evaluador = Evaluador(respuestas_dict, api_key, modelo_referencia=modelo_referencia)
        resultados = evaluador.evaluar_modelos_con_openai()

        for modelo, resultado in resultados.items():
            print(f"\n📊 Evaluación para {modelo}:\n")
            print(resultado.get("evaluacion", "❌ Evaluación no disponible"))

        guardar_resultados(resultados, "gpt_vs_gpt")

    elif modo_evaluacion == "gpt_vs_groundtruth":
        print("\n🤖 Evaluación realizada por GPT-4 comparando con Ground Truth")
        ground_truth = cargar_ground_truth()

        evaluador = Evaluador(
            respuestas_dict=respuestas_dict,
            openai_api_key=api_key,
            ground_truth=ground_truth
        )
        resultados = evaluador.evaluar_modelos_con_groundtruth_openai()

        for modelo, resultado in resultados.items():
            print(f"\n📊 Evaluación para {modelo}:\n")
            print(resultado.get("evaluacion", "❌ Evaluación no disponible"))

        guardar_resultados(resultados, "gpt_vs_groundtruth")

if __name__ == "__main__":
    main()
