"""Analysis result data models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import Field, validator

from .base import BaseModel


class TestType(str, Enum):
    """Statistical test types."""
    
    CHI_SQUARE = "chi_square"
    T_TEST = "t_test"
    ANOVA = "anova"
    CORRELATION = "correlation"
    PROPORTIONS = "proportions"


class SignificanceLevel(float, Enum):
    """Common significance levels."""
    
    VERY_HIGH = 0.001  # 99.9% confidence
    HIGH = 0.01       # 99% confidence
    MEDIUM = 0.05     # 95% confidence
    LOW = 0.10        # 90% confidence


class EffectSize(str, Enum):
    """Effect size classifications."""
    
    VERY_SMALL = "very_small"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"


class StatisticalTest(BaseModel):
    """Results of a statistical test."""
    
    test_type: TestType = Field(..., description="Type of statistical test")
    test_statistic: float = Field(..., description="Test statistic value")
    p_value: float = Field(..., description="P-value of the test")
    degrees_of_freedom: Optional[int] = Field(None, description="Degrees of freedom")
    
    # Interpretation
    is_significant: bool = Field(..., description="Whether result is statistically significant")
    significance_level: SignificanceLevel = Field(SignificanceLevel.MEDIUM, description="Significance level used")
    effect_size: Optional[float] = Field(None, description="Effect size measure")
    effect_size_interpretation: Optional[EffectSize] = Field(None, description="Effect size interpretation")
    
    # Additional metrics
    confidence_interval: Optional[List[float]] = Field(None, description="Confidence interval [lower, upper]")
    sample_sizes: Optional[Dict[str, int]] = Field(None, description="Sample sizes for groups")
    
    # Context
    variables_tested: List[str] = Field(..., description="Variables involved in the test")
    description: str = Field(..., description="Human-readable description of the test")
    interpretation: str = Field(..., description="Interpretation of the results")
    
    @validator('p_value')
    def validate_p_value(cls, v):
        """Validate p-value is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('P-value must be between 0.0 and 1.0')
        return v
    
    @validator('confidence_interval')
    def validate_confidence_interval(cls, v):
        """Validate confidence interval format."""
        if v is not None:
            if len(v) != 2:
                raise ValueError('Confidence interval must have exactly 2 values')
            if v[0] > v[1]:
                raise ValueError('Lower bound must be less than upper bound')
        return v
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "test_type": "chi_square",
                "test_statistic": 15.67,
                "p_value": 0.003,
                "degrees_of_freedom": 4,
                "is_significant": True,
                "significance_level": 0.05,
                "effect_size": 0.31,
                "effect_size_interpretation": "medium",
                "variables_tested": ["nse", "voting_intention"],
                "description": "Chi-square test of independence between NSE and voting intention",
                "interpretation": "There is a significant association between socioeconomic level and voting intention"
            }
        }


class AnalysisResult(BaseModel):
    """Complete analysis results for a survey."""
    
    # Basic information
    survey_id: str = Field(..., description="Survey identifier")
    total_responses: int = Field(..., description="Total number of responses")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Date of analysis")
    
    # Sample composition
    sample_composition: Dict[str, Any] = Field(..., description="Demographic composition of sample")
    
    # Data quality metrics
    completion_rate: float = Field(..., ge=0.0, le=1.0, description="Survey completion rate")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average response confidence")
    
    # Analysis results
    descriptive_statistics: Dict[str, Any] = Field(..., description="Descriptive statistics")
    statistical_tests: List[StatisticalTest] = Field(default_factory=list, description="Statistical test results")
    correlations: Optional[Dict[str, Any]] = Field(None, description="Correlation analysis")
    
    # Insights and interpretations
    key_insights: List[str] = Field(default_factory=list, description="Key insights from analysis")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on results")
    
    # Visualizations
    visualization_paths: List[str] = Field(default_factory=list, description="Paths to generated visualizations")
    
    # Metadata
    analysis_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters used in analysis")
    processing_time: Optional[float] = Field(None, description="Time taken for analysis (seconds)")
    
    @validator('completion_rate', 'average_confidence')
    def validate_rates(cls, v):
        """Validate rates are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Rates must be between 0.0 and 1.0')
        return v
    
    @validator('total_responses')
    def validate_total_responses(cls, v):
        """Validate total responses is positive."""
        if v < 0:
            raise ValueError('Total responses must be non-negative')
        return v
    
    def add_insight(self, insight: str) -> None:
        """Add a key insight to the analysis."""
        if insight not in self.key_insights:
            self.key_insights.append(insight)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the analysis."""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
    
    def get_significant_tests(self) -> List[StatisticalTest]:
        """Get only statistically significant tests."""
        return [test for test in self.statistical_tests if test.is_significant]
    
    class Config:
        """Model configuration."""
        
        schema_extra = {
            "example": {
                "survey_id": "survey_2024_01",
                "total_responses": 500,
                "sample_composition": {
                    "nse_distribution": {"A": 0.05, "B": 0.15, "C": 0.35, "D": 0.25, "E": 0.20},
                    "age_stats": {"mean": 42.3, "median": 41.0, "std": 15.2}
                },
                "completion_rate": 0.95,
                "average_confidence": 0.78,
                "key_insights": [
                    "Strong correlation between NSE and voting intention",
                    "Age significantly affects trust in institutions"
                ],
                "recommendations": [
                    "Target messaging differently by socioeconomic segment",
                    "Focus on trust-building among younger demographics"
                ]
            }
        }