import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ✅ Para evitar problemas en macOS al generar gráficos
import matplotlib.pyplot as plt
from fpdf import FPDF

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# === 🧠 Estado del agente ===
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    csv_path: str

# === 🔧 Tool para graficar y generar PDF ===
@tool
def graficar_csv(csv_path: str) -> str:
    """
    Genera un PDF con gráficas de distribución por columna (excluyendo la primera).
    """
    df = pd.read_csv(csv_path)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for col in df.columns[1:]:  # Excluir ID_Encuestado
        plt.figure(figsize=(8, 4))
        df[col].value_counts().plot(kind='bar')
        plt.title(col)
        plt.xlabel("Valores únicos")
        plt.ylabel("Frecuencia")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        img_path = os.path.join(output_dir, f"{col}.png")
        plt.savefig(img_path)
        plt.close()

        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=col, ln=True)
        pdf.image(img_path, x=10, y=30, w=180)

    pdf_path = os.path.join(output_dir, "distribuciones.pdf")
    pdf.output(pdf_path)
    return f"✅ PDF generado con gráficas: {pdf_path}"

# === ⚙️ Configuración del modelo y herramientas ===
tools = [graficar_csv]
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=1000,
    api_key=os.getenv("OPENAI_API_KEY")
).bind_tools(tools)

# === 🔁 Nodo principal del modelo ===
def model_call(state: AgentState) -> AgentState:
    user_msg = state["messages"][-1]
    system_msg = HumanMessage(content=f"Ayúdame a graficar el CSV ubicado en: {state['csv_path']}")
    response = model.invoke([system_msg, user_msg])
    return {"messages": [response], "csv_path": state["csv_path"]}

# === 🧭 Decisión del flujo ===
def should_continue(state: AgentState):
    last_msg = state["messages"][-1]
    if not last_msg.tool_calls:
        return "end"
    return "continue"

# === 🕸️ Construcción del grafo LangGraph ===
graph = StateGraph(AgentState)
graph.add_node("model", model_call)
graph.add_node("tools", ToolNode(tools=tools))
graph.set_entry_point("model")
graph.add_conditional_edges("model", should_continue, {
    "end": END,
    "continue": "tools"
})
graph.add_edge("tools", "model")
app = graph.compile()

# === 🚀 Ejecución principal ===
if __name__ == "__main__":
    state = {
        "messages": [HumanMessage(content="Haz un gráfico por cada pregunta del archivo")],
        "csv_path": "encuesta/test_panel_1.csv"
    }
    result = app.invoke(state)
    print(result["messages"][-1].content)
