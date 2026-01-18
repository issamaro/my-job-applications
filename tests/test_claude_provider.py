"""Tests for the Claude LLM provider."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import anthropic

from services.llm.claude import ClaudeProvider


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
def claude_provider():
    """Create a fresh ClaudeProvider instance."""
    return ClaudeProvider()


class TestClaudeProviderSuccess:
    """Tests for successful Claude provider operations."""

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_successful_generation(self, mock_get_client, claude_provider, sample_profile):
        """Test successful generation returns expected JSON structure."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        expected_response = {
            "job_title": "Software Engineer",
            "company_name": "TechCorp",
            "match_score": 85,
            "job_analysis": {
                "required_skills": [{"name": "Python", "matched": True}],
                "preferred_skills": [],
            },
            "resume": {
                "summary": "Experienced developer...",
                "work_experiences": [],
            },
        }

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text=f'{{"job_title": "Software Engineer", "company_name": "TechCorp", "match_score": 85, "job_analysis": {{"required_skills": [{{"name": "Python", "matched": true}}], "preferred_skills": []}}, "resume": {{"summary": "Experienced developer...", "work_experiences": []}}}}')
        ]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await claude_provider.analyze_and_generate(
            "Looking for Python developer...", sample_profile
        )

        assert result["job_title"] == "Software Engineer"
        assert result["company_name"] == "TechCorp"
        assert result["match_score"] == 85
        assert "job_analysis" in result
        assert "resume" in result

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_extracts_json_from_mixed_response(self, mock_get_client, claude_provider, sample_profile):
        """Test that JSON is extracted from response with surrounding text."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='Here is the analysis:\n\n{"job_title": "Engineer", "match_score": 75}\n\nLet me know if you need more.'
            )
        ]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await claude_provider.analyze_and_generate("JD...", sample_profile)

        assert result["job_title"] == "Engineer"
        assert result["match_score"] == 75

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_language_parameter_passed(self, mock_get_client, claude_provider, sample_profile):
        """Test that language parameter affects the prompt."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text='{"job_title": "Ingénieur", "match_score": 80}')
        ]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await claude_provider.analyze_and_generate(
            "JD...", sample_profile, language="fr"
        )

        # Verify the call was made with French instructions in the prompt
        call_args = mock_client.messages.create.call_args
        user_content = call_args.kwargs["messages"][0]["content"]
        assert "French" in user_content


class TestClaudeProviderErrors:
    """Tests for Claude provider error handling."""

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_connection_error_mapped(self, mock_get_client, claude_provider, sample_profile):
        """Test that API connection errors map to ConnectionError."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic.APIConnectionError(request=MagicMock())
        )

        with pytest.raises(ConnectionError) as exc_info:
            await claude_provider.analyze_and_generate("JD...", sample_profile)

        assert "Could not connect" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_rate_limit_error_mapped(self, mock_get_client, claude_provider, sample_profile):
        """Test that rate limit errors map to RuntimeError."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic.RateLimitError(
                message="Rate limited",
                response=mock_response,
                body={},
            )
        )

        with pytest.raises(RuntimeError) as exc_info:
            await claude_provider.analyze_and_generate("JD...", sample_profile)

        assert "busy" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_api_status_error_mapped(self, mock_get_client, claude_provider, sample_profile):
        """Test that API status errors map to RuntimeError with status/message."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_client.messages.create = AsyncMock(
            side_effect=anthropic.APIStatusError(
                message="Internal error",
                response=mock_response,
                body={},
            )
        )

        with pytest.raises(RuntimeError) as exc_info:
            await claude_provider.analyze_and_generate("JD...", sample_profile)

        error_msg = str(exc_info.value)
        assert "500" in error_msg
        assert "Internal error" in error_msg

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_no_json_in_response(self, mock_get_client, claude_provider, sample_profile):
        """Test that response without JSON raises ValueError."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not JSON at all")]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            await claude_provider.analyze_and_generate("JD...", sample_profile)

        assert "No JSON found" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("services.llm.claude._get_client")
    async def test_truncated_response_detected(self, mock_get_client, claude_provider, sample_profile):
        """Test that truncated responses are detected."""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        mock_response = MagicMock()
        # Response ends without closing brace
        mock_response.content = [MagicMock(text='{"job_title": "Engineer", "match_score": 75')]
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            await claude_provider.analyze_and_generate("JD...", sample_profile)

        assert "truncated" in str(exc_info.value).lower()
