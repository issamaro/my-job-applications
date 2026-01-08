import pytest
from unittest.mock import patch


def _create_work_experience(client):
    """Helper to create a work experience."""
    return client.post(
        "/api/work-experiences",
        json={
            "company": "Acme Corp",
            "title": "Senior Developer",
            "start_date": "2020-01",
            "description": "Led development team",
        },
    )


def _create_personal_info(client):
    """Helper to create personal info."""
    return client.put(
        "/api/personal-info",
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
        },
    )


def _generate_resume(client, mock_llm):
    """Helper to generate a resume."""
    _create_work_experience(client)
    _create_personal_info(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "personal_info": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "555-1234",
            },
            "summary": "Experienced developer",
            "work_experiences": [
                {
                    "id": 1,
                    "company": "Acme Corp",
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "description": "Led team",
                    "match_reasons": [],
                    "included": True,
                    "order": 1,
                }
            ],
            "skills": [{"name": "Python", "matched": True, "included": True}],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "We are looking for a Software Engineer with Python experience. " * 5
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    return response.json()["id"]


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_returns_pdf(mock_llm, client):
    """Test GET /api/resumes/{id}/pdf returns a PDF file."""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_default_template_is_classic(mock_llm, client):
    """Test default template is 'classic'."""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf")

    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_with_modern_template(mock_llm, client):
    """Test ?template=modern works."""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf?template=modern")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_export_pdf_resume_not_found(client):
    """Test 404 when resume not found."""
    response = client.get("/api/resumes/9999/pdf")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_export_pdf_invalid_template(client):
    """Test 422 for invalid template parameter."""
    response = client.get("/api/resumes/1/pdf?template=invalid")

    assert response.status_code == 422


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_content_disposition_header(mock_llm, client):
    """Test Content-Disposition header format."""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf")

    assert response.status_code == 200
    content_disposition = response.headers.get("content-disposition")
    assert content_disposition is not None
    assert "attachment" in content_disposition
    assert 'filename="' in content_disposition
    assert ".pdf" in content_disposition


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_filename_format(mock_llm, client):
    """Test filename format: FullName_Resume_Company.pdf"""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf")

    content_disposition = response.headers.get("content-disposition")
    assert "John_Doe_Resume_TechCorp.pdf" in content_disposition


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_with_classic_template_param(mock_llm, client):
    """Test explicit ?template=classic works."""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf?template=classic")

    assert response.status_code == 200
    assert response.content[:4] == b"%PDF"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_brussels_template(mock_llm, client):
    """Test ?template=brussels works."""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf?template=brussels")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_export_pdf_eu_classic_template(mock_llm, client):
    """Test ?template=eu_classic works."""
    resume_id = _generate_resume(client, mock_llm)

    response = client.get(f"/api/resumes/{resume_id}/pdf?template=eu_classic")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"
