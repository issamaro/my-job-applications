def test_list_skills_empty(client):
    """Test listing skills when none exist."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    assert response.json() == []


def test_add_skills_comma_parsing(client):
    """Test adding skills with comma parsing."""
    data = {"names": "Python, FastAPI, SQL"}
    response = client.post("/api/skills", json=data)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    skill_names = [s["name"] for s in results]
    assert "Python" in skill_names
    assert "FastAPI" in skill_names
    assert "SQL" in skill_names


def test_remove_skill(client):
    """Test removing a skill."""
    data = {"names": "Python, FastAPI"}
    create_response = client.post("/api/skills", json=data)
    skill_id = create_response.json()[0]["id"]

    response = client.delete(f"/api/skills/{skill_id}")
    assert response.status_code == 200
    assert response.json() == {"deleted": skill_id}

    # Verify only one skill remains
    response = client.get("/api/skills")
    assert len(response.json()) == 1


def test_duplicate_skill_handling(client):
    """Test that duplicate skills are not created."""
    data = {"names": "Python"}
    client.post("/api/skills", json=data)

    # Try to add Python again
    data = {"names": "Python, JavaScript"}
    response = client.post("/api/skills", json=data)
    assert response.status_code == 200

    # Should have only 2 skills total
    response = client.get("/api/skills")
    results = response.json()
    assert len(results) == 2


def test_skills_alphabetical_order(client):
    """Test that skills are returned in alphabetical order."""
    data = {"names": "Svelte, Python, FastAPI, React"}
    client.post("/api/skills", json=data)

    response = client.get("/api/skills")
    results = response.json()
    names = [s["name"] for s in results]
    assert names == ["FastAPI", "Python", "React", "Svelte"]


def test_delete_nonexistent_skill(client):
    """Test deleting a skill that doesn't exist."""
    response = client.delete("/api/skills/9999")
    assert response.status_code == 404
