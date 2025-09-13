"""
JCRD JSON Converter - Working implementation for native JCRD format

This converter handles .jcrd.json files and smart JSON detection for JCRD-like structures.
"""

import json
from typing import List, Optional
from .. import ImportResult, FormatConverter


class JCRDConverter:
    """Converter for JCRD JSON format"""

    @property
    def supported_extensions(self) -> List[str]:
        return ['.json', '.jcrd']

    @property
    def supported_mimetypes(self) -> List[str]:
        return ['application/json', 'text/json']

    @property
    def format_name(self) -> str:
        return "JCRD JSON"

    def can_handle(self, filename: str, mimetype: Optional[str] = None) -> bool:
        """Check if file looks like JCRD format"""
        return (
            filename.lower().endswith(('.json', '.jcrd')) or
            (mimetype and 'json' in mimetype.lower())
        )

    async def convert(self, file_content: bytes, filename: str) -> ImportResult:
        """Convert JCRD JSON to standardized JCRD format"""
        try:
            # Parse JSON
            text = file_content.decode('utf-8', errors='ignore')
            data = json.loads(text)

            if not isinstance(data, dict):
                return ImportResult(
                    success=False,
                    errors=[f"Expected JSON object, got {type(data).__name__}"]
                )

            # Validate JCRD structure
            warnings = []
            metadata = data.get('metadata', {})

            # Check for required JCRD fields
            if not metadata.get('tempo') and not metadata.get('bpm'):
                warnings.append("No tempo/BPM specified, defaulting to 120")
                if 'metadata' not in data:
                    data['metadata'] = {}
                data['metadata']['tempo'] = 120

            if not metadata.get('time_signature'):
                warnings.append("No time signature specified, defaulting to 4/4")
                data['metadata']['time_signature'] = '4/4'

            # Check for musical content
            has_progression = bool(data.get('chord_progression'))
            has_sections = bool(data.get('sections'))

            if not has_progression and not has_sections:
                warnings.append("No chord progression or sections found")

            # Extract title and artist
            title = (
                metadata.get('title') or
                data.get('title') or
                filename.rsplit('.', 1)[0]
            ).strip()

            artist = (
                metadata.get('artist') or
                data.get('artist') or
                ""
            ).strip()

            return ImportResult(
                success=True,
                jcrd_data=data,
                title=title,
                artist=artist,
                warnings=warnings,
                metadata={
                    'source_format': 'jcrd',
                    'source_filename': filename,
                    'has_progression': has_progression,
                    'has_sections': has_sections
                }
            )

        except json.JSONDecodeError as e:
            return ImportResult(
                success=False,
                errors=[f"Invalid JSON: {e}"]
            )
        except Exception as e:
            return ImportResult(
                success=False,
                errors=[f"Conversion failed: {e}"]
            )
