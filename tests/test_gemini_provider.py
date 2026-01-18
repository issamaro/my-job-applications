"""Tests for the Gemini LLM provider."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from services.llm.gemini import GeminiProvider


@pytest.fixture
def sample_profile():
    return {
        "personal_info": {
            "full_name": "John Doe",
            "email": "john@example.com",
        },
        "work_experiences": [
            {
                "id": 1,
                "company": "Acme Corp",
                "title": "Senior Developer",
                "start_date": "2020-01",
                "description": "Led development team",
            }
        ],
        "education": [],
        "skills": [{"id": 1, "name": "Python"}],
        "projects": [],
    }


@pytest.fixture
def gemini_provider():
    """Create a fresh GeminiProvider instance."""
    return GeminiProvider()


class TestGeminiProviderSuccess:
    """Tests for successful Gemini provider operations."""

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_successful_generation(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test successful generation returns expected JSON structure."""
        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = '{"job_title": "Software Engineer", "company_name": "TechCorp", "match_score": 85, "job_analysis": {}, "resume": {}}'

        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        result = await gemini_provider.analyze_and_generate(
            "Looking for Python developer...", sample_profile
        )

        assert result["job_title"] == "Software Engineer"
        assert result["company_name"] == "TechCorp"
        assert result["match_score"] == 85
        assert "job_analysis" in result
        assert "resume" in result

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_extracts_json_from_response(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that JSON is extracted correctly from Gemini response."""
        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Gemini with response_mime_type should return clean JSON, but test extraction anyway
        mock_response = MagicMock()
        mock_response.text = '{"job_title": "Engineer", "match_score": 75}'
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        result = await gemini_provider.analyze_and_generate("JD...", sample_profile)

        assert result["job_title"] == "Engineer"
        assert result["match_score"] == 75

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_uses_custom_model_from_env(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that custom model name from env is used."""
        mock_get_model.return_value = "gemini-1.5-pro"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = '{"job_title": "Test", "match_score": 50}'
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        await gemini_provider.analyze_and_generate("JD...", sample_profile)

        # Verify the model was passed to generate_content
        call_args = mock_client.aio.models.generate_content.call_args
        assert call_args.kwargs["model"] == "gemini-1.5-pro"


class TestGeminiProviderErrors:
    """Tests for Gemini provider error handling."""

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_api_error_401_invalid_key(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that 401 errors map to ValueError with API key message."""
        from google.genai import errors

        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        api_error = errors.APIError(code=401, response_json={"error": {"message": "Invalid API key"}})
        mock_client.aio.models.generate_content = AsyncMock(side_effect=api_error)

        with pytest.raises(ValueError) as exc_info:
            await gemini_provider.analyze_and_generate("JD...", sample_profile)

        assert "GEMINI_API_KEY" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_api_error_404_model_not_found(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that 404 errors map to ValueError with model not found."""
        from google.genai import errors

        mock_get_model.return_value = "nonexistent-model"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        api_error = errors.APIError(code=404, response_json={"error": {"message": "Model not found"}})
        mock_client.aio.models.generate_content = AsyncMock(side_effect=api_error)

        with pytest.raises(ValueError) as exc_info:
            await gemini_provider.analyze_and_generate("JD...", sample_profile)

        assert "Model not found" in str(exc_info.value)
        assert "nonexistent-model" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_api_error_429_rate_limit(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that 429 errors map to RuntimeError with rate limit message."""
        from google.genai import errors

        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        api_error = errors.APIError(code=429, response_json={"error": {"message": "Rate limit exceeded"}})
        mock_client.aio.models.generate_content = AsyncMock(side_effect=api_error)

        with pytest.raises(RuntimeError) as exc_info:
            await gemini_provider.analyze_and_generate("JD...", sample_profile)

        assert "busy" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_api_error_500_server_error(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that 500 errors map to RuntimeError with status/message."""
        from google.genai import errors

        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        api_error = errors.APIError(code=500, response_json={"error": {"message": "Internal server error"}})
        mock_client.aio.models.generate_content = AsyncMock(side_effect=api_error)

        with pytest.raises(RuntimeError) as exc_info:
            await gemini_provider.analyze_and_generate("JD...", sample_profile)

        error_msg = str(exc_info.value)
        assert "500" in error_msg
        assert "Internal server error" in error_msg

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_no_json_in_response(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that response without JSON raises ValueError."""
        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = "This is not JSON at all"
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            await gemini_provider.analyze_and_generate("JD...", sample_profile)

        assert "No JSON found" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_truncated_response_detected(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that truncated responses are detected."""
        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        # Response ends without closing brace
        mock_response.text = '{"job_title": "Engineer", "match_score": 75'
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            await gemini_provider.analyze_and_generate("JD...", sample_profile)

        assert "truncated" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @patch("services.llm.gemini._get_client")
    @patch("services.llm.gemini._get_model")
    async def test_connection_error_detected(
        self, mock_get_model, mock_get_client, gemini_provider, sample_profile
    ):
        """Test that connection errors are mapped to ConnectionError."""
        mock_get_model.return_value = "gemini-2.5-flash"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Simulate a connection error
        mock_client.aio.models.generate_content = AsyncMock(
            side_effect=Exception("Failed to connect to server")
        )

        with pytest.raises(ConnectionError) as exc_info:
            await gemini_provider.analyze_and_generate("JD...", sample_profile)

        assert "Could not connect" in str(exc_info.value)
