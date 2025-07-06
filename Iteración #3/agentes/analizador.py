import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from typing import TypedDict
import unicodedata

from langgraph.graph import StateGraph
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# === 🧠 Estado del agente ===
class AgentState(TypedDict):
    csv_path: str
    pdf_resultado: str

# === 🔧 Tool para graficar y generar PDF ===
@tool
def graficar_csv(csv_path: str) -> str:
    """
    Genera un PDF con gráficas de barras por columna (excepto la primera) de un CSV.
    El PDF se guarda en la carpeta 'output'.
    """
    if not os.path.exists(csv_path):
        return f"❌ El archivo CSV '{csv_path}' no existe."

    df = pd.read_csv(csv_path)
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=12)

    def normalizar_texto(texto: str) -> str:
        return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode()

    for col in df.columns[1:]:  # Excluir columna ID
        plt.figure(figsize=(8, 4))
        df[col].value_counts().plot(kind='bar')
        plt.title(col)
        plt.xlabel("Valores únicos")
        plt.ylabel("Frecuencia")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        pdf.add_page()
        safe_text = normalizar_texto(col)
        pdf.cell(200, 10, text=safe_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.image(buf, x=10, y=30, w=180)

    pdf_path = os.path.join(output_dir, "distribuciones.pdf")
    pdf.output(pdf_path)
    return f"✅ PDF generado con gráficas: {pdf_path}"

# === 🧠 Nodo que ejecuta la tool directamente ===
def ejecutar_grafica(state: AgentState) -> AgentState:
    resultado = graficar_csv.invoke({"csv_path": state["csv_path"]})
    return {"csv_path": state["csv_path"], "pdf_resultado": resultado}

# === 🕸️ Construcción de LangGraph ===
graph = StateGraph(AgentState)
graph.add_node("graficador", ejecutar_grafica)
graph.set_entry_point("graficador")
graph.set_finish_point("graficador")
app = graph.compile()

# === 🚀 Ejecución ===
if __name__ == "__main__":
    result = app.invoke({
        "csv_path": "encuesta/test_panel_1.csv",
        "pdf_resultado": ""
    })
    print(result["pdf_resultado"])
