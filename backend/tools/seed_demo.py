import json
import asyncio
from httpx import AsyncClient

API = "http://localhost:8000"

async def main():
    with open("/app/samples/demo_song.json", "r", encoding="utf-8") as f:
        sample = json.load(f)
    title = sample.get("metadata", {}).get("title") or "Demo Song"
    artist = sample.get("metadata", {}).get("artist") or ""
    content = json.dumps(sample)
    async with AsyncClient(timeout=30) as client:
        # create song with JSON content
        r = await client.post(f"{API}/songs", json={"title": title, "artist": artist, "content": content})
        r.raise_for_status()
        song = r.json()
        sid = song["id"]
        print("Created song", sid)
        # hit v1 timeline to warm mapping path
        r2 = await client.get(f"{API}/v1/songs/{sid}/timeline")
        print("timeline:", r2.status_code)
        r3 = await client.get(f"{API}/v1/songs/{sid}/timeline/debug")
        print("timeline/debug:", r3.status_code)

if __name__ == "__main__":
    asyncio.run(main())
