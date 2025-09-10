import json
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app import models

@pytest.mark.asyncio
async def test_timeline_api_jcrd_passthrough(async_client: AsyncClient, db_session: AsyncSession):
    jcrd = {
        "metadata": {"title": "Test Song", "artist": "Tester", "tempo": 150, "time_signature": "3/4", "key": "Key G"},
        "sections": [
            {"name": "intro", "start_time": 0.0, "end_time": 2.0, "chords": []},
            {"name": "verse", "start_time": 2.0, "end_time": 6.0, "chords": [
                {"chord": "G", "start_time": 2.0, "end_time": 3.0},
                {"chord": "C", "start_time": 3.0, "end_time": 4.0},
            ]},
        ],
        "chord_progression": [
            {"time": 4.0, "chord": "D", "duration": 1.0},
        ],
    }
    # Create a user (assuming minimal fields username/email may exist; adapt if model differs)
    user = models.User(email="tester@example.com") if hasattr(models, "User") else None
    if user:
        db_session.add(user)
        await db_session.flush()
        user_id = user.id
    else:
        user_id = 1  # fallback if user model absent
    song = models.Song(user_id=user_id, title="Test Song", artist="Tester", content=json.dumps(jcrd))
    db_session.add(song)
    await db_session.commit()
    await db_session.refresh(song)

    resp = await async_client.get(f"/v1/songs/{song.id}/timeline")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    tl = data["timeline"]
    assert tl["bpmDefault"] == 150
    assert tl["timeSigDefault"]["num"] == 3 and tl["timeSigDefault"]["den"] == 4
    assert any(s["name"] == "intro" for s in tl["sections"])
    symbols = [c["symbol"] for c in tl["chords"][:3]]
    # Expect G, C, D among first chords (order may vary after sorting)
    assert set(["G", "C"]).issubset(set(symbols))
    assert tl["key"].upper().startswith("G")
