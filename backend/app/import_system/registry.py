"""
Converter Registry - Pluggable format conversion system

This registry manages all format converters and provides a clean interface
for adding new format support without modifying core import logic.
"""

from typing import Dict, List, Optional, Type
from . import FormatConverter, ImportResult


class ConverterRegistry:
    """Central registry for all format converters"""

    def __init__(self):
        self._converters: Dict[str, FormatConverter] = {}
        self._extension_map: Dict[str, str] = {}
        self._mimetype_map: Dict[str, str] = {}

    def register(self, name: str, converter: FormatConverter) -> None:
        """Register a new format converter"""
        self._converters[name] = converter

        # Build lookup maps for fast format detection
        for ext in converter.supported_extensions:
            self._extension_map[ext.lower()] = name

        for mimetype in converter.supported_mimetypes:
            self._mimetype_map[mimetype] = name

    def get_converter(self, format_name: str) -> Optional[FormatConverter]:
        """Get converter by format name"""
        return self._converters.get(format_name)

    def find_converter(self, filename: str, mimetype: Optional[str] = None) -> Optional[FormatConverter]:
        """Find appropriate converter for a file"""
        # Try extension first
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if f'.{ext}' in self._extension_map:
            converter_name = self._extension_map[f'.{ext}']
            return self._converters.get(converter_name)

        # Try MIME type
        if mimetype and mimetype in self._mimetype_map:
            converter_name = self._mimetype_map[mimetype]
            return self._converters.get(converter_name)

        # Check each converter's can_handle method
        for converter in self._converters.values():
            if converter.can_handle(filename, mimetype):
                return converter

        return None

    def get_supported_formats(self) -> Dict[str, dict]:
        """Get list of all supported formats with metadata"""
        formats = {}
        for name, converter in self._converters.items():
            formats[name] = {
                'name': converter.format_name,
                'extensions': converter.supported_extensions,
                'mimetypes': converter.supported_mimetypes,
                'ready': True  # All registered converters are ready
            }
        return formats

    def list_converters(self) -> List[str]:
        """List all registered converter names"""
        return list(self._converters.keys())


# Global registry instance
registry = ConverterRegistry()
