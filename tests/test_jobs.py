import pytest
from unittest.mock import patch


def _create_job(client, original_text="A" * 150):
    """Helper to create a job."""
    response = client.post(
        "/api/jobs",
        json={"original_text": original_text},
    )
    return response


def test_list_jobs_empty(client):
    """Test GET /api/jobs returns empty list."""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert response.json() == []


def test_create_job_valid(client):
    """Test POST /api/jobs with valid text."""
    response = _create_job(client)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Untitled Job"
    assert data["resume_count"] == 0
    assert len(data["original_text"]) >= 100


def test_create_job_short_text(client):
    """Test POST /api/jobs with text < 100 chars."""
    response = client.post(
        "/api/jobs",
        json={"original_text": "Too short"},
    )
    assert response.status_code == 422


def test_get_job(client):
    """Test GET /api/jobs/{id} returns single job."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_get_job_not_found(client):
    """Test GET /api/jobs/{id} returns 404 for non-existent."""
    response = client.get("/api/jobs/999")
    assert response.status_code == 404


def test_update_job_title(client):
    """Test PUT /api/jobs/{id} updates title."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    response = client.put(
        f"/api/jobs/{job_id}",
        json={"title": "Senior Developer at Google"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Senior Developer at Google"


def test_update_job_text(client):
    """Test PUT /api/jobs/{id} updates original_text."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    new_text = "B" * 150
    response = client.put(
        f"/api/jobs/{job_id}",
        json={"original_text": new_text},
    )
    assert response.status_code == 200
    assert response.json()["original_text"] == new_text


def test_update_job_not_found(client):
    """Test PUT /api/jobs/{id} returns 404."""
    response = client.put(
        "/api/jobs/999",
        json={"title": "New Title"},
    )
    assert response.status_code == 404


def test_delete_job(client):
    """Test DELETE /api/jobs/{id} removes job."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/jobs/{job_id}")
    assert get_response.status_code == 404


def test_delete_job_not_found(client):
    """Test DELETE /api/jobs/{id} returns 404."""
    response = client.delete("/api/jobs/999")
    assert response.status_code == 404


def test_list_jobs_order(client):
    """Test jobs are ordered by updated_at DESC."""
    # Create three jobs
    job1 = _create_job(client, "First job " + "A" * 100).json()
    job2 = _create_job(client, "Second job " + "B" * 100).json()
    job3 = _create_job(client, "Third job " + "C" * 100).json()

    response = client.get("/api/jobs")
    assert response.status_code == 200
    jobs = response.json()

    # Most recently created should be first
    assert len(jobs) == 3
    assert jobs[0]["id"] == job3["id"]
    assert jobs[1]["id"] == job2["id"]
    assert jobs[2]["id"] == job1["id"]


def test_get_job_resumes_empty(client):
    """Test GET /api/jobs/{id}/resumes returns empty list."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    response = client.get(f"/api/jobs/{job_id}/resumes")
    assert response.status_code == 200
    assert response.json() == []


@patch("services.resume_generator.llm_service.analyze_and_generate")
def test_delete_job_cascades_to_resumes(mock_llm, client):
    """Test deleting job also deletes linked resumes."""
    # Setup profile for resume generation
    client.put(
        "/api/users",
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

    # Generate a resume (this creates a job)
    gen_response = client.post(
        "/api/resumes/generate",
        json={"job_description": "A" * 150},
    )
    resume_id = gen_response.json()["id"]

    # Get the job id from jobs list
    jobs_response = client.get("/api/jobs")
    job_id = jobs_response.json()[0]["id"]

    # Delete the job
    delete_response = client.delete(f"/api/jobs/{job_id}")
    assert delete_response.status_code == 204

    # Resume should also be deleted
    resume_response = client.get(f"/api/resumes/{resume_id}")
    assert resume_response.status_code == 404


def test_update_text_creates_version(client):
    """Test updating original_text creates a version entry."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    # Update text
    client.put(
        f"/api/jobs/{job_id}",
        json={"original_text": "Updated text " + "B" * 100},
    )

    # Check version was created
    versions_response = client.get(f"/api/jobs/{job_id}/versions")
    assert versions_response.status_code == 200
    versions = versions_response.json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1


def test_get_versions_empty(client):
    """Test GET /api/jobs/{id}/versions returns empty for new job."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    response = client.get(f"/api/jobs/{job_id}/versions")
    assert response.status_code == 200
    assert response.json() == []


def test_restore_version(client):
    """Test POST /api/jobs/{id}/versions/{vid}/restore."""
    create_response = _create_job(client, "Original text " + "A" * 100)
    job_id = create_response.json()["id"]
    original_text = create_response.json()["original_text"]

    # Update to new text
    new_text = "New text " + "B" * 100
    client.put(
        f"/api/jobs/{job_id}",
        json={"original_text": new_text},
    )

    # Get version id
    versions_response = client.get(f"/api/jobs/{job_id}/versions")
    version_id = versions_response.json()[0]["id"]

    # Restore to original
    restore_response = client.post(
        f"/api/jobs/{job_id}/versions/{version_id}/restore"
    )
    assert restore_response.status_code == 200
    assert restore_response.json()["original_text"] == original_text


def test_restore_version_not_found(client):
    """Test restore with non-existent version returns 404."""
    create_response = _create_job(client)
    job_id = create_response.json()["id"]

    response = client.post(f"/api/jobs/{job_id}/versions/999/restore")
    assert response.status_code == 404
