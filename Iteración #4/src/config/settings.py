"""
Configuración centralizada del sistema Buyer_Synthetic
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración del sistema"""
    
    # Rutas del proyecto
    BASE_DIR = Path(__file__).parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    OUTPUT_DIR = DATA_DIR / "output"
    
    # API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Survey Configuration
    MIN_SAMPLE_SIZE = 100
    MAX_SAMPLE_SIZE = 1000
    DEFAULT_SAMPLE_SIZE = 300
    
    # Demographics Peru 2024
    NSE_DISTRIBUTION = {
        "A": 0.05,  # 5%
        "B": 0.15,  # 15%
        "C": 0.35,  # 35%
        "D": 0.25,  # 25%
        "E": 0.20   # 20%
    }
    
    REGION_DISTRIBUTION = {
        "Lima": 0.33,
        "Costa": 0.11,
        "Sierra": 0.30,
        "Selva": 0.26
    }
    
    AGE_RANGES = {
        "18-24": 0.15,
        "25-34": 0.20,
        "35-44": 0.18,
        "45-54": 0.18,
        "55-64": 0.15,
        "65+": 0.14
    }
    
    # Preguntas electorales Peru 2026
    ELECTORAL_QUESTIONS = [
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
        },
        {
            "id": "principal_problema",
            "pregunta": "¿Cuál consideras que es el principal problema del país?",
            "tipo": "multiple",
            "opciones": ["Corrupción", "Economía", "Seguridad ciudadana", "Desempleo", "Salud", "Educación"]
        },
        {
            "id": "confianza_instituciones",
            "pregunta": "¿Qué tan confiado estás en las instituciones democráticas?",
            "tipo": "escala",
            "escala": "1-10"
        },
        {
            "id": "expectativa_economia",
            "pregunta": "¿Cómo crees que estará la economía del país en los próximos 6 meses?",
            "tipo": "multiple",
            "opciones": ["Mejor", "Igual", "Peor", "No sabe"]
        },
        {
            "id": "prioridad_gobierno",
            "pregunta": "¿Cuál debería ser la primera prioridad del próximo gobierno?",
            "tipo": "multiple",
            "opciones": ["Combatir la corrupción", "Mejorar la economía", "Fortalecer la seguridad", "Reformar la salud", "Mejorar la educación"]
        },
        {
            "id": "reforma_constitucional",
            "pregunta": "¿Estás a favor de una reforma constitucional?",
            "tipo": "multiple",
            "opciones": ["Muy a favor", "A favor", "En contra", "Muy en contra", "No sabe/No opina"]
        },
        {
            "id": "descentralizacion",
            "pregunta": "¿Consideras que Lima tiene demasiado poder político frente a las regiones?",
            "tipo": "multiple",
            "opciones": ["Definitivamente sí", "Probablemente sí", "Probablemente no", "Definitivamente no", "No sabe"]
        },
        {
            "id": "medios_informacion",
            "pregunta": "¿Cuál es tu principal fuente de información política?",
            "tipo": "multiple",
            "opciones": ["Televisión", "Redes sociales", "Radio", "Periódicos", "Conversaciones", "No me informo"]
        },
        {
            "id": "participacion_electoral",
            "pregunta": "¿Qué tan probable es que votes en las próximas elecciones?",
            "tipo": "escala",
            "escala": "1-10"
        }
    ]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def ensure_directories(cls):
        """Crear directorios necesarios"""
        directories = [
            cls.DATA_DIR / "input",
            cls.DATA_DIR / "output", 
            cls.DATA_DIR / "temp",
            cls.LOGS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validar configuración"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        cls.ensure_directories()
        return True

# Instancia global de configuración
settings = Settings()
settings.validate_config()