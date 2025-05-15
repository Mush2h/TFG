import pandas as pd

# Ruta al archivo CSV de entrada
input_path = "../data/eventos_prueba.csv"

# Rutas de salida
output_filtrado = "../data/logs_parseados_filtrados.json"
output_todos = "../data/logs_parseados_todos.json"

def parsear_logs(input_path, output_filtrado, output_todos):
    # Cargar CSV
    df = pd.read_csv(input_path)

    # Filtrar columnas clave correctamente 
    df = df[["timestamp", "agent.name", "rule.level", "rule.id", "rule.description"]]

    # Convertir la columna de timestamp a datetime con formato explícito 
    # Convertir la columna de timestamp a datetime con formato explícito
    # El formato esperado es: "Mar 15, 2023 @ 14:23:45.123"

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%b %d, %Y @ %H:%M:%S.%f",  # Formato esperado 
        errors='coerce'
    )

    # ------------------ PARSEO 1: Filtrar por nivel >= 7 ------------------
    df_filtrado = df[df["rule.level"] >= 7].copy()
    df_filtrado = df_filtrado.sort_values(by="timestamp", ascending=False)
    df_filtrado.to_json(output_filtrado, orient="records", lines=True)

    # ------------------ PARSEO 2: Todos los eventos, sin duplicados ------------------
    df_todos = df.drop_duplicates().copy()
    df_todos = df_todos.sort_values(by="timestamp", ascending=False)
    df_todos.to_json(output_todos, orient="records", lines=True)

    print(f"[✓] Parseo con nivel >= 7 exportado en: {output_filtrado}")
    print(f"[✓] Todos los eventos (sin duplicados) exportados en: {output_todos}")

# Ejecutar si el script se corre directamente
if __name__ == "__main__":
    parsear_logs(input_path, output_filtrado, output_todos)

