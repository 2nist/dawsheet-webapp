# Quick Setup: Default Beatles Import Workflow

## Make Beatles Import the Default Experience

### 1. Update Landing Page

Replace the current landing page with a Beatles-focused import interface:

```tsx
// web/pages/index.tsx - Make Beatles import prominent
export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-white mb-8 text-center">
          DAWSheet - Beatles Timeline Analyzer
        </h1>
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg p-8 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4">
              Import Beatles .jcrd.json Files
            </h2>
            <p className="text-gray-600 mb-6">
              Upload any Beatles chord progression file to see synchronized 
              sections, chords, and LRCLIB lyrics in an interactive timeline.
            </p>
            <FileImportButton onSuccess={() => router.push('/songs')} />
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 2. Add Sample Files Section

```tsx
// Show available Beatles songs
<div className="mt-8">
  <h3 className="text-lg font-medium mb-4">Sample Songs Available:</h3>
  <div className="grid grid-cols-2 gap-2 text-sm">
    <div>• Here Comes The Sun</div>
    <div>• Yesterday</div>
    <div>• Let It Be</div>
    <div>• Hey Jude</div>
  </div>
</div>
```

### 3. Direct Import URLs

Add quick import endpoints for common songs:

```python
# backend/app/main.py
@app.post("/import/beatles/{song_name}")
async def import_beatles_song(song_name: str):
    """Quick import for common Beatles songs"""
    file_map = {
        "here-comes-the-sun": "11_-_Abbey_Road_07_-_Here_Comes_The_Sun.jcrd.json",
        "yesterday": "05_-_Help!_13_-_Yesterday.jcrd.json",
        "let-it-be": "12_-_Let_It_Be_06_-_Let_It_Be.jcrd.json"
    }
    
    if song_name in file_map:
        file_path = f"References/Beatles-Chords/{file_map[song_name]}"
        # Load and import the file
```

### 4. Update Navigation

```tsx
// web/components/Layout.tsx - Add quick navigation
<nav className="bg-slate-800 text-white p-4">
  <div className="flex justify-between items-center">
    <Link href="/" className="text-xl font-bold">DAWSheet</Link>
    <div className="space-x-4">
      <Link href="/songs">Song Library</Link>
      <Link href="/import">Import Beatles</Link>
      <Link href="/timeline">Timeline View</Link>
    </div>
  </div>
</nav>
```

## Deployment Configuration

### 1. Environment Variables

```bash
# .env
NEXT_PUBLIC_API_BASE=http://localhost:8000
LYRICS_PROVIDER_ENABLED=true
DEFAULT_IMPORT_TYPE=beatles
```

### 2. Docker Compose Update

```yaml
# docker-compose.yml - Ensure volumes for Beatles data
services:
  api:
    volumes:
      - ./References:/app/References:ro
      - ./backend:/app
  web:
    environment:
      - DEFAULT_IMPORT_TYPE=beatles
```

## Default User Flow

1. **User visits app** → Sees Beatles import interface
2. **Clicks "Choose File"** → Browser opens to .jcrd.json files  
3. **Selects Beatles song** → Auto-imports with LRCLIB lyrics
4. **Views timeline** → Sees complete 4-rail synchronized display
5. **Explores controls** → Drag, zoom, navigate through song

## Quick Commands

```bash
# Start with Beatles import as default
docker compose up -d

# Import sample song programmatically  
curl -X POST http://localhost:8000/import/beatles/here-comes-the-sun

# View timeline directly
open http://localhost:3000/songs/1
```

This setup makes Beatles import the primary workflow while maintaining flexibility for other formats.