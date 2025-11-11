"""
Web scraping functionality for IMFDB pages
"""

import requests
import time
from bs4 import BeautifulSoup
from typing import Optional
import logging


class IMFDBScraper:
    """Handles HTTP requests and page fetching from IMFDB"""
    
    def __init__(self, delay: float = 2.0, max_retries: int = 3, verbose: bool = False):
        """
        Initialize the scraper
        
        Args:
            delay: Delay in seconds between requests (default: 2.0)
            max_retries: Maximum number of retry attempts (default: 3)
            verbose: Enable verbose logging (default: False)
        """
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Multiple user agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Set initial headers
        self._update_headers(0)
    
    def _update_headers(self, attempt: int):
        """Update session headers with rotated user agent"""
        user_agent = self.user_agents[attempt % len(self.user_agents)]
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a page from IMFDB with retry logic
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object if successful, None otherwise
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                
                # Rotate user agent on retries
                if attempt > 0:
                    self._update_headers(attempt)
                    wait_time = self.delay * (attempt + 1)  # Exponential backoff
                    self.logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    self.logger.info(f"Successfully retrieved page ({len(response.content)} bytes)")
                    return BeautifulSoup(response.content, "html.parser")
                    
                elif response.status_code == 403:
                    self.logger.warning(f"403 Forbidden (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        continue
                    else:
                        self.logger.error("Failed after all retry attempts. Consider using Selenium_Scraper.py")
                        
                else:
                    response.raise_for_status()
                    
            except requests.Timeout:
                self.logger.error(f"Timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to retrieve {url} after timeout")
                    
            except requests.RequestException as e:
                self.logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to retrieve {url} after {self.max_retries} attempts")
        
        return None
    
    def scrape_games(self, game_urls: dict) -> dict:
        """
        Scrape multiple games
        
        Args:
            game_urls: Dictionary mapping game names to URLs
            
        Returns:
            Dictionary mapping game names to BeautifulSoup objects
        """
        results = {}
        
        for game_name, url in game_urls.items():
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Scraping {game_name}")
            self.logger.info(f"{'='*60}")
            
            soup = self.fetch_page(url)
            if soup:
                results[game_name] = soup
                self.logger.info(f"✓ Successfully scraped {game_name}")
            else:
                self.logger.error(f"✗ Failed to scrape {game_name}")
            
            # Delay between requests (except for the last one)
            if game_name != list(game_urls.keys())[-1]:
                self.logger.info(f"Waiting {self.delay} seconds before next request...")
                time.sleep(self.delay)
        
        return results
