"""
Generador de respuestas sintéticas para encuestas.
Utiliza LLM para simular respuestas de usuarios reales.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import sys

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from funciones.llamar_llm import llamar_llm_directo
from funciones.leer_contexto import cargar_contexto

class GeneradorPanelSintetico:
    """Genera respuestas sintéticas para encuestas"""
    
    def __init__(self, contexto_archivo: str = None):
        self.contexto = cargar_contexto(contexto_archivo) if contexto_archivo else ""
        self.modelo = "gpt-4"
        self.temperatura = 0.7
        
    def generar_respuesta_individual(self, perfil: Dict[str, Any], pregunta: str) -> Dict[str, Any]:
        """Genera una respuesta individual para una pregunta"""
        
        prompt = f"""
        Contexto: {self.contexto}
        
        Eres una persona con el siguiente perfil:
        {json.dumps(perfil, indent=2, ensure_ascii=False)}
        
        Pregunta: {pregunta}
        
        Responde como si fueras realmente esta persona, considerando:
        - Tu edad, ubicación y contexto socioeconómico
        - Tus posibles experiencias y perspectivas
        - Un estilo de respuesta natural y coherente
        
        Responde en formato JSON con la estructura:
        {{
            "respuesta": "tu respuesta aquí",
            "confianza": 0.8,
            "razonamiento": "breve explicación del por qué respondiste así"
        }}
        """
        
        try:
            respuesta = llamar_llm_directo(prompt, self.modelo, self.temperatura)
            return json.loads(respuesta)
        except Exception as e:
            return {
                "respuesta": "Error al generar respuesta",
                "confianza": 0.0,
                "razonamiento": f"Error: {str(e)}"
            }
    
    def generar_panel_completo(self, perfiles: List[Dict], preguntas: List[str]) -> pd.DataFrame:
        """Genera un panel completo de respuestas"""
        
        resultados = []
        
        for i, perfil in enumerate(perfiles):
            print(f"Procesando perfil {i+1}/{len(perfiles)}: {perfil.get('nombre', 'Sin nombre')}")
            
            respuestas_perfil = {"perfil_id": i+1}
            respuestas_perfil.update(perfil)
            
            for j, pregunta in enumerate(preguntas):
                print(f"  Pregunta {j+1}/{len(preguntas)}")
                
                respuesta = self.generar_respuesta_individual(perfil, pregunta)
                respuestas_perfil[f"pregunta_{j+1}_respuesta"] = respuesta.get("respuesta", "")
                respuestas_perfil[f"pregunta_{j+1}_confianza"] = respuesta.get("confianza", 0.0)
                respuestas_perfil[f"pregunta_{j+1}_razonamiento"] = respuesta.get("razonamiento", "")
            
            resultados.append(respuestas_perfil)
        
        return pd.DataFrame(resultados)
    
    def generar_cuestionario_estructurado(self, esquema_cuestionario: Dict) -> pd.DataFrame:
        """Genera respuestas basadas en un esquema de cuestionario estructurado"""
        
        perfiles = esquema_cuestionario.get("perfiles", [])
        bloques = esquema_cuestionario.get("bloques", [])
        
        resultados = []
        
        for i, perfil in enumerate(perfiles):
            print(f"Procesando perfil {i+1}/{len(perfiles)}: {perfil.get('nombre', 'Sin nombre')}")
            
            respuestas_perfil = {"perfil_id": i+1}
            respuestas_perfil.update(perfil)
            
            for bloque in bloques:
                bloque_nombre = bloque.get("nombre", "Sin nombre")
                preguntas = bloque.get("preguntas", [])
                
                print(f"  Bloque: {bloque_nombre}")
                
                for j, pregunta_data in enumerate(preguntas):
                    pregunta_texto = pregunta_data.get("pregunta", "")
                    pregunta_tipo = pregunta_data.get("tipo", "abierta")
                    opciones = pregunta_data.get("opciones", [])
                    
                    # Adaptar prompt según tipo de pregunta
                    if pregunta_tipo == "multiple" and opciones:
                        prompt_adicional = f"Opciones disponibles: {', '.join(opciones)}"
                    elif pregunta_tipo == "escala":
                        prompt_adicional = "Responde con un número del 1 al 10"
                    else:
                        prompt_adicional = ""
                    
                    pregunta_completa = f"{pregunta_texto}. {prompt_adicional}"
                    
                    respuesta = self.generar_respuesta_individual(perfil, pregunta_completa)
                    
                    # Clave única para cada pregunta
                    clave_base = f"{bloque_nombre.lower().replace(' ', '_')}_p{j+1}"
                    respuestas_perfil[f"{clave_base}_respuesta"] = respuesta.get("respuesta", "")
                    respuestas_perfil[f"{clave_base}_confianza"] = respuesta.get("confianza", 0.0)
            
            resultados.append(respuestas_perfil)
        
        return pd.DataFrame(resultados)

def ejemplo_uso():
    """Ejemplo de uso del generador"""
    
    # Crear generador
    generador = GeneradorPanelSintetico()
    
    # Perfiles de ejemplo
    perfiles = [
        {
            "nombre": "Ana García",
            "edad": 28,
            "ciudad": "Lima",
            "nse": "B",
            "ocupacion": "Profesional",
            "ingresos": "3000-5000"
        },
        {
            "nombre": "Carlos Mendoza",
            "edad": 45,
            "ciudad": "Arequipa", 
            "nse": "C",
            "ocupacion": "Comerciante",
            "ingresos": "1500-3000"
        }
    ]
    
    # Preguntas de ejemplo
    preguntas = [
        "¿Cuál es tu mayor preocupación económica actual?",
        "¿Cómo calificarías la situación del país en una escala del 1 al 10?",
        "¿Qué factor es más importante al comprar un producto?"
    ]
    
    # Generar panel
    panel = generador.generar_panel_completo(perfiles, preguntas)
    
    # Guardar resultados
    output_path = Path("encuesta/test_panel_generado.csv")
    output_path.parent.mkdir(exist_ok=True)
    panel.to_csv(output_path, index=False)
    
    print(f"✅ Panel generado y guardado en: {output_path}")
    print(f"📊 Dimensiones: {panel.shape}")
    
    return panel

if __name__ == "__main__":
    ejemplo_uso()