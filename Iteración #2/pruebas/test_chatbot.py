# Importaciones necesarias
from typing import TypedDict, List                 # Tipado para definir estructuras de datos
from langchain_core.messages import HumanMessage   # Tipo de mensaje enviado por el usuario
from langchain_openai import ChatOpenAI            # Cliente para interactuar con modelos de OpenAI vía LangChain
from langgraph.graph import StateGraph, START, END # Herramientas para definir flujos de agentes con LangGraph
from dotenv import load_dotenv                     # Permite cargar variables de entorno desde un archivo .env
import os                                          # Acceso a variables del sistema, como OPENAI_API_KEY

# Carga las variables definidas en el archivo .env (como OPENAI_API_KEY)
load_dotenv()

# Define el estado que usará el agente: una lista de mensajes humanos
class AgentState(TypedDict):
    messages: List[HumanMessage]

# Inicializa el modelo de lenguaje GPT-4o con parámetros definidos
llm = ChatOpenAI(
    model="gpt-4o",                        # Modelo a utilizar
    temperature=0.0,                       # Determinismo (0.0 = máxima consistencia)
    max_tokens=1000,                       # Límite máximo de tokens por respuesta
    streaming=True,                        # Permite recibir la respuesta mientras se genera
    #api_key=os.getenv("OPENAI_API_KEY")   # Clave privada extraída del entorno
    api_key=os.getenv("OPENAI_API_KEY")   # Clave privada extraída del entorno
)

# Nodo del grafo que procesa el estado invocando al modelo de lenguaje
def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])     # Envia los mensajes al LLM y obtiene la respuesta
    print(f"\nAI: {response.content}")           # Imprime la respuesta de la IA
    return state                                 # Retorna el estado sin modificar (respuesta solo se imprime)

# Construcción del grafo con LangGraph
graph = StateGraph(AgentState)
graph.add_node("process", process)               # Nodo principal que ejecuta la lógica
graph.add_edge(START, "process")                 # El flujo comienza en "START" y va a "process"
graph.add_edge("process", END)                   # Luego de procesar, el flujo termina en "END"
agent = graph.compile()                          # Compila el grafo en un agente ejecutable

# Loop principal que recibe entradas del usuario e invoca al agente
user_input = input("Enter: ")
while user_input != "exit":
    # Invoca al agente con un nuevo mensaje humano cada vez
    agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter: ")