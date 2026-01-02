def test_list_projects_empty(client):
    """Test listing projects when none exist."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_add_project(client):
    """Test adding a project."""
    data = {
        "name": "Portfolio Website",
        "description": "Personal portfolio and blog",
        "technologies": "Svelte, Sass, Python",
        "url": "https://example.com",
    }
    response = client.post("/api/projects", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "Portfolio Website"
    assert result["technologies"] == "Svelte, Sass, Python"


def test_edit_project(client):
    """Test editing a project."""
    data = {
        "name": "Portfolio Website",
        "description": "Personal portfolio",
    }
    create_response = client.post("/api/projects", json=data)
    proj_id = create_response.json()["id"]

    updated_data = {
        "name": "Portfolio Website v2",
        "description": "Personal portfolio with blog",
        "url": "https://myportfolio.com",
    }
    response = client.put(f"/api/projects/{proj_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Portfolio Website v2"


def test_delete_project(client):
    """Test deleting a project."""
    data = {
        "name": "Test Project",
    }
    create_response = client.post("/api/projects", json=data)
    proj_id = create_response.json()["id"]

    response = client.delete(f"/api/projects/{proj_id}")
    assert response.status_code == 200
    assert response.json() == {"deleted": proj_id}

    # Verify deleted
    response = client.get(f"/api/projects/{proj_id}")
    assert response.status_code == 404


def test_get_nonexistent_project(client):
    """Test getting a project that doesn't exist."""
    response = client.get("/api/projects/9999")
    assert response.status_code == 404
