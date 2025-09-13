# DAWSheet Import System Guide

## Overview

The DAWSheet application now supports automatic import of `.jcrd.json` files (Beatles Chord Research Data) with integrated LRCLIB lyrics fetching. This creates a complete synchronized timeline view with sections, chords, and timestamped lyrics.

## Import Process

### 1. File Format Support

**Primary Format: `.jcrd.json` (Beatles files)**
```json
{
  "metadata": {
    "title": "07 - Here_Comes_The_Sun",
    "artist": "The Beatles",
    "album": "11 - Abbey_Road", 
    "tempo": 144,
    "time_signature": "4/4"
  },
  "sections": [
    {
      "name": "intro",
      "start_time": 0.35,
      "end_time": 14.704
    }
  ],
  "chord_progression": [
    {
      "time": 0.366281,
      "chord": "A",
      "duration": 3.239183
    }
  ]
}
```

### 2. Automatic Processing

When importing a `.jcrd.json` file, the system automatically:

1. **Title Cleaning**: Removes track numbers and underscores
   - `"07 - Here_Comes_The_Sun"` → `"Here Comes The Sun"`

2. **Artist Normalization**: Standardizes artist names
   - `"The Beatles"` → `"The Beatles"`

3. **LRCLIB Lyrics Fetching**: Searches for timestamped lyrics
   - Uses cleaned title and artist for better matching
   - Fetches synced lyrics with precise timestamps

4. **Data Conversion**: Transforms to timeline format
   - Sections with start beats and lengths
   - Chord progressions with beat positions
   - Lyrics with beat synchronization

### 3. Timeline Output

The imported song displays in a four-rail synchronized timeline:

- **Section Rail**: Song structure (intro, verse, chorus, bridge, outro)
- **Timeline Rail**: Beat markers and time signature
- **Chord Rail**: Chord progressions with symbols and timing  
- **Lyric Rail**: Timestamped lyrics from LRCLIB

## Backend Architecture

### Enhanced POST /songs Endpoint

```python
@app.post("/songs")
async def create_song(song: dict):
    """Enhanced song creation with automatic LRCLIB lyrics fetching"""
    
    # Check if this is a Beatles .jcrd.json file
    if "metadata" in song and song["metadata"].get("title"):
        # Clean title and artist
        clean_title = clean_title_for_lyrics(song["metadata"]["title"])
        clean_artist = normalize_artist_name(song["metadata"]["artist"])
        
        # Auto-fetch LRCLIB lyrics
        if LYRICS_ENABLED:
            lyrics_result = await search_timestamped_lyrics(
                title=clean_title, artist=clean_artist
            )
            if lyrics_result.get("matched"):
                new_song["lyrics"] = lyrics_result
```

### Timeline Conversion (/v1/songs/{id}/doc)

```python
# Convert Beatles sections
if parsed_content.get("sections"):
    for section in parsed_content["sections"]:
        doc["sections"].append({
            "id": f"section_{i}",
            "name": section.get("name"),
            "startBeat": section.get("start_time", 0) * 2,
            "lengthBeats": (section.get("end_time", 0) - section.get("start_time", 0)) * 2
        })

# Convert chord progression  
if parsed_content.get("chord_progression"):
    for chord in parsed_content["chord_progression"]:
        doc["chords"].append({
            "symbol": chord.get("chord"),
            "startBeat": chord.get("time", 0) * 2
        })
```

## Frontend Components

### FileImportButton Component

Enhanced to handle Beatles metadata extraction:

```tsx
// Detect Beatles .jcrd format
if (file.name.endsWith('.json') || file.name.endsWith('.jcrd')) {
  const parsed = JSON.parse(text);
  songData = {
    title: parsed.metadata?.title || parsed.title,
    artist: parsed.metadata?.artist || parsed.artist,
    content: text
  };
}
```

### Timeline Page (/songs/[id])

Four-rail synchronized display:

```tsx
<SectionRail sections={rotatingContent.sections} zoom={zoom} />
<BarRuler beatsPerBar={beatsPerBar} totalBeats={extendedTotalBeats} />
<ChordLane chords={rotatingContent.chords} zoom={zoom} />
<LyricLane lyrics={rotatingContent.lyrics} zoom={zoom} />
```

## Usage Instructions

### For Users

1. **Go to**: http://localhost:3000
2. **Click**: "Choose File" button
3. **Select**: Any `.jcrd.json` file from `References/Beatles-Chords/`
4. **Wait**: For automatic LRCLIB lyrics fetching (2-3 seconds)
5. **Click**: On imported song to view timeline
6. **Interact**: Drag timeline to navigate, scroll to zoom

### For Developers

1. **Start Services**:
   ```bash
   docker compose up -d api web
   ```

2. **Test Import**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     --data-binary "@References/Beatles-Chords/[song].jcrd.json" \
     http://localhost:8000/songs
   ```

3. **View Timeline**:
   ```bash
   curl http://localhost:8000/v1/songs/[id]/doc
   ```

## Data Flow

```
.jcrd.json file
    ↓ FileImportButton
POST /songs (with metadata detection)
    ↓ Title cleaning & LRCLIB search
Song stored with lyrics
    ↓ Timeline page request
GET /v1/songs/{id}/doc
    ↓ Beatles data conversion  
Timeline format with 4 rails
    ↓ React components
Synchronized timeline display
```

## Key Features

✅ **Automatic LRCLIB Integration**: No manual lyrics search needed
✅ **Smart Title Cleaning**: Handles track numbers and formatting  
✅ **Synchronized Timeline**: All rails move together
✅ **Real Beatles Data**: Authentic chord progressions and structure
✅ **Interactive Navigation**: Drag and scroll controls
✅ **Precise Timing**: Beat-level synchronization

## File Locations

- **Import UI**: `web/components/FileImportButton.tsx`
- **Backend Logic**: `backend/app/main.py`
- **Timeline View**: `web/pages/songs/[id].tsx`
- **Sample Data**: `References/Beatles-Chords/*.jcrd.json`
- **Title Cleaning**: `backend/app/utils/lyrics.py`
- **LRCLIB Service**: `backend/app/services/lyrics_providers/lrclib.py`

## Success Metrics

A successful import should result in:
- **Clean title** (no track numbers)
- **LRCLIB lyrics** with `lyrics_source: "lrclib_auto"`
- **Section rail** with song structure
- **Chord rail** with progression
- **Lyric rail** with timestamps
- **Interactive timeline** with synchronized scrolling

This system transforms raw Beatles chord data into a rich, interactive musical timeline with automatic lyrics integration.