#!/usr/bin/env python3
"""
IMFDB Game Data Scraper - CLI Entry Point

Scrape weapon data from IMFDB for various games.
"""

import argparse
import sys
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter


# Default games to scrape
DEFAULT_GAMES = {
    "MW2_2022": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)",
    "MW3_2023": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_III_(2023)",
    "Ready_or_Not": "https://www.imfdb.org/wiki/Ready_or_Not",
    "Delta_Force_2024": "https://www.imfdb.org/wiki/Delta_Force_(2024_VG)"
}


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Scrape weapon data from IMFDB game pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all default games
  python main.py
  
  # Scrape specific games
  python main.py --games MW2_2022 Ready_or_Not
  
  # Use TOC parsing method (faster)
  python main.py --method toc
  
  # Save to custom directory
  python main.py --output my_data
  
  # Export only CSV
  python main.py --format csv
  
  # Increase delay and enable verbose output
  python main.py --delay 3.0 -v
        """
    )
    
    parser.add_argument(
        '--games',
        nargs='+',
        choices=list(DEFAULT_GAMES.keys()),
        help='Specific games to scrape (default: all)'
    )
    
    parser.add_argument(
        '--method',
        choices=['content', 'toc'],
        default='content',
        help='Parsing method: content (accurate) or toc (fast) (default: content)'
    )
    
    parser.add_argument(
        '--output',
        default='output',
        help='Output directory (default: output)'
    )
    
    parser.add_argument(
        '--format',
        choices=['all', 'csv', 'json', 'markdown'],
        default='all',
        help='Output format (default: all)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )
    
    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum retry attempts (default: 3)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Determine which games to scrape
    if args.games:
        games_to_scrape = {game: DEFAULT_GAMES[game] for game in args.games}
    else:
        games_to_scrape = DEFAULT_GAMES
    
    print("\n" + "="*60)
    print("IMFDB Game Data Scraper")
    print("="*60)
    print(f"\nGames to scrape: {', '.join(games_to_scrape.keys())}")
    print(f"Parsing method: {args.method}")
    print(f"Output directory: {args.output}")
    print(f"Output format: {args.format}")
    print(f"Delay between requests: {args.delay}s")
    print(f"Max retries: {args.max_retries}")
    print("="*60 + "\n")
    
    # Initialize components
    scraper = IMFDBScraper(
        delay=args.delay,
        max_retries=args.max_retries,
        verbose=args.verbose
    )
    parser = WeaponParser(verbose=args.verbose)
    exporter = DataExporter(output_dir=args.output, verbose=args.verbose)
    
    # Scrape games
    print("🌐 Fetching pages from IMFDB...")
    scraped_pages = scraper.scrape_games(games_to_scrape)
    
    if not scraped_pages:
        print("\n❌ Failed to scrape any pages. Exiting.")
        sys.exit(1)
    
    print(f"\n✓ Successfully fetched {len(scraped_pages)}/{len(games_to_scrape)} pages")
    
    # Parse weapons
    print("\n🔍 Parsing weapon data...")
    all_weapons = []
    
    for game_name, soup in scraped_pages.items():
        weapons = parser.parse_weapons_from_page(soup, game_name, method=args.method)
        all_weapons.extend(weapons)
        print(f"  ✓ {game_name}: {len(weapons)} weapons")
    
    if not all_weapons:
        print("\n⚠️  No weapons found. This might indicate:")
        print("  - IMFDB page structure has changed")
        print("  - Pages are empty or behind protection")
        print("  - Try running with -v for verbose output")
        sys.exit(1)
    
    print(f"\n✓ Total weapons found: {len(all_weapons)}")
    
    # Export data
    print(f"\n💾 Exporting data to {args.output}/...")
    
    if args.format == 'all':
        exporter.save_all(all_weapons)
    elif args.format == 'csv':
        exporter.save_csv(all_weapons)
    elif args.format == 'json':
        exporter.save_json(all_weapons)
    elif args.format == 'markdown':
        exporter.save_markdown(all_weapons)
    
    # Print summary
    exporter.print_summary(all_weapons)
    
    print("✅ Done!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nRun with -v for verbose output to debug the issue.")
        sys.exit(1)
