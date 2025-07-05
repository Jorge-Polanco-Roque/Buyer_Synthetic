import os
import pandas as pd
from funciones.genera_llm import genera_llm

def llenar_csv(path_csv: str, context: str, columna_objetivo: str, otras_columnas: list) -> pd.DataFrame:
    """
    Carga un CSV, genera una nueva columna por fila usando LLM + contexto + columnas existentes,
    y guarda el resultado en 'encuesta_contestada'.
    """
    df = pd.read_csv(path_csv)

    def procesar_fila(row):
        datos = {col: row[col] for col in otras_columnas}
        # Llamada al LLM para generar contenido
        generado = genera_llm(context, datos)
        return generado

    df[columna_objetivo] = df.apply(procesar_fila, axis=1)

    # Guardar salida
    carpeta_origen = os.path.dirname(path_csv)
    carpeta_salida = carpeta_origen.replace("encuesta", "encuesta_contestada")
    os.makedirs(carpeta_salida, exist_ok=True)
    df.to_csv(os.path.join(carpeta_salida, os.path.basename(path_csv)), index=False)
    return df