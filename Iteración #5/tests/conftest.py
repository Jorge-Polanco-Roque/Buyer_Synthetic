"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from typing import Generator
import pandas as pd
import pytest
from unittest.mock import Mock

from buyer_synthetic.models.survey import SurveyProfile, SurveyQuestion, SurveyResponse
from buyer_synthetic.models.analysis import AnalysisResult
from buyer_synthetic.agents import SurveyCreatorAgent


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_profile() -> SurveyProfile:
    """Create a sample survey profile."""
    return SurveyProfile(
        nombre="María García López",
        edad=35,
        genero="F",
        ciudad="Lima",
        region="Lima",
        nse="C",
        ocupacion="Ingeniera",
        educacion="Universitaria",
        estado_civil="Casada",
        ingresos=3500
    )


@pytest.fixture
def sample_question() -> SurveyQuestion:
    """Create a sample survey question."""
    return SurveyQuestion(
        pregunta="¿Por quién votarías en las próximas elecciones?",
        tipo="multiple",
        opciones=["Candidato A", "Candidato B", "Voto en blanco"],
        requerida=True,
        categoria="Electoral"
    )


@pytest.fixture
def sample_response(sample_profile, sample_question) -> SurveyResponse:
    """Create a sample survey response."""
    return SurveyResponse(
        profile_id=str(sample_profile.id),
        question_id=str(sample_question.id),
        respuesta="Candidato A",
        confianza=0.8,
        razonamiento="Coincide con mis valores",
        tiempo_respuesta=15.5
    )


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame with survey profiles."""
    return pd.DataFrame([
        {
            "id": 1,
            "nombre": "Juan Pérez",
            "edad": 30,
            "genero": "M",
            "ciudad": "Lima",
            "region": "Lima",
            "nse": "C",
            "ocupacion": "Ingeniero",
            "educacion": "Universitaria",
            "estado_civil": "Soltero",
            "ingresos": 3000
        },
        {
            "id": 2,
            "nombre": "María García",
            "edad": 28,
            "genero": "F",
            "ciudad": "Arequipa",
            "region": "Sierra",
            "nse": "B",
            "ocupacion": "Doctora",
            "educacion": "Universitaria",
            "estado_civil": "Casada",
            "ingresos": 4500
        }
    ])


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"respuesta": "Test response", "confianza": 0.8}'
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def survey_creator() -> SurveyCreatorAgent:
    """Create a SurveyCreatorAgent instance."""
    return SurveyCreatorAgent(sample_size=10)


# Markers for different test types
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests") 
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "openai: Tests requiring OpenAI API")


# Skip OpenAI tests if no API key
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment."""
    import os
    
    if not os.getenv("OPENAI_API_KEY"):
        skip_openai = pytest.mark.skip(reason="OpenAI API key not available")
        for item in items:
            if "openai" in item.keywords:
                item.add_marker(skip_openai)