"""
Agente principal que orquesta el flujo de procesamiento de encuestas.
Utiliza LangGraph para manejar el estado y el flujo de trabajo.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
import json
import os
import sys

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from funciones.leer_contexto import cargar_contexto
from funciones.llamar_llm import procesar_con_llm
from funciones.llenar_csv import guardar_resultado
from funciones.calculo_matematico import calcular_operacion

# Estado del grafo
class EstadoEncuesta:
    """Clase para manejar el estado de la encuesta"""
    def __init__(self):
        self.datos_entrada: pd.DataFrame = None
        self.fila_actual: int = 0
        self.contexto: str = ""
        self.resultados: List[Dict] = []
        self.errores: List[str] = []

# Funciones del grafo
def cargar_datos(estado: Dict[str, Any]) -> Dict[str, Any]:
    """Carga los datos de entrada desde CSV"""
    try:
        archivo_csv = Path("encuesta/datos_entrada.csv")
        if not archivo_csv.exists():
            # Crear archivo de ejemplo si no existe
            crear_datos_ejemplo()
        
        df = pd.read_csv(archivo_csv)
        estado["datos_entrada"] = df
        estado["total_filas"] = len(df)
        estado["fila_actual"] = 0
        estado["resultados"] = []
        
        print(f"✅ Datos cargados: {len(df)} filas")
        return estado
        
    except Exception as e:
        estado["errores"] = [f"Error cargando datos: {str(e)}"]
        return estado

def cargar_contexto_sistema(estado: Dict[str, Any]) -> Dict[str, Any]:
    """Carga el contexto del sistema"""
    try:
        contexto = cargar_contexto()
        estado["contexto"] = contexto
        print("✅ Contexto cargado")
        return estado
        
    except Exception as e:
        estado["errores"] = estado.get("errores", []) + [f"Error cargando contexto: {str(e)}"]
        return estado

def procesar_fila(estado: Dict[str, Any]) -> Dict[str, Any]:
    """Procesa una fila individual"""
    try:
        df = estado["datos_entrada"]
        fila_idx = estado["fila_actual"]
        
        if fila_idx >= len(df):
            estado["procesamiento_completo"] = True
            return estado
        
        fila = df.iloc[fila_idx]
        contexto = estado["contexto"]
        
        # Procesar con LLM
        respuesta_llm = procesar_con_llm(fila, contexto)
        
        # Realizar cálculos matemáticos si es necesario
        if "valor_a" in fila and "valor_b" in fila:
            resultado_matematico = calcular_operacion(fila["valor_a"], fila["valor_b"])
        else:
            resultado_matematico = None
        
        # Guardar resultado
        resultado = {
            "fila_original": fila.to_dict(),
            "respuesta_llm": respuesta_llm,
            "calculo_matematico": resultado_matematico,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        estado["resultados"].append(resultado)
        estado["fila_actual"] += 1
        
        print(f"✅ Procesada fila {fila_idx + 1}/{len(df)}")
        return estado
        
    except Exception as e:
        error_msg = f"Error procesando fila {estado['fila_actual']}: {str(e)}"
        estado["errores"] = estado.get("errores", []) + [error_msg]
        estado["fila_actual"] += 1
        return estado

def verificar_completion(estado: Dict[str, Any]) -> str:
    """Verifica si el procesamiento está completo"""
    if estado.get("procesamiento_completo", False):
        return "guardar_resultados"
    elif estado["fila_actual"] >= estado.get("total_filas", 0):
        return "guardar_resultados"
    else:
        return "procesar_fila"

def guardar_resultados_finales(estado: Dict[str, Any]) -> Dict[str, Any]:
    """Guarda los resultados finales"""
    try:
        resultados = estado["resultados"]
        guardar_resultado(resultados)
        print("✅ Resultados guardados")
        return estado
        
    except Exception as e:
        estado["errores"] = estado.get("errores", []) + [f"Error guardando resultados: {str(e)}"]
        return estado

def crear_datos_ejemplo():
    """Crea un archivo de datos de ejemplo"""
    datos_ejemplo = {
        "id": [1, 2, 3, 4, 5],
        "nombre": ["Juan", "María", "Carlos", "Ana", "Luis"],
        "edad": [25, 32, 28, 45, 38],
        "ciudad": ["Lima", "Arequipa", "Trujillo", "Cusco", "Piura"],
        "valor_a": [10, 15, 8, 12, 20],
        "valor_b": [5, 8, 3, 7, 10]
    }
    
    df = pd.DataFrame(datos_ejemplo)
    os.makedirs("encuesta", exist_ok=True)
    df.to_csv("encuesta/datos_entrada.csv", index=False)
    print("✅ Archivo de ejemplo creado: encuesta/datos_entrada.csv")

def ejecutar_flujo_principal():
    """Ejecuta el flujo principal del sistema"""
    
    # Crear el grafo de estado
    workflow = StateGraph(dict)
    
    # Agregar nodos
    workflow.add_node("cargar_datos", cargar_datos)
    workflow.add_node("cargar_contexto", cargar_contexto_sistema)
    workflow.add_node("procesar_fila", procesar_fila)
    workflow.add_node("guardar_resultados", guardar_resultados_finales)
    
    # Definir el flujo
    workflow.add_edge(START, "cargar_datos")
    workflow.add_edge("cargar_datos", "cargar_contexto")
    workflow.add_edge("cargar_contexto", "procesar_fila")
    workflow.add_conditional_edges(
        "procesar_fila",
        verificar_completion,
        {
            "procesar_fila": "procesar_fila",
            "guardar_resultados": "guardar_resultados"
        }
    )
    workflow.add_edge("guardar_resultados", END)
    
    # Compilar el grafo
    app = workflow.compile()
    
    # Ejecutar el flujo
    estado_inicial = {}
    resultado_final = app.invoke(estado_inicial)
    
    # Mostrar resumen
    if "errores" in resultado_final and resultado_final["errores"]:
        print("\n❌ Errores encontrados:")
        for error in resultado_final["errores"]:
            print(f"  - {error}")
    
    print(f"\n📊 Resumen del procesamiento:")
    print(f"  - Total filas procesadas: {resultado_final.get('fila_actual', 0)}")
    print(f"  - Resultados generados: {len(resultado_final.get('resultados', []))}")
    print(f"  - Errores: {len(resultado_final.get('errores', []))}")
    
    return resultado_final

if __name__ == "__main__":
    ejecutar_flujo_principal()