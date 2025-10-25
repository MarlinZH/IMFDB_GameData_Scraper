#!/usr/bin/env python3
"""Unit tests for parser module"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser import WeaponParser


def test_extract_real_world_name():
    """Test weapon name extraction"""
    parser = WeaponParser()
    
    # Test cases
    test_cases = [
        # (input, expected_in_game, expected_real_world)
        ("AK-47", "AK-47", "AK-47"),
        ("Kastov 762 (AKM)", "Kastov 762", "AKM"),
        ("M4A1 Carbine", "M4A1 Carbine", "M4A1 Carbine"),
        ("Lachmann-556 (Heckler & Koch HK93)", "Lachmann-556", "Heckler & Koch HK93"),
        ("  Spaced Name  (Real Name)  ", "Spaced Name", "Real Name"),
    ]
    
    print("Testing weapon name extraction...\n")
    
    for input_text, expected_ingame, expected_real in test_cases:
        in_game, real_world = parser._extract_real_world_name(input_text)
        
        success = (in_game == expected_ingame and real_world == expected_real)
        status = "✅" if success else "❌"
        
        print(f"{status} Input: '{input_text}'")
        print(f"   Expected: in_game='{expected_ingame}', real='{expected_real}'")
        print(f"   Got:      in_game='{in_game}', real='{real_world}'")
        print()
        
        if not success:
            return False
    
    print("All tests passed! ✅\n")
    return True


def test_clean_text():
    """Test text cleaning"""
    parser = WeaponParser()
    
    test_cases = [
        ("Normal text", "Normal text"),
        ("  Trimmed  ", "Trimmed"),
        ("Multiple   spaces", "Multiple spaces"),
        ("\nNew\nlines\n", "New lines"),
        ("\tTabs\there\t", "Tabs here"),
    ]
    
    print("Testing text cleaning...\n")
    
    for input_text, expected in test_cases:
        result = parser._clean_text(input_text)
        success = (result == expected)
        status = "✅" if success else "❌"
        
        print(f"{status} Input: '{repr(input_text)}' -> '{result}'")
        if not success:
            print(f"   Expected: '{expected}'")
        
        if not success:
            return False
    
    print("\nAll tests passed! ✅\n")
    return True


if __name__ == '__main__':
    print("=" * 50)
    print("PARSER UNIT TESTS")
    print("=" * 50 + "\n")
    
    success = True
    
    success = test_clean_text() and success
    success = test_extract_real_world_name() and success
    
    if success:
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED ✅")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("SOME TESTS FAILED ❌")
        print("=" * 50)
        sys.exit(1)
