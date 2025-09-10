import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app import models


@pytest.mark.asyncio
async def test_timeline_endpoint_success(async_client: AsyncClient, db_session: AsyncSession):
    # Insert song with simple chord/lyric content (group markers + chord line + lyric line)
    song = models.Song(user_id=1, title="T", artist="A", content="1\nC  G  Am  F\nHello world\n")
    db_session.add(song)
    await db_session.commit()
    await db_session.refresh(song)
    r = await async_client.get(f"/v1/songs/{song.id}/timeline")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "timeline" in data
    tl = data["timeline"]
    assert tl["bpmDefault"] > 0
    assert len(tl["chords"]) >= 1
    assert len(tl["lyrics"]) >= 1


@pytest.mark.asyncio
async def test_timeline_endpoint_422(async_client: AsyncClient, db_session: AsyncSession):
    # Song with only lyrics, no chords
    song = models.Song(user_id=1, title="Only Lyrics", artist="A", content="Just a lyric line\n")
    db_session.add(song)
    await db_session.commit()
    await db_session.refresh(song)
    r = await async_client.get(f"/v1/songs/{song.id}/timeline")
    assert r.status_code == 422
    detail = r.json()["detail"]
    # Expect chords.empty in validation
    codes = {v["code"] for v in detail["validation"]}
    assert "chords.empty" in codes
