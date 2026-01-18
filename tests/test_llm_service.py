"""Integration tests for the LLM service module.

These tests verify the service interface works correctly with the
lazy-loading wrapper and provider abstraction.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import anthropic


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


@pytest.mark.asyncio
@patch("services.llm.claude._get_client")
async def test_analyze_and_generate_success(mock_get_client, sample_profile):
    """Test successful LLM response parsing through the service wrapper."""
    # Reset the lazy service singleton to ensure fresh provider
    from services.llm import llm_service
    llm_service._instance = None

    mock_client = AsyncMock()
    mock_get_client.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text='{"job_title": "Software Engineer", "company_name": "TechCorp", "match_score": 85, "job_analysis": {}, "resume": {}}'
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    result = await llm_service.analyze_and_generate(
        "We are looking for a Python developer...", sample_profile
    )

    assert result["job_title"] == "Software Engineer"
    assert result["match_score"] == 85


@pytest.mark.asyncio
@patch("services.llm.claude._get_client")
async def test_analyze_and_generate_extracts_json(mock_get_client, sample_profile):
    """Test that LLM service extracts JSON from response with surrounding text."""
    from services.llm import llm_service
    llm_service._instance = None

    mock_client = AsyncMock()
    mock_get_client.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text='Here is the analysis:\n\n{"job_title": "Engineer", "match_score": 75, "job_analysis": {}, "resume": {}}\n\nLet me know if you need more details.'
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    result = await llm_service.analyze_and_generate("JD text...", sample_profile)

    assert result["job_title"] == "Engineer"


@pytest.mark.asyncio
@patch("services.llm.claude._get_client")
async def test_analyze_and_generate_connection_error(mock_get_client, sample_profile):
    """Test handling of API connection errors."""
    from services.llm import llm_service
    llm_service._instance = None

    mock_client = AsyncMock()
    mock_get_client.return_value = mock_client
    mock_client.messages.create = AsyncMock(
        side_effect=anthropic.APIConnectionError(request=MagicMock())
    )

    with pytest.raises(ConnectionError) as exc_info:
        await llm_service.analyze_and_generate("JD text...", sample_profile)

    assert "Could not connect" in str(exc_info.value)


@pytest.mark.asyncio
@patch("services.llm.claude._get_client")
async def test_analyze_and_generate_rate_limit(mock_get_client, sample_profile):
    """Test handling of rate limit errors."""
    from services.llm import llm_service
    llm_service._instance = None

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
        await llm_service.analyze_and_generate("JD text...", sample_profile)

    assert "busy" in str(exc_info.value).lower()


@pytest.mark.asyncio
@patch("services.llm.claude._get_client")
async def test_analyze_and_generate_invalid_json(mock_get_client, sample_profile):
    """Test handling of invalid JSON response."""
    from services.llm import llm_service
    llm_service._instance = None

    mock_client = AsyncMock()
    mock_get_client.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="This is not JSON at all")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    with pytest.raises(ValueError) as exc_info:
        await llm_service.analyze_and_generate("JD text...", sample_profile)

    assert "No JSON found" in str(exc_info.value)
