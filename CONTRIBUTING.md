# Contributing to IMFDB Game Data Scraper

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/IMFDB_GameData_Scraper.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_parser.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and modular
- Maximum line length: 100 characters

### Example Function

```python
def parse_weapon(html: str, game: str) -> Dict[str, str]:
    """
    Parse weapon data from HTML content.
    
    Args:
        html: HTML content to parse
        game: Game name identifier
        
    Returns:
        Dictionary containing weapon data
        
    Raises:
        ValueError: If HTML is invalid
    """
    # Implementation
    pass
```

## Testing

- Add tests for new features
- Ensure existing tests pass
- Test with multiple games
- Test error handling

## Pull Request Guidelines

### PR Title Format
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

Examples:
- `feat: Add support for Selenium scraping`
- `fix: Handle missing TOC sections`
- `docs: Update README with examples`

### PR Description

Include:
- What changed and why
- How to test the changes
- Any breaking changes
- Screenshots (if UI changes)

## Adding New Games

To add support for a new game:

1. Add the game URL to `DEFAULT_GAMES` in `main.py`:
```python
DEFAULT_GAMES = {
    "New_Game": "https://www.imfdb.org/wiki/New_Game_Page",
}
```

2. Test the scraper:
```bash
python main.py --games New_Game -v
```

3. Document any special parsing requirements

## Reporting Bugs

When reporting bugs, include:

- Python version
- Operating system
- Full error message and traceback
- Steps to reproduce
- Expected vs actual behavior
- Verbose output (`python main.py -v`)

## Feature Requests

Feature requests are welcome! Please:

- Check existing issues first
- Describe the feature clearly
- Explain the use case
- Consider implementation complexity

## Areas for Contribution

### High Priority
- [ ] Selenium-based scraper for Cloudflare bypass
- [ ] Unit tests for all modules
- [ ] Support for more output formats (Excel, SQL)
- [ ] Notion API integration

### Medium Priority
- [ ] Caching mechanism
- [ ] Resume interrupted scrapes
- [ ] Parallel scraping
- [ ] Image downloading

### Nice to Have
- [ ] GUI interface
- [ ] Docker support
- [ ] Web API
- [ ] Scheduled scraping

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Follow GitHub's Community Guidelines

## Questions?

Feel free to:
- Open an issue for discussion
- Comment on existing issues
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
