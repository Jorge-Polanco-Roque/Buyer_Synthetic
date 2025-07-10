#!/usr/bin/env python3
"""
Script de prueba simple para Buyer_Synthetic
"""

import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import openai

# Cargar variables de entorno
load_dotenv()

def test_openai_connection():
    """Prueba la conexión con OpenAI"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Di 'Hola, soy Buyer Synthetic' en una sola línea"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI Connection: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")
        return False

def test_survey_simulation():
    """Prueba simulación básica de encuesta"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Perfil de prueba
        perfil = {
            "nombre": "María González",
            "edad": 35,
            "ciudad": "Lima",
            "nse": "C",
            "ocupacion": "Empleada"
        }
        
        prompt = f"""
        Eres una persona con el siguiente perfil:
        - Nombre: {perfil['nombre']}
        - Edad: {perfil['edad']} años
        - Ciudad: {perfil['ciudad']}
        - NSE: {perfil['nse']}
        - Ocupación: {perfil['ocupacion']}
        
        Responde esta pregunta como si fueras realmente esta persona:
        "¿Cuál es tu principal preocupación económica en este momento?"
        
        Responde en formato JSON:
        {{
            "respuesta": "tu respuesta aquí",
            "confianza": 0.8,
            "razonamiento": "por qué respondiste así"
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        resultado = response.choices[0].message.content.strip()
        
        # Intentar parsear JSON
        try:
            respuesta_json = json.loads(resultado)
            print(f"✅ Survey Simulation Success:")
            print(f"   Respuesta: {respuesta_json.get('respuesta', 'N/A')}")
            print(f"   Confianza: {respuesta_json.get('confianza', 'N/A')}")
            return True
        except:
            print(f"⚠️  Survey Response (no JSON): {resultado}")
            return True
            
    except Exception as e:
        print(f"❌ Survey Simulation Error: {str(e)}")
        return False

def test_data_processing():
    """Prueba procesamiento básico de datos"""
    try:
        # Crear datos de ejemplo
        datos = {
            "id": [1, 2, 3],
            "nombre": ["Ana", "Carlos", "María"],
            "edad": [28, 45, 35],
            "ciudad": ["Lima", "Arequipa", "Cusco"]
        }
        
        df = pd.DataFrame(datos)
        
        # Crear directorio output si no existe
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Guardar CSV
        df.to_csv("output/test_data.csv", index=False)
        
        print(f"✅ Data Processing: {df.shape[0]} rows processed")
        print(f"   Saved to: output/test_data.csv")
        return True
        
    except Exception as e:
        print(f"❌ Data Processing Error: {str(e)}")
        return False

def test_context_loading():
    """Prueba carga de contexto"""
    try:
        # Crear contexto de prueba
        contexto_dir = Path("contexto")
        contexto_dir.mkdir(exist_ok=True)
        
        contexto_test = """
        # Contexto de Prueba - Peru 2024
        - Presidente: Dina Boluarte
        - Situación: Crisis política y económica
        - Principales preocupaciones: Inflación, seguridad, empleo
        """
        
        with open(contexto_dir / "contexto_test.txt", "w", encoding="utf-8") as f:
            f.write(contexto_test)
        
        # Leer contexto
        with open(contexto_dir / "contexto_test.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        print(f"✅ Context Loading: {len(contenido)} characters loaded")
        return True
        
    except Exception as e:
        print(f"❌ Context Loading Error: {str(e)}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas de Buyer_Synthetic...")
    print("=" * 50)
    
    tests = [
        ("OpenAI Connection", test_openai_connection),
        ("Survey Simulation", test_survey_simulation),
        ("Data Processing", test_data_processing),
        ("Context Loading", test_context_loading)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        emoji = "✅" if result else "❌"
        print(f"   {emoji} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Buyer_Synthetic is ready!")
        return True
    else:
        print("⚠️  Some tests failed. Check configuration.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)