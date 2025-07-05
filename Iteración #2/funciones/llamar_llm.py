from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import os

# Inicializar el modelo LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,
    max_tokens=1000,
    streaming=False,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Leer el prompt base desde archivo
def cargar_prompt_base() -> str:
    ruta = os.path.join(os.getcwd(), "prompts", "prompt_perú2026.txt")
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"❌ No se encontró el archivo de prompt: {ruta}")
    with open(ruta, encoding="utf-8") as f:
        return f.read().strip()

# Cargar solo una vez al inicio
PROMPT_BASE = cargar_prompt_base()

# Construir el prompt dinámico y llamar al LLM
def llamar_llm(context: str, datos_fila: dict) -> str:
    prompt = PROMPT_BASE.format(context=context, datos=datos_fila)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
