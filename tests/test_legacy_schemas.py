from backend.app.legacy.schemas_song import LegacySong, LegacySection, LegacyLine, LegacyChord


def test_legacy_song_schema_basic():
    song = LegacySong(
        title="T",
        artist="A",
        content="line1\nline2",
        sections=[
            LegacySection(
                name="S1",
                lines=[LegacyLine(text="line1", chords=[LegacyChord(name="C")])],
            )
        ],
    )
    assert song.title == "T"
    assert song.artist == "A"
    assert song.sections and len(song.sections) == 1
    assert song.sections[0].lines[0].text == "line1"
    assert song.sections[0].lines[0].chords and song.sections[0].lines[0].chords[0].name == "C"
