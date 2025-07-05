import os
import json
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import time

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.5,
    max_tokens=2000,
    api_key=os.getenv("OPENAI_API_KEY")
)

def cargar_schema(path_txt: str):
    with open(path_txt, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    columnas = []
    instrucciones = []

    for bloque in schema["campos"]:
        for var in bloque["variables"]:
            nombre = var["nombre"]
            columnas.append(nombre)
            opciones = var.get("opciones", None)
            nota = var.get("nota", "")
            if opciones:
                opciones_str = ", ".join([f'"{opt}"' for opt in opciones])
                instrucciones.append(f'"{nombre}": elige entre {opciones_str}')
            else:
                instrucciones.append(f'"{nombre}": respuesta abierta coherente. {nota}'.strip())

    return columnas, instrucciones

def construir_prompt(instrucciones: list) -> str:
    prompt = (
        "Eres una persona peruana entre 18 y 65 años respondiendo una encuesta real.\n"
        "Debes contestar como si fueras un encuestado auténtico, usando exactamente las claves indicadas.\n\n"
        "Responde en formato JSON válido (sin comentarios ni texto adicional), respetando:\n"
        "- Las claves tal como aparecen.\n"
        "- Las opciones exactamente como están escritas (con acentos y mayúsculas si aplica).\n"
        "- Si alguna clave permite 'Otro', puedes generar una respuesta abierta coherente SOLO si se elige esa opción.\n\n"
        "Este es el formato esperado:\n\n"
        "{\n"
    )
    prompt += ",\n".join([f'  "{inst.split(":")[0].strip()}": ...  # {inst.split(":", 1)[1].strip()}' for inst in instrucciones])
    prompt += (
        "\n}\n\n"
        "⚠️ Devuelve únicamente un bloque JSON válido, sin explicaciones ni encabezados."
    )
    return prompt

def simular_respuestas_json(columnas: list, instrucciones: list, n: int = 2) -> pd.DataFrame:
    columnas_finales = ["ID_Encuestado"] + columnas
    filas = []

    for i in range(1, n + 1):
        print(f"\n👤 Generando respuestas para Persona {i}...")

        intentos = 0
        exito = False

        while intentos < 3 and not exito:
            try:
                prompt = construir_prompt(instrucciones)
                response = llm.invoke([HumanMessage(content=prompt)])
                respuesta = response.content.strip()

                # Forzar extracción de JSON puro
                json_start = respuesta.find("{")
                json_end = respuesta.rfind("}") + 1
                json_str = respuesta[json_start:json_end]

                data = json.loads(json_str)

                if set(data.keys()) != set(columnas):
                    raise ValueError("❌ Claves de respuesta no coinciden con las columnas.")

                fila = [f"P{i}"] + [data[col] for col in columnas]
                filas.append(fila)
                print("✅ Respuesta aceptada.")

                exito = True

            except Exception as e:
                print(f"❌ Error en Persona {i}, intento {intentos + 1}: {e}")
                intentos += 1
                time.sleep(1)

        if not exito:
            print(f"⚠️ Persona {i}: No se logró generar una respuesta válida.")
            fila = [f"P{i}"] + ["ERROR"] * len(columnas)
            filas.append(fila)

    return pd.DataFrame(filas, columns=columnas_finales)

if __name__ == "__main__":
    schema_path = os.path.join("otros", "test_1.txt")
    output_csv = os.path.join("encuesta", "test_panel_1.csv")

    columnas, instrucciones = cargar_schema(schema_path)
    df = simular_respuestas_json(columnas, instrucciones, n=2)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"\n✅ Archivo final guardado en: {output_csv}")
