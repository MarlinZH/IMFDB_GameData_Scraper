# Deduplication and Image Scraping Guide

This guide covers the new deduplication and image scraping features added to the IMFDB Game Data Scraper.

## Table of Contents
- [Deduplication](#deduplication)
- [Image Scraping](#image-scraping)
- [Combined Usage](#combined-usage)
- [Advanced Examples](#advanced-examples)

---

## Deduplication

The deduplication feature removes duplicate weapon entries using multiple strategies.

### Features

- **Three Deduplication Strategies:**
  - `exact`: Fast exact name matching
  - `fuzzy`: Accurate fuzzy string matching
  - `comprehensive`: Multi-pass approach (exact + fuzzy + hash-based)

- **Smart Matching:**
  - Normalizes weapon names (removes spaces, special characters)
  - Compares real-world names, in-game names, and TOC names
  - Uses SequenceMatcher for similarity detection (85% threshold)
  - Handles partial matches (e.g., "M4A1" vs "M4A1 Carbine")

- **Reports:**
  - Detailed statistics on duplicates removed
  - Breakdown by deduplication pass
  - Per-game weapon counts

### Basic Usage

```bash
# Enable deduplication with default comprehensive strategy
python main.py --deduplicate

# Use specific strategy
python main.py --deduplicate --dedup-strategy exact
python main.py --deduplicate --dedup-strategy fuzzy
python main.py --deduplicate --dedup-strategy comprehensive
```

### Example Output

```
🔄 Deduplicating weapons using 'comprehensive' strategy...
  ✓ Removed 12 duplicates
  ✓ 45 unique weapons remaining
  ✓ Deduplication report saved to output/deduplication_report.txt
```

### Sample Deduplication Report

```
============================================================
DEDUPLICATION REPORT
============================================================

Strategy: comprehensive
Original weapons: 57
Unique weapons: 45
Duplicates removed: 12
Reduction: 21.1%

Pass breakdown:
  - Exact matching: 8 duplicates
  - Fuzzy matching: 3 duplicates
  - Hash detection: 1 duplicates

Weapons by game:
  - Delta_Force_2024: 23 weapons
  - MW2_2022: 15 weapons
  - Ready_or_Not: 7 weapons
============================================================
```

---

## Image Scraping

The image scraper downloads weapon images from IMFDB and organizes them systematically.

### Features

- **Multi-Directory Organization:**
  - `by_game/`: Images organized by game
  - `by_weapon/`: Images organized by weapon name
  - `thumbnails/`: Thumbnail versions (future feature)

- **Smart Image Detection:**
  - Extracts images from weapon sections
  - Prefers full-size images over thumbnails
  - Handles various IMFDB image formats

- **Robust Downloading:**
  - Retry logic with exponential backoff
  - Validates downloaded images (minimum size check)
  - Skips already-downloaded images
  - Tracks download statistics

- **Reports:**
  - Success/failure rates
  - Total size downloaded
  - Per-weapon image counts

### Basic Usage

```bash
# Download images with default settings
python main.py --download-images

# Custom image directory
python main.py --download-images --image-dir my_weapon_images

# Adjust download delay
python main.py --download-images --image-delay 2.0
```

### Example Output

```
📷 Downloading weapon images to images/...
  ✓ Downloaded 34 images
  ✓ Skipped 8 existing images
  ✓ Total size: 12.45 MB
  ✓ Image report saved to images/image_report.txt
```

### Directory Structure

After running with `--download-images`, you'll have:

```
images/
├── by_game/
│   ├── Delta_Force_2024/
│   │   ├── M4A1_1.jpg
│   │   ├── M4A1_2.jpg
│   │   └── AK-47_1.jpg
│   └── MW2_2022/
│       ├── Desert_Eagle_1.jpg
│       └── Glock_17_1.jpg
├── by_weapon/
│   ├── M4A1/
│   │   ├── M4A1_1.jpg
│   │   └── M4A1_2.jpg
│   └── AK-47/
│       └── AK-47_1.jpg
├── thumbnails/
└── image_report.txt
```

### Sample Image Report

```
============================================================
IMAGE SCRAPING REPORT
============================================================

Total images processed: 42
Successful downloads: 34
Failed downloads: 2
Skipped (already exists): 8
Success rate: 81.0%
Total size: 12.45 MB

Images saved to: C:\Projects\IMFDB_GameData_Scraper\images
============================================================
```

---

## Combined Usage

Use both features together for the complete workflow:

```bash
# Full pipeline: scrape, deduplicate, and download images
python main.py --deduplicate --download-images

# With custom settings
python main.py \
  --deduplicate --dedup-strategy comprehensive \
  --download-images --image-dir weapons_img \
  --output data_output \
  --delay 2.0 \
  --image-delay 1.5 \
  -v
```

### Example Full Workflow Output

```
============================================================
IMFDB Game Data Scraper
============================================================

Games to scrape: MW2_2022, MW3_2023, Ready_or_Not, Delta_Force_2024
Parsing method: content
Output directory: output
Output format: all
Delay between requests: 2.0s
Max retries: 3
Deduplication: Enabled (comprehensive)
Download images: Enabled
Image directory: images
============================================================

🌐 Fetching pages from IMFDB...
  ✓ MW2_2022: Successfully fetched
  ✓ Delta_Force_2024: Successfully fetched
  ✓ Ready_or_Not: Successfully fetched

✓ Successfully fetched 3/4 pages

🔍 Parsing weapon data...
  ✓ MW2_2022: 18 weapons
  ✓ Delta_Force_2024: 25 weapons
  ✓ Ready_or_Not: 14 weapons

✓ Total weapons found: 57

🔄 Deduplicating weapons using 'comprehensive' strategy...
  ✓ Removed 12 duplicates
  ✓ 45 unique weapons remaining
  ✓ Deduplication report saved to output/deduplication_report.txt

📷 Downloading weapon images to images/...
  ✓ Downloaded: M4A1_1.jpg (245.3 KB)
  ✓ Downloaded: M4A1_2.jpg (198.7 KB)
  ✓ Downloaded: AK-47_1.jpg (312.5 KB)
  ... [more downloads] ...
  ✓ Downloaded 34 images
  ✓ Skipped 8 existing images
  ✓ Total size: 12.45 MB
  ✓ Image report saved to images/image_report.txt

💾 Exporting data to output/...
  ✓ Saved: output/weapons.csv
  ✓ Saved: output/weapons.json
  ✓ Saved: output/weapons.md

✅ Done!
```

---

## Advanced Examples

### Example 1: Scrape Single Game with Images

```bash
python main.py \
  --games Delta_Force_2024 \
  --download-images \
  --image-dir delta_force_weapons \
  -v
```

### Example 2: Deduplicate Existing Data

```bash
# First run without deduplication
python main.py --no-deduplicate

# Analyze results, then run with deduplication
python main.py --deduplicate --dedup-strategy fuzzy
```

### Example 3: High-Quality Image Collection

```bash
# Slower, more careful scraping for high-quality images
python main.py \
  --download-images \
  --delay 3.0 \
  --image-delay 2.0 \
  --max-retries 5 \
  -v
```

### Example 4: Export Only Deduplicated JSON

```bash
python main.py \
  --deduplicate \
  --format json \
  --output clean_data
```

### Example 5: Development/Testing Mode

```bash
# Test with single game, fast scraping
python main.py \
  --games Ready_or_Not \
  --method toc \
  --delay 1.0 \
  --deduplicate --dedup-strategy exact \
  -v
```

---

## Configuration Tips

### Optimal Settings for Different Scenarios

**Quick Test Run:**
```bash
python main.py --games Delta_Force_2024 --method toc --delay 1.0
```

**Production Data Collection:**
```bash
python main.py \
  --deduplicate --dedup-strategy comprehensive \
  --download-images \
  --delay 2.5 \
  --image-delay 1.5 \
  --max-retries 5
```

**Image-Only Update:**
```bash
python main.py \
  --download-images \
  --image-delay 1.0 \
  --no-deduplicate
```

**Analysis Mode (No Images):**
```bash
python main.py \
  --deduplicate \
  --format all \
  --output analysis_output
```

---

## Troubleshooting

### Deduplication Issues

**Too many duplicates removed:**
- Try `--dedup-strategy exact` for stricter matching
- Check deduplication report for details

**Not enough duplicates removed:**
- Use `--dedup-strategy comprehensive` for more aggressive matching
- Increase similarity threshold by modifying `src/deduplicator.py`

### Image Download Issues

**Images failing to download:**
- Increase `--max-retries` and `--image-delay`
- Check if IMFDB has rate limiting
- Run with `-v` for detailed error messages

**Images too small/corrupted:**
- Check `image_report.txt` for failed downloads
- Manually verify IMFDB page structure hasn't changed

**Disk space concerns:**
- Images are typically 100-500 KB each
- Use `--games` to limit scope
- Monitor with `image_report.txt`

---

## Programmatic Usage

You can also use the modules programmatically:

```python
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.deduplicator import WeaponDeduplicator
from src.image_scraper import WeaponImageScraper

# Initialize components
scraper = IMFDBScraper(delay=2.0, verbose=True)
parser = WeaponParser(verbose=True)
deduplicator = WeaponDeduplicator(verbose=True)
image_scraper = WeaponImageScraper(output_dir='images', verbose=True)

# Scrape and parse
games = {"Delta_Force": "https://www.imfdb.org/wiki/Delta_Force_(2024_VG)"}
pages = scraper.scrape_games(games)
weapons = parser.parse_weapons_from_page(pages["Delta_Force"], "Delta_Force")

# Deduplicate
unique_weapons, stats = deduplicator.deduplicate_weapons(weapons, strategy='comprehensive')
print(deduplicator.generate_deduplication_report(weapons, unique_weapons, stats))

# Download images
weapon_images = image_scraper.scrape_all_weapon_images(unique_weapons, pages)
print(image_scraper.generate_image_report())
```

---

## Next Steps

- Explore the generated reports for insights
- Integrate with Notion using the image paths
- Build analytics dashboards with the deduplicated data
- Create weapon comparison visualizations
