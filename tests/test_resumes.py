import pytest
from unittest.mock import patch, AsyncMock


def test_list_resumes_empty(client):
    """Test listing resumes when none exist."""
    response = client.get("/api/resumes")
    assert response.status_code == 200
    assert response.json() == []


def test_generate_resume_empty_job_description(client):
    """Test generating resume with empty job description."""
    response = client.post("/api/resumes/generate", json={"job_description": ""})
    assert response.status_code == 422


def test_generate_resume_short_job_description(client):
    """Test generating resume with job description under 100 characters."""
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": "Short JD"},
    )
    assert response.status_code == 422


def test_generate_resume_no_profile(client):
    """Test generating resume when user has no work experience."""
    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    assert response.status_code == 400
    assert "work experience" in response.json()["detail"].lower()


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


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_resume_success(mock_llm, client):
    """Test successful resume generation."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {
            "required_skills": [{"name": "Python", "matched": True}],
            "preferred_skills": [],
        },
        "resume": {
            "summary": "Experienced developer",
            "work_experiences": [
                {
                    "id": 1,
                    "company": "Acme Corp",
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "description": "Led team",
                    "match_reasons": ["Python"],
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
    assert response.status_code == 200
    result = response.json()
    assert result["job_title"] == "Software Engineer"
    assert result["match_score"] == 85.5
    assert result["id"] is not None


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_get_resume_after_generation(mock_llm, client):
    """Test getting a resume by ID after generation."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    resume_id = create_response.json()["id"]

    response = client.get(f"/api/resumes/{resume_id}")
    assert response.status_code == 200
    assert response.json()["id"] == resume_id


def test_get_resume_not_found(client):
    """Test getting a resume that doesn't exist."""
    response = client.get("/api/resumes/9999")
    assert response.status_code == 404


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_list_resumes_with_history(mock_llm, client):
    """Test listing resumes returns history."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    client.post("/api/resumes/generate", json={"job_description": long_jd})

    response = client.get("/api/resumes")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["job_title"] == "Software Engineer"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_update_resume(mock_llm, client):
    """Test updating a resume."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Original",
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
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    resume_id = create_response.json()["id"]

    update_data = {
        "resume": {
            "summary": "Updated summary",
            "work_experiences": [
                {
                    "id": 1,
                    "company": "Acme Corp",
                    "title": "Senior Developer",
                    "start_date": "2020-01",
                    "description": "Updated description",
                    "match_reasons": [],
                    "included": True,
                    "order": 1,
                }
            ],
            "skills": [],
            "education": [],
            "projects": [],
        }
    }

    response = client.put(f"/api/resumes/{resume_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["resume"]["summary"] == "Updated summary"


def test_update_resume_not_found(client):
    """Test updating a resume that doesn't exist."""
    update_data = {
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        }
    }
    response = client.put("/api/resumes/9999", json=update_data)
    assert response.status_code == 404


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_delete_resume(mock_llm, client):
    """Test deleting a resume."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    resume_id = create_response.json()["id"]

    response = client.delete(f"/api/resumes/{resume_id}")
    assert response.status_code == 204

    response = client.get(f"/api/resumes/{resume_id}")
    assert response.status_code == 404


def test_delete_resume_not_found(client):
    """Test deleting a resume that doesn't exist."""
    response = client.delete("/api/resumes/9999")
    assert response.status_code == 404


def test_get_complete_profile(client):
    """Test getting the complete profile."""
    _create_work_experience(client)

    response = client.get("/api/profile/complete")
    assert response.status_code == 200
    result = response.json()
    assert "personal_info" in result
    assert "work_experiences" in result
    assert "education" in result
    assert "skills" in result
    assert "projects" in result
    assert len(result["work_experiences"]) == 1


# Tests for job_id linkage

