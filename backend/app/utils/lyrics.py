"""
Utilities for cleaning and normalizing song titles for better lyrics matching.
"""
import re
from typing import Optional


def clean_title_for_lyrics(title: Optional[str]) -> str:
    """
    Clean song title for better lyrics matching with external services like LRCLIB.

    This function handles common title formatting issues that prevent successful
    lyrics matching:
    - Removes track numbers (e.g., "07 - Title" -> "Title")
    - Converts underscores to spaces (e.g., "Can't_Buy_Me_Love" -> "Can't Buy Me Love")
    - Normalizes whitespace

    Args:
        title: The original song title (can be None)

    Returns:
        Cleaned title string, or empty string if input was None/empty

    Examples:
        >>> clean_title_for_lyrics("07 - Can't_Buy_Me_Love")
        "Can't Buy Me Love"

        >>> clean_title_for_lyrics("01. Hey Jude")
        "Hey Jude"

        >>> clean_title_for_lyrics("Track_Name_With_Underscores")
        "Track Name With Underscores"
    """
    if not title:
        return ""

    # Remove track numbers (e.g., "07 - Title" -> "Title", "01. Title" -> "Title")
    # Handle various formats: "03- Title", "  03-  Title  ", "07 - Title"
    cleaned = re.sub(r'^\s*\d+\s*[-.]?\s*', '', title)

    # Replace underscores with spaces
    cleaned = cleaned.replace('_', ' ')

    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def normalize_artist_name(artist: Optional[str]) -> str:
    """
    Clean artist name for better lyrics matching.

    Args:
        artist: The original artist name (can be None)

    Returns:
        Cleaned artist string, or empty string if input was None/empty
    """
    if not artist:
        return ""

    # Replace underscores with spaces
    cleaned = artist.replace('_', ' ')

    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned
