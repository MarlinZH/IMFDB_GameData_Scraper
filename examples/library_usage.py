#!/usr/bin/env python3
"""
Example: Using IMFDB Scraper as a library

This example shows how to use the scraper programmatically.
"""

from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter


def main():
    """Example usage of the library"""
    
    # Initialize components
    scraper = IMFDBScraper(delay=2.0, verbose=True)
    parser = WeaponParser(verbose=True)
    exporter = DataExporter(output_dir="example_output")
    
    # Define game to scrape
    game_url = "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)"
    game_name = "MW2_2022"
    
    print(f"Scraping {game_name}...")
    
    # Fetch the page
    soup = scraper.fetch_page(game_url)
    
    if not soup:
        print("Failed to fetch page")
        return
    
    # Parse weapons using content method
    weapons = parser.parse_weapons_from_page(soup, game_name, method='content')
    
    print(f"\nFound {len(weapons)} weapons")
    
    # Export to all formats
    exporter.save_all(weapons, base_filename=f"{game_name}_weapons")
    
    # Print summary
    exporter.print_summary(weapons)
    
    print(f"\n✓ Data saved to example_output/")


if __name__ == "__main__":
    main()
