from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
import pandas as pd

# Cargar variables desde .env
load_dotenv()

# Importar funciones externas
from funciones.leer_contexto import leer_contexto
from funciones.llamar_llm import llamar_llm as llamar_llm_func
from funciones.calculo_matematico import calculo_matematico

# Definición del estado
class AgentState(TypedDict):
    carpeta_contexto: str
    path_csv: str
    df: pd.DataFrame
    row_idx: int
    row_data: dict
    context: str
    columna_llm: str
    resultado_math: float

# Configurar LLM (referencia si quisieras usarlo directo)
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,
    max_tokens=1000,
    streaming=False,
    api_key=os.getenv("OPENAI_API_KEY")
)

# --- FUNCIONES NODO ---

def cargar_contexto(state: AgentState) -> AgentState:
    contexto = leer_contexto(state["carpeta_contexto"])
    return {"context": contexto}

def cargar_csv(state: AgentState) -> AgentState:
    df = pd.read_csv(state["path_csv"])
    return {"df": df}

def seleccionar_fila(state: AgentState) -> AgentState:
    fila = state["df"].iloc[state["row_idx"]].to_dict()
    return {"row_data": fila}

def nodo_llamar_llm(state: AgentState) -> AgentState:
    output = llamar_llm_func(state["context"], state["row_data"])
    return {"columna_llm": output}

def guardar_resultados(state: AgentState) -> AgentState:
    df = state["df"]
    idx = state["row_idx"]
    df.at[idx, "llm"] = state["columna_llm"]
    df.at[idx, "math"] = state["resultado_math"]
    return {}

def avanzar_fila(state: AgentState) -> AgentState:
    return {"row_idx": state["row_idx"] + 1}

# --- CONSTRUCCIÓN DEL GRAFO ---
graph = StateGraph(AgentState)

graph.add_node("cargar_contexto", cargar_contexto)
graph.add_node("cargar_csv", cargar_csv)
graph.add_node("seleccionar_fila", seleccionar_fila)
graph.add_node("llamar_llm", nodo_llamar_llm)
graph.add_node("calculo", calculo_matematico)
graph.add_node("guardar", guardar_resultados)
graph.add_node("avanzar", avanzar_fila)

graph.add_edge(START, "cargar_contexto")
graph.add_edge("cargar_contexto", "cargar_csv")
graph.add_edge("cargar_csv", "seleccionar_fila")
graph.add_edge("seleccionar_fila", "llamar_llm")
graph.add_edge("llamar_llm", "calculo")
graph.add_edge("calculo", "guardar")
graph.add_edge("guardar", "avanzar")

# Condición para seguir procesando
def condicion(state: AgentState) -> str:
    if state["row_idx"] < len(state["df"]):
        return "seleccionar_fila"
    return END

graph.add_conditional_edges("avanzar", condicion, {
    "seleccionar_fila": "seleccionar_fila",
    END: END
})

# Compilar agente
agent = graph.compile()

# MAIN
def main():
    cwd = os.getcwd()
    initial_state = {
        "carpeta_contexto": os.path.join(cwd, "contexto"),
        "path_csv": os.path.join(cwd, "encuesta", "Ejemplo_CSV.csv"),
        "row_idx": 0,
        "df": pd.DataFrame()
    }

    final_state = agent.invoke(initial_state)

    output_path = os.path.join(cwd, "output", "resultado_final.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_state["df"].to_csv(output_path, index=False)
    print(f"✅ Proceso completado. Archivo guardado en: {output_path}")

if __name__ == "__main__":
    main()
