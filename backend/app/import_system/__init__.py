"""
Unified Import System Architecture

This module provides a pluggable, extensible import system that can handle
multiple file formats and convert them all to the standardized JCRD format.

Architecture Overview:
1. Format Detection - Identify file type from extension and content
2. Converter Registry - Pluggable converters for each format
3. JCRD Normalization - All converters output to JCRD standard
4. Lyrics Integration - Automatic lyrics fetching with global title cleaning
5. Song Creation - Consistent song creation with metadata preservation

Supported Formats (Planned):
- ✅ .jcrd.json - Native format (direct processing)
- 🚧 .json - General JSON (smart detection for various schemas)
- 🚧 .mp3 - Audio analysis → chord progression extraction
- 🚧 .cho - ChordPro format → chord progression + lyrics
- 🚧 .mid/.midi - MIDI analysis → timing + chord detection
- 🚧 .lab - Audio annotation → timestamped chord labels
- 🚧 .jams - JSON Annotated Music Specification
- 🚧 .xml - MusicXML → musical notation analysis
- 🚧 .rrp - RealBand/Reaper projects → timeline extraction
- 🚧 .txt - Text-based chord charts → pattern detection
- 🚧 .pdf - PDF chord charts → OCR + pattern recognition

Flow:
File Upload → Format Detection → Converter Selection → JCRD Output →
Lyrics Integration → Song Creation → Response

Benefits:
- Single import endpoint (/import/unified)
- Consistent behavior across all formats
- Easy to add new format support
- No threading issues (single processing pipeline)
- Automatic lyrics integration
- Extensible without breaking existing functionality
"""

from typing import Dict, List, Optional, Any, Protocol, Union
from pathlib import Path
import mimetypes


class ImportResult:
    """Standardized result from any import operation"""

    def __init__(
        self,
        success: bool,
        jcrd_data: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        artist: Optional[str] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.jcrd_data = jcrd_data or {}
        self.title = title or "Untitled"
        self.artist = artist or ""
        self.warnings = warnings or []
        self.errors = errors or []
        self.metadata = metadata or {}


class FormatConverter(Protocol):
    """Protocol for format-specific converters"""

    @property
    def supported_extensions(self) -> List[str]:
        """List of file extensions this converter handles"""
        ...

    @property
    def supported_mimetypes(self) -> List[str]:
        """List of MIME types this converter handles"""
        ...

    @property
    def format_name(self) -> str:
        """Human-readable name for this format"""
        ...

    async def convert(self, file_content: bytes, filename: str) -> ImportResult:
        """Convert file content to JCRD format"""
        ...

    def can_handle(self, filename: str, mimetype: Optional[str] = None) -> bool:
        """Check if this converter can handle the given file"""
        ...


class FormatDetector:
    """Detects file format from filename and content analysis"""

    @staticmethod
    def detect_format(filename: str, content: bytes) -> Dict[str, Any]:
        """
        Detect file format and return metadata

        Returns:
            {
                'format': str,           # Detected format (jcrd, mp3, midi, etc.)
                'extension': str,        # File extension
                'mimetype': str,         # MIME type
                'confidence': float,     # Detection confidence (0.0-1.0)
                'analysis': dict         # Format-specific analysis
            }
        """
        ext = Path(filename).suffix.lower()
        mimetype, _ = mimetypes.guess_type(filename)

        # Basic format detection logic
        format_map = {
            '.json': 'json',
            '.jcrd': 'jcrd',
            '.mp3': 'mp3',
            '.wav': 'audio',
            '.flac': 'audio',
            '.mid': 'midi',
            '.midi': 'midi',
            '.cho': 'chordpro',
            '.lab': 'lab',
            '.jams': 'jams',
            '.xml': 'musicxml',
            '.rrp': 'reaper',
            '.txt': 'text',
            '.pdf': 'pdf'
        }

        detected_format = format_map.get(ext, 'unknown')
        confidence = 1.0 if detected_format != 'unknown' else 0.0

        # For JSON files, try to detect JCRD vs generic JSON
        if detected_format == 'json':
            try:
                import json
                data = json.loads(content.decode('utf-8', errors='ignore'))
                if isinstance(data, dict):
                    # Check for JCRD markers
                    metadata = data.get('metadata', {})
                    has_tempo = 'tempo' in metadata or 'bpm' in metadata
                    has_structure = 'sections' in data or 'chord_progression' in data
                    if has_tempo and has_structure:
                        detected_format = 'jcrd'
                        confidence = 0.95
            except:
                pass

        return {
            'format': detected_format,
            'extension': ext,
            'mimetype': mimetype or 'application/octet-stream',
            'confidence': confidence,
            'analysis': {
                'size_bytes': len(content),
                'filename': filename
            }
        }


# Format support status for UI display
FORMAT_STATUS = {
    'jcrd': {'status': '✅', 'name': 'JCRD JSON', 'ready': True},
    'json': {'status': '✅', 'name': 'Generic JSON', 'ready': True},
    'mp3': {'status': '🚧', 'name': 'MP3 Audio', 'ready': False},
    'audio': {'status': '🚧', 'name': 'Audio Files', 'ready': False},
    'midi': {'status': '🚧', 'name': 'MIDI', 'ready': False},
    'chordpro': {'status': '🚧', 'name': 'ChordPro', 'ready': False},
    'lab': {'status': '🚧', 'name': 'Audio Labels', 'ready': False},
    'jams': {'status': '🚧', 'name': 'JAMS', 'ready': False},
    'musicxml': {'status': '🚧', 'name': 'MusicXML', 'ready': False},
    'reaper': {'status': '🚧', 'name': 'Reaper Project', 'ready': False},
    'text': {'status': '🚧', 'name': 'Text Charts', 'ready': False},
    'pdf': {'status': '🚧', 'name': 'PDF Charts', 'ready': False},
}
