"""
Configuración centralizada del sistema Buyer_Synthetic
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class SurveyMode(str, Enum):
    """Modos de operación de encuestas"""
    DEMO = "Demo Mode"
    GENAI = "GenAI Mode"

class Settings:
    """Configuración del sistema"""
    
    # Rutas del proyecto
    BASE_DIR = Path(__file__).parent.parent.parent.parent
    SRC_DIR = BASE_DIR / "src"
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    OUTPUT_DIR = DATA_DIR / "output"
    
    # Vault Configuration
    VAULT_ENABLED = os.getenv("VAULT_ENABLED", "false").lower() == "true"
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://localhost:8200")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")
    
    def __init__(self):
        """Initialize settings with optional Vault integration."""
        self._secret_manager = None
        if self.VAULT_ENABLED:
            self._init_vault()
    
    def _init_vault(self):
        """Initialize Vault client if enabled."""
        try:
            from .vault_client import get_secret_manager
            self._secret_manager = get_secret_manager()
            if self._secret_manager:
                logger.info("Vault secrets manager initialized successfully")
            else:
                logger.warning("Vault enabled but not authenticated, falling back to env vars")
        except ImportError:
            logger.warning("Vault client not available, install hvac package for Vault support")
        except Exception as e:
            logger.error(f"Failed to initialize Vault: {e}")
    
    def _get_secret_or_env(self, vault_key: str, env_key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from Vault if available, otherwise from environment."""
        if self._secret_manager:
            try:
                vault_value = self._secret_manager.get_api_key(vault_key)
                if vault_value:
                    return vault_value
            except Exception as e:
                logger.debug(f"Failed to get secret from Vault: {e}")
        
        return os.getenv(env_key, default)
    
    # API Configuration
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return self._get_secret_or_env("openai", "OPENAI_API_KEY")
    
    @property
    def DEFAULT_MODEL(self) -> str:
        return os.getenv("DEFAULT_MODEL", "gpt-4")
    
    @property
    def TEMPERATURE(self) -> float:
        return float(os.getenv("TEMPERATURE", "0.7"))
    
    @property
    def MAX_TOKENS(self) -> int:
        return int(os.getenv("MAX_TOKENS", "2000"))
    
    # Survey Configuration
    MIN_SAMPLE_SIZE = 100
    MAX_SAMPLE_SIZE = 1000
    DEFAULT_SAMPLE_SIZE = 300
    
    # Survey Mode Configuration
    DEFAULT_SURVEY_MODE = SurveyMode.DEMO
    
    # LangGraph Configuration
    LANGGRAPH_MAX_RETRIES = 2
    LANGGRAPH_VALIDATION_THRESHOLD = 0.7
    
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
        """Validar configuración (no obligatoria para demo)"""
        cls.ensure_directories()
        return True

# Instancia global de configuración
settings = Settings()
settings.validate_config()