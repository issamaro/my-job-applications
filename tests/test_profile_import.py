import database


def test_import_profile_happy_path(client):
    """Test importing a complete valid profile."""
    data = {
        "personal_info": {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1 555 123 4567",
            "location": "San Francisco, CA",
            "linkedin_url": "https://linkedin.com/in/janedoe",
            "summary": "Experienced engineer"
        },
        "work_experiences": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "start_date": "2020-01",
                "end_date": None,
                "is_current": True,
                "description": "Lead development",
                "location": "SF"
            }
        ],
        "education": [
            {
                "institution": "State University",
                "degree": "BS",
                "field_of_study": "Computer Science",
                "graduation_year": 2018,
                "gpa": 3.8,
                "notes": "Dean's List"
            }
        ],
        "skills": [
            {"name": "Python"},
            {"name": "JavaScript"}
        ],
        "projects": [
            {
                "name": "Open Source Tool",
                "description": "A CLI tool",
                "technologies": "Python, Click",
                "url": "https://github.com/example",
                "start_date": "2022-06",
                "end_date": "2022-12"
            }
        ]
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Profile imported successfully"
    assert result["counts"]["work_experiences"] == 1
    assert result["counts"]["education"] == 1
    assert result["counts"]["skills"] == 2
    assert result["counts"]["projects"] == 1

    # Verify data was actually imported
    pi_response = client.get("/api/personal-info")
    assert pi_response.status_code == 200
    pi = pi_response.json()
    assert pi["full_name"] == "Jane Doe"
    assert pi["email"] == "jane@example.com"


def test_import_preserves_photo(client):
    """Test that importing preserves existing photo."""
    # First, set up a personal info with a photo
    with database.get_db() as conn:
        conn.execute(
            """
            INSERT INTO personal_info (id, full_name, email, photo)
            VALUES (1, 'Old Name', 'old@example.com', 'data:image/png;base64,ABC123')
            """
        )
        conn.commit()

    # Now import new profile
    data = {
        "personal_info": {
            "full_name": "New Name",
            "email": "new@example.com"
        },
        "work_experiences": [],
        "education": [],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 200

    # Verify photo was preserved
    with database.get_db() as conn:
        cursor = conn.execute("SELECT full_name, email, photo FROM personal_info WHERE id = 1")
        row = cursor.fetchone()
        assert row["full_name"] == "New Name"
        assert row["email"] == "new@example.com"
        assert row["photo"] == "data:image/png;base64,ABC123"


def test_import_missing_personal_info(client):
    """Test that missing personal_info section returns 422."""
    data = {
        "work_experiences": [],
        "education": [],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 422


def test_import_missing_required_field(client):
    """Test that missing required field returns 422 with field path."""
    data = {
        "personal_info": {
            "full_name": "Jane Doe"
            # Missing email
        },
        "work_experiences": [],
        "education": [],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 422
    detail = response.json()["detail"]
    # Check that email is mentioned in the error
    assert any("email" in str(err).lower() for err in detail)


def test_import_invalid_date_format(client):
    """Test that invalid date format returns 422."""
    data = {
        "personal_info": {
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        },
        "work_experiences": [
            {
                "company": "Tech Corp",
                "title": "Engineer",
                "start_date": "01/2020"  # Invalid format, should be YYYY-MM
            }
        ],
        "education": [],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 422


def test_import_invalid_email(client):
    """Test that invalid email returns 422."""
    data = {
        "personal_info": {
            "full_name": "Jane Doe",
            "email": "not-an-email"
        },
        "work_experiences": [],
        "education": [],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 422


def test_import_empty_arrays_clears_existing(client):
    """Test that empty arrays clear existing data for those sections."""
    # First, create some existing data
    client.post("/api/work-experiences", json={
        "company": "Old Company",
        "title": "Old Title",
        "start_date": "2019-01"
    })
    client.post("/api/skills", json={"names": "OldSkill"})

    # Verify data exists
    we_response = client.get("/api/work-experiences")
    assert len(we_response.json()) == 1
    skills_response = client.get("/api/skills")
    assert len(skills_response.json()) == 1

    # Import with empty arrays
    data = {
        "personal_info": {
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        },
        "work_experiences": [],
        "education": [],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 200

    # Verify data was cleared
    we_response = client.get("/api/work-experiences")
    assert len(we_response.json()) == 0
    skills_response = client.get("/api/skills")
    assert len(skills_response.json()) == 0


def test_import_atomicity_on_failure(client):
    """Test that partial failure rolls back entire import."""
    # Create some existing data
    client.post("/api/work-experiences", json={
        "company": "Original Company",
        "title": "Original Title",
        "start_date": "2019-01"
    })

    # Try to import with valid personal_info but invalid work_experience
    data = {
        "personal_info": {
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        },
        "work_experiences": [
            {
                "company": "Tech Corp",
                "title": "Engineer",
                "start_date": "invalid-date"  # This should fail validation
            }
        ],
        "education": [],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 422

    # Original data should still exist (validation happens before DB changes)
    we_response = client.get("/api/work-experiences")
    experiences = we_response.json()
    assert len(experiences) == 1
    assert experiences[0]["company"] == "Original Company"


def test_import_graduation_year_validation(client):
    """Test graduation year validation."""
    data = {
        "personal_info": {
            "full_name": "Jane Doe",
            "email": "jane@example.com"
        },
        "work_experiences": [],
        "education": [
            {
                "institution": "University",
                "degree": "BS",
                "graduation_year": 1800  # Invalid: must be between 1900 and 2100
            }
        ],
        "skills": [],
        "projects": []
    }

    response = client.put("/api/profile/import", json=data)
    assert response.status_code == 422
