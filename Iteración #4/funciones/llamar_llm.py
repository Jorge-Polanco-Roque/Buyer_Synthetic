"""
Funciones para llamar a modelos de lenguaje (LLM).
Soporte para OpenAI GPT y otros modelos.
"""

import openai
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import time

# Cargar variables de entorno
load_dotenv()

class ConfiguracionLLM:
    """Configuración para modelos LLM"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.modelo_default = os.getenv("DEFAULT_MODEL", "gpt-4")
        self.temperatura_default = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens_default = int(os.getenv("MAX_TOKENS", "2000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Configurar OpenAI
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            print("⚠️  OPENAI_API_KEY no encontrada en variables de entorno")

config = ConfiguracionLLM()

def llamar_llm_directo(
    prompt: str, 
    modelo: str = None,
    temperatura: float = None,
    max_tokens: int = None,
    reintentos: int = 3
) -> str:
    """
    Llama directamente a un modelo LLM con el prompt dado.
    
    Args:
        prompt: Texto del prompt
        modelo: Modelo a usar (por defecto gpt-4)
        temperatura: Creatividad del modelo (0.0 - 1.0)
        max_tokens: Máximo número de tokens
        reintentos: Número de reintentos en caso de error
        
    Returns:
        str: Respuesta del modelo
    """
    
    # Usar valores por defecto si no se especifican
    modelo = modelo or config.modelo_default
    temperatura = temperatura if temperatura is not None else config.temperatura_default
    max_tokens = max_tokens or config.max_tokens_default
    
    if not config.openai_api_key:
        return "Error: No se encontró API key de OpenAI"
    
    for intento in range(reintentos):
        try:
            if config.debug:
                print(f"🔄 Intento {intento + 1}: Llamando a {modelo}")
                print(f"📝 Prompt: {prompt[:200]}...")
            
            response = openai.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperatura,
                max_tokens=max_tokens
            )
            
            resultado = response.choices[0].message.content
            
            if config.debug:
                print(f"✅ Respuesta recibida: {len(resultado)} caracteres")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error en intento {intento + 1}: {str(e)}")
            if intento < reintentos - 1:
                time.sleep(2 ** intento)  # Backoff exponencial
            else:
                return f"Error después de {reintentos} intentos: {str(e)}"

def procesar_con_llm(fila_datos: Dict[str, Any], contexto: str = "") -> Dict[str, Any]:
    """
    Procesa una fila de datos con LLM usando contexto.
    
    Args:
        fila_datos: Datos de la fila a procesar
        contexto: Contexto adicional para el LLM
        
    Returns:
        Dict: Resultado del procesamiento
    """
    
    # Construir prompt contextualizado
    prompt = f"""
{contexto}

Tienes los siguientes datos de una persona:
{json.dumps(fila_datos, indent=2, ensure_ascii=False)}

Basándote en estos datos y el contexto proporcionado, responde las siguientes preguntas:

1. ¿Cuál crees que sería la principal preocupación de esta persona en este momento?
2. ¿Cómo calificaría la situación económica actual del país en una escala del 1 al 10?
3. ¿Qué factor sería más importante para esta persona al tomar una decisión de compra importante?
4. ¿Cuál sería su nivel de confianza en las instituciones políticas actuales? (1-10)
5. ¿Qué aspiraciones tendría para los próximos 5 años?

Responde en formato JSON con la siguiente estructura:
{{
    "preocupacion_principal": "respuesta aquí",
    "calificacion_economia": 7,
    "factor_compra": "respuesta aquí", 
    "confianza_instituciones": 4,
    "aspiraciones": "respuesta aquí",
    "perfil_comportamental": "resumen del perfil de comportamiento",
    "confianza_respuesta": 0.85
}}

Importante: Responde como si fueras realmente esta persona, considerando su edad, ubicación, y contexto socioeconómico.
"""
    
    respuesta_texto = llamar_llm_directo(prompt)
    
    # Intentar parsear JSON
    try:
        respuesta_json = json.loads(respuesta_texto)
        return respuesta_json
    except json.JSONDecodeError:
        # Si falla el JSON, extraer información básica
        return {
            "respuesta_cruda": respuesta_texto,
            "error": "No se pudo parsear JSON",
            "confianza_respuesta": 0.3
        }

def procesar_cuestionario_estructurado(
    perfil: Dict[str, Any], 
    cuestionario: Dict[str, Any],
    contexto: str = ""
) -> Dict[str, Any]:
    """
    Procesa un cuestionario estructurado completo.
    
    Args:
        perfil: Perfil de la persona
        cuestionario: Estructura del cuestionario
        contexto: Contexto adicional
        
    Returns:
        Dict: Respuestas del cuestionario
    """
    
    # Construir prompt para cuestionario completo
    prompt = f"""
{contexto}

