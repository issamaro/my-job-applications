def test_list_education_empty(client):
    """Test listing education when none exists."""
    response = client.get("/api/education")
    assert response.status_code == 200
    assert response.json() == []


def test_add_education(client):
    """Test adding education entry."""
    data = {
        "institution": "State University",
        "degree": "BS",
        "field_of_study": "Computer Science",
        "graduation_year": 2017,
        "notes": "Graduated magna cum laude",
    }
    response = client.post("/api/education", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["institution"] == "State University"
    assert result["degree"] == "BS"
    assert result["graduation_year"] == 2017


def test_edit_education(client):
    """Test editing an education entry."""
    data = {
        "institution": "State University",
        "degree": "BS",
        "field_of_study": "Computer Science",
        "graduation_year": 2017,
    }
    create_response = client.post("/api/education", json=data)
    edu_id = create_response.json()["id"]

    updated_data = {
        "institution": "State University",
        "degree": "BS",
        "field_of_study": "Computer Science",
        "graduation_year": 2017,
        "gpa": 3.8,
        "notes": "Graduated with honors",
    }
    response = client.put(f"/api/education/{edu_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["gpa"] == 3.8


def test_delete_education(client):
    """Test deleting an education entry."""
    data = {
        "institution": "State University",
        "degree": "BS",
    }
    create_response = client.post("/api/education", json=data)
    edu_id = create_response.json()["id"]

    response = client.delete(f"/api/education/{edu_id}")
    assert response.status_code == 200
    assert response.json() == {"deleted": edu_id}

    # Verify deleted
    response = client.get(f"/api/education/{edu_id}")
    assert response.status_code == 404


def test_get_nonexistent_education(client):
    """Test getting education that doesn't exist."""
    response = client.get("/api/education/9999")
    assert response.status_code == 404
