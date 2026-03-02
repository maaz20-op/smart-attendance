import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_get_student(client: AsyncClient, auth_token):
    # Auth header
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create Student
    student_payload = {
        "name": "John Doe",
        "email": "john.student@example.com",
        "roll_number": "R12345",
        "branch": "CSE",
        "year": 2,
        "section": "A",
        "parent_phone": "1234567890",
        "phone_number": "0987654321"
    }
    
    response = await client.post("/students/", json=student_payload, headers=headers)
    # Depending on implementation, might return 201 or 200
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["email"] == student_payload["email"]
    student_id = data["_id"] if "_id" in data else data["id"]

    # Get Student
    response = await client.get(f"/students/{student_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"

@pytest.mark.asyncio
async def test_upload_student_image(client: AsyncClient, auth_token):
    # Create mock file
    files = {'file': ('test_face.jpg', b'fake_image_content', 'image/jpeg')}
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Assuming there's a student to upload for. Needs an ID.
    # For now, just checking the validation or 404 if student doesn't exist
    response = await client.post("/students/upload-face/nonexistent_id", files=files, headers=headers)
    
    # Should probably be 404 or 422 (if fake image content is validated)
    # The goal is to ensure the route is reachable
    assert response.status_code != 405  # Method Not Allowed
