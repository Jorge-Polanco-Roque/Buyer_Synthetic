"""
Audit Chatbot using LangGraph for querying agent traces and process analysis.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ..config.settings import Settings
from ..core.tracer import get_tracer, TraceLevel
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AuditChatState(TypedDict):
    """State for audit chatbot conversation"""
    user_query: str
    conversation_history: List[Dict[str, str]]
    query_intent: str
    extracted_filters: Dict[str, Any]
    relevant_traces: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    response: str
    follow_up_suggestions: List[str]


@dataclass
class QueryIntent:
    """Query intent classification"""
    TRACE_LOOKUP = "trace_lookup"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ERROR_ANALYSIS = "error_analysis"
    PROCESS_EXPLANATION = "process_explanation"
    COMPARISON = "comparison"
    METRICS = "metrics"
    GENERAL = "general"


class AuditChatbot:
    """
    LangGraph-based chatbot for auditing agent processes and traces.
    Can answer questions about what agents did, how they performed, and why.
    """
    
    def __init__(self, model: str = "gpt-4"):
        self.settings = Settings()
        self.tracer = get_tracer()
        self.logger = logger
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.3,  # Lower temperature for more factual responses
            api_key=self.settings.OPENAI_API_KEY
        )
        
        # Create workflow
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the audit chatbot workflow"""
        
        workflow = StateGraph(AuditChatState)
        
        # Add nodes
        workflow.add_node("classify_intent", self._classify_query_intent)
        workflow.add_node("extract_filters", self._extract_query_filters)
        workflow.add_node("fetch_traces", self._fetch_relevant_traces)
        workflow.add_node("analyze_data", self._analyze_trace_data)
        workflow.add_node("generate_response", self._generate_response)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add edges
        workflow.add_edge("classify_intent", "extract_filters")
        workflow.add_edge("extract_filters", "fetch_traces")
        workflow.add_edge("fetch_traces", "analyze_data")
        workflow.add_edge("analyze_data", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def chat(self, user_query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Process user query and return audit information
        
        Args:
            user_query: User's question about the process
            conversation_history: Previous conversation messages
            
        Returns:
            Response with analysis and follow-up suggestions
        """
        
        logger.info(f"Processing audit query: {user_query[:100]}...")
        
        # Initialize state
        initial_state = AuditChatState(
            user_query=user_query,
            conversation_history=conversation_history or [],
            query_intent="",
            extracted_filters={},
            relevant_traces=[],
            analysis_results={},
            response="",
            follow_up_suggestions=[]
        )
        
        try:
            # Execute workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "response": final_state["response"],
                "follow_up_suggestions": final_state["follow_up_suggestions"],
                "query_intent": final_state["query_intent"],
                "traces_analyzed": len(final_state["relevant_traces"]),
                "analysis_results": final_state["analysis_results"]
            }
            
        except Exception as e:
            logger.error(f"Error in audit chatbot: {e}")
            return {
                "response": f"Lo siento, ocurrió un error al procesar tu consulta: {str(e)}",
                "follow_up_suggestions": ["Intenta reformular tu pregunta", "Verifica que existan trazas de procesos"],
                "query_intent": "error",
                "traces_analyzed": 0,
                "analysis_results": {}
            }
    
    def _classify_query_intent(self, state: AuditChatState) -> AuditChatState:
        """Classify the intent of the user query"""
        
        query = state["user_query"].lower()
        
        # Intent classification patterns
        intent_patterns = {
            QueryIntent.TRACE_LOOKUP: [
                r"trace.*\b(\w+)\b", r"proceso.*\b(\w+)\b", r"ejecución.*\b(\w+)\b",
                r"qué pasó", r"que paso", r"mostrar.*proceso"
            ],
            QueryIntent.PERFORMANCE_ANALYSIS: [
                r"rendimiento", r"performance", r"tiempo", r"duración", r"velocidad",
                r"cuánto.*tardó", r"cuanto.*tardo", r"lento", r"rápido"
            ],
            QueryIntent.ERROR_ANALYSIS: [
                r"error", r"fallo", r"problema", r"excepción", r"falló",
                r"qué salió mal", r"que salio mal", r"por qué.*error"
            ],
            QueryIntent.PROCESS_EXPLANATION: [
                r"cómo.*funciona", r"como.*funciona", r"explicar.*proceso",
                r"pasos", r"workflow", r"algoritmo", r"lógica"
            ],
            QueryIntent.COMPARISON: [
                r"comparar", r"diferencia", r"vs", r"antes.*después",
                r"mejor.*peor", r"cambio"
            ],
            QueryIntent.METRICS: [
                r"métricas", r"metricas", r"estadísticas", r"estadisticas",
                r"tokens", r"llamadas", r"api", r"costos"
            ]
        }
        
        # Find matching intent
        detected_intent = QueryIntent.GENERAL
        for intent, patterns in intent_patterns.items():
            if any(re.search(pattern, query) for pattern in patterns):
                detected_intent = intent
                break
        
        state["query_intent"] = detected_intent
        logger.debug(f"Classified query intent: {detected_intent}")
        
        return state
    
    def _extract_query_filters(self, state: AuditChatState) -> AuditChatState:
        """Extract filters from the user query"""
        
        query = state["user_query"]
        filters = {}
        
        # Extract time-based filters
        time_patterns = {
            r"hoy": lambda: datetime.now().strftime("%Y-%m-%d"),
            r"ayer": lambda: (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            r"última.*hora": lambda: (datetime.now() - timedelta(hours=1)).isoformat(),
            r"ultimas?.*(\d+).*horas": lambda m: (datetime.now() - timedelta(hours=int(m.group(1)))).isoformat(),
            r"últimos?.*(\d+).*días": lambda m: (datetime.now() - timedelta(days=int(m.group(1)))).isoformat(),
        }
        
        for pattern, time_func in time_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if callable(time_func):
                    filters["start_time"] = time_func() if not match.groups() else time_func(match)
                break
        
        # Extract agent name
        agent_pattern = r"agente?\s+(\w+)|(\w+)\s+agent"
        agent_match = re.search(agent_pattern, query, re.IGNORECASE)
        if agent_match:
            filters["agent_name"] = agent_match.group(1) or agent_match.group(2)
        
        # Extract trace ID
        trace_pattern = r"trace[-_]?id[:\s]*([a-f0-9\-]{36})"
        trace_match = re.search(trace_pattern, query, re.IGNORECASE)
        if trace_match:
            filters["trace_id"] = trace_match.group(1)
        
        # Extract operation
        operation_patterns = [
            r"operación\s+(\w+)", r"operacion\s+(\w+)",
            r"execute_(\w+)", r"proceso\s+(\w+)"
        ]
        for pattern in operation_patterns:
            op_match = re.search(pattern, query, re.IGNORECASE)
            if op_match:
                filters["operation"] = op_match.group(1)
                break
        
        # Extract level filters
        level_patterns = {
            "error": TraceLevel.ERROR,
            "validation": TraceLevel.VALIDATION,
            "llm": TraceLevel.LLM_CALL
        }
        for keyword, level in level_patterns.items():
            if keyword in query.lower():
                filters["level"] = level
                break
        
        state["extracted_filters"] = filters
        logger.debug(f"Extracted filters: {filters}")
        
        return state
    
    def _fetch_relevant_traces(self, state: AuditChatState) -> AuditChatState:
        """Fetch traces based on extracted filters"""
        
        filters = state["extracted_filters"]
        
        # Query traces with filters
        traces = self.tracer.query_traces(
            trace_id=filters.get("trace_id"),
            agent_name=filters.get("agent_name"),
            operation=filters.get("operation"),
            level=filters.get("level"),
            start_time=filters.get("start_time"),
            limit=100
        )
        
        state["relevant_traces"] = traces
        logger.debug(f"Found {len(traces)} relevant traces")
        
        return state
    
    def _analyze_trace_data(self, state: AuditChatState) -> AuditChatState:
        """Analyze fetched trace data based on query intent"""
        
        traces = state["relevant_traces"]
        intent = state["query_intent"]
        analysis = {}
        
        if not traces:
            analysis["summary"] = "No se encontraron trazas que coincidan con los criterios."
            state["analysis_results"] = analysis
            return state
        
        # Group traces by trace_id for better analysis
        traces_by_id = {}
        for trace in traces:
            trace_id = trace["trace_id"]
            if trace_id not in traces_by_id:
                traces_by_id[trace_id] = []
            traces_by_id[trace_id].append(trace)
        
        if intent == QueryIntent.PERFORMANCE_ANALYSIS:
            analysis = self._analyze_performance(traces, traces_by_id)
        
        elif intent == QueryIntent.ERROR_ANALYSIS:
            analysis = self._analyze_errors(traces)
        
        elif intent == QueryIntent.PROCESS_EXPLANATION:
            analysis = self._analyze_process_flow(traces_by_id)
        
        elif intent == QueryIntent.METRICS:
            analysis = self._analyze_metrics(traces)
        
        else:
            analysis = self._general_analysis(traces, traces_by_id)
        
        state["analysis_results"] = analysis
        return state
    
    def _analyze_performance(self, traces: List[Dict], traces_by_id: Dict) -> Dict[str, Any]:
        """Analyze performance metrics"""
        
        durations = [t["duration_ms"] for t in traces if t.get("duration_ms")]
        tokens = [t["tokens_used"] for t in traces if t.get("tokens_used")]
        
        analysis = {
            "type": "performance",
            "total_executions": len(traces_by_id),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "total_tokens": sum(tokens),
            "avg_tokens_per_call": sum(tokens) / len(tokens) if tokens else 0,
            "slowest_operations": self._get_slowest_operations(traces_by_id),
            "performance_summary": self._generate_performance_summary(durations, tokens)
        }
        
        return analysis
    
    def _analyze_errors(self, traces: List[Dict]) -> Dict[str, Any]:
        """Analyze error patterns"""
        
        error_traces = [t for t in traces if t["level"] == "error"]
        
        error_types = {}
        error_nodes = {}
        
        for trace in error_traces:
            error_type = trace.get("error_type", "Unknown")
            node_name = trace.get("node_name", "Unknown")
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            error_nodes[node_name] = error_nodes.get(node_name, 0) + 1
        
        analysis = {
            "type": "error",
            "total_errors": len(error_traces),
            "error_types": error_types,
            "error_nodes": error_nodes,
            "recent_errors": error_traces[:5],  # Last 5 errors
            "error_summary": self._generate_error_summary(error_traces, error_types, error_nodes)
        }
        
        return analysis
    
    def _analyze_process_flow(self, traces_by_id: Dict) -> Dict[str, Any]:
        """Analyze process flow and workflow patterns"""
        
        if not traces_by_id:
            return {"type": "process", "flows": []}
        
        # Analyze a representative trace
        sample_trace_id = list(traces_by_id.keys())[0]
        sample_traces = sorted(traces_by_id[sample_trace_id], key=lambda x: x["timestamp"])
        
        flow_steps = []
        for trace in sample_traces:
            if trace["level"] in ["node_enter", "node_exit", "agent_start", "agent_end"]:
                flow_steps.append({
                    "step": trace["level"],
                    "node": trace.get("node_name"),
                    "timestamp": trace["timestamp"],
                    "duration_ms": trace.get("duration_ms")
                })
        
        analysis = {
            "type": "process",
            "sample_trace_id": sample_trace_id,
            "total_traces_analyzed": len(traces_by_id),
            "flow_steps": flow_steps,
            "common_patterns": self._identify_common_patterns(traces_by_id),
            "process_summary": self._generate_process_summary(flow_steps, len(traces_by_id))
        }
        
        return analysis
    
    def _analyze_metrics(self, traces: List[Dict]) -> Dict[str, Any]:
        """Analyze various metrics"""
        
        llm_calls = [t for t in traces if t["level"] == "llm_response"]
        validations = [t for t in traces if t["level"] == "validation"]
        
        total_tokens = sum(t["tokens_used"] for t in llm_calls if t.get("tokens_used"))
        validation_scores = [t["validation_score"] for t in validations if t.get("validation_score")]
        
        analysis = {
            "type": "metrics",
            "total_llm_calls": len(llm_calls),
            "total_tokens_used": total_tokens,
            "total_validations": len(validations),
            "avg_validation_score": sum(validation_scores) / len(validation_scores) if validation_scores else 0,
            "validation_pass_rate": len([v for v in validations if v.get("validation_passed")]) / len(validations) if validations else 0,
            "metrics_summary": self._generate_metrics_summary(len(llm_calls), total_tokens, validation_scores)
        }
        
        return analysis
    
    def _general_analysis(self, traces: List[Dict], traces_by_id: Dict) -> Dict[str, Any]:
        """General analysis for unclassified queries"""
        
        agents = set(t["agent_name"] for t in traces)
        operations = set(t["operation"] for t in traces)
        levels = set(t["level"] for t in traces)
        
        analysis = {
            "type": "general",
            "total_traces": len(traces),
            "unique_executions": len(traces_by_id),
            "agents_involved": list(agents),
            "operations_performed": list(operations),
            "trace_levels": list(levels),
            "time_range": {
                "start": min(t["timestamp"] for t in traces),
                "end": max(t["timestamp"] for t in traces)
            },
            "general_summary": self._generate_general_summary(traces, traces_by_id, agents, operations)
        }
        
        return analysis
    
    def _generate_response(self, state: AuditChatState) -> AuditChatState:
        """Generate natural language response based on analysis"""
        
        analysis = state["analysis_results"]
        intent = state["query_intent"]
        query = state["user_query"]
        
        # Create context for LLM
        context = self._build_response_context(analysis, intent, query)
        
        # Generate response using LLM
        messages = [
            SystemMessage(content="""Eres un asistente especializado en auditoría de procesos de agentes de IA. 
            Tu trabajo es explicar de manera clara y útil qué hicieron los agentes, cómo lo hicieron, 
            y cualquier información relevante sobre su rendimiento o errores.
            
            Responde en español de manera conversacional pero informativa. 
            Incluye datos específicos cuando estén disponibles.
            Si no hay datos suficientes, explica qué información falta."""),
            
            HumanMessage(content=f"""
            Pregunta del usuario: {query}
            
            Análisis de trazas: {json.dumps(analysis, indent=2)}
            
            Por favor, proporciona una respuesta clara y útil basada en este análisis.
            """)
        ]
        
        try:
            response = self.llm.invoke(messages)
            state["response"] = response.content
            
            # Generate follow-up suggestions
            state["follow_up_suggestions"] = self._generate_follow_up_suggestions(analysis, intent)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state["response"] = "No pude generar una respuesta. Por favor, intenta reformular tu pregunta."
            state["follow_up_suggestions"] = []
        
        return state
    
    def _build_response_context(self, analysis: Dict, intent: str, query: str) -> str:
        """Build context for response generation"""
        # This method builds structured context for the LLM
        # Implementation depends on analysis type
        return json.dumps(analysis, indent=2)
    
    def _generate_follow_up_suggestions(self, analysis: Dict, intent: str) -> List[str]:
        """Generate relevant follow-up questions"""
        
        suggestions = []
        
        if analysis.get("type") == "performance":
            suggestions.extend([
                "¿Qué operaciones fueron más lentas?",
                "¿Cómo se compara con ejecuciones anteriores?",
                "¿Hubo algún error de rendimiento?"
            ])
        
        elif analysis.get("type") == "error":
            suggestions.extend([
                "¿Cuál fue la causa raíz de los errores?",
                "¿En qué nodos ocurrieron más errores?",
                "¿Cómo se pueden prevenir estos errores?"
            ])
        
        elif analysis.get("type") == "process":
            suggestions.extend([
                "¿Cuáles fueron los inputs y outputs?",
                "¿Qué validaciones se realizaron?",
                "¿Cuántas llamadas a LLM se hicieron?"
            ])
        
        else:
            suggestions.extend([
                "¿Puedes mostrar más detalles?",
                "¿Hubo algún error en el proceso?",
                "¿Cómo fue el rendimiento?"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    # Helper methods for analysis
    def _get_slowest_operations(self, traces_by_id: Dict) -> List[Dict]:
        """Get slowest operations"""
        operations = []
        for trace_id, traces in traces_by_id.items():
            total_duration = sum(t.get("duration_ms", 0) for t in traces)
            if total_duration > 0:
                operations.append({
                    "trace_id": trace_id,
                    "duration_ms": total_duration,
                    "agent": traces[0].get("agent_name"),
                    "operation": traces[0].get("operation")
                })
        
        return sorted(operations, key=lambda x: x["duration_ms"], reverse=True)[:5]
    
    def _identify_common_patterns(self, traces_by_id: Dict) -> List[str]:
        """Identify common execution patterns"""
        patterns = []
        
        # Count node sequences
        sequences = {}
        for traces in traces_by_id.values():
            nodes = [t.get("node_name") for t in traces if t.get("node_name")]
            sequence = " -> ".join(nodes)
            sequences[sequence] = sequences.get(sequence, 0) + 1
        
        # Get most common sequences
        common = sorted(sequences.items(), key=lambda x: x[1], reverse=True)[:3]
        patterns = [f"{seq} (repetido {count} veces)" for seq, count in common]
        
        return patterns
    
    def _generate_performance_summary(self, durations: List[float], tokens: List[int]) -> str:
        """Generate performance summary text"""
        if not durations:
            return "No hay datos de rendimiento disponibles."
        
        avg_duration = sum(durations) / len(durations)
        total_tokens = sum(tokens) if tokens else 0
        
        return f"Duración promedio: {avg_duration:.1f}ms, Total tokens: {total_tokens}"
    
    def _generate_error_summary(self, errors: List[Dict], error_types: Dict, error_nodes: Dict) -> str:
        """Generate error summary text"""
        if not errors:
            return "No se encontraron errores en las trazas analizadas."
        
        most_common_type = max(error_types.items(), key=lambda x: x[1]) if error_types else ("Unknown", 0)
        most_common_node = max(error_nodes.items(), key=lambda x: x[1]) if error_nodes else ("Unknown", 0)
        
        return f"Errores más comunes: {most_common_type[0]} en nodo {most_common_node[0]}"
    
    def _generate_process_summary(self, flow_steps: List[Dict], total_executions: int) -> str:
        """Generate process summary text"""
        if not flow_steps:
            return "No hay información de flujo de proceso disponible."
        
        nodes = [step["node"] for step in flow_steps if step["node"]]
        return f"Proceso con {len(set(nodes))} nodos únicos, ejecutado {total_executions} veces"
    
    def _generate_metrics_summary(self, llm_calls: int, tokens: int, scores: List[float]) -> str:
        """Generate metrics summary text"""
        avg_score = sum(scores) / len(scores) if scores else 0
        return f"LLM calls: {llm_calls}, Tokens: {tokens}, Validación promedio: {avg_score:.2f}"
    
    def _generate_general_summary(self, traces: List[Dict], traces_by_id: Dict, agents: set, operations: set) -> str:
        """Generate general summary text"""
        return f"Analizadas {len(traces)} trazas de {len(agents)} agentes realizando {len(operations)} operaciones"


# Convenience function
def create_audit_chatbot() -> AuditChatbot:
    """Create an audit chatbot instance"""
    return AuditChatbot()