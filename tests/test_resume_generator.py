import pytest
from unittest.mock import patch, AsyncMock


def _setup_profile(client):
    """Helper to create profile data."""
    client.put(
        "/api/personal-info",
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
        },
    )
    client.post(
        "/api/work-experiences",
        json={
            "company": "Acme Corp",
            "title": "Senior Developer",
            "start_date": "2020-01",
            "description": "Led development team building Python applications",
        },
    )
    client.post("/api/skills", json={"names": "Python, AWS, Docker"})
    client.post(
        "/api/education",
        json={
            "institution": "State University",
            "degree": "BS",
            "field_of_study": "Computer Science",
            "graduation_year": 2017,
        },
    )


def test_generate_with_valid_profile(client):
    """Test that profile service returns complete profile."""
    _setup_profile(client)

    response = client.get("/api/profile/complete")
    assert response.status_code == 200

    profile = response.json()
    assert profile["personal_info"]["full_name"] == "John Doe"
    assert len(profile["work_experiences"]) == 1
    assert len(profile["skills"]) == 3
    assert len(profile["education"]) == 1


def test_profile_completeness_check(client):
    """Test that profile service correctly checks for work experience."""
    from services.profile import profile_service

    assert profile_service.has_work_experience() is False

    client.post(
        "/api/work-experiences",
        json={
            "company": "Test Co",
            "title": "Developer",
            "start_date": "2020-01",
        },
    )

    assert profile_service.has_work_experience() is True


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_preserves_personal_info(mock_llm, client):
    """Test that generated resume includes personal info from profile."""
    _setup_profile(client)

    mock_llm.return_value = {
        "job_title": "Software Engineer",
        "company_name": "TechCorp",
        "match_score": 80,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Experienced developer",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    response = client.post(
        "/api/resumes/generate",
        json={"job_description": "A" * 150},
    )

    assert response.status_code == 200
    resume = response.json()["resume"]
    assert resume["personal_info"]["full_name"] == "John Doe"
    assert resume["personal_info"]["email"] == "john@example.com"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_generate_saves_to_database(mock_llm, client):
    """Test that generated resume is saved to database."""
    _setup_profile(client)

    mock_llm.return_value = {
        "job_title": "Python Developer",
        "company_name": "StartupCo",
        "match_score": 92,
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

    response = client.post(
        "/api/resumes/generate",
        json={"job_description": "Looking for Python developer..." + "A" * 100},
    )

    assert response.status_code == 200
    resume_id = response.json()["id"]

    get_response = client.get(f"/api/resumes/{resume_id}")
    assert get_response.status_code == 200
    saved_resume = get_response.json()
    assert saved_resume["job_title"] == "Python Developer"
    assert saved_resume["match_score"] == 92


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_update_preserves_personal_info(mock_llm, client):
    """Test that updating resume preserves personal info."""
    _setup_profile(client)

    mock_llm.return_value = {
        "job_title": "Engineer",
        "company_name": "Corp",
        "match_score": 70,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Original",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": "A" * 150},
    )
    resume_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/resumes/{resume_id}",
        json={
            "resume": {
                "summary": "Updated summary",
                "work_experiences": [],
                "skills": [],
                "education": [],
                "projects": [],
            }
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["resume"]["summary"] == "Updated summary"
    assert updated["resume"]["personal_info"]["full_name"] == "John Doe"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_delete_removes_job_description(mock_llm, client):
    """Test that deleting resume also deletes job description."""
    _setup_profile(client)

    mock_llm.return_value = {
        "job_title": "Engineer",
        "company_name": "Corp",
        "match_score": 70,
        "job_analysis": {"required_skills": [], "preferred_skills": []},
        "resume": {
            "summary": "Test",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    create_response = client.post(
        "/api/resumes/generate",
        json={"job_description": "A" * 150},
    )
    resume_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/resumes/{resume_id}")
    assert delete_response.status_code == 204

    history_response = client.get("/api/resumes")
    assert history_response.json() == []


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_job_analysis_persists_with_existing_jd(mock_llm, client):
    """Test that job_analysis is saved when generating with existing job_description_id."""
    _setup_profile(client)

    # First, create a job description via save endpoint
    save_response = client.post(
        "/api/job-descriptions",
        json={"raw_text": "Looking for Senior Python Developer with FastAPI experience. " + "A" * 100},
    )
    assert save_response.status_code == 201
    jd_id = save_response.json()["id"]

    # Now generate resume with that existing JD
    mock_llm.return_value = {
        "job_title": "Senior Python Developer",
        "company_name": "TechStartup",
        "match_score": 88,
        "job_analysis": {
            "required_skills": [
                {"name": "Python", "matched": True},
                {"name": "FastAPI", "matched": True},
            ],
            "preferred_skills": [{"name": "Docker", "matched": False}],
        },
        "resume": {
            "summary": "Experienced Python developer",
            "work_experiences": [],
            "skills": [],
            "education": [],
            "projects": [],
        },
    }

    response = client.post(
        "/api/resumes/generate",
        json={
            "job_description": "Looking for Senior Python Developer with FastAPI experience. " + "A" * 100,
            "job_description_id": jd_id,
        },
    )

    assert response.status_code == 200
    resume_data = response.json()
    resume_id = resume_data["id"]

    # Verify job_analysis is in immediate response
    assert resume_data["job_analysis"] is not None
    assert len(resume_data["job_analysis"]["required_skills"]) == 2

    # Verify job_analysis persists when fetching resume (simulates page refresh)
    get_response = client.get(f"/api/resumes/{resume_id}")
    assert get_response.status_code == 200
    fetched_resume = get_response.json()

    assert fetched_resume["job_analysis"] is not None
    assert fetched_resume["job_analysis"]["required_skills"][0]["name"] == "Python"
    assert fetched_resume["job_analysis"]["required_skills"][1]["name"] == "FastAPI"


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_job_analysis_updates_on_regenerate(mock_llm, client):
    """Test that job_analysis is updated when regenerating from same JD."""
    _setup_profile(client)

    # Create JD with existing title (not "Untitled Job")
    save_response = client.post(
        "/api/job-descriptions",
        json={"raw_text": "Backend Developer position. " + "A" * 100},
    )
    jd_id = save_response.json()["id"]

    # Update the JD to have a non-default title
    from database import get_db
    with get_db() as conn:
        conn.execute("UPDATE job_descriptions SET title = ? WHERE id = ?", ("Backend Developer at Corp", jd_id))
        conn.commit()

    # Generate with updated analysis
    mock_llm.return_value = {
        "job_title": "Backend Developer",
        "company_name": "Corp",
        "match_score": 75,
        "job_analysis": {
            "required_skills": [{"name": "Node.js", "matched": False}],
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

    response = client.post(
        "/api/resumes/generate",
        json={
            "job_description": "Backend Developer position. " + "A" * 100,
            "job_description_id": jd_id,
        },
    )

    assert response.status_code == 200
    resume_id = response.json()["id"]

    # Verify updated analysis persists
    get_response = client.get(f"/api/resumes/{resume_id}")
    fetched_resume = get_response.json()

    assert fetched_resume["job_analysis"] is not None
    assert fetched_resume["job_analysis"]["required_skills"][0]["name"] == "Node.js"
