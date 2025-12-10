#!/usr/bin/env python3
"""
IMFDB Game Data Scraper - CLI Entry Point

Scrape weapon data from IMFDB for various games with deduplication and image downloading.
"""

import argparse
import sys
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter
from src.deduplicator import WeaponDeduplicator
from src.image_scraper import WeaponImageScraper


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
  # Scrape all default games with deduplication and images
  python main.py --deduplicate --download-images
  
  # Scrape specific games
  python main.py --games MW2_2022 Ready_or_Not
  
  # Use fuzzy deduplication strategy
  python main.py --deduplicate --dedup-strategy fuzzy
  
  # Download images only (skip deduplication)
  python main.py --download-images --no-deduplicate
  
  # Use TOC parsing method (faster)
  python main.py --method toc
  
  # Save to custom directory
  python main.py --output my_data --image-dir my_images
  
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
        help='Output directory for data exports (default: output)'
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
    
    # Deduplication options
    parser.add_argument(
        '--deduplicate',
        action='store_true',
        help='Enable weapon deduplication'
    )
    
    parser.add_argument(
        '--no-deduplicate',
        action='store_true',
        help='Disable weapon deduplication (overrides --deduplicate)'
    )
    
    parser.add_argument(
        '--dedup-strategy',
        choices=['exact', 'fuzzy', 'comprehensive'],
        default='comprehensive',
        help='Deduplication strategy (default: comprehensive)'
    )
    
    # Image scraping options
    parser.add_argument(
        '--download-images',
        action='store_true',
        help='Download weapon images from IMFDB'
    )
    
    parser.add_argument(
        '--image-dir',
        default='images',
        help='Directory to save weapon images (default: images)'
    )
    
    parser.add_argument(
        '--image-delay',
        type=float,
        default=1.0,
        help='Delay between image downloads in seconds (default: 1.0)'
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
    
    # Determine deduplication setting
    deduplicate_enabled = args.deduplicate and not args.no_deduplicate
    
    print("\n" + "="*60)
    print("IMFDB Game Data Scraper")
    print("="*60)
    print(f"\nGames to scrape: {', '.join(games_to_scrape.keys())}")
    print(f"Parsing method: {args.method}")
    print(f"Output directory: {args.output}")
    print(f"Output format: {args.format}")
    print(f"Delay between requests: {args.delay}s")
    print(f"Max retries: {args.max_retries}")
    print(f"Deduplication: {'Enabled (' + args.dedup_strategy + ')' if deduplicate_enabled else 'Disabled'}")
    print(f"Download images: {'Enabled' if args.download_images else 'Disabled'}")
    if args.download_images:
        print(f"Image directory: {args.image_dir}")
    print("="*60 + "\n")
    
    # Initialize components
    scraper = IMFDBScraper(
        delay=args.delay,
        max_retries=args.max_retries,
        verbose=args.verbose
    )
    parser = WeaponParser(verbose=args.verbose)
    exporter = DataExporter(output_dir=args.output, verbose=args.verbose)
    
    if deduplicate_enabled:
        deduplicator = WeaponDeduplicator(verbose=args.verbose)
    
    if args.download_images:
        image_scraper = WeaponImageScraper(
            output_dir=args.image_dir,
            delay=args.image_delay,
            max_retries=args.max_retries,
            verbose=args.verbose
        )
    
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
    
    # Deduplicate weapons if enabled
    if deduplicate_enabled:
        print(f"\n🔄 Deduplicating weapons using '{args.dedup_strategy}' strategy...")
        deduplicated_weapons, dedup_stats = deduplicator.deduplicate_weapons(
            all_weapons, 
            strategy=args.dedup_strategy
        )
        
        print(f"  ✓ Removed {dedup_stats['duplicates_removed']} duplicates")
        print(f"  ✓ {dedup_stats['unique_count']} unique weapons remaining")
        
        # Generate and save deduplication report
        dedup_report = deduplicator.generate_deduplication_report(
            all_weapons, 
            deduplicated_weapons, 
            dedup_stats
        )
        
        if args.verbose:
            print("\n" + dedup_report)
        
        # Save deduplication report
        report_path = f"{args.output}/deduplication_report.txt"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(dedup_report)
            print(f"  ✓ Deduplication report saved to {report_path}")
        except Exception as e:
            print(f"  ⚠️  Failed to save deduplication report: {e}")
        
        # Use deduplicated weapons for export and image downloading
        weapons_to_export = deduplicated_weapons
    else:
        weapons_to_export = all_weapons
    
    # Download images if enabled
    if args.download_images:
        print(f"\n📷 Downloading weapon images to {args.image_dir}/...")
        weapon_images = image_scraper.scrape_all_weapon_images(
            weapons_to_export, 
            scraped_pages
        )
        
        # Get and display statistics
        image_stats = image_scraper.get_statistics()
        print(f"  ✓ Downloaded {image_stats['successful_downloads']} images")
        print(f"  ✓ Skipped {image_stats['skipped']} existing images")
        if image_stats['failed_downloads'] > 0:
            print(f"  ⚠️  Failed to download {image_stats['failed_downloads']} images")
        print(f"  ✓ Total size: {image_stats['total_size_mb']:.2f} MB")
        
        # Generate and save image report
        image_report = image_scraper.generate_image_report()
        
        if args.verbose:
            print("\n" + image_report)
        
        # Save image report
        report_path = f"{args.image_dir}/image_report.txt"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(image_report)
            print(f"  ✓ Image report saved to {report_path}")
        except Exception as e:
            print(f"  ⚠️  Failed to save image report: {e}")
    
    # Export data
    print(f"\n💾 Exporting data to {args.output}/...")
    
    if args.format == 'all':
        exporter.save_all(weapons_to_export)
    elif args.format == 'csv':
        exporter.save_csv(weapons_to_export)
    elif args.format == 'json':
        exporter.save_json(weapons_to_export)
    elif args.format == 'markdown':
        exporter.save_markdown(weapons_to_export)
    
    # Print summary
    exporter.print_summary(weapons_to_export)
    
    print("\n✅ Done!\n")


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
