"""
Audit Dashboard - Interfaz web para el chatbot de auditoría con Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

from ..agents.audit_chatbot import create_audit_chatbot
from ..core.tracer import get_tracer
from ..utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main audit dashboard application"""
    
    st.set_page_config(
        page_title="🔍 Buyer Synthetic™ - Audit Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 **Buyer Synthetic™ - Audit Dashboard**")
    st.markdown("**Auditoría Inteligente de Procesos de Agentes con LangGraph**")
    
    # Initialize components
    if 'chatbot' not in st.session_state:
        with st.spinner("Inicializando chatbot de auditoría..."):
            st.session_state.chatbot = create_audit_chatbot()
            st.session_state.tracer = get_tracer()
            st.session_state.conversation_history = []
    
    # Sidebar with controls
    setup_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat de Auditoría", 
        "📊 Dashboard de Trazas", 
        "🔍 Explorador de Trazas",
        "📈 Métricas y Rendimiento"
    ])
    
    with tab1:
        chat_interface()
    
    with tab2:
        traces_dashboard()
    
    with tab3:
        traces_explorer()
    
    with tab4:
        metrics_dashboard()


def setup_sidebar():
    """Setup sidebar controls"""
    
    st.sidebar.header("🛠️ Configuración")
    
    # Time range selector
    st.sidebar.subheader("📅 Rango de Tiempo")
    time_option = st.sidebar.selectbox(
        "Seleccionar período:",
        ["Última hora", "Últimas 24 horas", "Últimos 7 días", "Último mes", "Personalizado"]
    )
    
    if time_option == "Personalizado":
        start_date = st.sidebar.date_input("Fecha inicio")
        end_date = st.sidebar.date_input("Fecha fin")
        st.session_state.time_filter = {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    else:
        # Calculate time range based on selection
        now = datetime.now()
        if time_option == "Última hora":
            start_time = now - timedelta(hours=1)
        elif time_option == "Últimas 24 horas":
            start_time = now - timedelta(days=1)
        elif time_option == "Últimos 7 días":
            start_time = now - timedelta(days=7)
        else:  # Último mes
            start_time = now - timedelta(days=30)
        
        st.session_state.time_filter = {
            "start": start_time.isoformat(),
            "end": now.isoformat()
        }
    
    # Agent filter
    st.sidebar.subheader("🤖 Filtros de Agente")
    agent_filter = st.sidebar.multiselect(
        "Agentes:",
        ["SurveyExecutorLangGraph", "SurveyCreator", "ResultsVisualizer"],
        default=[]
    )
    st.session_state.agent_filter = agent_filter
    
    # Quick actions
    st.sidebar.subheader("⚡ Acciones Rápidas")
    
    if st.sidebar.button("🔄 Actualizar Datos"):
        st.rerun()
    
    if st.sidebar.button("🗑️ Limpiar Conversación"):
        st.session_state.conversation_history = []
        st.rerun()
    
    # Stats summary
    st.sidebar.subheader("📊 Resumen Rápido")
    try:
        recent_traces = st.session_state.tracer.query_traces(
            start_time=st.session_state.time_filter["start"],
            limit=1000
        )
        
        total_traces = len(recent_traces)
        unique_executions = len(set(t["trace_id"] for t in recent_traces))
        error_count = len([t for t in recent_traces if t["level"] == "error"])
        
        st.sidebar.metric("Total Trazas", total_traces)
        st.sidebar.metric("Ejecuciones Únicas", unique_executions)
        st.sidebar.metric("Errores", error_count)
        
        if total_traces > 0:
            error_rate = (error_count / total_traces) * 100
            st.sidebar.metric("Tasa de Errores", f"{error_rate:.1f}%")
    
    except Exception as e:
        st.sidebar.error(f"Error cargando estadísticas: {e}")


def chat_interface():
    """Chat interface for audit queries"""
    
    st.header("💬 Chat de Auditoría Inteligente")
    st.markdown("Pregúntame sobre cualquier proceso, error, o métrica de los agentes.")
    
    # Example questions
    with st.expander("💡 Ejemplos de preguntas que puedes hacer"):
        st.markdown("""
        **Análisis de Procesos:**
        - "¿Qué pasó en la última ejecución?"
        - "Muéstrame el trace-id abc123..."
        - "¿Cómo funcionó el agente SurveyExecutor hoy?"
        
        **Análisis de Rendimiento:**
        - "¿Cuánto tiempo tardaron las encuestas?"
        - "¿Qué operación fue más lenta?"
        - "¿Cuántos tokens se usaron en total?"
        
        **Análisis de Errores:**
        - "¿Hubo errores en las últimas 24 horas?"
        - "¿Por qué falló la validación?"
        - "¿Qué tipos de errores son más comunes?"
        
        **Métricas:**
        - "¿Cuántas llamadas a LLM se hicieron?"
        - "¿Cuál fue la tasa de validación exitosa?"
        - "¿Cómo fue el rendimiento general?"
        """)
    
    # Display conversation history
    for i, message in enumerate(st.session_state.conversation_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                
                # Show analysis results if available
                if "analysis_results" in message and message["analysis_results"]:
                    with st.expander("📊 Análisis Detallado"):
                        st.json(message["analysis_results"])
                
                # Show follow-up suggestions
                if "follow_up_suggestions" in message and message["follow_up_suggestions"]:
                    st.markdown("**💡 Preguntas relacionadas:**")
                    for suggestion in message["follow_up_suggestions"]:
                        if st.button(f"➤ {suggestion}", key=f"suggest_{i}_{suggestion}"):
                            process_user_query(suggestion)
    
    # Chat input
    user_query = st.chat_input("Escribe tu pregunta sobre los procesos...")
    
    if user_query:
        process_user_query(user_query)


def process_user_query(query: str):
    """Process user query through the audit chatbot"""
    
    # Add user message to history
    st.session_state.conversation_history.append({
        "role": "user",
        "content": query
    })
    
    # Display user message
    with st.chat_message("user"):
        st.write(query)
    
    # Process query with chatbot
    with st.chat_message("assistant"):
        with st.spinner("Analizando trazas y generando respuesta..."):
            try:
                response = st.session_state.chatbot.chat(
                    user_query=query,
                    conversation_history=st.session_state.conversation_history
                )
                
                # Display response
                st.write(response["response"])
                
                # Show analysis results
                if response.get("analysis_results"):
                    with st.expander("📊 Análisis Detallado"):
                        st.json(response["analysis_results"])
                
                # Show follow-up suggestions
                if response.get("follow_up_suggestions"):
                    st.markdown("**💡 Preguntas relacionadas:**")
                    cols = st.columns(len(response["follow_up_suggestions"]))
                    for i, suggestion in enumerate(response["follow_up_suggestions"]):
                        with cols[i]:
                            if st.button(f"➤ {suggestion}", key=f"new_suggest_{suggestion}"):
                                process_user_query(suggestion)
                
                # Add assistant response to history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response["response"],
                    "analysis_results": response.get("analysis_results", {}),
                    "follow_up_suggestions": response.get("follow_up_suggestions", [])
                })
                
            except Exception as e:
                st.error(f"Error procesando consulta: {e}")
                logger.error(f"Chat error: {e}")


