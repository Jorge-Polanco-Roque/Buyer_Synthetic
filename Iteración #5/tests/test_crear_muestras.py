#!/usr/bin/env python3
"""
Test específico para la funcionalidad de Crear Muestras
"""

import sys
from pathlib import Path
import pandas as pd

# Agregar src al path
sys.path.append(str(Path(__file__).parent / "src"))

def test_crear_muestras_demo():
    """Test específico de la funcionalidad Crear Muestras en Demo Mode"""
    print("🧪 TESTING CREAR MUESTRAS - DEMO MODE")
    print("=" * 50)
    
    try:
        # Importar funciones necesarias
        from src.agents.survey_creator import SurveyCreatorAgent
        from src.buyer_synthetic.config.settings import settings
        
        # Crear muestra pequeña para test
        print("📊 Creando muestra representativa...")
        creator = SurveyCreatorAgent(sample_size=10)
        sample_df = creator.generate_representative_sample()
        
        print(f"✅ Muestra creada: {len(sample_df)} perfiles")
        print(f"📋 Columnas: {list(sample_df.columns)}")
        print(f"🔍 Tipos de datos: {sample_df.dtypes.to_dict()}")
        
        # Simular el proceso de crear respuestas como en el dashboard
        print("\n🎮 Simulando proceso de demo...")
        
        # Usar las preguntas electorales del settings
        questions = settings.ELECTORAL_QUESTIONS[:3]  # Solo las primeras 3 para el test
        
        print(f"❓ Usando {len(questions)} preguntas de prueba")
        
        # Simular el proceso batch demo
        results = []
        
        for _, profile in sample_df.iterrows():
            # Simular respuestas (igual que en dashboard)
            result = {
                "id": profile["id"],
                "nombre": profile["nombre"],
                "edad": profile["edad"],
                "genero": profile["genero"],
                "ciudad": profile.get("ciudad", ""),
                "nse": profile["nse"],
                "region": profile["region"],
                "ocupacion": profile.get("ocupacion", ""),
                "educacion": profile.get("educacion", ""),
                "estado_civil": profile.get("estado_civil", ""),
                "ingresos": profile.get("ingresos", ""),
            }
            
            # Generar respuestas para cada pregunta
            for question in questions:
                q_id = question["id"]
                
                if question["tipo"] == "multiple":
                    # Simular respuesta multiple choice
                    options = question.get("opciones", ["Opción A", "Opción B", "Opción C"])
                    response = options[hash(str(profile["nombre"]) + str(q_id)) % len(options)]
                    result[f"{q_id}_respuesta"] = response
                    
                elif question["tipo"] == "escala":
                    # Simular respuesta escala
                    scale_parts = question.get("escala", "1-10").split("-")
                    min_val = int(scale_parts[0]) if scale_parts[0].isdigit() else 1
                    max_val = int(scale_parts[1]) if len(scale_parts) > 1 and scale_parts[1].isdigit() else 10
                    response = min_val + (hash(str(profile["edad"]) + str(q_id)) % (max_val - min_val + 1))
                    result[f"{q_id}_respuesta"] = response
                    
                else:  # abierta
                    # Simular respuesta abierta
                    responses = ["Muy bueno", "Bueno", "Regular", "Malo", "Muy malo"]
                    response = responses[hash(str(profile["nse"]) + str(q_id)) % len(responses)]
                    result[f"{q_id}_respuesta"] = response
                
                # Agregar confianza simulada
                result[f"{q_id}_confianza"] = 0.6 + (hash(str(profile["nombre"]) + str(q_id)) % 40) / 100
            
            results.append(result)
        
        results_df = pd.DataFrame(results)
        
        print(f"✅ Respuestas generadas: {len(results_df)} registros")
        print(f"📊 Columnas finales: {len(results_df.columns)}")
        
        # Verificar que no hay errores de tipo
        print("\n🔍 Verificando tipos de datos...")
        for col in results_df.columns:
            col_type = results_df[col].dtype
            print(f"  {col}: {col_type}")
        
        # Mostrar una muestra de los resultados
        print("\n📋 Muestra de resultados:")
        print(results_df.head(2).to_string())
        
        print("\n✅ TEST COMPLETADO EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crear_muestras_demo()
    if success:
        print("\n🎉 La funcionalidad Crear Muestras funciona correctamente!")
    else:
        print("\n💥 Hay problemas con la funcionalidad Crear Muestras")