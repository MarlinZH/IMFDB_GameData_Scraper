"""
HTML parsing and weapon data extraction
"""

import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging


class WeaponParser:
    """Parses IMFDB pages to extract weapon information"""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the parser
        
        Args:
            verbose: Enable verbose logging (default: False)
        """
        log_level = logging.DEBUG if verbose else logging.INFO
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        
        # Categories to skip
        self.skip_categories = [
            'cast', 'crew', 'trivia', 'gallery', 'references', 
            'see also', 'external links', 'contents'
        ]
    
    def parse_weapons_from_page(self, soup: BeautifulSoup, game_name: str, 
                                method: str = 'content') -> List[Dict]:
        """
        Parse weapons from a BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object of the page
            game_name: Name of the game
            method: Parsing method - 'content' or 'toc' (default: 'content')
            
        Returns:
            List of weapon dictionaries
        """
        if method == 'toc':
            return self._parse_from_toc(soup, game_name)
        else:
            return self._parse_from_content(soup, game_name)
    
    def _parse_from_content(self, soup: BeautifulSoup, game_name: str) -> List[Dict]:
        """
        Parse weapons by analyzing page content (more accurate)
        
        Args:
            soup: BeautifulSoup object of the page
            game_name: Name of the game
            
        Returns:
            List of weapon dictionaries
        """
        weapons = []
        current_category = ""
        
        self.logger.info(f"Parsing {game_name} using content method")
        
        # Find all headings and process sequentially
        for tag in soup.find_all(['h2', 'h3', 'h4']):
            tag_text = tag.get_text().strip()
            
            # h2 tags are categories
            if tag.name == 'h2':
                # Skip non-weapon categories
                if any(skip in tag_text.lower() for skip in self.skip_categories):
                    continue
                current_category = tag_text
                self.logger.debug(f"  Category: {current_category}")
            
            # h3 and h4 tags are weapons
            elif tag.name in ['h3', 'h4'] and current_category:
                weapon_name = tag_text
                
                # Extract real-world and in-game names
                real_world_name, in_game_name = self._extract_weapon_names(
                    soup, weapon_name, tag
                )
                
                weapon_data = {
                    'game': game_name,
                    'category': current_category,
                    'toc_name': weapon_name,
                    'real_world_name': real_world_name,
                    'in_game_name': in_game_name
                }
                
                weapons.append(weapon_data)
                self.logger.debug(f"    Weapon: {weapon_name}")
        
        self.logger.info(f"Found {len(weapons)} weapons using content method")
        return weapons
    
    def _parse_from_toc(self, soup: BeautifulSoup, game_name: str) -> List[Dict]:
        """
        Parse weapons from Table of Contents (faster but less detailed)
        
        Args:
            soup: BeautifulSoup object of the page
            game_name: Name of the game
            
        Returns:
            List of weapon dictionaries
        """
        weapons = []
        
        self.logger.info(f"Parsing {game_name} using TOC method")
        
        # Find the TOC
        toc = soup.find('div', {'class': 'toc'})
        
        if not toc:
            self.logger.warning("No TOC found, falling back to content method")
            return self._parse_from_content(soup, game_name)
        
        # Parse TOC structure
        for category_li in toc.find_all('li', class_='toclevel-1'):
            category_span = category_li.find('span', class_='toctext')
            if not category_span:
                continue
            
            category_name = category_span.get_text().strip()
            
            # Skip non-weapon categories
            if any(skip in category_name.lower() for skip in self.skip_categories):
                continue
            
            self.logger.debug(f"  Category: {category_name}")
            
            # Find weapons in this category (toclevel-2)
            for weapon_li in category_li.find_all('li', class_='toclevel-2'):
                weapon_span = weapon_li.find('span', class_='toctext')
                if weapon_span:
                    toc_weapon_name = weapon_span.get_text().strip()
                    
                    # Try to extract more details from page content
                    real_world_name, in_game_name = self._extract_weapon_names(
                        soup, toc_weapon_name, None
                    )
                    
                    weapon_data = {
                        'game': game_name,
                        'category': category_name,
                        'toc_name': toc_weapon_name,
                        'real_world_name': real_world_name,
                        'in_game_name': in_game_name
                    }
                    
                    weapons.append(weapon_data)
                    self.logger.debug(f"    Weapon: {toc_weapon_name}")
        
        self.logger.info(f"Found {len(weapons)} weapons using TOC method")
        return weapons
    
    def _extract_weapon_names(self, soup: BeautifulSoup, weapon_name: str, 
                             heading_tag: Optional[BeautifulSoup] = None) -> tuple:
        """
        Extract real-world and in-game weapon names
        
        Args:
            soup: BeautifulSoup object of the page
            weapon_name: The weapon name from heading/TOC
            heading_tag: Optional heading tag to start from
            
        Returns:
            Tuple of (real_world_name, in_game_name)
        """
        real_world_name = ""
        in_game_name = ""
        
        # If no heading tag provided, search for it
        if not heading_tag:
            heading_tag = soup.find(['h3', 'h4'], 
                                   string=re.compile(re.escape(weapon_name), re.IGNORECASE))
        
        if not heading_tag:
            return real_world_name, in_game_name
        
        # Analyze the heading text itself
        heading_text = heading_tag.get_text().strip()
        
        # Pattern: "Real Name (In-Game Name)" or "Real Name - In-Game Name"
        parentheses_match = re.search(r'(.+?)\s*\((.+?)\)', heading_text)
        dash_match = re.search(r'(.+?)\s*-\s*(.+?)$', heading_text)
        
        if parentheses_match:
            real_world_name = parentheses_match.group(1).strip()
            in_game_name = parentheses_match.group(2).strip()
        elif dash_match:
            real_world_name = dash_match.group(1).strip()
            in_game_name = dash_match.group(2).strip()
        
        # Look at following paragraphs for more context
        next_elements = []
        sibling = heading_tag.find_next_sibling()
        while sibling and sibling.name not in ['h2', 'h3', 'h4'] and len(next_elements) < 3:
            if sibling.name in ['p', 'div', 'ul']:
                next_elements.append(sibling)
            sibling = sibling.find_next_sibling()
        
        # Extract from content
        for element in next_elements:
            text = element.get_text()
            
            # Patterns for real weapon names
            if not real_world_name:
                patterns = [
                    r'The (.+?) (?:is|appears|can be)',
                    r'A (.+?) (?:is|appears|can be)',
                    r'An (.+?) (?:is|appears|can be)',
                    r'Based on (?:the )?(.+?)[\.,]',
                    r'Actually (?:a |an |the )?(.+?)[\.,]'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        candidate = match.group(1).strip()
                        if 3 < len(candidate) < 100:
                            real_world_name = candidate
                            break
            
            # Patterns for in-game names
            if not in_game_name:
                patterns = [
                    r'(?:called|named|known as|appears as)\s+"(.+?)"',
                    r'in-game (?:as |name[:\s]+)"?(.+?)"?[\.,\n]',
                    r'"(.+?)"\s+(?:in|is the)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        in_game_name = match.group(1).strip()
                        break
        
        # Use weapon_name as fallback for in-game name
        if not in_game_name:
            in_game_name = weapon_name
        
        # Clean up names
        real_world_name = re.sub(r'\s+', ' ', real_world_name).strip()
        in_game_name = re.sub(r'\s+', ' ', in_game_name).strip()
        
        return real_world_name, in_game_name
