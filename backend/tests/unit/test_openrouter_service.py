"""
Unit tests for OpenRouter service
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from app.services.openrouter import OpenRouterService, clean_json_string


class TestCleanJsonString:
    """Test the clean_json_string function"""

    def test_valid_json_unchanged(self):
        """Test that valid JSON is returned unchanged"""
        valid_json = '{"match_percentage": 85, "reasoning": "Good match"}'
        result = clean_json_string(valid_json)
        assert json.loads(result) == {"match_percentage": 85, "reasoning": "Good match"}

    def test_json_with_newlines(self):
        """Test that JSON with actual newlines is cleaned"""
        json_with_newlines = """{
  "match_percentage": 85,
  "reasoning": "This is a good match.
The candidate has strong experience."
}"""
        result = clean_json_string(json_with_newlines)
        parsed = json.loads(result)
        assert parsed["match_percentage"] == 85
        assert "The candidate has strong experience." in parsed["reasoning"]

    def test_json_with_tabs(self):
        """Test that JSON with tabs is cleaned"""
        json_with_tabs = '{"reasoning": "Section 1:\tGood fit\nSection 2:\tNeeds work"}'
        result = clean_json_string(json_with_tabs)
        parsed = json.loads(result)
        assert "Good fit" in parsed["reasoning"]
        assert "Needs work" in parsed["reasoning"]

    def test_json_with_multiple_control_chars(self):
        """Test that JSON with multiple control characters is cleaned"""
        json_with_control = '{"text": "Line 1\nLine 2\rLine 3\tTabbed"}'
        result = clean_json_string(json_with_control)
        parsed = json.loads(result)
        assert "Line 1" in parsed["text"]
        assert "Line 2" in parsed["text"]
        assert "Line 3" in parsed["text"]
        assert "Tabbed" in parsed["text"]

    def test_json_with_escaped_quotes(self):
        """Test that JSON with escaped quotes is handled correctly"""
        json_with_quotes = '{"text": "He said \\"hello\\""}'
        result = clean_json_string(json_with_quotes)
        parsed = json.loads(result)
        assert 'He said "hello"' in parsed["text"]

    def test_empty_json_object(self):
        """Test that empty JSON object is handled"""
        empty_json = "{}"
        result = clean_json_string(empty_json)
        assert json.loads(result) == {}

    def test_json_array(self):
        """Test that JSON arrays are handled"""
        json_array = '[{"name": "Test\nItem"}]'
        result = clean_json_string(json_array)
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert "Test" in parsed[0]["name"]


@pytest.mark.asyncio
class TestOpenRouterService:
    """Test the OpenRouterService class"""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for OpenRouter"""
        with patch('app.services.openrouter.get_settings') as mock:
            settings = Mock()
            settings.openrouter_base_url = "https://api.openrouter.ai/api/v1"
            settings.openrouter_api_key = "test-api-key"
            settings.openrouter_model = "anthropic/claude-3.5-sonnet"
            mock.return_value = settings
            yield mock

    @pytest.fixture
    def openrouter_service(self, mock_settings):
        """Create an OpenRouterService instance"""
        return OpenRouterService()

    async def test_analyze_job_match_success(self, openrouter_service):
        """Test successful job match analysis"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": '{"match_percentage": 85.5, "reasoning": "Strong match with relevant experience"}'
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json = Mock(return_value=mock_response)
            mock_response_obj.raise_for_status = Mock()

            mock_post = AsyncMock(return_value=mock_response_obj)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await openrouter_service.analyze_job_match(
                job_ad="Looking for a Python developer",
                resume="Experienced Python developer with 5 years"
            )

            assert result["match_percentage"] == 85.5
            assert result["reasoning"] == "Strong match with relevant experience"

    async def test_analyze_job_match_with_control_chars(self, openrouter_service):
        """Test job match analysis with control characters in response"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": """{
  "match_percentage": 90,
  "reasoning": "Excellent match.
Strong technical skills.

Key points:
- Python expertise
- FastAPI experience"
}"""
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json = Mock(return_value=mock_response)
            mock_response_obj.raise_for_status = Mock()

            mock_post = AsyncMock(return_value=mock_response_obj)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await openrouter_service.analyze_job_match(
                job_ad="Looking for a Python developer",
                resume="Experienced Python developer"
            )

            assert result["match_percentage"] == 90.0
            assert "Excellent match" in result["reasoning"]
            assert "Python expertise" in result["reasoning"]

    async def test_extract_job_application_fields_success(self, openrouter_service):
        """Test successful job application field extraction"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": """{
  "company_name": "Tech Corp",
  "role_name": "Senior Software Engineer",
  "extracted_content": "Clean job posting content"
}"""
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json = Mock(return_value=mock_response)
            mock_response_obj.raise_for_status = Mock()

            mock_post = AsyncMock(return_value=mock_response_obj)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await openrouter_service.extract_job_application_fields(
                job_ad="Tech Corp is hiring a Senior Software Engineer"
            )

            assert result["company_name"] == "Tech Corp"
            assert result["role_name"] == "Senior Software Engineer"
            assert result["extracted_content"] == "Clean job posting content"

    async def test_analyze_job_match_api_error(self, openrouter_service):
        """Test handling of API errors during job match analysis"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.raise_for_status = Mock(side_effect=Exception("API Error"))

            mock_post = AsyncMock(return_value=mock_response_obj)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            with pytest.raises(Exception) as exc_info:
                await openrouter_service.analyze_job_match(
                    job_ad="Job ad",
                    resume="Resume"
                )
            assert "API Error" in str(exc_info.value)

    async def test_extract_fields_with_unknown_values(self, openrouter_service):
        """Test extraction when company or role is unknown"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": '{"company_name": "Unknown", "role_name": "Software Engineer", "extracted_content": "Content"}'
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json = Mock(return_value=mock_response)
            mock_response_obj.raise_for_status = Mock()

            mock_post = AsyncMock(return_value=mock_response_obj)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await openrouter_service.extract_job_application_fields(
                job_ad="Seeking a software engineer"
            )

            assert result["company_name"] == "Unknown"
            assert result["role_name"] == "Software Engineer"

    async def test_analyze_job_match_percentage_conversion(self, openrouter_service):
        """Test that match percentage is converted to float"""
        mock_response = {
            "choices": [{
                "message": {
                    "content": '{"match_percentage": 75, "reasoning": "Good match"}'
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.json = Mock(return_value=mock_response)
            mock_response_obj.raise_for_status = Mock()

            mock_post = AsyncMock(return_value=mock_response_obj)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await openrouter_service.analyze_job_match(
                job_ad="Job ad",
                resume="Resume"
            )

            assert isinstance(result["match_percentage"], float)
            assert result["match_percentage"] == 75.0