Eres una persona con el siguiente perfil:
{json.dumps(perfil, indent=2, ensure_ascii=False)}

Responde el siguiente cuestionario como si fueras realmente esta persona:

{json.dumps(cuestionario, indent=2, ensure_ascii=False)}

Instrucciones:
- Responde desde tu perspectiva personal basada en tu perfil
- Sé coherente en todas tus respuestas
- Usa un lenguaje natural y auténtico
- Incluye matices y dudas cuando sea apropiado
- Considera tu contexto socioeconómico y cultural

Responde en formato JSON manteniendo la estructura del cuestionario pero con tus respuestas.
"""
    
    respuesta_texto = llamar_llm_directo(prompt, max_tokens=3000)
    
    try:
        respuesta_json = json.loads(respuesta_texto)
        return respuesta_json
    except json.JSONDecodeError:
        return {
            "respuesta_cruda": respuesta_texto,
            "error": "No se pudo parsear JSON del cuestionario",
            "confianza_respuesta": 0.2
        }

def validar_respuesta_json(respuesta: str, esquema_esperado: Dict = None) -> Dict[str, Any]:
    """
    Valida y corrige respuestas JSON del LLM.
    
    Args:
        respuesta: Respuesta del LLM
        esquema_esperado: Esquema JSON esperado
        
    Returns:
        Dict: Respuesta validada
    """
    
    try:
        # Intentar parsear JSON
        datos = json.loads(respuesta)
        
        # Validar esquema si se proporciona
        if esquema_esperado:
            for campo_requerido in esquema_esperado.get("required", []):
                if campo_requerido not in datos:
                    print(f"⚠️  Campo requerido faltante: {campo_requerido}")
        
        return {
            "valido": True,
            "datos": datos,
            "error": None
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {str(e)}")
        
        # Intentar extraer JSON de texto con formato mixto
        try:
            # Buscar JSON entre ```json y ```
            inicio = respuesta.find('```json')
            if inicio != -1:
                fin = respuesta.find('```', inicio + 7)
                if fin != -1:
                    json_texto = respuesta[inicio + 7:fin]
                    datos = json.loads(json_texto)
                    return {
                        "valido": True,
                        "datos": datos,
                        "error": "JSON extraído de texto mixto"
                    }
        except:
            pass
        
        return {
            "valido": False,
            "datos": {"respuesta_cruda": respuesta},
            "error": f"Error JSON: {str(e)}"
        }

def generar_variaciones_respuesta(
    prompt_base: str, 
    num_variaciones: int = 3,
    temperatura_base: float = 0.7
) -> List[str]:
    """
    Genera múltiples variaciones de una respuesta para aumentar diversidad.
    
    Args:
        prompt_base: Prompt base
        num_variaciones: Número de variaciones
        temperatura_base: Temperatura base
        
    Returns:
        List[str]: Lista de variaciones
    """
    
    variaciones = []
    
    for i in range(num_variaciones):
        # Variar la temperatura para cada variación
        temperatura = temperatura_base + (i * 0.1)
        
        # Agregar variación al prompt
        prompt_variado = f"{prompt_base}\n\nVariación {i+1}: Proporciona una perspectiva ligeramente diferente pero coherente."
        
        respuesta = llamar_llm_directo(prompt_variado, temperatura=temperatura)
        variaciones.append(respuesta)
    
    return variaciones

if __name__ == "__main__":
    # Ejemplo de uso
    print("🧠 Probando funciones LLM...")
    
    # Ejemplo simple
    respuesta = llamar_llm_directo("¿Cuál es la capital de Perú?")
    print(f"Respuesta: {respuesta}")
    
    # Ejemplo con datos
    datos_ejemplo = {
        "nombre": "María",
        "edad": 32,
        "ciudad": "Lima",
        "ocupacion": "Profesional"
    }
    
    resultado = procesar_con_llm(datos_ejemplo, "Contexto de encuesta política en Perú")
    print(f"Resultado procesado: {resultado}")