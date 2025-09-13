# 🎵 DAWSheet Application Menu Tree & Route Map

## 📁 **MAIN NAVIGATION**

```
🏠 http://localhost:3000/
├── 📚 /songs                    → Song Library & Management
├── 📥 /import-json             → JSON Import with Lyrics Integration  ⭐
├── 📥 /import                  → Legacy Multi-format Import
├── 📖 /library                 → Song Library (Alternative View)
├── 🎛️  /timeline               → Timeline Viewer
├── ✏️  /editor                 → Song Editor
├── 🎙️  /record                 → Recording Interface
└── 🧪 [Development Pages]      → Design & Testing Pages
```

---

## 🎯 **CORE FUNCTIONALITY ROUTES**

### **📚 Song Management**
```
/songs                          📋 Song Library & Dashboard ⭐
├── → Lists all songs with metadata
├── → Create new songs
├── → Edit existing songs
├── → Quick actions (delete, duplicate)
└── → **DRAG & DROP [trk] LOGO** → Import files instantly

/songs/[id]                     🎵 Individual Song View ⭐
├── → Timeline visualization with lyrics rail
├── → Chord progression display
├── → Section markers
├── → Interactive scrolling timeline
└── → **LYRICS RAIL DISPLAY** (emerald badges)

/songs/[id]/timeline            📊 Dedicated Timeline View
├── → Full-screen timeline mode
└── → Advanced timeline controls

/songs/from-draft/[id]          📝 Draft to Song Conversion
└── → Convert draft songs to final songs
```

### **📥 Import System**
```
/import-json                    🎯 **PRIMARY IMPORT** ⭐
├── → Upload JSON song files
├── → **AUTO-FETCH LYRICS** from LRCLIB
├── → "Include Lyrics" checkbox (default: ON)
├── → Real-time import status
├── → **SMART TITLE CLEANING** (removes track numbers, fixes underscores)
└── → Direct integration with song view

/import                         🔧 Legacy Multi-format Import
├── → Text/lyrics parsing
├── → Multiple file formats
├── → Bulk import capabilities
├── → **UNIFIED TITLE CLEANING** (same as import-json)
└── → Advanced parsing options
```

### **🎵 Lyrics Integration (Global)**
```
Title Cleaning Pipeline         🧹 **UNIVERSAL LYRICS MATCHING**
├── → Removes track numbers (e.g., "07 - Title" → "Title")
├── → Converts underscores to spaces (e.g., "Can't_Buy_Me_Love" → "Can't Buy Me Love")
├── → Normalizes whitespace
├── → Applied to ALL import methods and manual lyrics fetching
└── → Utility: backend/app/utils/lyrics.py
```

### **📖 Library Management**
```
/library                        📚 Song Library (Grid View)
├── → Server status indicator
├── → Song grid with thumbnails
├── → Bulk operations
└── → Search & filtering

/library/[id]                   📄 Library Song Details
├── → Song metadata view
├── → Library-specific actions
└── → Quick edit options
```

---

## 🎛️ **PRODUCTION TOOLS**

### **🎵 Creative Tools**
```
/timeline                       📊 Global Timeline Viewer
├── → Cross-song timeline analysis
├── → Timeline comparison tools
└── → Export options

/editor                         ✏️ Song Structure Editor
├── → Chord progression editing
├── → Section arrangement
├── → BPM & time signature
└── → Metadata editing

/record                         🎙️ Recording Interface
├── → Audio recording controls
├── → Metronome & click track
├── → Recording session management
└── → Audio export options
```

---

## 🧪 **DEVELOPMENT & TESTING**

### **🎨 Design System**
```
/design                         🎨 Main Design System Demo
/design-simple                  🎨 Simplified Design Demo
/design-test                    🧪 Design Testing Page
/design0000                     🎨 Design Iteration Demo
/design.legacy                  📜 Legacy Design Reference
```

### **🔧 Development Tools**
```
/selector-demo                  🎯 Component Selector Demo
/legacy                         📜 Legacy System Interface
├── → Legacy API integration
└── → Backward compatibility testing
```

---

## 🎯 **RECOMMENDED WORKFLOW**

### **🚀 For New Songs:**
```
1. 📥 /import-json              → Import song structure + auto-fetch lyrics
2. 🎵 /songs/[id]              → View with lyrics rail
3. ✏️  /editor                  → Fine-tune arrangement
4. 🎙️  /record                 → Record your version
```

### **📚 For Existing Songs:**
```
1. 📚 /songs or /library        → Browse your collection
2. 🎵 /songs/[id]              → View with timeline + lyrics
3. 📊 /timeline                → Analyze song structure
4. ✏️  /editor                  → Make adjustments
```

---

## ⭐ **KEY FEATURES BY ROUTE**

### **🎵 /songs/[id] - Song View** (LYRICS RAIL ✨)
- **Emerald lyrics badges** positioned at beat locations
- **Horizontal scrolling** through timeline
- **Hover timestamps** showing exact timing
- **Synchronized with chords** and sections

### **📥 /import-json** (IMPORT WITH LYRICS ✨)
- **"Include Lyrics" checkbox** (enabled by default)
- **LRCLIB integration** for automatic lyrics fetching
- **Real-time status** of import + lyrics process
- **Direct navigation** to imported song

### **📚 /songs** (MAIN LIBRARY)
- **Server status indicator** (online/offline/checking)
- **Quick song creation** and management
- **Search and filtering** capabilities
- **Bulk operations** support

---

## 🔗 **API ENDPOINTS REFERENCE**

```
Backend: http://localhost:8000
Frontend: http://localhost:3000

Key APIs:
├── /v1/songs/[id]/doc         → Song data with lyrics
├── /songs/[id]/lyrics         → Fetch lyrics from LRCLIB
├── /import/json               → Import JSON songs
└── /health                    → Backend status check
```

---

## 🎯 **YOUR CURRENT TASK**

You mentioned trying the **/import-json** path - this is indeed the **correct route** for:
- ✅ JSON song import
- ✅ Automatic lyrics fetching
- ✅ Integration with song view lyrics rail

The path `/import-jason` would be a 404 - the correct path is `/import-json` (with 'json', not 'jason').
