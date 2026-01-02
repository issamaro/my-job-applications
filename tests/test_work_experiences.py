def test_list_work_experiences_empty(client):
    """Test listing work experiences when none exist."""
    response = client.get("/api/work-experiences")
    assert response.status_code == 200
    assert response.json() == []


def test_add_first_work_experience(client):
    """Test adding the first work experience."""
    data = {
        "company": "Acme Corp",
        "title": "Senior Developer",
        "start_date": "2020-01",
        "description": "Led development team",
        "location": "San Francisco, CA",
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["company"] == "Acme Corp"
    assert result["title"] == "Senior Developer"
    assert result["id"] is not None


def test_add_multiple_work_experiences(client):
    """Test adding multiple work experiences."""
    exp1 = {
        "company": "Acme Corp",
        "title": "Senior Developer",
        "start_date": "2020-01",
        "is_current": True,
    }
    exp2 = {
        "company": "StartupCo",
        "title": "Developer",
        "start_date": "2017-03",
        "end_date": "2019-12",
    }
    client.post("/api/work-experiences", json=exp1)
    client.post("/api/work-experiences", json=exp2)

    response = client.get("/api/work-experiences")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2


def test_edit_work_experience(client):
    """Test editing an existing work experience."""
    data = {
        "company": "Acme Corp",
        "title": "Developer",
        "start_date": "2020-01",
    }
    create_response = client.post("/api/work-experiences", json=data)
    exp_id = create_response.json()["id"]

    updated_data = {
        "company": "Acme Corp",
        "title": "Senior Developer",
        "start_date": "2020-01",
        "description": "Promoted to senior role",
    }
    response = client.put(f"/api/work-experiences/{exp_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Senior Developer"


def test_delete_work_experience(client):
    """Test deleting a work experience."""
    data = {
        "company": "Acme Corp",
        "title": "Developer",
        "start_date": "2020-01",
    }
    create_response = client.post("/api/work-experiences", json=data)
    exp_id = create_response.json()["id"]

    response = client.delete(f"/api/work-experiences/{exp_id}")
    assert response.status_code == 200
    assert response.json() == {"deleted": exp_id}

    # Verify deleted
    response = client.get(f"/api/work-experiences/{exp_id}")
    assert response.status_code == 404


def test_mark_current_position(client):
    """Test marking a position as current (end_date null)."""
    data = {
        "company": "Acme Corp",
        "title": "Developer",
        "start_date": "2020-01",
        "is_current": True,
    }
    response = client.post("/api/work-experiences", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["is_current"] is True
    assert result["end_date"] is None


def test_chronological_ordering(client):
    """Test that work experiences are ordered newest first."""
    older = {
        "company": "OldCo",
        "title": "Junior Developer",
        "start_date": "2015-01",
        "end_date": "2017-12",
    }
    newer = {
        "company": "NewCo",
        "title": "Senior Developer",
        "start_date": "2020-01",
    }
    current = {
        "company": "CurrentCo",
        "title": "Lead Developer",
        "start_date": "2018-01",
        "is_current": True,
    }
    client.post("/api/work-experiences", json=older)
    client.post("/api/work-experiences", json=newer)
    client.post("/api/work-experiences", json=current)

    response = client.get("/api/work-experiences")
    results = response.json()
    # Current first, then by start_date DESC
    assert results[0]["company"] == "CurrentCo"
    assert results[1]["company"] == "NewCo"
    assert results[2]["company"] == "OldCo"


def test_get_nonexistent_work_experience(client):
    """Test getting a work experience that doesn't exist."""
    response = client.get("/api/work-experiences/9999")
    assert response.status_code == 404
