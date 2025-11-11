# Usage Guide

Complete guide for using the IMFDB Game Data Scraper.

## Table of Contents

- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Library Usage](#library-usage)
- [Output Formats](#output-formats)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MarlinZH/IMFDB_GameData_Scraper.git
cd IMFDB_GameData_Scraper

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

Scrape all default games:

```bash
python main.py
```

This will:
1. Fetch pages from IMFDB for all default games
2. Parse weapon data using the content method
3. Save output to `output/` directory in all formats (CSV, JSON, Markdown)
4. Display a summary of the scraped data

## CLI Usage

### Command Line Options

```bash
python main.py [OPTIONS]
```

#### Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--games GAME [GAME ...]` | Specific games to scrape | All games |
| `--method {content,toc}` | Parsing method | content |
| `--output DIR` | Output directory | output |
| `--format {all,csv,json,markdown}` | Output format | all |
| `--delay SECONDS` | Delay between requests | 2.0 |
| `--max-retries N` | Maximum retry attempts | 3 |
| `-v, --verbose` | Enable verbose output | False |

### Examples

#### Scrape specific games

```bash
python main.py --games MW2_2022 Ready_or_Not
```

#### Use TOC method (faster)

```bash
python main.py --method toc
```

The TOC method:
- ✅ Faster processing
- ✅ Good for quick overviews
- ❌ May miss weapons not listed in TOC
- ❌ Less detailed information

The content method (default):
- ✅ More accurate and comprehensive
- ✅ Extracts real-world and in-game names
- ✅ Captures all weapons
- ❌ Slower processing

#### Export only CSV

```bash
python main.py --format csv
```

#### Custom output directory

```bash
python main.py --output my_weapons_data
```

#### Be extra careful with rate limiting

```bash
python main.py --delay 5.0 --max-retries 5
```

#### Debug mode

```bash
python main.py -v
```

Verbose mode shows:
- Detailed HTTP requests
- Parsing progress
- Regex matching attempts
- Debug-level logging

### Available Games

The scraper supports these games by default:

- `MW2_2022` - Call of Duty: Modern Warfare II (2022)
- `MW3_2023` - Call of Duty: Modern Warfare III (2023)
- `Ready_or_Not` - Ready or Not
- `Delta_Force_2024` - Delta Force (2024)

To add more games, edit `main.py` and add entries to the `DEFAULT_GAMES` dictionary.

## Library Usage

You can also use the scraper as a Python library in your own scripts.

### Basic Example

```python
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter

# Initialize
scraper = IMFDBScraper(delay=2.0)
parser = WeaponParser()
exporter = DataExporter(output_dir="my_data")

# Scrape a single game
url = "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)"
soup = scraper.fetch_page(url)

# Parse weapons
weapons = parser.parse_weapons_from_page(soup, "MW2", method='content')

# Export
exporter.save_all(weapons, "mw2_weapons")
exporter.print_summary(weapons)
```

### Advanced Example

```python
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter

# Initialize with custom settings
scraper = IMFDBScraper(
    delay=3.0,
    max_retries=5,
    verbose=True
)

parser = WeaponParser(verbose=True)
exporter = DataExporter(output_dir="output", verbose=True)

# Define multiple games
games = {
    "MW2": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)",
    "RoN": "https://www.imfdb.org/wiki/Ready_or_Not"
}

# Scrape all games
scraped_pages = scraper.scrape_games(games)

# Parse each game
all_weapons = []
for game_name, soup in scraped_pages.items():
    weapons = parser.parse_weapons_from_page(soup, game_name, method='content')
    all_weapons.extend(weapons)
    print(f"{game_name}: {len(weapons)} weapons")

# Export combined data
exporter.save_all(all_weapons, "combined_weapons")

# Or export per-game
for game_name, soup in scraped_pages.items():
    weapons = parser.parse_weapons_from_page(soup, game_name)
    exporter.save_all(weapons, f"{game_name}_weapons")
```

### Working with the Data

```python
import pandas as pd

# Load the CSV
df = pd.read_csv("output/weapons.csv")

# Filter by game
mw2_weapons = df[df['game'] == 'MW2_2022']

# Filter by category
assault_rifles = df[df['category'].str.contains('Rifle', case=False)]

# Find weapons with real-world names
real_weapons = df[df['real_world_name'] != '']

# Export filtered data
assault_rifles.to_csv("assault_rifles.csv", index=False)
```

## Output Formats

### CSV Format

Simple tabular format, great for spreadsheets and data analysis.

```csv
game,category,toc_name,real_world_name,in_game_name
MW2_2022,Assault Rifles,M4A1,Colt M4A1 Carbine,M4
MW2_2022,Handguns,Glock 17,Glock 17,X12
```

### JSON Format

Structured format, perfect for programmatic use.

```json
[
  {
    "game": "MW2_2022",
    "category": "Assault Rifles",
    "toc_name": "M4A1",
    "real_world_name": "Colt M4A1 Carbine",
    "in_game_name": "M4"
  }
]
```

### Markdown Format

Human-readable table format, great for documentation.

```markdown
# IMFDB Weapons Data

Total weapons: 150

| game     | category        | toc_name | real_world_name    | in_game_name |
|----------|-----------------|----------|-------------------|--------------|
| MW2_2022 | Assault Rifles  | M4A1     | Colt M4A1 Carbine | M4           |
```

## Troubleshooting

### Issue: 403 Forbidden Error

**Problem**: IMFDB is blocking requests

**Solutions**:
1. Increase delay: `python main.py --delay 5.0`
2. Use fewer retries: `python main.py --max-retries 2`
3. Try at different times of day
4. Use Selenium scraper (see `Selenium_Scraper.py`)
5. Consider using a VPN

### Issue: No weapons found

**Problem**: Parser returns empty results

**Solutions**:
1. Run with verbose mode: `python main.py -v`
2. Try TOC method: `python main.py --method toc`
3. Check if IMFDB page structure changed
4. Verify the URL is correct

### Issue: Rate limiting

**Problem**: Getting blocked after several requests

**Solutions**:
1. Increase delay: `--delay 3.0` or higher
2. Reduce max retries: `--max-retries 2`
3. Scrape games one at a time
4. Use the `--games` option to limit scraping

### Issue: Import errors

**Problem**: `ModuleNotFoundError` or import issues

**Solutions**:
```bash
# Ensure you're in the project directory
cd IMFDB_GameData_Scraper

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# If using as library, install in development mode
pip install -e .
```

## Advanced Usage

### Adding New Games

Edit `main.py` and add to `DEFAULT_GAMES`:

```python
DEFAULT_GAMES = {
    # Existing games...
    "My_Game": "https://www.imfdb.org/wiki/My_Game_Page",
}
```

### Custom Parsing Logic

Extend the `WeaponParser` class:

```python
from src.parser import WeaponParser

class CustomParser(WeaponParser):
    def _extract_weapon_names(self, soup, weapon_name, heading_tag):
        # Your custom extraction logic
        real_world, in_game = super()._extract_weapon_names(
            soup, weapon_name, heading_tag
        )
        
        # Add custom processing
        return real_world, in_game
```

### Batch Processing

Process multiple games in parallel:

```python
from concurrent.futures import ThreadPoolExecutor
from src.scraper import IMFDBScraper
from src.parser import WeaponParser

scraper = IMFDBScraper(delay=3.0)
parser = WeaponParser()

def scrape_and_parse(game_name, url):
    soup = scraper.fetch_page(url)
    if soup:
        return parser.parse_weapons_from_page(soup, game_name)
    return []

games = {
    "MW2": "https://www.imfdb.org/wiki/...",
    "MW3": "https://www.imfdb.org/wiki/...",
}

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [
        executor.submit(scrape_and_parse, name, url)
        for name, url in games.items()
    ]
    
    all_weapons = []
    for future in futures:
        all_weapons.extend(future.result())
```

**Note**: Be respectful with parallel requests. Use small max_workers and appropriate delays.

### Integration with Notion

Use the Notion API to upload scraped data:

```python
from notion_client import Client

# Initialize Notion client
notion = Client(auth="your_token")

# Create database or get existing
database_id = "your_database_id"

# Upload weapons
for weapon in weapons:
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {"title": [{"text": {"content": weapon['in_game_name']}}]},
            "Game": {"select": {"name": weapon['game']}},
            "Category": {"select": {"name": weapon['category']}},
            "Real Name": {"rich_text": [{"text": {"content": weapon['real_world_name']}}]},
        }
    )
```

## Getting Help

If you encounter issues:

1. Check this usage guide
2. Review [QUICKSTART.md](QUICKSTART.md)
3. Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
4. Search existing [GitHub Issues](https://github.com/MarlinZH/IMFDB_GameData_Scraper/issues)
5. Create a new issue with:
   - Command you ran
   - Full error message
   - Output from verbose mode (`-v`)
   - Your Python version

## Best Practices

1. **Always use delays**: Default 2.0s is minimum, 3.0s+ is better
2. **Start small**: Test with one game before scraping all
3. **Check robots.txt**: Respect IMFDB's crawling policies
4. **Use verbose mode** for debugging
5. **Save your data**: Don't re-scrape unnecessarily
6. **Report issues**: Help improve the scraper

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical implementation details
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- See [examples/](examples/) directory for more code examples
