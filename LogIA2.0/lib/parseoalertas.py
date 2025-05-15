import pandas as pd

# Ruta al archivo CSV de entrada
input_path = "../data/eventos_prueba.csv"

# Rutas de salida
output_filtrado = "../data/logs_parseados_filtrados.json"
output_todos = "../data/logs_parseados_todos.json"
output_por_description = "../data/logs_parseados_por_rule_description_unica.json"

def parsear_logs(input_path, output_filtrado, output_todos, output_por_description):
    # Cargar CSV
    df = pd.read_csv(input_path)

    # Filtrar columnas clave correctamente
    df = df[["timestamp", "agent.name", "rule.level", "rule.id", "rule.description"]]

    # Convertir la columna de timestamp a datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="%b %d, %Y @ %H:%M:%S.%f",
        errors='coerce'
    )

    # ------------------ PARSEO 1: Filtrar por nivel >= 7 ------------------
    df_filtrado = df[df["rule.level"] >= 7].copy()
    df_filtrado = df_filtrado.sort_values(by="timestamp", ascending=False)
    df_filtrado.to_json(output_filtrado, orient="records", lines=True)

    # ------------------ PARSEO 2: Todos los eventos (con duplicados), ordenados por rule.id ------------------
    df_todos = df.copy()
    df_todos = df_todos.sort_values(by="rule.id", ascending=True)
    df_todos.to_json(output_todos, orient="records", lines=True)

    # ------------------ PARSEO 3: Descripciones únicas + contador + orden por nivel ------------------
    # Contar ocurrencias de cada descripción
    conteo = df["rule.description"].value_counts().rename("recuento").reset_index()
    conteo.rename(columns={"index": "rule.description"}, inplace=True)

    # Obtener eventos únicos (último por timestamp)
    df_description_unicos = (
        df.sort_values(by="timestamp", ascending=False)
          .drop_duplicates(subset="rule.description")
    )

    # Unir con el recuento
    df_description_unicos = pd.merge(df_description_unicos, conteo, on="rule.description")

    # Ordenar por nivel de amenaza
    df_description_unicos = df_description_unicos.sort_values(by="rule.level", ascending=False)

    # Exportar
    df_description_unicos.to_json(output_por_description, orient="records", lines=True)

    print(f"[✓] Parseo con nivel >= 7 exportado en: {output_filtrado}")
    print(f"[✓] Todos los eventos (ordenados por rule.id) exportados en: {output_todos}")
    print(f"[✓] Eventos únicos por rule.description ordenados por nivel con recuento exportados en: {output_por_description}")

# Ejecutar si el script se corre directamente
if __name__ == "__main__":
    parsear_logs(input_path, output_filtrado, output_todos, output_por_description)
