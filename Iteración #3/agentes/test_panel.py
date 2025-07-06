import os
import json
import pandas as pd
import time
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-nano-2025-04-14",
    temperature=0.9,
    max_tokens=2000,
    api_key=os.getenv("OPENAI_API_KEY")
)

# === Funciones auxiliares ===

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


def cargar_contexto(path_dir: str) -> str:
    contexto = ""
    for filename in sorted(os.listdir(path_dir)):
        if filename.endswith((".txt", ".md")):
            with open(os.path.join(path_dir, filename), "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                contexto += f"{contenido}\n\n"
    return contexto.strip()


def construir_prompt(instrucciones: list, contexto: str = "") -> str:
    prompt = ""
    if contexto:
        prompt += f"CONTEXTUALIZACIÓN:\n{contexto}\n\n"

    prompt += (
        "Eres una persona peruana respondiendo una encuesta real.\n"
        "Debes contestar como si fueras un encuestado auténtico y único, usando exactamente las claves indicadas.\n\n"
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


# === Función para el nodo del grafo ===

def generar_respuesta(state: dict) -> dict:
    instrucciones = state["instrucciones"]
    columnas = state["columnas"]
    i = state["persona"]
    contexto = state["contexto"]

    prompt = construir_prompt(instrucciones, contexto)
    intentos = 0
    exito = False
    inicio_tiempo = time.time()

    while intentos < 3 and not exito:
        try:
            respuesta = llm.invoke([HumanMessage(content=prompt)]).content.strip()
            json_start = respuesta.find("{")
            json_end = respuesta.rfind("}") + 1
            json_str = respuesta[json_start:json_end]
            data = json.loads(json_str)

            if set(data.keys()) != set(columnas):
                raise ValueError("❌ Claves de respuesta no coinciden con las columnas.")

            fila = [f"P{i}"] + [data[col] for col in columnas]
            print(f"✅ Persona {i} generada en {time.time() - inicio_tiempo:.2f} s.")
            return {"fila": fila, "exitosa": True}

        except Exception as e:
            print(f"❌ Persona {i}, intento {intentos + 1}: {e}")
            intentos += 1
            time.sleep(1)

    print(f"⚠️ Persona {i} sin respuesta válida. Tiempo: {time.time() - inicio_tiempo:.2f} s.")
    return {"fila": [f"P{i}"] + ["ERROR"] * len(columnas), "exitosa": False}


# === Orquestación LangGraph ===

def simular_respuestas_con_langgraph(columnas: list, instrucciones: list, contexto: str, n: int = 2) -> pd.DataFrame:
    columnas_finales = ["ID_Encuestado"] + columnas
    filas = []

    builder = StateGraph(state_schema=dict)
    builder.add_node("simular", generar_respuesta)
    builder.set_entry_point("simular")
    builder.set_finish_point("simular")

    graph = builder.compile()

    inicio_total = time.time()
    for i in range(1, n + 1):
        print(f"\n👤 Generando respuestas para Persona {i}...")
        state = {
            "persona": i,
            "instrucciones": instrucciones,
            "columnas": columnas,
            "contexto": contexto
        }
        salida = graph.invoke(state)
        fila = salida.get("fila", [f"P{i}"] + ["ERROR"] * len(columnas))
        filas.append(fila)
    fin_total = time.time()

    print(f"\n🕒 Tiempo total de ejecución: {fin_total - inicio_total:.2f} segundos")
    return pd.DataFrame(filas, columns=columnas_finales)


# === Ejecución principal ===

if __name__ == "__main__":
    schema_path = os.path.join("otros", "test_1.txt")
    contexto_dir = "contexto"
    output_csv = os.path.join("encuesta", "test_panel_1.csv")

    columnas, instrucciones = cargar_schema(schema_path)
    contexto = cargar_contexto(contexto_dir)

    df = simular_respuestas_con_langgraph(columnas, instrucciones, contexto, n=20)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"\n✅ Archivo final guardado en: {output_csv}")
