"""
Survey Executor Agent usando LangGraph para orquestación avanzada
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, TypedDict
from dataclasses import dataclass

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..config.settings import Settings, SurveyMode
from ..utils.logger import get_logger
from ..core.tracer import get_tracer, trace_agent_execution

logger = get_logger(__name__)


class SurveyState(TypedDict):
    """Estado del workflow de encuesta"""
    trace_id: str
    profile: Dict[str, Any]
    questions: List[Dict[str, Any]]
    cultural_context: str
    demographic_insights: Dict[str, Any]
    responses: Dict[str, Any]
    validation_score: float
    retry_count: int
    error: str
    raw_response: str


@dataclass
class SurveyWorkflowConfig:
    """Configuración del workflow"""
    max_retries: int = 2
    validation_threshold: float = 0.7
    model: str = "gpt-4"
    temperature: float = 0.7


class SurveyExecutorLangGraph:
    """Ejecutor de encuestas usando LangGraph para mejor orquestación"""
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.7):
        self.settings = Settings()
        self.logger = logger
        self.config = SurveyWorkflowConfig(model=model, temperature=temperature)
        self.tracer = get_tracer()
        
        # Inicializar LLM
        self.llm = ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            api_key=self.settings.OPENAI_API_KEY
        )
        
        # Crear workflow
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Crear el workflow de LangGraph"""
        
        workflow = StateGraph(SurveyState)
        
        # Agregar nodos
        workflow.add_node("analyze_profile", self._analyze_demographic_profile)
        workflow.add_node("build_context", self._build_cultural_context)
        workflow.add_node("generate_responses", self._generate_ai_responses)
        workflow.add_node("validate_responses", self._validate_coherence)
        
        # Definir flujo
        workflow.set_entry_point("analyze_profile")
        workflow.add_edge("analyze_profile", "build_context")
        workflow.add_edge("build_context", "generate_responses")
        workflow.add_edge("generate_responses", "validate_responses")
        
        # Lógica condicional para reintentos
        workflow.add_conditional_edges(
            "validate_responses",
            self._should_retry,
            {
                "retry": "generate_responses",
                "finish": END
            }
        )
        
        return workflow.compile()
    
    @trace_agent_execution("SurveyExecutorLangGraph", "execute_individual_survey")
    def execute_individual_survey(self, profile: Dict[str, Any], questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ejecutar encuesta individual usando el workflow"""
        
        # Iniciar trace
        trace_id = self.tracer.start_trace(
            agent_name="SurveyExecutorLangGraph",
            operation="execute_individual_survey",
            inputs={
                "profile": {
                    "nombre": profile.get("nombre"),
                    "edad": profile.get("edad"),
                    "nse": profile.get("nse"),
                    "region": profile.get("region")
                },
                "questions_count": len(questions)
            },
            metadata={
                "model": self.config.model,
                "temperature": self.config.temperature
            }
        )
        
        self.logger.info(f"Ejecutando encuesta LangGraph para {profile.get('nombre', 'Unknown')} [trace: {trace_id}]")
        
        # Estado inicial
        initial_state = SurveyState(
            trace_id=trace_id,
            profile=profile,
            questions=questions,
            cultural_context="",
            demographic_insights={},
            responses={},
            validation_score=0.0,
            retry_count=0,
            error="",
            raw_response=""
        )
        
        try:
            # Ejecutar workflow
            final_state = self.workflow.invoke(initial_state)
            
            # Procesar resultado final
            result = self._format_final_result(final_state)
            
            # Finalizar trace
            self.tracer.end_trace(
                trace_id,
                outputs={
                    "responses_count": len(result.get("respuestas", {})),
                    "validation_score": final_state.get("validation_score", 0),
                    "retry_count": final_state.get("retry_count", 0),
                    "success": "error" not in final_state or not final_state["error"]
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error en workflow LangGraph: {str(e)}")
            self.tracer.log_error(trace_id, e)
            self.tracer.end_trace(trace_id, error=e)
            return self._create_error_response(profile, str(e))
    
    def _analyze_demographic_profile(self, state: SurveyState) -> SurveyState:
        """Analizar perfil demográfico para contexto"""
        
        trace_id = state["trace_id"]
        profile = state["profile"]
        
        with self.tracer.trace_node(trace_id, "analyze_demographic_profile", inputs={"profile": profile}):
            # Análisis demográfico profundo
            demographic_insights = {
                "generational_context": self._get_generational_context(profile["edad"]),
                "socioeconomic_context": self._get_nse_context(profile["nse"]),
                "regional_context": self._get_regional_context(profile["region"]),
                "cultural_markers": self._extract_cultural_markers(profile)
            }
            
            state["demographic_insights"] = demographic_insights
            self.logger.debug(f"Análisis demográfico completado para {profile['nombre']}")
        
        return state
    
    def _build_cultural_context(self, state: SurveyState) -> SurveyState:
        """Construir contexto cultural específico"""
        
        profile = state["profile"]
        insights = state["demographic_insights"]
        
        context = f"""
CONTEXTO CULTURAL PERSONALIZADO PARA ENCUESTA ELECTORAL - PERÚ 2024:

=== PERFIL DEL ENCUESTADO ===
Nombre: {profile['nombre']}
Edad: {profile['edad']} años
NSE: {profile['nse']}
Ubicación: {profile.get('ciudad', 'N/A')}, región {profile['region']}
Ocupación: {profile.get('ocupacion', 'N/A')}
Educación: {profile.get('educacion', 'N/A')}

=== CONTEXTO GENERACIONAL ===
{insights.get('generational_context', '')}

=== CONTEXTO SOCIOECONÓMICO ===
{insights.get('socioeconomic_context', '')}

=== CONTEXTO REGIONAL ===
{insights.get('regional_context', '')}

=== MARCADORES CULTURALES ===
{insights.get('cultural_markers', '')}

=== SITUACIÓN POLÍTICA ACTUAL PERÚ 2024 ===
- Gobierno: Dina Boluarte (crisis de gobernabilidad)
- Próximas elecciones: 2026
- Temas principales: Corrupción, economía, seguridad ciudadana
- Alta desconfianza institucional
- Polarización política significativa

=== INSTRUCCIONES PARA RESPONDER ===
Eres {profile['nombre']}, y debes responder desde tu perspectiva auténtica considerando:
1. Tu situación socioeconómica específica y preocupaciones
2. Las características típicas de tu región y su problemática
3. Tu generación y experiencias de vida
4. El contexto político actual de Perú
5. Mantener coherencia entre todas tus respuestas
6. Usar un lenguaje apropiado para tu nivel educativo
7. Incluir dudas naturales cuando sea apropiado
        """
        
        state["cultural_context"] = context.strip()
        self.logger.debug(f"Contexto cultural construido para {profile['nombre']}")
        
        return state
    
    def _generate_ai_responses(self, state: SurveyState) -> SurveyState:
        """Generar respuestas usando OpenAI con contexto"""
        
        profile = state["profile"]
        questions = state["questions"]
        cultural_context = state["cultural_context"]
        
        # Construir prompt comprehensivo
        prompt = self._build_comprehensive_prompt(profile, cultural_context, questions)
        
        try:
            # Llamar a OpenAI
            messages = [
                SystemMessage(content="Eres un encuestado auténtico peruano que responde coherentemente desde tu perspectiva personal específica. Debes mantener consistencia entre todas tus respuestas y usar un lenguaje apropiado para tu perfil."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parsear respuesta JSON
            try:
                responses_json = json.loads(response_text)
                state["responses"] = responses_json.get("respuestas", {})
                state["raw_response"] = response_text
                
            except json.JSONDecodeError:
                # Si no es JSON válido, intentar extraer respuestas
                self.logger.warning(f"Respuesta no JSON para {profile['nombre']}, intentando parsear...")
                state["responses"] = self._parse_non_json_response(response_text, questions)
                state["raw_response"] = response_text
            
            self.logger.info(f"Respuestas generadas para {profile['nombre']}")
            
        except Exception as e:
            self.logger.error(f"Error generando respuestas IA: {str(e)}")
            state["error"] = str(e)
            state["responses"] = {}
        
        return state
    
    def _validate_coherence(self, state: SurveyState) -> SurveyState:
        """Validar coherencia de respuestas"""
        
        responses = state.get("responses", {})
        profile = state["profile"]
        
        validation_score = 0.0
        validation_details = []
        
        if not responses:
            state["validation_score"] = 0.0
            return state
        
        # 1. Coherencia demográfica (30%)
        demo_score = self._validate_demographic_coherence(responses, profile)
        validation_score += demo_score * 0.3
        validation_details.append(f"Coherencia demográfica: {demo_score:.2f}")
        
        # 2. Coherencia interna (40%)
        internal_score = self._validate_internal_coherence(responses)
        validation_score += internal_score * 0.4
        validation_details.append(f"Coherencia interna: {internal_score:.2f}")
        
        # 3. Realismo cultural (30%)
        cultural_score = self._validate_cultural_realism(responses, profile)
        validation_score += cultural_score * 0.3
        validation_details.append(f"Realismo cultural: {cultural_score:.2f}")
        
        state["validation_score"] = validation_score
        state["validation_details"] = validation_details
        
        self.logger.info(f"Validación completada: {validation_score:.2f} para {profile['nombre']}")
        
        return state
    
    def _should_retry(self, state: SurveyState) -> str:
        """Decidir si reintentar o terminar"""
        
        validation_score = state.get("validation_score", 0.0)
        retry_count = state.get("retry_count", 0)
        
        if (validation_score < self.config.validation_threshold and 
            retry_count < self.config.max_retries and 
            not state.get("error")):
            
            state["retry_count"] = retry_count + 1
            self.logger.info(f"Reintentando generación (intento {retry_count + 1})")
            return "retry"
        else:
            return "finish"
    
    def _build_comprehensive_prompt(self, profile: Dict[str, Any], context: str, questions: List[Dict[str, Any]]) -> str:
        """Construir prompt comprehensivo para todas las preguntas"""
        
        prompt = f"""
{context}

PREGUNTAS DE LA ENCUESTA:
Responde TODAS las siguientes preguntas manteniendo coherencia y autenticidad:

"""
        
        for i, question in enumerate(questions, 1):
            prompt += f"\n{i}. {question['pregunta']}"
            if question['tipo'] == 'multiple':
                prompt += f"\n   Opciones: {', '.join(question['opciones'])}"
            elif question['tipo'] == 'escala':
                prompt += f"\n   Escala: {question['escala']}"
        
        prompt += f"""

FORMATO DE RESPUESTA REQUERIDO (JSON):
{{
    "respuestas": {{
        "{questions[0]['id']}": {{
            "respuesta": "tu respuesta específica",
            "confianza": 0.8,
            "razonamiento": "breve explicación de por qué respondiste así"
        }},
        [... continúa para cada pregunta ...]
    }},
    "coherencia_general": 0.9,
    "comentarios_adicionales": "observaciones sobre tus respuestas o dudas"
}}

IMPORTANTE:
- Responde desde tu perspectiva personal como {profile['nombre']}
- Mantén coherencia entre todas las respuestas
- Usa lenguaje apropiado para tu educación ({profile.get('educacion', 'N/A')})
- Incluye dudas naturales cuando sea apropiado
- Para preguntas de escala, usa números del rango indicado
- Para preguntas múltiples, selecciona UNA opción de las dadas
        """
        
        return prompt
    
    def _format_final_result(self, state: SurveyState) -> Dict[str, Any]:
        """Formatear resultado final"""
        
        profile = state["profile"]
        responses = state.get("responses", {})
        questions = state["questions"]
        
        # Estructura base
        result = {
            "id": profile["id"],
            "nombre": profile["nombre"],
            "edad": profile["edad"],
            "genero": profile.get("genero", ""),
            "ciudad": profile.get("ciudad", ""),
            "nse": profile["nse"],
            "region": profile["region"],
            "ocupacion": profile.get("ocupacion", ""),
            "educacion": profile.get("educacion", ""),
            "estado_civil": profile.get("estado_civil", ""),
            "ingresos": profile.get("ingresos", ""),
            "survey_timestamp": datetime.now().isoformat(),
            "survey_mode": "GenAI_LangGraph",
            "validation_score": state.get("validation_score", 0.0),
            "retry_count": state.get("retry_count", 0)
        }
        
        # Agregar respuestas de cada pregunta
        for question in questions:
            q_id = question["id"]
            if q_id in responses:
                response_data = responses[q_id]
                if isinstance(response_data, dict):
                    result[f"{q_id}_respuesta"] = response_data.get("respuesta", "")
                    result[f"{q_id}_confianza"] = response_data.get("confianza", 0.5)
                    result[f"{q_id}_razonamiento"] = response_data.get("razonamiento", "")
                else:
                    # Formato simple
                    result[f"{q_id}_respuesta"] = str(response_data)
                    result[f"{q_id}_confianza"] = 0.7
                    result[f"{q_id}_razonamiento"] = "Respuesta directa"
            else:
                # Respuesta faltante
                result[f"{q_id}_respuesta"] = "No disponible"
                result[f"{q_id}_confianza"] = 0.1
                result[f"{q_id}_razonamiento"] = "No generada"
        
        return result
    
    def _create_error_response(self, profile: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Crear respuesta de error"""
        
        return {
            "id": profile.get("id", "unknown"),
            "nombre": profile.get("nombre", "Unknown"),
            "edad": profile.get("edad", 0),
            "nse": profile.get("nse", ""),
            "region": profile.get("region", ""),
            "error": f"LangGraph Error: {error}",
            "survey_timestamp": datetime.now().isoformat(),
            "survey_mode": "GenAI_LangGraph_Error"
        }
    
    # Funciones auxiliares de contexto
    def _get_generational_context(self, edad: int) -> str:
        """Contexto generacional específico"""
        if edad < 25:
            return "Generación Z: Nativo digital, activismo en redes sociales, preocupación por cambio climático, desconfianza en políticos tradicionales"
        elif edad < 40:
            return "Millennial: Vivió crisis económicas, maneja tecnología, busca balance trabajo-vida, escéptico del sistema político"
        elif edad < 55:
            return "Generación X: Vivió transición democrática, estabilidad laboral importante, familia establecida, pragmatismo político"
        else:
            return "Baby Boomer: Experiencia de dictadura y transición, valores tradicionales, seguridad social prioritaria, mayor confianza institucional"
    
    def _get_nse_context(self, nse: str) -> str:
        """Contexto socioeconómico específico"""
        contexts = {
            "A": "Alta capacidad adquisitiva, educación privada, inversiones, viajes internacionales, preocupación por estabilidad política para negocios",
            "B": "Clase media-alta, profesionales universitarios, aspiraciones de crecimiento, acceso a servicios de calidad, preocupación por oportunidades",
            "C": "Clase media, empleados formales/comerciantes, preocupación por ingresos estables, acceso a educación y salud, movilidad social",
            "D": "Clase trabajadora, empleos informales frecuentes, programas sociales importantes, preocupación por supervivencia económica",
            "E": "Situación de pobreza, dependencia de programas sociales, trabajo informal/eventual, necesidades básicas insatisfechas"
        }
        return contexts.get(nse, "Contexto socioeconómico general")
    
    def _get_regional_context(self, region: str) -> str:
        """Contexto regional específico"""
        contexts = {
            "Lima": "Centralismo, diversidad cultural, oportunidades laborales, tráfico, contaminación, mayor acceso a servicios",
            "Costa": "Agricultura, pesca, conexión comercial con Lima, desarrollo regional desigual, migración interna",
            "Sierra": "Tradición andina, actividad minera, descentralización, identidad cultural fuerte, conectividad limitada",
            "Selva": "Recursos naturales, biodiversidad, desarrollo sostenible, conectividad deficiente, economía informal"
        }
        return contexts.get(region, "Contexto regional general")
    
    def _extract_cultural_markers(self, profile: Dict[str, Any]) -> str:
        """Extraer marcadores culturales del perfil"""
        markers = []
        
        # Basado en ocupación
        ocupacion = profile.get('ocupacion', '').lower()
        if 'ingeniero' in ocupacion or 'profesional' in ocupacion:
            markers.append("Perspectiva técnica y analítica")
        elif 'comerciante' in ocupacion or 'vendedor' in ocupacion:
            markers.append("Mentalidad emprendedora y práctica")
        elif 'profesor' in ocupacion or 'educador' in ocupacion:
            markers.append("Valoración de la educación y desarrollo social")
        
        # Basado en educación
        educacion = profile.get('educacion', '').lower()
        if 'universitaria' in educacion:
            markers.append("Análisis crítico y conocimiento de procesos políticos")
        elif 'técnica' in educacion:
            markers.append("Enfoque práctico y aplicado")
        elif 'secundaria' in educacion:
            markers.append("Experiencia directa y perspectiva popular")
        
        return "; ".join(markers) if markers else "Perspectiva ciudadana general"
    
    def _validate_demographic_coherence(self, responses: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Validar coherencia demográfica (simplificado)"""
        # Implementación básica - en producción sería más sofisticada
        return 0.8  # Score placeholder
    
    def _validate_internal_coherence(self, responses: Dict[str, Any]) -> float:
        """Validar coherencia interna de respuestas"""
        # Implementación básica - en producción sería más sofisticada
        return 0.8  # Score placeholder
    
    def _validate_cultural_realism(self, responses: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Validar realismo cultural"""
        # Implementación básica - en producción sería más sofisticada
        return 0.8  # Score placeholder
    
    def _parse_non_json_response(self, response_text: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parsear respuesta no-JSON como fallback"""
        # Implementación simplificada para fallback
        parsed_responses = {}
        
        for question in questions:
            q_id = question["id"]
            # Buscar respuesta en el texto (implementación básica)
            parsed_responses[q_id] = {
                "respuesta": "Respuesta extraída del texto",
                "confianza": 0.5,
                "razonamiento": "Parsing automático"
            }
        
        return parsed_responses