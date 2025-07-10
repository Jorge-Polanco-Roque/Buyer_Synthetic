"""
Funciones para cargar y manejar archivos de contexto.
"""

from pathlib import Path
from typing import Dict, List, Optional
import os

def cargar_contexto(archivo: str = None) -> str:
    """
    Carga el contexto desde archivos de texto.
    
    Args:
        archivo: Nombre del archivo de contexto (opcional)
        
    Returns:
        str: Contenido del contexto
    """
    
    contexto_dir = Path("contexto")
    
    if not contexto_dir.exists():
        contexto_dir.mkdir(parents=True, exist_ok=True)
        crear_contexto_base()
    
    # Si se especifica un archivo, cargar solo ese
    if archivo:
        ruta_archivo = contexto_dir / archivo
        if ruta_archivo.exists():
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"⚠️  Archivo no encontrado: {ruta_archivo}")
            return ""
    
    # Cargar todos los archivos de contexto
    contexto_completo = []
    
    archivos_contexto = [
        "contexto_general.txt",
        "contexto_politico.txt", 
        "perfiles_demograficos.txt"
    ]
    
    for archivo_nombre in archivos_contexto:
        ruta_archivo = contexto_dir / archivo_nombre
        if ruta_archivo.exists():
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                if contenido:
                    contexto_completo.append(f"## {archivo_nombre.replace('.txt', '').replace('_', ' ').title()}\n{contenido}")
    
    return "\n\n".join(contexto_completo)

def cargar_contexto_especifico(tipo_contexto: str) -> str:
    """
    Carga un contexto específico según el tipo.
    
    Args:
        tipo_contexto: Tipo de contexto ('politico', 'demografico', 'general')
        
    Returns:
        str: Contenido del contexto específico
    """
    
    mapeo_archivos = {
        'politico': 'contexto_politico.txt',
        'demografico': 'perfiles_demograficos.txt',
        'general': 'contexto_general.txt'
    }
    
    archivo = mapeo_archivos.get(tipo_contexto)
    if archivo:
        return cargar_contexto(archivo)
    else:
        print(f"⚠️  Tipo de contexto no reconocido: {tipo_contexto}")
        return ""

def listar_archivos_contexto() -> List[str]:
    """
    Lista todos los archivos de contexto disponibles.
    
    Returns:
        List[str]: Lista de nombres de archivos
    """
    
    contexto_dir = Path("contexto")
    if not contexto_dir.exists():
        return []
    
    archivos = []
    for archivo in contexto_dir.glob("*.txt"):
        archivos.append(archivo.name)
    
    return sorted(archivos)

