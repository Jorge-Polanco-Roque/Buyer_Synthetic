"""Unit tests for data models."""

import pytest
from pydantic import ValidationError
from buyer_synthetic.models.survey import SurveyProfile, SurveyQuestion, SurveyResponse
from buyer_synthetic.models.analysis import StatisticalTest, AnalysisResult


class TestSurveyProfile:
    """Tests for SurveyProfile model."""
    
    def test_valid_profile_creation(self, sample_profile):
        """Test creating a valid survey profile."""
        assert sample_profile.nombre == "María García López"
        assert sample_profile.edad == 35
        assert sample_profile.nse == "C"
    
    def test_age_validation(self):
        """Test age validation rules."""
        with pytest.raises(ValidationError) as exc_info:
            SurveyProfile(
                nombre="Test",
                edad=17,  # Too young
                genero="F",
                ciudad="Lima", 
                region="Lima",
                nse="C",
                ocupacion="Student",
                educacion="Secundaria",
                estado_civil="Soltera",
                ingresos=1000
            )
        
        assert "Age must be 18 or older" in str(exc_info.value)
    
    def test_income_validation(self):
        """Test income format validation."""
        profile = SurveyProfile(
            nombre="Test",
            edad=25,
            genero="M",
            ciudad="Lima",
            region="Lima", 
            nse="C",
            ocupacion="Worker",
            educacion="Técnica",
            estado_civil="Soltero",
            ingresos="S/ 2,500"  # String format
        )
        
        assert profile.ingresos == 2500  # Should be converted to int


class TestSurveyQuestion:
    """Tests for SurveyQuestion model."""
    
    def test_valid_question_creation(self, sample_question):
        """Test creating a valid survey question."""
        assert sample_question.tipo == "multiple"
        assert len(sample_question.opciones) == 3
    
    def test_multiple_choice_validation(self):
        """Test validation for multiple choice questions."""
        with pytest.raises(ValidationError) as exc_info:
            SurveyQuestion(
                pregunta="Test question?",
                tipo="multiple",
                opciones=None  # Missing options
            )
        
        assert "Multiple choice questions must have options" in str(exc_info.value)
    
    def test_scale_validation(self):
        """Test validation for scale questions."""
        with pytest.raises(ValidationError) as exc_info:
            SurveyQuestion(
                pregunta="Rate this?",
                tipo="escala",
                escala=None  # Missing scale
            )
        
        assert "Scale questions must have scale definition" in str(exc_info.value)
    
    def test_valid_scale_format(self):
        """Test valid scale format."""
        question = SurveyQuestion(
            pregunta="Rate from 1 to 10",
            tipo="escala",
            escala="1-10"
        )
        assert question.escala == "1-10"


class TestSurveyResponse:
    """Tests for SurveyResponse model."""
    
    def test_valid_response_creation(self, sample_response):
        """Test creating a valid survey response."""
        assert sample_response.respuesta == "Candidato A"
        assert sample_response.confianza == 0.8
    
    def test_confidence_validation(self):
        """Test confidence level validation."""
        with pytest.raises(ValidationError) as exc_info:
            SurveyResponse(
                profile_id="123",
                question_id="456",
                respuesta="Test",
                confianza=1.5  # Invalid confidence > 1.0
            )
        
        assert "Confidence must be between 0.0 and 1.0" in str(exc_info.value)


class TestStatisticalTest:
    """Tests for StatisticalTest model."""
    
    def test_valid_test_creation(self):
        """Test creating a valid statistical test result."""
        test = StatisticalTest(
            test_type="chi_square",
            test_statistic=15.67,
            p_value=0.003,
            degrees_of_freedom=4,
            is_significant=True,
            variables_tested=["nse", "voting_intention"],
            description="Chi-square test of independence",
            interpretation="Significant association found"
        )
        
        assert test.test_type == "chi_square"
        assert test.is_significant is True
    
    def test_p_value_validation(self):
        """Test p-value validation."""
        with pytest.raises(ValidationError) as exc_info:
            StatisticalTest(
                test_type="t_test",
                test_statistic=2.5,
                p_value=1.5,  # Invalid p-value > 1.0
                is_significant=False,
                variables_tested=["var1", "var2"],
                description="Test",
                interpretation="Test interpretation"
            )
        
        assert "P-value must be between 0.0 and 1.0" in str(exc_info.value)
    
    def test_confidence_interval_validation(self):
        """Test confidence interval validation."""
        with pytest.raises(ValidationError) as exc_info:
            StatisticalTest(
                test_type="t_test",
                test_statistic=2.5,
                p_value=0.05,
                is_significant=True,
                confidence_interval=[0.8, 0.2],  # Invalid: lower > upper
                variables_tested=["var1", "var2"],
                description="Test",
                interpretation="Test interpretation"
            )
        
        assert "Lower bound must be less than upper bound" in str(exc_info.value)


class TestAnalysisResult:
    """Tests for AnalysisResult model."""
    
    def test_valid_analysis_creation(self):
        """Test creating a valid analysis result."""
        analysis = AnalysisResult(
            survey_id="test_survey",
            total_responses=100,
            sample_composition={"nse": {"A": 0.1, "B": 0.2}},
            completion_rate=0.95,
            average_confidence=0.8,
            descriptive_statistics={"mean_age": 35.5}
        )
        
        assert analysis.total_responses == 100
        assert analysis.completion_rate == 0.95
    
    def test_rate_validation(self):
        """Test validation of rates."""
        with pytest.raises(ValidationError) as exc_info:
            AnalysisResult(
                survey_id="test",
                total_responses=100,
                sample_composition={},
                completion_rate=1.5,  # Invalid rate > 1.0
                average_confidence=0.8,
                descriptive_statistics={}
            )
        
        assert "Rates must be between 0.0 and 1.0" in str(exc_info.value)
    
    def test_insights_management(self):
        """Test adding insights and recommendations."""
        analysis = AnalysisResult(
            survey_id="test",
            total_responses=100,
            sample_composition={},
            completion_rate=0.95,
            average_confidence=0.8,
            descriptive_statistics={}
        )
        
        analysis.add_insight("Test insight")
        analysis.add_recommendation("Test recommendation")
        
        assert "Test insight" in analysis.key_insights
        assert "Test recommendation" in analysis.recommendations
        
        # Test no duplicates
        analysis.add_insight("Test insight")
        assert analysis.key_insights.count("Test insight") == 1