def _create_job(client, original_text=None):
    """Helper to create a job."""
    if original_text is None:
        original_text = "A" * 150
    return client.post(
        "/api/jobs",
        json={"original_text": original_text},
    )


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_with_job_id_links_to_existing(mock_llm, client):
    """Test generating resume with job_id links to existing JD."""
    _create_work_experience(client)

    # Create a job description first
    jd_response = _create_job(client)
    jd_id = jd_response.json()["id"]

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd, "job_id": jd_id},
    )
    assert response.status_code == 200

    # Verify the resume is linked to the existing JD
    jd_resumes_response = client.get(f"/api/jobs/{jd_id}/resumes")
    assert jd_resumes_response.status_code == 200
    resumes = jd_resumes_response.json()
    assert len(resumes) == 1
    assert resumes[0]["id"] == response.json()["id"]


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_without_job_id_creates_new(mock_llm, client):
    """Test generating resume without job_id creates new JD."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    assert response.status_code == 200

    # Check that job descriptions increased
    jd_response = client.get("/api/jobs")
    assert jd_response.status_code == 200
    jds = jd_response.json()
    assert len(jds) >= 1


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_updates_untitled_job_title(mock_llm, client):
    """Test generating resume updates title from 'Untitled Job' to extracted title."""
    _create_work_experience(client)

    # Create a job description with "Untitled Job" title
    jd_response = _create_job(client)
    jd_id = jd_response.json()["id"]

    # Update the title to "Untitled Job"
    client.put(f"/api/jobs/{jd_id}", json={"title": "Untitled Job"})

    mock_llm.return_value = {
        "job_title": "Senior Developer",
        "company_name": "NewCorp",
        "match_score": 90.0,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd, "job_id": jd_id},
    )
    assert response.status_code == 200

    # Verify title was updated
    jd_get_response = client.get(f"/api/jobs/{jd_id}")
    assert jd_get_response.status_code == 200
    assert jd_get_response.json()["title"] == "Senior Developer at NewCorp"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_preserves_custom_title(mock_llm, client):
    """Test generating resume preserves custom title (not 'Untitled Job')."""
    _create_work_experience(client)

    # Create a job description
    jd_response = _create_job(client)
    jd_id = jd_response.json()["id"]

    # Set a custom title
    custom_title = "My Dream Job"
    client.put(f"/api/jobs/{jd_id}", json={"title": custom_title})

    mock_llm.return_value = {
        "job_title": "Different Title",
        "company_name": "OtherCorp",
        "match_score": 80.0,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd, "job_id": jd_id},
    )
    assert response.status_code == 200

    # Verify custom title was preserved
    jd_get_response = client.get(f"/api/jobs/{jd_id}")
    assert jd_get_response.status_code == 200
    assert jd_get_response.json()["title"] == custom_title


def test_generate_with_nonexistent_job_id(client):
    """Test generating resume with non-existent job_id returns error."""
    _create_work_experience(client)

    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd, "job_id": 99999},
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


# Tests for Job Analysis Isolation per Resume


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_job_analysis_stored_in_resume(mock_llm, client):
    """Test that job_analysis is stored directly in the resume record."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {
            "required_skills": [{"name": "Python", "matched": True}],
            "preferred_skills": [{"name": "Docker", "matched": False}],
        },
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    assert response.status_code == 200
    result = response.json()

    # Verify job_analysis is in the response
    assert result["job_analysis"] is not None
    assert len(result["job_analysis"]["required_skills"]) == 1
    assert result["job_analysis"]["required_skills"][0]["name"] == "Python"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_job_analysis_persists_on_page_refresh(mock_llm, client):
    """Test that job_analysis persists when retrieving resume by ID (page refresh)."""
    _create_work_experience(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {
            "required_skills": [{"name": "Python", "matched": True}],
            "preferred_skills": [],
        },
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd},
    )
    resume_id = create_response.json()["id"]

    # Simulate page refresh - get resume by ID
    get_response = client.get(f"/api/resumes/{resume_id}")
    assert get_response.status_code == 200
    result = get_response.json()

    # Verify job_analysis is still there
    assert result["job_analysis"] is not None
    assert result["job_analysis"]["required_skills"][0]["name"] == "Python"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_two_resumes_same_jd_independent_job_analysis(mock_llm, client):
    """Test that two resumes from same JD have independent job_analysis."""
    _create_work_experience(client)

    # Create a job description first
    jd_response = _create_job(client)
    jd_id = jd_response.json()["id"]

    # First resume generation - Python skills matched
    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 85.5,
        "job_analysis": {
            "required_skills": [{"name": "Python", "matched": True}],
            "preferred_skills": [],
        },
        "resume": {
            "summary": "Python focused",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    long_jd = "A" * 150
    response1 = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd, "job_id": jd_id},
    )
    resume1_id = response1.json()["id"]

    # Second resume generation - Java skills matched (different analysis)
    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 75.0,
        "job_analysis": {
            "required_skills": [{"name": "Java", "matched": True}],
            "preferred_skills": [{"name": "Spring", "matched": True}],
        },
        "resume": {
            "summary": "Java focused",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    response2 = client.post(
        "/api/resumes/generate",
        json={"job_description": long_jd, "job_id": jd_id},
    )
    resume2_id = response2.json()["id"]

    # Verify both resumes exist and have different job_analysis
    get1 = client.get(f"/api/resumes/{resume1_id}")
    get2 = client.get(f"/api/resumes/{resume2_id}")

    assert get1.status_code == 200
    assert get2.status_code == 200

    # First resume should have Python
    assert get1.json()["job_analysis"]["required_skills"][0]["name"] == "Python"
    # Second resume should have Java
    assert get2.json()["job_analysis"]["required_skills"][0]["name"] == "Java"

    # Verify they're linked to the same JD
    jd_resumes = client.get(f"/api/jobs/{jd_id}/resumes")
    assert len(jd_resumes.json()) == 2
