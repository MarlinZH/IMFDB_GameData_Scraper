# IMFDB Game Data Scraper

A Python tool for scraping weapon data from [IMFDB (Internet Movie Firearms Database)](https://www.imfdb.org/) to create comprehensive game guides in Notion or other platforms.

## Features

- 🎮 Scrapes weapon data from IMFDB game pages
- 🔫 Extracts both in-game and real-world weapon names
- 📊 Exports data in multiple formats (CSV, JSON, Markdown)
- 🛡️ Built-in rate limiting and error handling
- 🎯 Two parsing methods: content-based (accurate) and TOC-based (fast)
- 📝 Detailed logging and statistics

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

### Basic Usage

Scrape all default games:
```bash
python main.py
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
```

### Available Games

By default, the scraper supports:
- `MW2_2022` - Call of Duty: Modern Warfare II (2022)
- `MW3_2023` - Call of Duty: Modern Warfare III (2023)
- `Ready_or_Not` - Ready or Not
- `Delta_Force_2024` - Delta Force (2024)

## Output

The scraper generates files in the `output/` directory (or custom directory if specified):

- **weapons.csv** - Comma-separated values format
- **weapons.json** - JSON format for programmatic use
- **weapons.md** - Markdown table for documentation

### Output Schema

Each weapon entry contains:
- `game` - Game name/identifier
- `category` - Weapon category (e.g., Assault Rifles, Handguns)
- `in_game_name` - Name as it appears in the game
- `real_world_name` - Actual firearm designation
- `toc_name` - Original name from the page's table of contents

## Project Structure

```
IMFDB_GameData_Scraper/
├── src/
│   ├── __init__.py
│   ├── scraper.py      # Web scraping logic
│   ├── parser.py       # HTML parsing and data extraction
│   └── exporter.py     # Data export utilities
├── main.py             # CLI entry point
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

## How It Works

1. **Scraping**: The `IMFDBScraper` class fetches game pages from IMFDB with proper rate limiting and retry logic
2. **Parsing**: The `WeaponParser` extracts weapon information from HTML, identifying categories and weapon names
3. **Exporting**: The `DataExporter` saves the data in your preferred format(s)

### Parsing Methods

#### Content Method (Default)
- Parses the entire page content
- More accurate and detailed
- Captures all weapons even if TOC is incomplete
- Recommended for most use cases

#### TOC Method
- Parses only the Table of Contents
- Faster processing
- May miss weapons not listed in TOC
- Good for quick overviews

## Adding New Games

To add a new game, edit `main.py` and add to the `DEFAULT_GAMES` dictionary:

```python
DEFAULT_GAMES = {
    # ... existing games ...
    "Your_Game": "https://www.imfdb.org/wiki/Your_Game_Page",
}
```

## Using as a Library

You can also import and use the scraper in your own Python scripts:

```python
from src.scraper import IMFDBScraper
from src.parser import WeaponParser
from src.exporter import DataExporter

# Initialize
scraper = IMFDBScraper(delay=2.0)
parser = WeaponParser()
exporter = DataExporter(output_dir="my_data")

# Scrape a game
url = "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)"
soup = scraper.fetch_page(url)

# Parse weapons
weapons = parser.parse_weapons_from_page(soup, "MW2")

# Export
exporter.save_csv(weapons, "mw2_weapons.csv")
exporter.print_summary(weapons)
```

## Troubleshooting

### Cloudflare Protection

If IMFDB is behind Cloudflare protection and blocking requests:

1. The repository includes `Selenium_Scraper.py` as a reference for browser-based scraping
2. Install Selenium dependencies: `pip install selenium webdriver-manager`
3. Consider using residential proxies or browser automation for Cloudflare bypass

### Rate Limiting

If you get blocked or rate limited:
- Increase the delay: `python main.py --delay 5.0`
- Scrape games one at a time
- Use a VPN or wait before retrying

### No Weapons Found

If the scraper returns no weapons:
- Check if the IMFDB page structure has changed
- Try the alternative parsing method: `python main.py --method toc`
- Use verbose mode to debug: `python main.py -v`

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

## License

MIT License - feel free to use this project for personal and educational purposes.

## Acknowledgments

- [IMFDB](https://www.imfdb.org/) - Internet Movie Firearms Database
- All IMFDB contributors who maintain the weapon data

## Support

If you encounter issues:
1. Check the [Issues](https://github.com/MarlinZH/IMFDB_GameData_Scraper/issues) page
2. Create a new issue with details about your problem
3. Include verbose output (`-v`) and error messages

---

**Note**: This scraper is not affiliated with or endorsed by IMFDB. Use responsibly.
