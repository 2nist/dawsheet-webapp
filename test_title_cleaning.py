#!/usr/bin/env python3
"""Test script for title cleaning utility"""

import sys
import os
# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.utils.lyrics import clean_title_for_lyrics, normalize_artist_name

def test_title_cleaning():
    test_cases = [
        ("07 - Can't_Buy_Me_Love", "Can't Buy Me Love"),
        ("01. Hey Jude", "Hey Jude"),
        ("Track_Name_With_Underscores", "Track Name With Underscores"),
        ("  03-  Let It Be  ", "Let It Be"),
        ("The_Beatles", "The Beatles"),
    ]

    print("🧪 Testing Title Cleaning Utility")
    print("=" * 50)

    all_passed = True
    for input_title, expected in test_cases:
        result = clean_title_for_lyrics(input_title)
        passed = result == expected
        all_passed = all_passed and passed

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} '{input_title}' -> '{result}' (expected: '{expected}')")

    print("=" * 50)
    print(f"Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed

if __name__ == "__main__":
    test_title_cleaning()
