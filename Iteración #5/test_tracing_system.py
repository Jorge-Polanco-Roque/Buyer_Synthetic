#!/usr/bin/env python3
"""
Test script para demostrar el sistema de trazabilidad y chatbot de auditoría
"""

import time
import json
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from buyer_synthetic.agents.survey_executor_langgraph import SurveyExecutorLangGraph
from buyer_synthetic.agents.audit_chatbot import create_audit_chatbot
from buyer_synthetic.core.tracer import get_tracer
from buyer_synthetic.config.settings import settings

def create_sample_profile():
    """Create a sample demographic profile"""
    return {
        "nombre": "María González",
        "edad": 35,
        "nse": "C",
        "region": "Lima",
        "ciudad": "Lima",
        "ocupacion": "Profesional",
        "educacion": "Superior"
    }

def create_sample_questions():
    """Create sample survey questions"""
    return [
        {
            "id": "intent_voto",
            "pregunta": "Si las elecciones presidenciales fueran hoy, ¿por quién votarías?",
            "tipo": "multiple",
            "opciones": ["Candidato A", "Candidato B", "Candidato C", "Voto en blanco", "No votaría", "No sabe/No opina"]
        },
        {
            "id": "aprobacion_gobierno",
            "pregunta": "¿Cómo calificarías la gestión del actual gobierno?",
            "tipo": "escala",
            "escala": "1-10"
        }
    ]

def test_survey_execution():
    """Test survey execution with tracing"""
    
    print("🚀 Iniciando test del sistema de trazabilidad...")
    print("=" * 60)
    
    # Create executor with tracing
    executor = SurveyExecutorLangGraph()
    
    # Create sample data
    profile = create_sample_profile()
    questions = create_sample_questions()
    
    print(f"📊 Ejecutando encuesta para: {profile['nombre']}")
    print(f"📝 Preguntas: {len(questions)}")
    
    try:
        # Execute survey (this will generate traces)
        start_time = time.time()
        result = executor.execute_individual_survey(profile, questions)
        duration = time.time() - start_time
        
        print(f"✅ Encuesta completada en {duration:.2f} segundos")
        print(f"📈 Respuestas generadas: {len(result.get('respuestas', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")
        return False

def test_audit_chatbot():
    """Test the audit chatbot with sample queries"""
    
    print("\n🤖 Iniciando test del chatbot de auditoría...")
    print("=" * 60)
    
    # Create chatbot
    chatbot = create_audit_chatbot()
    
    # Sample queries to test
    test_queries = [
        "¿Qué procesos se ejecutaron en la última hora?",
        "¿Hubo algún error en las ejecuciones recientes?",
        "¿Cuánto tiempo tardó la última encuesta?",
        "¿Cuántos tokens se usaron en total?",
        "¿Cómo fue el rendimiento del agente SurveyExecutorLangGraph?",
        "¿Qué validaciones se realizaron?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n💬 Pregunta {i}: {query}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            response = chatbot.chat(query)
            duration = time.time() - start_time
            
            print(f"🤖 Respuesta ({duration:.2f}s):")
            print(response["response"])
            
            if response.get("follow_up_suggestions"):
                print("\n💡 Sugerencias de seguimiento:")
                for suggestion in response["follow_up_suggestions"]:
                    print(f"  • {suggestion}")
            
            print(f"\n📊 Trazas analizadas: {response.get('traces_analyzed', 0)}")
            print(f"🎯 Intent detectado: {response.get('query_intent', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Error procesando consulta: {e}")
        
        time.sleep(1)  # Small delay between queries

def test_trace_queries():
    """Test direct trace queries"""
    
    print("\n🔍 Probando consultas directas de trazas...")
    print("=" * 60)
    
    tracer = get_tracer()
    
    # Query recent traces
    print("📊 Consultando trazas recientes...")
    recent_traces = tracer.query_traces(limit=10)
    
    print(f"📈 Encontradas {len(recent_traces)} trazas")
    
    if recent_traces:
        # Show summary of first trace
        first_trace = recent_traces[0]
        print(f"\n🔍 Detalle de la primera traza:")
        print(f"  • ID: {first_trace['trace_id']}")
        print(f"  • Agente: {first_trace['agent_name']}")
        print(f"  • Operación: {first_trace['operation']}")
        print(f"  • Nivel: {first_trace['level']}")
        print(f"  • Timestamp: {first_trace['timestamp']}")
        
        if first_trace.get('duration_ms'):
            print(f"  • Duración: {first_trace['duration_ms']}ms")
        
        # Get full trace summary
        if first_trace['level'] == 'agent_start':
            print(f"\n📋 Resumen completo de la traza:")
            summary = tracer.get_trace_summary(first_trace['trace_id'])
            print(json.dumps(summary, indent=2, ensure_ascii=False))

def main():
    """Main test function"""
    
    print("🔍 **Buyer Synthetic™ - Test Sistema de Trazabilidad**")
    print("=" * 70)
    
    # Check if we can access the database
    try:
        tracer = get_tracer()
        existing_traces = tracer.query_traces(limit=1)
        print(f"🗄️  Base de datos de trazas: OK ({len(existing_traces)} trazas existentes)")
    except Exception as e:
        print(f"❌ Error accediendo a base de datos: {e}")
        return False
    
    # Test 1: Execute survey with tracing
    success = test_survey_execution()
    if not success:
        print("❌ Test de ejecución falló, continuando...")
    
    # Test 2: Test audit chatbot
    test_audit_chatbot()
    
    # Test 3: Test direct trace queries
    test_trace_queries()
    
    print("\n🎉 **Test completado!**")
    print("\n📌 **Próximos pasos:**")
    print("1. Ejecuta `make audit-dashboard` para ver el dashboard web")
    print("2. Ejecuta `make dev` para usar el sistema principal")
    print("3. Usa el chatbot para hacer preguntas sobre los procesos")
    
    print("\n💡 **Ejemplos de uso del chatbot:**")
    print("  • '¿Qué pasó en la última ejecución?'")
    print("  • '¿Hubo errores en las últimas 24 horas?'")
    print("  • '¿Cuánto tiempo tardaron las encuestas?'")
    print("  • '¿Qué validaciones fallaron?'")
    
    return True

if __name__ == "__main__":
    main()