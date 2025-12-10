"""
Weapon image scraping and processing functionality
"""

import os
import re
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging


class WeaponImageScraper:
    """Handles downloading and processing weapon images from IMFDB"""
    
    def __init__(self, output_dir: str = 'images', delay: float = 1.0, 
                 max_retries: int = 3, verbose: bool = False):
        """
        Initialize the image scraper
        
        Args:
            output_dir: Directory to save images (default: 'images')
            delay: Delay in seconds between image downloads (default: 1.0)
            max_retries: Maximum retry attempts for failed downloads (default: 3)
            verbose: Enable verbose logging (default: False)
        """
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.max_retries = max_retries
        
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory structure
        self._create_directories()
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.imfdb.org/'
        })
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'skipped': 0,
            'total_size_bytes': 0
        }
    
    def _create_directories(self):
        """Create output directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different games
        (self.output_dir / 'by_game').mkdir(exist_ok=True)
        (self.output_dir / 'by_weapon').mkdir(exist_ok=True)
        (self.output_dir / 'thumbnails').mkdir(exist_ok=True)
    
    def scrape_weapon_images(self, soup: BeautifulSoup, weapon_name: str, 
                           game_name: str, heading_tag: Optional[BeautifulSoup] = None) -> List[str]:
        """
        Extract image URLs for a specific weapon from a page
        
        Args:
            soup: BeautifulSoup object of the page
            weapon_name: Name of the weapon
            game_name: Name of the game
            heading_tag: Optional heading tag to start search from
            
        Returns:
            List of image URLs
        """
        image_urls = []
        
        # If no heading tag provided, search for it
        if not heading_tag:
            heading_tag = soup.find(['h3', 'h4'], 
                                   string=re.compile(re.escape(weapon_name), re.IGNORECASE))
        
        if not heading_tag:
            self.logger.debug(f"No heading found for weapon: {weapon_name}")
            return image_urls
        
        # Find all content between this heading and the next heading
        current = heading_tag.find_next_sibling()
        
        while current and current.name not in ['h2', 'h3', 'h4']:
            # Look for images in this section
            if current.name in ['div', 'p', 'ul', 'table']:
                # Find all images and thumbs
                images = current.find_all(['img', 'a'], 
                                        class_=re.compile(r'image|thumb', re.IGNORECASE))
                
                for img_element in images:
                    img_url = self._extract_image_url(img_element)
                    if img_url and img_url not in image_urls:
                        image_urls.append(img_url)
            
            current = current.find_next_sibling()
        
        self.logger.debug(f"Found {len(image_urls)} images for {weapon_name}")
        return image_urls
    
    def _extract_image_url(self, element: BeautifulSoup) -> Optional[str]:
        """
        Extract image URL from an element
        
        Args:
            element: BeautifulSoup element (img or a tag)
            
        Returns:
            Image URL or None
        """
        if element.name == 'img':
            # Get src or data-src
            url = element.get('src') or element.get('data-src')
        elif element.name == 'a':
            # Check if link points to an image
            href = element.get('href', '')
            if any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                url = href
            else:
                # Look for img inside the link
                img = element.find('img')
                if img:
                    url = img.get('src') or img.get('data-src')
                else:
                    url = None
        else:
            url = None
        
        if url:
            # Convert relative URLs to absolute
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = urljoin('https://www.imfdb.org', url)
            
            # Skip thumbnails if full image is available
            if '/thumb/' in url:
                # Try to get full image URL by removing /thumb/ and size suffix
                url = re.sub(r'/thumb/([^/]+)/\d+px-([^/]+)$', r'/\1/\2', url)
        
        return url
    
    def download_weapon_images(self, weapon: Dict, image_urls: List[str]) -> List[str]:
        """
        Download images for a weapon
        
        Args:
            weapon: Weapon dictionary with metadata
            image_urls: List of image URLs to download
            
        Returns:
            List of local file paths for downloaded images
        """
        downloaded_files = []
        game_name = weapon.get('game', 'unknown')
        weapon_name = weapon.get('real_world_name') or weapon.get('toc_name', 'unknown')
        
        # Sanitize names for file system
        safe_game_name = self._sanitize_filename(game_name)
        safe_weapon_name = self._sanitize_filename(weapon_name)
        
        # Create game subdirectory
        game_dir = self.output_dir / 'by_game' / safe_game_name
        game_dir.mkdir(parents=True, exist_ok=True)
        
        # Create weapon subdirectory
        weapon_dir = self.output_dir / 'by_weapon' / safe_weapon_name
        weapon_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, image_url in enumerate(image_urls):
            self.stats['total_processed'] += 1
            
            try:
                # Generate filename
                file_extension = self._get_file_extension(image_url)
                filename = f"{safe_weapon_name}_{idx+1}{file_extension}"
                
                # Save to both game and weapon directories
                game_filepath = game_dir / filename
                weapon_filepath = weapon_dir / filename
                
                # Skip if already downloaded
                if game_filepath.exists():
                    self.logger.debug(f"Image already exists: {filename}")
                    self.stats['skipped'] += 1
                    downloaded_files.append(str(game_filepath))
                    continue
                
                # Download image
                success, file_size = self._download_image(image_url, game_filepath)
                
                if success:
                    # Copy to weapon directory
                    self._copy_file(game_filepath, weapon_filepath)
                    
                    downloaded_files.append(str(game_filepath))
                    self.stats['successful_downloads'] += 1
                    self.stats['total_size_bytes'] += file_size
                    
                    self.logger.info(f"✓ Downloaded: {filename} ({file_size/1024:.1f} KB)")
                else:
                    self.stats['failed_downloads'] += 1
                
                # Delay between downloads
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error downloading {image_url}: {e}")
                self.stats['failed_downloads'] += 1
        
        return downloaded_files
    
    def _download_image(self, url: str, filepath: Path) -> Tuple[bool, int]:
        """
        Download an image from URL to filepath
        
        Args:
            url: Image URL
            filepath: Local file path to save to
            
        Returns:
            Tuple of (success boolean, file size in bytes)
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Write image to file
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = filepath.stat().st_size
                
                # Verify image is valid (at least 1KB)
                if file_size < 1024:
                    self.logger.warning(f"Image too small ({file_size} bytes): {url}")
                    filepath.unlink()
                    return False, 0
                
                return True, file_size
                
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt+1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to download after {self.max_retries} attempts: {url}")
                    return False, 0
                time.sleep(self.delay * (attempt + 1))
        
        return False, 0
    
    def _copy_file(self, src: Path, dst: Path):
        """Copy file from src to dst"""
        try:
            import shutil
            shutil.copy2(src, dst)
        except Exception as e:
            self.logger.warning(f"Failed to copy {src} to {dst}: {e}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for file system
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove extra spaces and underscores
        sanitized = re.sub(r'[_\s]+', '_', sanitized)
        
        # Trim to reasonable length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized.strip('_')
    
    def _get_file_extension(self, url: str) -> str:
        """
        Extract file extension from URL
        
        Args:
            url: Image URL
            
        Returns:
            File extension with dot (e.g., '.jpg')
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Common image extensions
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            if ext in path:
                return ext
        
        # Default to .jpg if unknown
        return '.jpg'
    
    def scrape_all_weapon_images(self, weapons: List[Dict], 
                                 scraped_pages: Dict[str, BeautifulSoup]) -> Dict[str, List[str]]:
        """
        Scrape and download images for all weapons
        
        Args:
            weapons: List of weapon dictionaries
            scraped_pages: Dictionary mapping game names to BeautifulSoup objects
            
        Returns:
            Dictionary mapping weapon identifiers to lists of local file paths
        """
        self.logger.info(f"Starting image scraping for {len(weapons)} weapons")
        
        weapon_images = {}
        
        for weapon in weapons:
            game_name = weapon.get('game', '')
            weapon_name = weapon.get('toc_name', '')
            
            if not game_name or not weapon_name:
                continue
            
            # Get the soup for this game
            soup = scraped_pages.get(game_name)
            if not soup:
                self.logger.warning(f"No page found for game: {game_name}")
                continue
            
            # Extract image URLs
            image_urls = self.scrape_weapon_images(soup, weapon_name, game_name)
            
            if image_urls:
                # Download images
                downloaded_files = self.download_weapon_images(weapon, image_urls)
                
                # Store results
                weapon_id = f"{game_name}|{weapon_name}"
                weapon_images[weapon_id] = downloaded_files
        
        self.logger.info(f"Image scraping complete. Downloaded {self.stats['successful_downloads']} images")
        
        return weapon_images
    
    def get_statistics(self) -> Dict:
        """
        Get download statistics
        
        Returns:
            Dictionary with download statistics
        """
        stats = self.stats.copy()
        
        # Add derived statistics
        if stats['total_processed'] > 0:
            stats['success_rate'] = (stats['successful_downloads'] / stats['total_processed']) * 100
        else:
            stats['success_rate'] = 0.0
        
        stats['total_size_mb'] = stats['total_size_bytes'] / (1024 * 1024)
        
        return stats
    
    def generate_image_report(self) -> str:
        """
        Generate a detailed image scraping report
        
        Returns:
            Formatted report string
        """
        stats = self.get_statistics()
        
        report = []
        report.append("=" * 60)
        report.append("IMAGE SCRAPING REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal images processed: {stats['total_processed']}")
        report.append(f"Successful downloads: {stats['successful_downloads']}")
        report.append(f"Failed downloads: {stats['failed_downloads']}")
        report.append(f"Skipped (already exists): {stats['skipped']}")
        report.append(f"Success rate: {stats['success_rate']:.1f}%")
        report.append(f"Total size: {stats['total_size_mb']:.2f} MB")
        report.append(f"\nImages saved to: {self.output_dir.absolute()}")
        report.append("=" * 60)
        
        return "\n".join(report)
