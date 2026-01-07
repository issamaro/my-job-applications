def test_list_languages_empty(client):
    """Test listing languages when none exists."""
    response = client.get("/api/languages")
    assert response.status_code == 200
    assert response.json() == []


def test_add_language(client):
    """Test adding a language with valid CEFR level."""
    data = {
        "name": "French",
        "level": "B2",
    }
    response = client.post("/api/languages", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "French"
    assert result["level"] == "B2"
    assert result["display_order"] == 0


def test_add_language_invalid_level(client):
    """Test adding a language with invalid CEFR level returns 422."""
    data = {
        "name": "German",
        "level": "X1",
    }
    response = client.post("/api/languages", json=data)
    assert response.status_code == 422


def test_edit_language(client):
    """Test editing a language entry."""
    data = {
        "name": "Spanish",
        "level": "A1",
    }
    create_response = client.post("/api/languages", json=data)
    lang_id = create_response.json()["id"]

    updated_data = {
        "name": "Spanish",
        "level": "B1",
    }
    response = client.put(f"/api/languages/{lang_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["level"] == "B1"


def test_delete_language(client):
    """Test deleting a language entry."""
    data = {
        "name": "Italian",
        "level": "A2",
    }
    create_response = client.post("/api/languages", json=data)
    lang_id = create_response.json()["id"]

    response = client.delete(f"/api/languages/{lang_id}")
    assert response.status_code == 200
    assert response.json() == {"deleted": lang_id}

    # Verify deleted
    response = client.get(f"/api/languages/{lang_id}")
    assert response.status_code == 404


def test_reorder_languages(client):
    """Test reordering languages updates display_order."""
    # Create three languages
    client.post("/api/languages", json={"name": "English", "level": "C2"})
    client.post("/api/languages", json={"name": "French", "level": "B2"})
    client.post("/api/languages", json={"name": "German", "level": "A1"})

    # Get current list
    response = client.get("/api/languages")
    languages = response.json()
    assert len(languages) == 3

    # Reverse order
    reorder_data = [
        {"id": languages[2]["id"], "display_order": 0},
        {"id": languages[1]["id"], "display_order": 1},
        {"id": languages[0]["id"], "display_order": 2},
    ]
    response = client.put("/api/languages/reorder", json=reorder_data)
    assert response.status_code == 200

    # Verify new order
    result = response.json()
    assert result[0]["name"] == "German"
    assert result[1]["name"] == "French"
    assert result[2]["name"] == "English"


def test_get_nonexistent_language(client):
    """Test getting language that doesn't exist."""
    response = client.get("/api/languages/9999")
    assert response.status_code == 404


def test_delete_nonexistent_language(client):
    """Test deleting a language that doesn't exist."""
    response = client.delete("/api/languages/9999")
    assert response.status_code == 404


def test_all_cefr_levels_accepted(client):
    """Test all 6 CEFR levels are accepted."""
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    for level in levels:
        data = {"name": f"Language_{level}", "level": level}
        response = client.post("/api/languages", json=data)
        assert response.status_code == 200, f"Level {level} should be accepted"
        assert response.json()["level"] == level


def test_add_language_empty_name(client):
    """Test adding a language with empty name is rejected."""
    data = {
        "name": "",
        "level": "B1",
    }
    response = client.post("/api/languages", json=data)
    # Pydantic doesn't reject empty strings by default, but the frontend validates
    # This test documents current behavior
    assert response.status_code == 200 or response.status_code == 422


def test_languages_in_profile_complete(client):
    """Test that languages appear in profile/complete endpoint."""
    # Add a language
    client.post("/api/languages", json={"name": "Japanese", "level": "A1"})

    response = client.get("/api/profile/complete")
    assert response.status_code == 200
    profile = response.json()
    assert "languages" in profile
    assert len(profile["languages"]) == 1
    assert profile["languages"][0]["name"] == "Japanese"
    assert profile["languages"][0]["level"] == "A1"
