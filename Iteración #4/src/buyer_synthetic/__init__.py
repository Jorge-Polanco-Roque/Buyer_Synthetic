"""
Buyer Synthetic™ - AI-powered survey analysis platform.

A comprehensive platform for creating representative demographic samples,
executing AI-powered surveys, and generating detailed statistical analysis
with visualizations.

Author: Buyer Synthetic Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Buyer Synthetic Team"
__email__ = "contact@buyersynthetic.com"
__license__ = "MIT"

# Public API exports
from .agents import (
    SurveyCreatorAgent,
    SurveyExecutorAgent, 
    ResultsVisualizerAgent
)
from .analysis import StatisticalAnalyzer
from .utils.logger import get_logger
from .config.settings import Settings
from .models import (
    SurveyProfile,
    SurveyQuestion,
    SurveyResponse,
    AnalysisResult
)

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
    
    # Core functionality
    "SurveyCreatorAgent",
    "SurveyExecutorAgent",
    "ResultsVisualizerAgent",
    "StatisticalAnalyzer",
    "get_logger",
    "Settings",
    
    # Data models
    "SurveyProfile",
    "SurveyQuestion", 
    "SurveyResponse",
    "AnalysisResult",
]