# Architecture Documentation

## System Overview

The IMFDB Game Data Scraper follows a modular, layered architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌─────────────────────────┐  │
│  │   CLI Tool   │              │   Python Library API    │  │
│  │  (main.py)   │              │  (import src modules)   │  │
│  └──────┬───────┘              └──────────┬──────────────┘  │
│         │                                  │                 │
└─────────┼──────────────────────────────────┼─────────────────┘
          │                                  │
          v                                  v
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐   ┌─────────────┐   ┌───────────────┐   │
│  │  IMFDBScraper│   │WeaponParser │   │ DataExporter  │   │
│  │              │   │             │   │               │   │
│  │ - fetch()    │──>│ - parse()   │──>│ - to_csv()    │   │
│  │ - rate_limit │   │ - extract() │   │ - to_json()   │   │
│  │ - retry()    │   │ - clean()   │   │ - to_md()     │   │
│  └──────────────┘   └─────────────┘   └───────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
          │                     │                    │
          v                     v                    v
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ Requests │  │BeautifulSoup│  │ Pandas/File System  │   │
│  │   HTTP   │  │     HTML    │  │   Storage/Export    │   │
│  └──────────┘  └─────────────┘  └─────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
          │                     │                    │
          v                     v                    v
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│             ┌───────────────────────────┐                    │
│             │   IMFDB Website           │                    │
│             │   (www.imfdb.org)         │                    │
│             └───────────────────────────┘                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. User Input
   └─> Game selection, options
   
2. Scraping Phase
   ├─> IMFDBScraper.fetch_page(url)
   ├─> Rate limiting applied
   ├─> HTTP request sent
   ├─> Response received
   └─> BeautifulSoup object created
   
3. Parsing Phase
   ├─> WeaponParser.parse_weapons_from_page()
   ├─> Find headers (h2, h3, h4)
   ├─> Extract categories
   ├─> Extract weapon names
   ├─> Parse real-world equivalents
   └─> Create weapon dictionaries
   
4. Export Phase
   ├─> DataExporter.to_dataframe()
   ├─> Convert to desired format(s)
   │   ├─> CSV
   │   ├─> JSON
   │   └─> Markdown
   └─> Save to disk
   
5. Output
   └─> Files written to output directory
```

## Component Interactions

### IMFDBScraper

```python
class IMFDBScraper:
    """
    Responsibilities:
    - HTTP session management
    - Rate limiting enforcement
    - Retry logic for failed requests
    - User agent handling
    """
    
    def __init__(delay, user_agent):
        # Setup session, configure delays
        
    def fetch_page(url, max_retries):
        # Rate limit
        # Make request
        # Handle errors
        # Return BeautifulSoup
        
    def scrape_game(game_name, url):
        # Wrapper with logging
        
    def scrape_multiple_games(games_dict):
        # Batch processing
```

### WeaponParser

```python
class WeaponParser:
    """
    Responsibilities:
    - HTML structure analysis
    - Weapon data extraction
    - Text normalization
    - Name pattern matching
    """
    
    def parse_weapons_from_page(soup, game_name):
        # Parse from main content
        # Extract all weapons
        
    def parse_weapons_from_toc(soup, game_name):
        # Parse from table of contents
        # Faster but less detailed
        
    def _extract_real_world_name(text):
        # Pattern: "In-Game (Real)" -> (In-Game, Real)
        
    def _clean_text(text):
        # Normalize whitespace
```

### DataExporter

```python
class DataExporter:
    """
    Responsibilities:
    - Format conversion
    - File I/O operations
    - Statistical analysis
    - Summary generation
    """
    
    def to_dataframe(weapons):
        # Convert list to DataFrame
        
    def save_csv(weapons, filename):
        # Export to CSV
        
    def save_json(weapons, filename):
        # Export to JSON
        
    def save_markdown(weapons, filename):
        # Export to Markdown table
        
    def save_all_formats(weapons, base_filename):
        # Export to all formats
        
    def print_summary(weapons):
        # Statistical analysis
```

## Design Patterns

### 1. Single Responsibility Principle
- Each class has one clear purpose
- Scraper handles HTTP
- Parser handles HTML
- Exporter handles file I/O

### 2. Dependency Injection
```python
# Components are loosely coupled
scraper = IMFDBScraper(delay=2.0)
parser = WeaponParser()
exporter = DataExporter(output_dir="output")
```

### 3. Error Handling Strategy
```python
# Try-catch at every external interaction
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"Failed: {e}")
    # Retry or graceful degradation
```

### 4. Rate Limiting Pattern
```python
# Enforced at scraper level
def _rate_limit(self):
    elapsed = time.time() - self._last_request_time
    if elapsed < self.delay:
        time.sleep(self.delay - elapsed)
```

### 5. Strategy Pattern (Parsing)
```python
# Two parsing strategies
if method == 'toc':
    weapons = parser.parse_weapons_from_toc(soup, game)
else:
    weapons = parser.parse_weapons_from_page(soup, game)
```

## Configuration

### Environment Variables (Future)
```bash
IMFDB_RATE_LIMIT=2.0
IMFDB_USER_AGENT="custom"
IMFDB_OUTPUT_DIR="output"
IMFDB_MAX_RETRIES=3
```

### Config File (Future)
```yaml
scraper:
  delay: 2.0
  max_retries: 3
  timeout: 30
  
parser:
  method: content
  skip_sections: [gallery, notes]
  
exporter:
  formats: [csv, json, markdown]
  output_dir: output
```

## Extensibility Points

### Adding New Games
```python
# Simple configuration
GAMES = {
    "New_Game": "https://www.imfdb.org/wiki/New_Game"
}
```

### Adding New Export Formats
```python
# Extend DataExporter class
def save_excel(self, weapons, filename):
    df = self.to_dataframe(weapons)
    df.to_excel(filename, index=False)
```

### Custom Parsing Logic
```python
# Extend WeaponParser
class CustomParser(WeaponParser):
    def parse_special_format(self, soup):
        # Custom logic
        pass
```

## Performance Considerations

### Rate Limiting
- Default: 2 seconds between requests
- Configurable via CLI
- Respects server resources

### Memory Usage
- Processes one game at a time
- Releases resources after parsing
- Suitable for large datasets

### Concurrency (Future)
```python
# Potential async implementation
async def scrape_games_async(games):
    tasks = [scrape_game(name, url) for name, url in games.items()]
    return await asyncio.gather(*tasks)
```

## Security Considerations

### User Agent
- Identifies scraper politely
- Configurable for transparency

### Rate Limiting
- Prevents overwhelming servers
- Ethical scraping practice

### Error Handling
- No sensitive data in logs
- Graceful failure modes

## Testing Strategy

### Unit Tests
- Parser logic (text extraction)
- Data transformations
- Edge cases

### Integration Tests (Future)
- Full scrape workflow
- Export format validation
- Error recovery

### End-to-End Tests (Future)
- CLI command execution
- File generation verification
- Data accuracy checks

## Monitoring & Logging

### Log Levels
```python
DEBUG   # Detailed flow information
INFO    # Progress updates
WARNING # Recoverable issues
ERROR   # Failed operations
```

### Metrics (Future)
- Requests per minute
- Success rate
- Parse accuracy
- Execution time

---

This architecture provides a solid foundation for maintainability, extensibility, and scalability.
