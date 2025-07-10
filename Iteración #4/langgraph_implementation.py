"""
Implementación sugerida con LangGraph para mejor orquestación de encuestas
"""

from typing import TypedDict, List, Dict, Any
from langgraph import StateGraph, END
import openai
from dataclasses import dataclass

class SurveyState(TypedDict):
    """Estado del workflow de encuesta"""
    profile: Dict[str, Any]
    questions: List[Dict[str, Any]]
    cultural_context: str
    responses: Dict[str, Any]
    validation_score: float
    retry_count: int

@dataclass
class SurveyWorkflowConfig:
    """Configuración del workflow"""
    max_retries: int = 2
    validation_threshold: float = 0.7
    model: str = "gpt-4"
    temperature: float = 0.7

def analyze_demographic_profile(state: SurveyState) -> SurveyState:
    """Analizar perfil demográfico para contexto"""
    profile = state["profile"]
    
    # Análisis demográfico profundo
    demographic_insights = {
        "generational_context": get_generational_context(profile["edad"]),
        "socioeconomic_context": get_nse_context(profile["nse"]),
        "regional_context": get_regional_context(profile["region"]),
        "cultural_markers": extract_cultural_markers(profile)
    }
    
    state["demographic_insights"] = demographic_insights
    return state

def build_cultural_context(state: SurveyState) -> SurveyState:
    """Construir contexto cultural específico"""
    profile = state["profile"]
    insights = state.get("demographic_insights", {})
    
    context = f"""
    CONTEXTO CULTURAL PERSONALIZADO:
    
    Perfil Demográfico:
    - {profile['nombre']}, {profile['edad']} años, NSE {profile['nse']}
    - Vive en {profile['ciudad']}, región {profile['region']}
    - {insights.get('generational_context', '')}
    
    Contexto Socioeconómico:
    - {insights.get('socioeconomic_context', '')}
    
    Contexto Regional:
    - {insights.get('regional_context', '')}
    
    Marcadores Culturales:
    - {insights.get('cultural_markers', '')}
    
    INSTRUCCIONES:
    Responde como si fueras exactamente esta persona, considerando:
    1. Tu situación socioeconómica específica
    2. Las preocupaciones típicas de tu región
    3. Tu generación y experiencias de vida
    4. El contexto político actual de Perú 2024
    """
    
    state["cultural_context"] = context
    return state

def generate_ai_responses(state: SurveyState) -> SurveyState:
    """Generar respuestas usando OpenAI con contexto"""
    
    client = openai.OpenAI()
    
    prompt = build_comprehensive_prompt(
        state["profile"],
        state["cultural_context"], 
        state["questions"]
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un encuestado auténtico que responde coherentemente desde tu perspectiva personal."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        responses_text = response.choices[0].message.content
        responses_json = parse_responses(responses_text)
        
        state["responses"] = responses_json
        state["raw_response"] = responses_text
        
    except Exception as e:
        state["error"] = str(e)
        state["responses"] = {}
    
    return state

def validate_coherence(state: SurveyState) -> SurveyState:
    """Validar coherencia de respuestas"""
    responses = state.get("responses", {})
    profile = state["profile"]
    
    validation_score = 0.0
    validation_details = []
    
    # 1. Coherencia demográfica
    demo_score = validate_demographic_coherence(responses, profile)
    validation_score += demo_score * 0.3
    validation_details.append(f"Coherencia demográfica: {demo_score:.2f}")
    
    # 2. Coherencia interna
    internal_score = validate_internal_coherence(responses)
    validation_score += internal_score * 0.4
    validation_details.append(f"Coherencia interna: {internal_score:.2f}")
    
    # 3. Realismo cultural
    cultural_score = validate_cultural_realism(responses, profile)
    validation_score += cultural_score * 0.3
    validation_details.append(f"Realismo cultural: {cultural_score:.2f}")
    
    state["validation_score"] = validation_score
    state["validation_details"] = validation_details
    
    return state

def should_retry(state: SurveyState) -> str:
    """Decidir si reintentar o terminar"""
    config = SurveyWorkflowConfig()
    
    validation_score = state.get("validation_score", 0.0)
    retry_count = state.get("retry_count", 0)
    
    if validation_score < config.validation_threshold and retry_count < config.max_retries:
        state["retry_count"] = retry_count + 1
        return "generate_ai_responses"  # Reintentar
    else:
        return END  # Terminar

def create_survey_workflow() -> StateGraph:
    """Crear workflow completo de encuesta"""
    
    workflow = StateGraph(SurveyState)
    
    # Agregar nodos
    workflow.add_node("analyze_profile", analyze_demographic_profile)
    workflow.add_node("build_context", build_cultural_context)
    workflow.add_node("generate_responses", generate_ai_responses)
    workflow.add_node("validate_responses", validate_coherence)
    
    # Definir flujo
    workflow.set_entry_point("analyze_profile")
    workflow.add_edge("analyze_profile", "build_context")
    workflow.add_edge("build_context", "generate_responses")
    workflow.add_edge("generate_responses", "validate_responses")
    
    # Lógica condicional para reintentos
    workflow.add_conditional_edges(
        "validate_responses",
        should_retry,
        {
            "generate_responses": "generate_responses",
            END: END
        }
    )
    
    return workflow.compile()

# Funciones auxiliares
def get_generational_context(edad: int) -> str:
    """Contexto generacional específico"""
    if edad < 25:
        return "Generación Z: nativo digital, activismo social, preocupación ambiental"
    elif edad < 40:
        return "Millennial: crisis económica, tecnología, balance trabajo-vida"
    elif edad < 55:
        return "Generación X: estabilidad laboral, familia, pragmatismo político"
    else:
        return "Baby Boomer: experiencia política, valores tradicionales, seguridad social"

def get_nse_context(nse: str) -> str:
    """Contexto socioeconómico específico"""
    contexts = {
        "A": "Alta capacidad adquisitiva, acceso a educación privada, inversiones, viajes",
        "B": "Clase media-alta, profesionales, aspiraciones de crecimiento, estabilidad",
        "C": "Clase media, empleados, comerciantes, preocupación por ingresos",
        "D": "Clase trabajadora, empleos informales, programas sociales, supervivencia",
        "E": "Pobreza, dependencia de programas sociales, necesidades básicas"
    }
    return contexts.get(nse, "Contexto general")

def get_regional_context(region: str) -> str:
    """Contexto regional específico"""
    contexts = {
        "Lima": "Centralismo, diversidad cultural, oportunidades laborales, tráfico",
        "Costa": "Agricultura, pesca, conexión con Lima, desarrollo regional",
        "Sierra": "Tradición andina, minería, descentralización, identidad cultural",
        "Selva": "Recursos naturales, conectividad, desarrollo sostenible"
    }
    return contexts.get(region, "Contexto general")

# Ejemplo de uso
async def execute_survey_with_langgraph(profile: Dict[str, Any], questions: List[Dict[str, Any]]):
    """Ejecutar encuesta usando LangGraph"""
    
    workflow = create_survey_workflow()
    
    initial_state = SurveyState(
        profile=profile,
        questions=questions,
        cultural_context="",
        responses={},
        validation_score=0.0,
        retry_count=0
    )
    
    # Ejecutar workflow
    final_state = await workflow.ainvoke(initial_state)
    
    return {
        "responses": final_state["responses"],
        "validation_score": final_state["validation_score"],
        "validation_details": final_state.get("validation_details", []),
        "cultural_context": final_state["cultural_context"]
    }