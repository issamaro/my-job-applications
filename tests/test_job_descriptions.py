import pytest
from unittest.mock import patch


def _create_job_description(client, raw_text="A" * 150):
    """Helper to create a job description."""
    response = client.post(
        "/api/job-descriptions",
        json={"raw_text": raw_text},
    )
    return response


def test_list_job_descriptions_empty(client):
    """Test GET /api/job-descriptions returns empty list."""
    response = client.get("/api/job-descriptions")
    assert response.status_code == 200
    assert response.json() == []


def test_create_job_description_valid(client):
    """Test POST /api/job-descriptions with valid text."""
    response = _create_job_description(client)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Untitled Job"
    assert data["resume_count"] == 0
    assert len(data["raw_text"]) >= 100


def test_create_job_description_short_text(client):
    """Test POST /api/job-descriptions with text < 100 chars."""
    response = client.post(
        "/api/job-descriptions",
        json={"raw_text": "Too short"},
    )
    assert response.status_code == 422


def test_get_job_description(client):
    """Test GET /api/job-descriptions/{id} returns single JD."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    response = client.get(f"/api/job-descriptions/{jd_id}")
    assert response.status_code == 200
    assert response.json()["id"] == jd_id


def test_get_job_description_not_found(client):
    """Test GET /api/job-descriptions/{id} returns 404 for non-existent."""
    response = client.get("/api/job-descriptions/999")
    assert response.status_code == 404


def test_update_job_description_title(client):
    """Test PUT /api/job-descriptions/{id} updates title."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    response = client.put(
        f"/api/job-descriptions/{jd_id}",
        json={"title": "Senior Developer at Google"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Senior Developer at Google"


def test_update_job_description_text(client):
    """Test PUT /api/job-descriptions/{id} updates raw_text."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    new_text = "B" * 150
    response = client.put(
        f"/api/job-descriptions/{jd_id}",
        json={"raw_text": new_text},
    )
    assert response.status_code == 200
    assert response.json()["raw_text"] == new_text


def test_update_job_description_not_found(client):
    """Test PUT /api/job-descriptions/{id} returns 404."""
    response = client.put(
        "/api/job-descriptions/999",
        json={"title": "New Title"},
    )
    assert response.status_code == 404


def test_delete_job_description(client):
    """Test DELETE /api/job-descriptions/{id} removes JD."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    response = client.delete(f"/api/job-descriptions/{jd_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/job-descriptions/{jd_id}")
    assert get_response.status_code == 404


def test_delete_job_description_not_found(client):
    """Test DELETE /api/job-descriptions/{id} returns 404."""
    response = client.delete("/api/job-descriptions/999")
    assert response.status_code == 404


def test_list_job_descriptions_order(client):
    """Test job descriptions are ordered by updated_at DESC."""
    # Create three JDs
    jd1 = _create_job_description(client, "First JD " + "A" * 100).json()
    jd2 = _create_job_description(client, "Second JD " + "B" * 100).json()
    jd3 = _create_job_description(client, "Third JD " + "C" * 100).json()

    response = client.get("/api/job-descriptions")
    assert response.status_code == 200
    jobs = response.json()

    # Most recently created should be first
    assert len(jobs) == 3
    assert jobs[0]["id"] == jd3["id"]
    assert jobs[1]["id"] == jd2["id"]
    assert jobs[2]["id"] == jd1["id"]


def test_get_job_description_resumes_empty(client):
    """Test GET /api/job-descriptions/{id}/resumes returns empty list."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    response = client.get(f"/api/job-descriptions/{jd_id}/resumes")
    assert response.status_code == 200
    assert response.json() == []


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_delete_job_description_cascades_to_resumes(mock_llm, client):
    """Test deleting JD also deletes linked resumes."""
    # Setup profile for resume generation
    client.put(
        "/api/personal-info",
        json={"full_name": "John Doe", "email": "john@example.com"},
    )
    client.post(
        "/api/work-experiences",
        json={
            "company": "Acme Corp",
            "title": "Developer",
            "start_date": "2020-01",
        },
    )

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

    # Generate a resume (this creates a JD)
    gen_response = client.post(
        "/api/resumes/generate",
        json={"job_description": "A" * 150},
    )
    resume_id = gen_response.json()["id"]

    # Get the JD id from job descriptions list
    jd_response = client.get("/api/job-descriptions")
    jd_id = jd_response.json()[0]["id"]

    # Delete the JD
    delete_response = client.delete(f"/api/job-descriptions/{jd_id}")
    assert delete_response.status_code == 204

    # Resume should also be deleted
    resume_response = client.get(f"/api/resumes/{resume_id}")
    assert resume_response.status_code == 404


def test_update_text_creates_version(client):
    """Test updating raw_text creates a version entry."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    # Update text
    client.put(
        f"/api/job-descriptions/{jd_id}",
        json={"raw_text": "Updated text " + "B" * 100},
    )

    # Check version was created
    versions_response = client.get(f"/api/job-descriptions/{jd_id}/versions")
    assert versions_response.status_code == 200
    versions = versions_response.json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1


def test_get_versions_empty(client):
    """Test GET /api/job-descriptions/{id}/versions returns empty for new JD."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    response = client.get(f"/api/job-descriptions/{jd_id}/versions")
    assert response.status_code == 200
    assert response.json() == []


def test_restore_version(client):
    """Test POST /api/job-descriptions/{id}/versions/{vid}/restore."""
    create_response = _create_job_description(client, "Original text " + "A" * 100)
    jd_id = create_response.json()["id"]
    original_text = create_response.json()["raw_text"]

    # Update to new text
    new_text = "New text " + "B" * 100
    client.put(
        f"/api/job-descriptions/{jd_id}",
        json={"raw_text": new_text},
    )

    # Get version id
    versions_response = client.get(f"/api/job-descriptions/{jd_id}/versions")
    version_id = versions_response.json()[0]["id"]

    # Restore to original
    restore_response = client.post(
        f"/api/job-descriptions/{jd_id}/versions/{version_id}/restore"
    )
    assert restore_response.status_code == 200
    assert restore_response.json()["raw_text"] == original_text


def test_restore_version_not_found(client):
    """Test restore with non-existent version returns 404."""
    create_response = _create_job_description(client)
    jd_id = create_response.json()["id"]

    response = client.post(f"/api/job-descriptions/{jd_id}/versions/999/restore")
    assert response.status_code == 404
