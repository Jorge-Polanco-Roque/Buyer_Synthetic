# agentes/test_panel.py

import os
import json
import csv
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=1800,
    api_key=os.getenv("OPENAI_API_KEY")
)

def cargar_schema_desde_txt(path_txt: str) -> list:
    with open(path_txt, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    columnas = []
    for bloque in schema["campos"]:
        for var in bloque["variables"]:
            columnas.append(var["nombre"])
    return columnas

def simular_respuestas_csv(columnas: list, n: int = 2) -> pd.DataFrame:
    columnas_finales = ["ID_Encuestado"] + columnas
    filas = []

    for i in range(1, n + 1):
        print(f"👤 Generando respuestas para Persona {i}...")

        prompt = (
            f"Eres una persona peruana entre 18 y 65 años respondiendo una encuesta real. "
            f"Responde con realismo, sin repetir las preguntas. Da una respuesta breve para cada variable.\n\n"
            f"Variables:\n"
        )
        for col in columnas:
            prompt += f"- {col}\n"

        prompt += (
            f"\nDevuelve una única línea CSV con las respuestas en el mismo orden, separadas por comas. "
            f"Escapa con comillas si alguna respuesta contiene comas. No incluyas encabezados ni explicaciones.\n"
        )

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            linea_csv = response.content.strip()

            parsed_row = next(csv.reader([linea_csv]))
            if len(parsed_row) != len(columnas):
                raise ValueError("❌ Número de respuestas no coincide con las variables.")

            fila = [f"P{i}"] + parsed_row
            filas.append(fila)

        except Exception as e:
            print(f"❌ Error en Persona {i}: {e}")

    return pd.DataFrame(filas, columns=columnas_finales)

if __name__ == "__main__":
    schema_path = os.path.join("otros", "test_1.txt")
    output_csv = os.path.join("encuesta", "test_panel_1.csv")

    columnas = cargar_schema_desde_txt(schema_path)
    df = simular_respuestas_csv(columnas, n=2)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Archivo final guardado en: {output_csv}")
