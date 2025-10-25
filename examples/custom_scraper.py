#!/usr/bin/env python3
"""Example: Custom scraper usage"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter


def main():
    """Example of using the scraper as a library"""
    
    # Custom game to scrape
    custom_games = {
        "Escape from Tarkov": "https://www.imfdb.org/wiki/Escape_from_Tarkov",
        "Squad": "https://www.imfdb.org/wiki/Squad"
    }
    
    # Initialize components
    scraper = IMFDBScraper(delay=2.0)
    parser = WeaponParser()
    exporter = DataExporter(output_dir="custom_output")
    
    all_weapons = []
    
    # Scrape each game
    for game_name, url in custom_games.items():
        print(f"\nScraping {game_name}...")
        
        # Fetch the page
        soup = scraper.fetch_page(url)
        if not soup:
            print(f"Failed to fetch {game_name}")
            continue
        
        # Parse weapons
        weapons = parser.parse_weapons_from_page(soup, game_name)
        all_weapons.extend(weapons)
        
        print(f"Found {len(weapons)} weapons")
    
    # Export results
    if all_weapons:
        print(f"\nTotal weapons: {len(all_weapons)}")
        
        # Save in all formats
        files = exporter.save_all_formats(all_weapons, "custom_games")
        
        for format_type, filepath in files.items():
            if filepath:
                print(f"Saved {format_type}: {filepath}")
        
        # Print summary
        exporter.print_summary(all_weapons)
    else:
        print("No weapons found!")


if __name__ == '__main__':
    main()
