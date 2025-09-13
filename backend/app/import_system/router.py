"""
Unified Import Router - Single endpoint for all file formats

This router provides a clean, consistent interface for importing any supported
file format into the DAWSheet system.

Endpoint: POST /import/unified
- Accepts multiple files
- Auto-detects formats
- Converts to JCRD standard
- Integrates lyrics automatically
- Returns consistent results

Flow:
1. File upload and validation
2. Format detection for each file
3. Converter selection and execution
4. JCRD normalization
5. Lyrics integration (with global title cleaning)
6. Song creation and response
"""

from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import asyncio

from .registry import registry
from .converters.jcrd import JCRDConverter
from .converters.audio import MP3Converter, WAVConverter
from .converters.notation import MIDIConverter, MusicXMLConverter
from .converters.text_formats import ChordProConverter, TextChartConverter, PDFConverter
from .converters.specialized import LABConverter, JAMSConverter, ReaperConverter
from . import FormatDetector, FORMAT_STATUS, ImportResult
from ..utils.lyrics import clean_title_for_lyrics, normalize_artist_name
from ..services.lyrics_providers.lrclib import search_timestamped_lyrics
from ..config import settings

router = APIRouter(prefix="/import", tags=["unified-import"])


def _register_all_converters():
    """Register all available converters with the registry"""

    # Working converters
    registry.register("jcrd", JCRDConverter())

    # Stub converters (ready for implementation)
    registry.register("mp3", MP3Converter())
    registry.register("wav", WAVConverter())
    registry.register("midi", MIDIConverter())
    registry.register("musicxml", MusicXMLConverter())
    registry.register("chordpro", ChordProConverter())
    registry.register("text", TextChartConverter())
    registry.register("pdf", PDFConverter())
    registry.register("lab", LABConverter())
    registry.register("jams", JAMSConverter())
    registry.register("reaper", ReaperConverter())


# Initialize converters on module load
_register_all_converters()


@router.get("/formats")
async def get_supported_formats():
    """Get list of all supported file formats and their status"""
    registered_formats = registry.get_supported_formats()

    # Merge with planned formats that aren't yet registered
    all_formats = {**FORMAT_STATUS}

    # Update with actual registration status
    for name, info in registered_formats.items():
        if name in all_formats:
            all_formats[name].update(info)
        else:
            all_formats[name] = info

    return {
        "supported_formats": all_formats,
        "total_formats": len(all_formats),
        "ready_formats": len([f for f in all_formats.values() if f.get('ready', False)]),
        "planned_formats": len([f for f in all_formats.values() if not f.get('ready', False)])
    }


@router.post("/unified")
async def import_unified(
    files: List[UploadFile] = File(...),
    include_lyrics: Optional[bool] = Query(default=True),
    save_songs: Optional[bool] = Query(default=True)
):
    """
    Unified import endpoint for all file formats

    Args:
        files: List of files to import (supports multiple formats)
        include_lyrics: Whether to auto-fetch lyrics from LRCLIB
        save_songs: Whether to save imported songs to database

    Returns:
        {
            "success": true,
            "imported": [...],      # Successfully imported files
            "failed": [...],        # Failed imports with errors
            "warnings": [...],      # Non-fatal warnings
            "statistics": {...}     # Import statistics
        }
    """

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    results = {
        "success": True,
        "imported": [],
        "failed": [],
        "warnings": [],
        "statistics": {
            "total_files": len(files),
            "successful": 0,
            "failed": 0,
            "formats_used": {},
            "lyrics_found": 0
        }
    }

    # Process each file
    for file in files:
        try:
            # Read file content
            content = await file.read()
            filename = file.filename or "unknown"

            # Detect format
            format_info = FormatDetector.detect_format(filename, content)
            format_name = format_info['format']

            # Track format usage
            if format_name not in results["statistics"]["formats_used"]:
                results["statistics"]["formats_used"][format_name] = 0
            results["statistics"]["formats_used"][format_name] += 1

            # Find appropriate converter
            converter = registry.find_converter(filename, file.content_type)

            if not converter:
                results["failed"].append({
                    "filename": filename,
                    "format": format_name,
                    "error": f"No converter available for format '{format_name}'",
                    "supported": format_name in FORMAT_STATUS
                })
                results["statistics"]["failed"] += 1
                continue

            # Convert to JCRD
            import_result = await converter.convert(content, filename)

            if not import_result.success:
                results["failed"].append({
                    "filename": filename,
                    "format": format_name,
                    "errors": import_result.errors,
                    "warnings": import_result.warnings
                })
                results["statistics"]["failed"] += 1
                continue

            # Add any converter warnings to global warnings
            if import_result.warnings:
                results["warnings"].extend([
                    f"{filename}: {warning}" for warning in import_result.warnings
                ])

            # Auto-fetch lyrics if enabled and no lyrics in result
            lyrics_data = None
            if include_lyrics and settings.LYRICS_PROVIDER_ENABLED:
                if import_result.title:
                    try:
                        # Use global title cleaning utilities
                        clean_title = clean_title_for_lyrics(import_result.title)
                        clean_artist = normalize_artist_name(import_result.artist)

                        lyrics_data = await search_timestamped_lyrics(
                            title=clean_title,
                            artist=clean_artist,
                            timeout=5.0
                        )

                        if lyrics_data and lyrics_data.get("matched"):
                            results["statistics"]["lyrics_found"] += 1

                    except Exception as e:
                        results["warnings"].append(
                            f"{filename}: Lyrics search failed: {e}"
                        )

            # Prepare final result
            file_result = {
                "filename": filename,
                "format": format_name,
                "title": import_result.title,
                "artist": import_result.artist,
                "jcrd_data": import_result.jcrd_data,
                "metadata": import_result.metadata,
                "lyrics": lyrics_data,
                "format_confidence": format_info.get('confidence', 1.0)
            }

            # Save to database if requested
            if save_songs:
                # TODO: Implement song saving
                # This would integrate with the existing song repository
                file_result["saved"] = False
                file_result["save_error"] = "Song saving not yet implemented in unified import"

            results["imported"].append(file_result)
            results["statistics"]["successful"] += 1

        except Exception as e:
            results["failed"].append({
                "filename": file.filename or "unknown",
                "format": "unknown",
                "error": f"Unexpected error: {e}"
            })
            results["statistics"]["failed"] += 1

    # Update overall success status
    results["success"] = results["statistics"]["successful"] > 0

    return JSONResponse(results)


@router.get("/status")
async def import_system_status():
    """Get status of the unified import system"""
    return {
        "system": "Unified Import System",
        "version": "1.0.0",
        "registered_converters": registry.list_converters(),
        "lyrics_integration": settings.LYRICS_PROVIDER_ENABLED,
        "title_cleaning": "Global (backend/app/utils/lyrics.py)",
        "architecture": {
            "format_detection": "Automatic",
            "converter_registry": "Pluggable",
            "output_format": "JCRD Standard",
            "lyrics_integration": "Automatic with title cleaning",
            "extensibility": "Easy to add new formats"
        }
    }
