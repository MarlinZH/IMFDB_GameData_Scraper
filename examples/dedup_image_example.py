#!/usr/bin/env python3
"""
Example: Using Deduplication and Image Scraping

This example demonstrates how to use the deduplication and image 
scraping features programmatically.
"""

from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.deduplicator import WeaponDeduplicator
from src.image_scraper import WeaponImageScraper
from src.exporter import DataExporter


def main():
    """
    Example workflow: scrape Delta Force weapons, deduplicate, 
    download images, and export data.
    """
    
    print("="*60)
    print("IMFDB Deduplication & Image Scraping Example")
    print("="*60)
    
    # Configuration
    game_url = "https://www.imfdb.org/wiki/Delta_Force_(2024_VG)"
    game_name = "Delta_Force_2024"
    
    # Initialize components
    print("\n1. Initializing components...")
    scraper = IMFDBScraper(delay=2.0, verbose=False)
    parser = WeaponParser(verbose=False)
    deduplicator = WeaponDeduplicator(verbose=True)
    image_scraper = WeaponImageScraper(
        output_dir='example_images',
        delay=1.0,
        verbose=True
    )
    exporter = DataExporter(output_dir='example_output', verbose=False)
    
    # Step 1: Scrape the game page
    print("\n2. Scraping IMFDB page...")
    soup = scraper.fetch_page(game_url)
    
    if not soup:
        print("❌ Failed to fetch page. Exiting.")
        return
    
    print("✓ Successfully fetched page")
    
    # Step 2: Parse weapons
    print("\n3. Parsing weapon data...")
    weapons = parser.parse_weapons_from_page(soup, game_name, method='content')
    print(f"✓ Found {len(weapons)} weapons")
    
    # Display sample weapons
    print("\nSample weapons:")
    for weapon in weapons[:5]:
        print(f"  - {weapon.get('toc_name', 'Unknown')}")
        if weapon.get('real_world_name'):
            print(f"    Real: {weapon['real_world_name']}")
        if weapon.get('in_game_name'):
            print(f"    In-game: {weapon['in_game_name']}")
    
    # Step 3: Deduplicate weapons
    print("\n4. Deduplicating weapons...")
    print("   Testing different strategies:")
    
    # Test exact strategy
    print("\n   Strategy: EXACT")
    exact_weapons, exact_stats = deduplicator.deduplicate_weapons(
        weapons.copy(), 
        strategy='exact'
    )
    print(f"   Removed {exact_stats['duplicates_removed']} duplicates")
    
    # Test fuzzy strategy
    print("\n   Strategy: FUZZY")
    fuzzy_weapons, fuzzy_stats = deduplicator.deduplicate_weapons(
        weapons.copy(), 
        strategy='fuzzy'
    )
    print(f"   Removed {fuzzy_stats['duplicates_removed']} duplicates")
    
    # Test comprehensive strategy (recommended)
    print("\n   Strategy: COMPREHENSIVE (recommended)")
    unique_weapons, comp_stats = deduplicator.deduplicate_weapons(
        weapons.copy(), 
        strategy='comprehensive'
    )
    print(f"   Removed {comp_stats['duplicates_removed']} duplicates")
    
    # Generate report
    print("\n5. Generating deduplication report...")
    report = deduplicator.generate_deduplication_report(
        weapons, 
        unique_weapons, 
        comp_stats
    )
    print(report)
    
    # Save report
    with open('example_output/deduplication_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("\n✓ Report saved to example_output/deduplication_report.txt")
    
    # Step 4: Download weapon images
    print("\n6. Downloading weapon images...")
    print(f"   Attempting to download images for {len(unique_weapons)} unique weapons")
    
    # Create pages dict for image scraper
    scraped_pages = {game_name: soup}
    
    # Download images
    weapon_images = image_scraper.scrape_all_weapon_images(
        unique_weapons, 
        scraped_pages
    )
    
    # Display statistics
    image_stats = image_scraper.get_statistics()
    print(f"\n   Results:")
    print(f"   - Successfully downloaded: {image_stats['successful_downloads']}")
    print(f"   - Failed: {image_stats['failed_downloads']}")
    print(f"   - Skipped (existing): {image_stats['skipped']}")
    print(f"   - Total size: {image_stats['total_size_mb']:.2f} MB")
    print(f"   - Success rate: {image_stats['success_rate']:.1f}%")
    
    # Generate image report
    print("\n7. Generating image scraping report...")
    image_report = image_scraper.generate_image_report()
    print(image_report)
    
    # Save image report
    with open('example_images/image_report.txt', 'w', encoding='utf-8') as f:
        f.write(image_report)
    print("\n✓ Report saved to example_images/image_report.txt")
    
    # Step 5: Export data
    print("\n8. Exporting weapon data...")
    exporter.save_all(unique_weapons)
    print("✓ Data exported to example_output/")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Original weapons: {len(weapons)}")
    print(f"After deduplication: {len(unique_weapons)}")
    print(f"Duplicates removed: {comp_stats['duplicates_removed']}")
    print(f"Reduction: {comp_stats['duplicates_removed']/len(weapons)*100:.1f}%")
    print(f"\nImages downloaded: {image_stats['successful_downloads']}")
    print(f"Total image size: {image_stats['total_size_mb']:.2f} MB")
    print(f"\nData exported to: example_output/")
    print(f"Images saved to: example_images/")
    print("="*60)
    
    print("\n✅ Example complete!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
