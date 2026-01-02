def test_long_text_in_description(client):
    """Test that long text (2000 chars) is accepted in description."""
    long_text = "A" * 2000
    data = {
        "company": "Acme Corp",
        "title": "Developer",
        "start_date": "2020-01",
        "description": long_text,
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 200
    assert len(response.json()["description"]) == 2000


def test_special_characters_in_text(client):
    """Test that special characters (quotes, unicode) are handled."""
    data = {
        "full_name": "José García-López",
        "email": "jose@example.com",
        "summary": 'Said "Hello, World!" and wrote some code <script>alert("XSS")</script>',
    }
    response = client.put("/api/personal-info", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["full_name"] == "José García-López"
    assert "<script>" in result["summary"]


def test_required_field_validation_work_experience(client):
    """Test required field validation for work experience."""
    # Missing company
    data = {
        "title": "Developer",
        "start_date": "2020-01",
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 422

    # Missing title
    data = {
        "company": "Acme Corp",
        "start_date": "2020-01",
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 422

    # Missing start_date
    data = {
        "company": "Acme Corp",
        "title": "Developer",
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 422


def test_date_format_validation(client):
    """Test date format validation (YYYY-MM)."""
    # Valid date
    data = {
        "company": "Acme Corp",
        "title": "Developer",
        "start_date": "2020-01",
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 200

    # Invalid date format
    data = {
        "company": "Acme Corp",
        "title": "Developer",
        "start_date": "01/2020",
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 422

    # Invalid date format
    data = {
        "company": "Acme Corp",
        "title": "Developer",
        "start_date": "2020-1",
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 422


def test_unicode_in_skills(client):
    """Test unicode characters in skills."""
    data = {"names": "日本語, Español, Français"}
    response = client.post("/api/skills", json=data)
    assert response.status_code == 200
    names = [s["name"] for s in response.json()]
    assert "日本語" in names
    assert "Español" in names