def traces_dashboard():
    """Dashboard overview of traces"""
    
    st.header("📊 Dashboard de Trazas")
    
    try:
        # Fetch traces
        traces = st.session_state.tracer.query_traces(
            start_time=st.session_state.time_filter["start"],
            agent_name=st.session_state.agent_filter[0] if st.session_state.agent_filter else None,
            limit=1000
        )
        
        if not traces:
            st.warning("No se encontraron trazas en el rango de tiempo seleccionado.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(traces)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_traces = len(df)
            st.metric("Total Trazas", total_traces)
        
        with col2:
            unique_executions = df['trace_id'].nunique()
            st.metric("Ejecuciones Únicas", unique_executions)
        
        with col3:
            error_count = len(df[df['level'] == 'error'])
            st.metric("Errores", error_count)
        
        with col4:
            avg_duration = df['duration_ms'].mean() if 'duration_ms' in df.columns else 0
            st.metric("Duración Promedio", f"{avg_duration:.1f}ms")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            # Traces over time
            traces_over_time = df.groupby(df['timestamp'].dt.floor('H')).size()
            fig_time = px.line(
                x=traces_over_time.index, 
                y=traces_over_time.values,
                title="Trazas por Hora",
                labels={"x": "Tiempo", "y": "Cantidad de Trazas"}
            )
            st.plotly_chart(fig_time, use_container_width=True)
        
        with col2:
            # Level distribution
            level_counts = df['level'].value_counts()
            fig_levels = px.pie(
                values=level_counts.values,
                names=level_counts.index,
                title="Distribución por Nivel"
            )
            st.plotly_chart(fig_levels, use_container_width=True)
        
        # Agent performance
        if 'agent_name' in df.columns:
            st.subheader("📊 Rendimiento por Agente")
            
            agent_stats = df.groupby('agent_name').agg({
                'trace_id': 'nunique',
                'duration_ms': 'mean',
                'level': lambda x: (x == 'error').sum()
            }).round(1)
            
            agent_stats.columns = ['Ejecuciones', 'Duración Prom. (ms)', 'Errores']
            st.dataframe(agent_stats, use_container_width=True)
        
        # Recent errors
        error_traces = df[df['level'] == 'error'].sort_values('timestamp', ascending=False)
        if not error_traces.empty:
            st.subheader("🚨 Errores Recientes")
            
            error_display = error_traces[['timestamp', 'agent_name', 'node_name', 'error_type', 'error_message']].head(10)
            st.dataframe(error_display, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error cargando dashboard: {e}")
        logger.error(f"Dashboard error: {e}")


def traces_explorer():
    """Detailed traces explorer"""
    
    st.header("🔍 Explorador de Trazas Detallado")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trace_id_filter = st.text_input("🔍 Trace ID:", placeholder="Buscar por ID específico...")
    
    with col2:
        level_filter = st.selectbox(
            "📊 Nivel:",
            ["Todos", "agent_start", "agent_end", "node_enter", "node_exit", "llm_call", "llm_response", "validation", "error"]
        )
    
    with col3:
        operation_filter = st.text_input("⚙️ Operación:", placeholder="Filtrar por operación...")
    
    # Search button
    if st.button("🔍 Buscar Trazas"):
        try:
            # Build filters
            filters = {}
            if trace_id_filter:
                filters["trace_id"] = trace_id_filter
            if level_filter != "Todos":
                filters["level"] = level_filter
            if operation_filter:
                filters["operation"] = operation_filter
            
            # Add time filter
            filters["start_time"] = st.session_state.time_filter["start"]
            
            # Query traces
            traces = st.session_state.tracer.query_traces(**filters, limit=100)
            
            if traces:
                st.success(f"Encontradas {len(traces)} trazas")
                
                # Display traces
                for i, trace in enumerate(traces[:20]):  # Limit display
                    with st.expander(f"Trace {i+1}: {trace['trace_id'][:8]}... - {trace['level']} - {trace['timestamp']}"):
                        
                        # Basic info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Agente:** {trace['agent_name']}")
                            st.write(f"**Operación:** {trace['operation']}")
                        
                        with col2:
                            st.write(f"**Nivel:** {trace['level']}")
                            if trace.get('node_name'):
                                st.write(f"**Nodo:** {trace['node_name']}")
                        
                        with col3:
                            if trace.get('duration_ms'):
                                st.write(f"**Duración:** {trace['duration_ms']:.1f}ms")
                            if trace.get('tokens_used'):
                                st.write(f"**Tokens:** {trace['tokens_used']}")
                        
                        # Additional data
                        if trace.get('inputs'):
                            st.write("**Inputs:**")
                            try:
                                inputs = json.loads(trace['inputs']) if isinstance(trace['inputs'], str) else trace['inputs']
                                st.json(inputs)
                            except:
                                st.text(trace['inputs'])
                        
                        if trace.get('outputs'):
                            st.write("**Outputs:**")
                            try:
                                outputs = json.loads(trace['outputs']) if isinstance(trace['outputs'], str) else trace['outputs']
                                st.json(outputs)
                            except:
                                st.text(trace['outputs'])
                        
                        if trace.get('error_message'):
                            st.error(f"**Error:** {trace['error_message']}")
                        
                        if trace.get('prompt'):
                            with st.expander("Ver Prompt"):
                                st.text(trace['prompt'])
                        
                        if trace.get('response'):
                            with st.expander("Ver Respuesta"):
                                st.text(trace['response'])
            
            else:
                st.warning("No se encontraron trazas con los filtros especificados.")
        
        except Exception as e:
            st.error(f"Error buscando trazas: {e}")
            logger.error(f"Explorer error: {e}")


def metrics_dashboard():
    """Metrics and performance dashboard"""
    
    st.header("📈 Métricas y Rendimiento")
    
    try:
        # Fetch traces for metrics
        traces = st.session_state.tracer.query_traces(
            start_time=st.session_state.time_filter["start"],
            limit=1000
        )
        
        if not traces:
            st.warning("No hay datos disponibles para mostrar métricas.")
            return
        
        df = pd.DataFrame(traces)
        
        # Performance metrics
        st.subheader("⚡ Métricas de Rendimiento")
        
        # Duration analysis
        duration_data = df[df['duration_ms'].notna()]
        if not duration_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_duration = px.histogram(
                    duration_data, 
                    x='duration_ms',
                    title="Distribución de Duración",
                    labels={"duration_ms": "Duración (ms)", "count": "Frecuencia"}
                )
                st.plotly_chart(fig_duration, use_container_width=True)
            
            with col2:
                # Duration by agent
                if 'agent_name' in duration_data.columns:
                    fig_agent_duration = px.box(
                        duration_data,
                        x='agent_name',
                        y='duration_ms',
                        title="Duración por Agente"
                    )
                    st.plotly_chart(fig_agent_duration, use_container_width=True)
        
        # Token usage
        st.subheader("🔤 Uso de Tokens")
        token_data = df[df['tokens_used'].notna()]
        
        if not token_data.empty:
            total_tokens = token_data['tokens_used'].sum()
            avg_tokens = token_data['tokens_used'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tokens", f"{total_tokens:,}")
            with col2:
                st.metric("Promedio por Llamada", f"{avg_tokens:.1f}")
            with col3:
                st.metric("Costo Estimado (GPT-4)", f"${total_tokens * 0.00003:.2f}")
            
            # Token usage over time
            token_data['timestamp'] = pd.to_datetime(token_data['timestamp'])
            tokens_over_time = token_data.set_index('timestamp')['tokens_used'].resample('H').sum()
            
            fig_tokens = px.line(
                x=tokens_over_time.index,
                y=tokens_over_time.values,
                title="Uso de Tokens por Hora",
                labels={"x": "Tiempo", "y": "Tokens"}
            )
            st.plotly_chart(fig_tokens, use_container_width=True)
        
        # Validation metrics
        st.subheader("✅ Métricas de Validación")
        validation_data = df[df['level'] == 'validation']
        
        if not validation_data.empty:
            passed_validations = validation_data['validation_passed'].sum()
            total_validations = len(validation_data)
            pass_rate = (passed_validations / total_validations) * 100 if total_validations > 0 else 0
            
            avg_score = validation_data['validation_score'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tasa de Éxito", f"{pass_rate:.1f}%")
            with col2:
                st.metric("Total Validaciones", total_validations)
            with col3:
                st.metric("Puntuación Promedio", f"{avg_score:.2f}")
            
            # Validation scores distribution
            fig_validation = px.histogram(
                validation_data,
                x='validation_score',
                title="Distribución de Puntuaciones de Validación",
                labels={"validation_score": "Puntuación", "count": "Frecuencia"}
            )
            st.plotly_chart(fig_validation, use_container_width=True)
        
        # Error analysis
        st.subheader("🚨 Análisis de Errores")
        error_data = df[df['level'] == 'error']
        
        if not error_data.empty:
            error_types = error_data['error_type'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_error_types = px.pie(
                    values=error_types.values,
                    names=error_types.index,
                    title="Tipos de Error"
                )
                st.plotly_chart(fig_error_types, use_container_width=True)
            
            with col2:
                # Errors by node
                if 'node_name' in error_data.columns:
                    error_nodes = error_data['node_name'].value_counts()
                    fig_error_nodes = px.bar(
                        x=error_nodes.values,
                        y=error_nodes.index,
                        orientation='h',
                        title="Errores por Nodo"
                    )
                    st.plotly_chart(fig_error_nodes, use_container_width=True)
        else:
            st.success("🎉 No se encontraron errores en el período seleccionado!")
    
    except Exception as e:
        st.error(f"Error cargando métricas: {e}")
        logger.error(f"Metrics error: {e}")


if __name__ == "__main__":
    main()