# In-memory storage for songs (will be replaced with database later)
from typing import List, Dict, Optional
from datetime import datetime
from ..models.song import Song, SongCreate, SongUpdate
import uuid

class SongRepository:
    def __init__(self):
        # Initialize with some demo data
        self.songs: Dict[int, Song] = {
            1: Song(
                id=1,
                title="Hey Jude",
                artist="The Beatles",
                content="Hey Jude, don't make it bad...",
                metadata={"key": "F", "tempo": 72},
                created_at=datetime.fromisoformat("2024-01-01T00:00:00"),
                sections=[
                    {"id": "1", "name": "Intro", "start_beat": 0, "length_beats": 16, "color": "#8B5CF6"},
                    {"id": "2", "name": "Verse", "start_beat": 16, "length_beats": 32, "color": "#10B981"}
                ]
            ),
            2: Song(
                id=2,
                title="Let It Be",
                artist="The Beatles",
                content="When I find myself in times of trouble...",
                metadata={"key": "C", "tempo": 76},
                created_at=datetime.fromisoformat("2024-01-02T00:00:00")
            ),
            3: Song(
                id=3,
                title="Yesterday",
                artist="The Beatles",
                content="Yesterday, all my troubles seemed so far away...",
                metadata={"key": "F", "tempo": 85},
                created_at=datetime.fromisoformat("2024-01-03T00:00:00")
            )
        }
        self.next_id = 4

    def get_all(self) -> List[Song]:
        return list(self.songs.values())

    def get_by_id(self, song_id: int) -> Optional[Song]:
        return self.songs.get(song_id)

    def create(self, song_data: SongCreate) -> Song:
        song = Song(
            id=self.next_id,
            **song_data.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.songs[self.next_id] = song
        self.next_id += 1
        return song

    def update(self, song_id: int, song_data: SongUpdate) -> Optional[Song]:
        if song_id not in self.songs:
            return None

        existing_song = self.songs[song_id]
        update_data = song_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(existing_song, field, value)

        existing_song.updated_at = datetime.now()
        return existing_song

    def delete(self, song_id: int) -> bool:
        if song_id in self.songs:
            del self.songs[song_id]
            return True
        return False

    def copy(self, song_id: int) -> Optional[Song]:
        original = self.songs.get(song_id)
        if not original:
            return None

        # Create a copy with new ID and title prefix
        copy_data = original.model_dump()
        copy_data['title'] = f"Copy of {original.title}"
        copy_data['id'] = None  # Will be assigned by create

        # Generate new IDs for sections and lanes
        if 'sections' in copy_data:
            for section in copy_data['sections']:
                section['id'] = str(uuid.uuid4())

        if 'lanes' in copy_data:
            for lane in copy_data['lanes']:
                lane['id'] = str(uuid.uuid4())
                for item in lane.get('items', []):
                    item['id'] = str(uuid.uuid4())

        song_create = SongCreate(**{k: v for k, v in copy_data.items() if k != 'id'})
        return self.create(song_create)

# Global repository instance
song_repository = SongRepository()