def crear_contexto_base():
    """Crea archivos de contexto base si no existen"""
    
    contexto_dir = Path("contexto")
    contexto_dir.mkdir(parents=True, exist_ok=True)
    
    # Contexto general
    contexto_general = """
# Contexto General para Buyer Synthetic

## Propósito
Este sistema simula respuestas de encuestas utilizando inteligencia artificial para generar datos sintéticos realistas que reflejen comportamientos y opiniones de grupos demográficos específicos.

## Principios de Simulación
- Las respuestas deben ser coherentes con el perfil demográfico del encuestado
- Mantener consistencia en las respuestas relacionadas
- Reflejar variabilidad natural en las opiniones humanas
- Considerar factores culturales y socioeconómicos

## Instrucciones Generales
- Responder desde la perspectiva del perfil asignado
- Usar un lenguaje natural y conversacional
- Incluir elementos de incertidumbre cuando sea apropiado
- Evitar respuestas demasiado perfectas o artificiales
"""
    
    with open(contexto_dir / "contexto_general.txt", 'w', encoding='utf-8') as f:
        f.write(contexto_general)
    
    # Contexto político
    contexto_politico = """
# Contexto Político - Perú 2024-2026

## Situación Política Actual
- Presidente: Dina Boluarte (desde diciembre 2022)
- Congreso fragmentado con múltiples partidos
- Alta polarización política
- Protestas sociales intermitentes
- Crisis de gobernabilidad

## Principales Temas de Debate
- Reforma constitucional
- Anticorrupción
- Política económica
- Seguridad ciudadana
- Descentralización
- Política minera y ambiental

## Próximas Elecciones (2026)
- Elecciones presidenciales y congresales
- Posibles candidatos en evaluación
- Nuevos partidos políticos emergentes
- Electores jóvenes como factor clave

## Percepciones Comunes
- Desconfianza en instituciones políticas
- Demanda de renovación política
- Priorización de temas económicos
- Preocupación por la corrupción
"""
    
    with open(contexto_dir / "contexto_politico.txt", 'w', encoding='utf-8') as f:
        f.write(contexto_politico)
    
    # Perfiles demográficos
    perfiles_demograficos = """
# Perfiles Demográficos - Perú

## Por Nivel Socioeconómico
### NSE A (5%)
- Ingresos: S/ 10,000+ mensuales
- Educación: Superior completa
- Ocupación: Ejecutivos, profesionales independientes
- Preocupaciones: Inversiones, calidad de vida, educación hijos

### NSE B (15%)
- Ingresos: S/ 4,000 - S/ 10,000 mensuales
- Educación: Superior completa/técnica
- Ocupación: Profesionales, gerentes medios
- Preocupaciones: Estabilidad laboral, vivienda, educación

### NSE C (35%)
- Ingresos: S/ 2,000 - S/ 4,000 mensuales
- Educación: Secundaria completa/técnica
- Ocupación: Empleados, comerciantes
- Preocupaciones: Ingresos, seguridad, salud

### NSE D (25%)
- Ingresos: S/ 1,000 - S/ 2,000 mensuales
- Educación: Secundaria incompleta/completa
- Ocupación: Obreros, comerciantes menores
- Preocupaciones: Trabajo estable, necesidades básicas

### NSE E (20%)
- Ingresos: Menos de S/ 1,000 mensuales
- Educación: Primaria/secundaria incompleta
- Ocupación: Trabajos eventuales, informal
- Preocupaciones: Supervivencia, programas sociales

## Por Región
### Lima (33% población)
- Más urbanizada y cosmopolita
- Mayor acceso a servicios
- Diversidad cultural y económica

### Costa (11% población)
- Actividad pesquera y agrícola
- Ciudades intermedias
- Conexión con Lima

### Sierra (30% población)
- Actividad minera y agrícola
- Población mayoritariamente quechua
- Menores ingresos promedio

### Selva (26% población)
- Actividad agrícola y forestal
- Población dispersa
- Desafíos de conectividad
"""
    
    with open(contexto_dir / "perfiles_demograficos.txt", 'w', encoding='utf-8') as f:
        f.write(perfiles_demograficos)
    
    print("✅ Archivos de contexto base creados")

def agregar_contexto_personalizado(nombre_archivo: str, contenido: str) -> bool:
    """
    Agrega un archivo de contexto personalizado.
    
    Args:
        nombre_archivo: Nombre del archivo (sin extensión)
        contenido: Contenido del archivo
        
    Returns:
        bool: True si se creó exitosamente
    """
    
    try:
        contexto_dir = Path("contexto")
        contexto_dir.mkdir(parents=True, exist_ok=True)
        
        if not nombre_archivo.endswith('.txt'):
            nombre_archivo += '.txt'
        
        with open(contexto_dir / nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"✅ Contexto personalizado creado: {nombre_archivo}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando contexto: {str(e)}")
        return False

if __name__ == "__main__":
    # Ejemplo de uso
    print("Archivos de contexto disponibles:")
    for archivo in listar_archivos_contexto():
        print(f"  - {archivo}")
    
    print("\nCargando contexto completo...")
    contexto = cargar_contexto()
    print(f"Contexto cargado: {len(contexto)} caracteres")