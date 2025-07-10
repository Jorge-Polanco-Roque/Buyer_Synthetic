#!/usr/bin/env python3
"""
Script principal para ejecutar el sistema Buyer_Synthetic.
Sistema de simulación de encuestas con AI para investigación de mercado.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from agentes.flujo import ejecutar_flujo_principal
from viz.viz_flujo import generar_diagrama_flujo

def main():
    """Función principal del sistema"""
    print("🚀 Iniciando Buyer_Synthetic - Sistema de Encuestas con AI")
    print("=" * 60)
    
    try:
        # Ejecutar flujo principal
        print("📊 Ejecutando flujo de procesamiento...")
        ejecutar_flujo_principal()
        
        # Generar visualización del flujo
        print("📈 Generando diagrama de flujo...")
        generar_diagrama_flujo()
        
        print("✅ Proceso completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())