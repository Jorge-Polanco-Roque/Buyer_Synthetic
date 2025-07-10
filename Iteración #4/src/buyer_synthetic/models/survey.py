"""Survey-related data models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import Field, validator

from .base import BaseModel


class NSELevel(str, Enum):
    """Socioeconomic level classification."""
    
    A = "A"  # High income
    B = "B"  # Upper middle income  
    C = "C"  # Middle income
    D = "D"  # Lower middle income
    E = "E"  # Low income


class Region(str, Enum):
    """Geographic regions of Peru."""
    
    LIMA = "Lima"
    COSTA = "Costa" 
    SIERRA = "Sierra"
    SELVA = "Selva"


class Gender(str, Enum):
    """Gender classification."""
    
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    PREFER_NOT_SAY = "P"


class QuestionType(str, Enum):
    """Survey question types."""
    
    MULTIPLE_CHOICE = "multiple"
    SCALE = "escala"
    OPEN_ENDED = "abierta"
    BINARY = "binary"


class SurveyProfile(BaseModel):
    """Demographic profile for survey participant."""
    
    # Basic demographics
    nombre: str = Field(..., description="Full name of the participant")
    edad: int = Field(..., ge=18, le=100, description="Age in years")
    genero: Gender = Field(..., description="Gender identity")
    
    # Geographic information
    ciudad: str = Field(..., description="City of residence")
    region: Region = Field(..., description="Geographic region")
    
    # Socioeconomic information
    nse: NSELevel = Field(..., description="Socioeconomic level")
    ocupacion: str = Field(..., description="Occupation")
    educacion: str = Field(..., description="Education level")
    estado_civil: str = Field(..., description="Marital status")
    ingresos: Union[int, str] = Field(..., description="Monthly income")
    
    @validator('edad')
    def validate_age(cls, v):
        """Validate age is reasonable for voting."""
        if v < 18:
            raise ValueError('Age must be 18 or older for voting eligibility')
        return v
    
    @validator('ingresos')
    def validate_income(cls, v):
        """Validate income format."""
        if isinstance(v, str):
            # Remove currency symbols and commas
            cleaned = v.replace('S/', '').replace(',', '').strip()
            if cleaned.isdigit():
                return int(cleaned)
        return v
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "nombre": "María García López",
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
        }


class SurveyQuestion(BaseModel):
    """Survey question definition."""
    
    pregunta: str = Field(..., description="Question text")
    tipo: QuestionType = Field(..., description="Question type")
    opciones: Optional[List[str]] = Field(None, description="Options for multiple choice")
    escala: Optional[str] = Field(None, description="Scale definition (e.g., '1-10')")
    requerida: bool = Field(True, description="Whether question is required")
    categoria: Optional[str] = Field(None, description="Question category")
    
    @validator('opciones')
    def validate_opciones(cls, v, values):
        """Validate options for multiple choice questions."""
        if values.get('tipo') == QuestionType.MULTIPLE_CHOICE and not v:
            raise ValueError('Multiple choice questions must have options')
        return v
    
    @validator('escala') 
    def validate_escala(cls, v, values):
        """Validate scale format."""
        if values.get('tipo') == QuestionType.SCALE:
            if not v:
                raise ValueError('Scale questions must have scale definition')
            # Validate scale format (e.g., "1-10")
            if '-' in v:
                try:
                    start, end = v.split('-')
                    int(start), int(end)
                except ValueError:
                    raise ValueError('Scale must be in format "start-end" (e.g., "1-10")')
        return v
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "pregunta": "¿Por quién votarías en las próximas elecciones?",
                "tipo": "multiple",
                "opciones": ["Candidato A", "Candidato B", "Voto en blanco"],
                "requerida": True,
                "categoria": "Electoral"
            }
        }


class SurveyResponse(BaseModel):
    """Response to a survey question."""
    
    # Profile reference
    profile_id: str = Field(..., description="Reference to survey profile")
    
    # Question reference  
    question_id: str = Field(..., description="Reference to question")
    
    # Response data
    respuesta: Union[str, int, float] = Field(..., description="Response value")
    confianza: float = Field(0.5, ge=0.0, le=1.0, description="Confidence level")
    razonamiento: Optional[str] = Field(None, description="Reasoning behind response")
    
    # Metadata
    tiempo_respuesta: Optional[float] = Field(None, description="Time taken to respond (seconds)")
    metadatos: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('confianza')
    def validate_confidence(cls, v):
        """Validate confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "profile_id": "profile_123",
                "question_id": "intent_voto",
                "respuesta": "Candidato A",
                "confianza": 0.8,
                "razonamiento": "Coincide con mis valores políticos",
                "tiempo_respuesta": 15.5
            }
        }