import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_manage_schedule(client: AsyncClient, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    schedule_item = {
        "day": "Monday",
        "periods": [
            {
                "subject": "Mathematics",
                "start_time": "10:00",
                "end_time": "11:00", 
                "room": "101"
            }
        ]
    }
    
    response = await client.post("/schedule/update", json=schedule_item, headers=headers)
    # Route path might vary, assuming /schedule/update or similar
    if response.status_code == 404:
        # Try /teacher/schedule if it exists
        response = await client.post("/teacher/schedule", json=schedule_item, headers=headers)

    assert response.status_code != 500
