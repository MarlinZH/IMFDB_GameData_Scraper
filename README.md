# IMFDB Game Data Scraper

A Python tool for scraping weapon data from [IMFDB (Internet Movie Firearms Database)](https://www.imfdb.org/) to create comprehensive game guides in Notion or other platforms.

## Features

- 🎮 Scrapes weapon data from IMFDB game pages
- 🔫 Extracts both in-game and real-world weapon names
- 🧹 **NEW: Intelligent deduplication with fuzzy matching**
- 📷 **NEW: Automatic weapon image downloading**
- 📊 Exports data in multiple formats (CSV, JSON, Markdown)
- 🛡️ Built-in rate limiting and error handling
- 🎯 Two parsing methods: content-based (accurate) and TOC-based (fast)
- 📝 Detailed logging and statistics

## What's New in v1.1.0

### Deduplication
- Three strategies: exact, fuzzy, and comprehensive
- Removes duplicate weapon entries automatically
- Handles name variations (e.g., "M4A1" vs "M4A1 Carbine")
- Generates detailed deduplication reports

### Image Scraping
- Downloads weapon images from IMFDB
- Organizes images by game and weapon
- Tracks download statistics
- Skips already-downloaded images
- Validates image quality

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/MarlinZH/IMFDB_GameData_Scraper.git
cd IMFDB_GameData_Scraper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
# Basic scraping
python main.py

# With deduplication and image downloading
python main.py --deduplicate --download-images

# Full featured run
python main.py --deduplicate --download-images --delay 2.0 -v
```

### Deduplication Options

```bash
# Enable deduplication with comprehensive strategy (recommended)
python main.py --deduplicate

# Choose specific strategy
python main.py --deduplicate --dedup-strategy exact
python main.py --deduplicate --dedup-strategy fuzzy
python main.py --deduplicate --dedup-strategy comprehensive

# Disable deduplication
python main.py --no-deduplicate
```

### Image Scraping Options

```bash
# Download weapon images
python main.py --download-images

# Custom image directory
python main.py --download-images --image-dir my_weapons

# Adjust download speed
python main.py --download-images --image-delay 2.0
```

### Advanced Options

```bash
# Scrape specific games
python main.py --games MW2_2022 Ready_or_Not

# Use TOC parsing method (faster but less detailed)
python main.py --method toc

# Save to custom directory
python main.py --output my_weapons_data

# Export only CSV format
python main.py --format csv

# Increase delay between requests (be nice to servers!)
python main.py --delay 3.0

# Verbose output for debugging
python main.py -v

# Complete example
python main.py \
  --games Delta_Force_2024 \
  --deduplicate --dedup-strategy comprehensive \
  --download-images --image-dir delta_images \
  --output delta_data \
  --delay 2.0 \
  -v
```

### Available Games

By default, the scraper supports:
- `MW2_2022` - Call of Duty: Modern Warfare II (2022)
- `MW3_2023` - Call of Duty: Modern Warfare III (2023)
- `Ready_or_Not` - Ready or Not
- `Delta_Force_2024` - Delta Force (2024)

## Output

### Data Files

The scraper generates files in the `output/` directory (or custom directory):

- **weapons.csv** - Comma-separated values format
- **weapons.json** - JSON format for programmatic use
- **weapons.md** - Markdown table for documentation
- **deduplication_report.txt** - Statistics about removed duplicates (if enabled)

### Image Files

Images are organized in the `images/` directory (or custom directory):

```
images/
├── by_game/          # Images organized by game
│   ├── Delta_Force_2024/
│   └── MW2_2022/
├── by_weapon/        # Images organized by weapon name
│   ├── M4A1/
│   └── AK-47/
├── thumbnails/       # Thumbnail versions (future)
└── image_report.txt  # Download statistics
```

### Data Schema

Each weapon entry contains:
- `game` - Game name/identifier
- `category` - Weapon category (e.g., Assault Rifles, Handguns)
- `in_game_name` - Name as it appears in the game
- `real_world_name` - Actual firearm designation
- `toc_name` - Original name from the page's table of contents

## Documentation

- **[DEDUP_IMAGE_GUIDE.md](DEDUP_IMAGE_GUIDE.md)** - Complete guide to deduplication and image scraping
- **[USAGE.md](USAGE.md)** - Detailed usage instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture overview
- **[examples/](examples/)** - Example scripts

## Project Structure

```
IMFDB_GameData_Scraper/
├── src/
│   ├── __init__.py
│   ├── scraper.py       # Web scraping logic
│   ├── parser.py        # HTML parsing and data extraction
│   ├── exporter.py      # Data export utilities
│   ├── deduplicator.py  # NEW: Deduplication logic
│   └── image_scraper.py # NEW: Image downloading
├── examples/
│   └── dedup_image_example.py  # Example usage
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── DEDUP_IMAGE_GUIDE.md # Feature guide
└── README.md
```

## How It Works

1. **Scraping**: Fetches game pages from IMFDB with rate limiting
2. **Parsing**: Extracts weapon information from HTML
3. **Deduplication** *(optional)*: Removes duplicate entries using fuzzy matching
4. **Image Downloading** *(optional)*: Downloads and organizes weapon images
5. **Exporting**: Saves data in your preferred format(s)

## Using as a Library

```python
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.deduplicator import WeaponDeduplicator
from src.image_scraper import WeaponImageScraper
from src.exporter import DataExporter

# Initialize
scraper = IMFDBScraper(delay=2.0)
parser = WeaponParser()
deduplicator = WeaponDeduplicator()
image_scraper = WeaponImageScraper(output_dir='images')
exporter = DataExporter(output_dir='data')

# Scrape and parse
url = "https://www.imfdb.org/wiki/Delta_Force_(2024_VG)"
soup = scraper.fetch_page(url)
weapons = parser.parse_weapons_from_page(soup, "Delta_Force")

# Deduplicate
unique_weapons, stats = deduplicator.deduplicate_weapons(
    weapons, 
    strategy='comprehensive'
)

# Download images
pages = {"Delta_Force": soup}
weapon_images = image_scraper.scrape_all_weapon_images(unique_weapons, pages)

# Export
exporter.save_all(unique_weapons)
```

## Troubleshooting

### Cloudflare Protection

If IMFDB blocks requests:
1. Use `Selenium_Scraper.py` for browser-based scraping
2. Install: `pip install selenium webdriver-manager`
3. Increase delays: `--delay 5.0`

### Rate Limiting

If blocked:
- Increase delay: `--delay 5.0`
- Scrape fewer games at once
- Wait before retrying

### No Weapons Found

If no results:
- Try alternative method: `--method toc`
- Use verbose mode: `-v`
- Check if IMFDB page structure changed

### Image Download Issues

If images fail:
- Increase retry attempts: `--max-retries 5`
- Increase image delay: `--image-delay 2.0`
- Check `image_report.txt` for details

## Legal & Ethical Considerations

- ⚖️ This tool is for educational and personal use only
- 🤝 Be respectful of IMFDB's servers (default rate limiting is 2 seconds)
- 📜 IMFDB content is user-contributed; verify accuracy independently
- 🚫 Do not use this tool for commercial purposes without permission
- ✅ Always check robots.txt and terms of service

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - feel free to use this project for personal and educational purposes.

## Acknowledgments

- [IMFDB](https://www.imfdb.org/) - Internet Movie Firearms Database
- All IMFDB contributors who maintain the weapon data

## Support

If you encounter issues:
1. Check the [Issues](https://github.com/MarlinZH/IMFDB_GameData_Scraper/issues) page
2. Review [DEDUP_IMAGE_GUIDE.md](DEDUP_IMAGE_GUIDE.md) for common questions
3. Create a new issue with:
   - Verbose output (`-v`)
   - Error messages
   - Steps to reproduce

---

**Note**: This scraper is not affiliated with or endorsed by IMFDB. Use responsibly.
