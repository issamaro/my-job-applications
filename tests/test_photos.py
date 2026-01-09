import base64


# Sample valid base64 image data (small 1x1 JPEG)
VALID_JPEG_DATA = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBEQCEAwEPwAB//9k="
VALID_PNG_DATA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def create_personal_info(client):
    """Helper to create personal info before photo tests."""
    return client.put(
        "/api/users",
        json={"full_name": "Test User", "email": "test@example.com"},
    )


def test_get_photo_empty(client):
    """GET /api/photos returns null when no photo."""
    response = client.get("/api/photos")
    assert response.status_code == 200
    assert response.json() is None


def test_get_photo_no_personal_info(client):
    """GET /api/photos returns null when no personal info exists."""
    response = client.get("/api/photos")
    assert response.status_code == 200
    assert response.json() is None


def test_upload_photo_no_personal_info(client):
    """PUT /api/photos returns 400 when no personal info exists."""
    response = client.put("/api/photos", json={"image_data": VALID_JPEG_DATA})
    assert response.status_code == 400
    assert "Personal info must be created first" in response.json()["detail"]


def test_upload_photo(client):
    """PUT /api/photos with valid data URL returns 200."""
    create_personal_info(client)
    response = client.put("/api/photos", json={"image_data": VALID_JPEG_DATA})
    assert response.status_code == 200
    assert response.json()["image_data"] == VALID_JPEG_DATA


def test_get_photo_after_upload(client):
    """GET /api/photos returns uploaded photo."""
    create_personal_info(client)
    client.put("/api/photos", json={"image_data": VALID_JPEG_DATA})

    response = client.get("/api/photos")
    assert response.status_code == 200
    assert response.json()["image_data"] == VALID_JPEG_DATA


def test_replace_photo(client):
    """PUT /api/photos replaces existing photo."""
    create_personal_info(client)
    client.put("/api/photos", json={"image_data": VALID_JPEG_DATA})

    response = client.put("/api/photos", json={"image_data": VALID_PNG_DATA})
    assert response.status_code == 200
    assert response.json()["image_data"] == VALID_PNG_DATA

    # Verify it was actually replaced
    get_response = client.get("/api/photos")
    assert get_response.json()["image_data"] == VALID_PNG_DATA


def test_delete_photo(client):
    """DELETE /api/photos removes photo."""
    create_personal_info(client)
    client.put("/api/photos", json={"image_data": VALID_JPEG_DATA})

    response = client.delete("/api/photos")
    assert response.status_code == 204

    # Verify it was deleted
    get_response = client.get("/api/photos")
    assert get_response.json() is None


def test_delete_photo_not_found(client):
    """DELETE /api/photos returns 404 when no photo."""
    create_personal_info(client)
    response = client.delete("/api/photos")
    assert response.status_code == 404


def test_invalid_data_url_format(client):
    """PUT with invalid format returns 422."""
    create_personal_info(client)

    # Missing data: prefix
    response = client.put(
        "/api/photos", json={"image_data": "image/jpeg;base64,abc123"}
    )
    assert response.status_code == 422

    # Invalid mime type
    response = client.put(
        "/api/photos", json={"image_data": "data:image/gif;base64,abc123"}
    )
    assert response.status_code == 422

    # Invalid base64 characters
    response = client.put(
        "/api/photos", json={"image_data": "data:image/jpeg;base64,!!!invalid!!!"}
    )
    assert response.status_code == 422


def test_data_url_too_large(client):
    """PUT with oversized data returns 422."""
    create_personal_info(client)

    # Create a data URL larger than 15MB limit
    # Base64 encoding increases size by ~33%, so 12MB raw data -> ~16MB base64
    large_base64 = base64.b64encode(b"x" * 12_000_000).decode()
    large_data_url = f"data:image/jpeg;base64,{large_base64}"

    response = client.put("/api/photos", json={"image_data": large_data_url})
    assert response.status_code == 422


def test_photo_included_in_personal_info(client):
    """Photo field is included when getting personal info."""
    create_personal_info(client)
    client.put("/api/photos", json={"image_data": VALID_JPEG_DATA})

    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json()["photo"] == VALID_JPEG_DATA
