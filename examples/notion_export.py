#!/usr/bin/env python3
"""Example: Export data in Notion-friendly format"""

import sys
import json
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper import IMFDBScraper
from src.parser import WeaponParser


def format_for_notion(weapons: List[Dict[str, str]]) -> List[Dict]:
    """
    Format weapons data for Notion database import.
    
    Notion database properties:
    - Name (title): In-game weapon name
    - Real Name (text): Real-world designation
    - Category (select): Weapon category
    - Game (select): Game name
    """
    notion_data = []
    
    for weapon in weapons:
        notion_entry = {
            "Name": weapon['in_game_name'],
            "Real Name": weapon['real_world_name'],
            "Category": weapon['category'],
            "Game": weapon['game'],
            "Notes": f"TOC: {weapon['toc_name']}"
        }
        notion_data.append(notion_entry)
    
    return notion_data


def main():
    """Scrape and format for Notion"""
    
    # Game to scrape
    game_name = "MW2_2022"
    game_url = "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)"
    
    print(f"Scraping {game_name} for Notion import...\n")
    
    # Scrape
    scraper = IMFDBScraper(delay=2.0)
    soup = scraper.fetch_page(game_url)
    
    if not soup:
        print("Failed to fetch page")
        return
    
    # Parse
    parser = WeaponParser()
    weapons = parser.parse_weapons_from_page(soup, game_name)
    
    if not weapons:
        print("No weapons found")
        return
    
    print(f"Found {len(weapons)} weapons\n")
    
    # Format for Notion
    notion_data = format_for_notion(weapons)
    
    # Save
    output_dir = Path("custom_output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{game_name}_notion.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(notion_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved Notion-formatted data to: {output_file}")
    print(f"\nTo import into Notion:")
    print(f"1. Create a database with properties: Name, Real Name, Category, Game")
    print(f"2. Use a CSV import tool or Notion API to import {output_file}")
    print(f"3. Or manually copy the data from the JSON file")
    
    # Show preview
    print(f"\n--- Preview (first 3 entries) ---")
    for entry in notion_data[:3]:
        print(json.dumps(entry, indent=2))
        print()


if __name__ == '__main__':
    main()
