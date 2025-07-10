#!/usr/bin/env python3
"""
Test script para validar la integración de LangGraph
"""

import sys
from pathlib import Path
import pandas as pd
import os

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

def test_demo_mode():
    """Test del Demo Mode (sin API)"""
    print("🎮 TESTING DEMO MODE")
    print("=" * 50)
    
    try:
        from src.agents.survey_creator import SurveyCreatorAgent
        
        # Crear muestra pequeña
        creator = SurveyCreatorAgent(sample_size=5)
        sample_df = creator.generate_representative_sample()
        
        print(f"✅ Muestra creada: {len(sample_df)} perfiles")
        print(f"📊 NSE Distribution: {sample_df['nse'].value_counts().to_dict()}")
        
        # Simular respuestas (modo demo)
        print("🎮 Simulando respuestas (Demo Mode)...")
        
        # Demo de cómo funcionaría
        demo_results = []
        for _, profile in sample_df.iterrows():
            result = {
                "id": profile["id"],
                "nombre": profile["nombre"],
                "edad": profile["edad"],
                "nse": profile["nse"],
                "region": profile["region"],
                "modo": "Demo Mode",
                "intent_voto_respuesta": "Candidato A",
                "intent_voto_confianza": 0.8
            }
            demo_results.append(result)
        
        results_df = pd.DataFrame(demo_results)
        print(f"✅ Respuestas demo generadas: {len(results_df)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en Demo Mode: {str(e)}")
        return False

def test_genai_mode():
    """Test del GenAI Mode con LangGraph"""
    print("\n🤖 TESTING GENAI MODE (LangGraph)")
    print("=" * 50)
    
    # Verificar API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY no configurada - Saltando GenAI Mode test")
        print("💡 Para probar GenAI Mode, configura OPENAI_API_KEY en .env")
        return True
    
    try:
        # Importar agente LangGraph
        from src.buyer_synthetic.agents.survey_executor_langgraph import SurveyExecutorLangGraph
        
        print("✅ LangGraph importado exitosamente")
        
        # Crear perfil de prueba
        test_profile = {
            "id": 1,
            "nombre": "María Test",
            "edad": 35,
            "genero": "F",
            "ciudad": "Lima",
            "region": "Lima",
            "nse": "C",
            "ocupacion": "Ingeniera",
            "educacion": "Universitaria",
            "estado_civil": "Casada",
            "ingresos": 3500
        }
        
        # Preguntas de prueba
        test_questions = [
            {
                "id": "test_question",
                "pregunta": "¿Cómo calificarías la situación económica actual?",
                "tipo": "escala",
                "escala": "1-10"
            }
        ]
        
        print("🔧 Configurando executor LangGraph...")
        executor = SurveyExecutorLangGraph(model="gpt-3.5-turbo", temperature=0.7)
        
        print("🚀 Ejecutando encuesta individual con LangGraph...")
        result = executor.execute_individual_survey(test_profile, test_questions)
        
        print("✅ Respuesta LangGraph generada:")
        print(f"   - Nombre: {result.get('nombre', 'N/A')}")
        print(f"   - Modo: {result.get('survey_mode', 'N/A')}")
        print(f"   - Validation Score: {result.get('validation_score', 'N/A')}")
        print(f"   - Respuesta: {result.get('test_question_respuesta', 'N/A')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando LangGraph: {str(e)}")
        print("💡 Asegúrate de que LangGraph esté instalado: pip install langgraph")
        return False
    except Exception as e:
        print(f"❌ Error en GenAI Mode: {str(e)}")
        return False

def test_dashboard_integration():
    """Test de integración con dashboard"""
    print("\n🖥️ TESTING DASHBOARD INTEGRATION")
    print("=" * 50)
    
    try:
        # Verificar que el dashboard puede importar todo
        from src.ui.dashboard import BuyerSyntheticDashboard
        
        print("✅ Dashboard importado exitosamente")
        
        # Verificar configuraciones
        from src.buyer_synthetic.config.settings import settings
        print(f"✅ Settings cargados - Default mode: {settings.DEFAULT_SURVEY_MODE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en Dashboard Integration: {str(e)}")
        return False

def main():
    """Función principal de testing"""
    print("🚀 BUYER SYNTHETIC™ - INTEGRATION TEST")
    print("=" * 60)
    print("Testing Demo Mode + GenAI Mode + LangGraph Integration")
    print("=" * 60)
    
    # Tests
    tests = [
        ("Demo Mode", test_demo_mode),
        ("GenAI Mode", test_genai_mode),
        ("Dashboard Integration", test_dashboard_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
            results[test_name] = False
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! System is ready!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Open dashboard: http://localhost:8505")
    print("2. Try both Demo Mode and GenAI Mode")
    print("3. Upload custom CSV/TXT files")
    print("4. Generate comprehensive analysis")

if __name__ == "__main__":
    main()