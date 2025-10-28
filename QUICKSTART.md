# Quick Start Guide

Get started with the IMFDB Game Data Scraper in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/MarlinZH/IMFDB_GameData_Scraper.git
cd IMFDB_GameData_Scraper

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### Scrape All Default Games

```bash
python main.py
```

This will scrape:
- Call of Duty: Modern Warfare II (2022)
- Call of Duty: Modern Warfare III (2023)
- Ready or Not
- Delta Force (2024)

### Scrape Specific Games

```bash
python main.py --games MW2_2022 Ready_or_Not
```

### Choose Output Format

```bash
# CSV only
python main.py --format csv

# JSON only
python main.py --format json

# All formats (default)
python main.py --format all
```

### Change Output Directory

```bash
python main.py --output my_data
```

## Output Files

After running, you'll find in the `output/` directory:

- **weapons.csv** - Spreadsheet format
- **weapons.json** - JSON format for APIs
- **weapons.md** - Markdown table for documentation

## Data Structure

Each weapon entry contains:

| Field | Description | Example |
|-------|-------------|---------|
| game | Game identifier | "MW2_2022" |
| category | Weapon type | "Assault Rifles" |
| in_game_name | Name in game | "Kastov 762" |
| real_world_name | Real firearm | "AKM" |
| toc_name | Original page text | "Kastov 762 (AKM)" |

## Common Commands

```bash
# Full scrape with verbose output
python main.py -v

# Quick scrape using TOC method
python main.py --method toc

# Slower scraping (more respectful)
python main.py --delay 5.0

# See all options
python main.py --help
```

## Troubleshooting

### Problem: No weapons found

**Solution:** Try the alternative parsing method:
```bash
python main.py --method toc
```

### Problem: Connection errors

**Solution:** Increase the delay:
```bash
python main.py --delay 5.0
```

### Problem: Rate limited

**Solution:** Wait 15-30 minutes, then try again with longer delay.

## Next Steps

1. **Import to Notion**: Check `examples/notion_export.py`
2. **Custom Games**: See `examples/custom_scraper.py`
3. **Run Tests**: `python tests/test_parser.py`
4. **Read Full Docs**: See `README.md`

## Using as a Library

```python
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter

# Setup
scraper = IMFDBScraper(delay=2.0)
parser = WeaponParser()
exporter = DataExporter()

# Scrape
url = "https://www.imfdb.org/wiki/Your_Game"
soup = scraper.fetch_page(url)

# Parse
weapons = parser.parse_weapons_from_page(soup, "Your_Game")

# Export
exporter.save_csv(weapons, "my_weapons.csv")
```

## Tips

- ✅ Always use rate limiting (default 2 seconds is good)
- ✅ Run with `-v` flag first time to see what's happening
- ✅ Check the `output/` folder after each run
- ✅ Start with one game to test before scraping all
- ⚠️ Be respectful to IMFDB servers - don't spam requests
- ⚠️ Verify scraped data - it may need manual correction

## Help & Support

- Check [README.md](README.md) for detailed documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Open an [issue](https://github.com/MarlinZH/IMFDB_GameData_Scraper/issues) for bugs

---

**Happy scraping!** 🎮🔫
