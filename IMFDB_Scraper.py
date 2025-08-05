import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin

class IMFDBScraper:
    def __init__(self, delay=2):
        """Initialize the scraper with optional delay between requests"""
        self.delay = delay
        self.session = requests.get(url)
        # self.session.headers.update({
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #     'Accept-Language': 'en-US,en;q=0.9',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'DNT': '1',
        #     'Connection': 'keep-alive',
        #     'Upgrade-Insecure-Requests': '1',
        #     'Sec-Fetch-Dest': 'document',
        #     'Sec-Fetch-Mode': 'navigate',
        #     'Sec-Fetch-Site': 'none',
        #     'Cache-Control': 'max-age=0'
        # })
    
    def extract_weapon_info(self, soup, weapon_name):
        """Extract both real-world name and in-game name from the page content"""
        real_world_name = ""
        ingame_name = ""
        
        # Look for headings that match the weapon name
        headings = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(re.escape(weapon_name), re.IGNORECASE))
        
        for heading in headings:
            # Get the heading text which often contains both names
            heading_text = heading.get_text().strip()
            
            # Look for the next paragraph or content after the heading
            next_elements = heading.find_next_siblings(['p', 'div', 'ul'])[:3]  # Check first few elements
            
            # Extract from heading patterns
            heading_patterns = [
                r'(.+?)\s*-\s*(.+?)$',  # "Real Name - Game Name" or vice versa
                r'(.+?)\s*\((.+?)\)',   # "Name (Alternative Name)"
                r'"(.+?)"',             # Quoted in-game names
            ]
            
            for pattern in heading_patterns:
                match = re.search(pattern, heading_text)
                if match:
                    if 'as' in heading_text.lower() or 'called' in heading_text.lower():
                        real_world_name = match.group(1).strip()
                        ingame_name = match.group(2).strip() if len(match.groups()) > 1 else ""
                    else:
                        real_world_name = match.group(1).strip()
                        if len(match.groups()) > 1:
                            ingame_name = match.group(2).strip()
            
            # Extract from content paragraphs
            for element in next_elements:
                if not element:
                    continue
                    
                text = element.get_text()
                
                # Patterns for real weapon names
                real_world_patterns = [
                    r'The (.+?) (?:is|appears|can be)',
                    r'A (.+?) (?:is|appears|can be)',
                    r'An (.+?) (?:is|appears|can be)',
                    r'Based on (?:the )?(.+?)[\.,]',
                    r'Real weapon[:\s]+(.+?)[\.,\n]',
                    r'Actually (?:a |an |the )?(.+?)[\.,]'
                ]
                
                # Patterns for in-game names
                ingame_patterns = [
                    r'(?:called|named|known as|appears as)\s+"(.+?)"',
                    r'(?:called|named|known as|appears as)\s+(.+?)[\.,\n]',
                    r'in-game (?:as |name[:\s]+)"?(.+?)"?[\.,\n]',
                    r'game (?:calls it|names it)\s+"?(.+?)"?[\.,\n]',
                    r'"(.+?)"\s+(?:in|is the)',
                    r'labeled as\s+"?(.+?)"?[\.,\n]'
                ]
                
                # Try to find real-world name if not found yet
                if not real_world_name:
                    for pattern in real_world_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            candidate = match.group(1).strip()
                            # Filter out obvious non-weapon terms
                            if not any(word in candidate.lower() for word in ['game', 'weapon', 'gun', 'rifle', 'it', 'this', 'that']):
                                real_world_name = candidate
                                break
                
                # Try to find in-game name if not found yet
                if not ingame_name:
                    for pattern in ingame_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            ingame_name = match.group(1).strip()
                            break
                
                if real_world_name and ingame_name:
                    break
        
        # Clean up extracted names
        if real_world_name:
            real_world_name = re.sub(r'\s+', ' ', real_world_name).strip()
        if ingame_name:
            ingame_name = re.sub(r'\s+', ' ', ingame_name).strip()
            
        return real_world_name, ingame_name
    
    def scrape_game_weapons(self, game_name, url):
        """Scrape weapons from a single game page"""
        print(f"Scraping {game_name} from {url}")
        weapons = []
        
        try:
            print(f"Making request to {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 403:
                print(f"403 Forbidden for {game_name}. Trying with different approach...")
                # Try with a fresh session and longer delay
                time.sleep(5)
                backup_session = requests.Session()
                backup_session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
                })
                response = backup_session.get(url, timeout=30)
            
            response.raise_for_status()
            print(f"Successfully retrieved {game_name} page ({len(response.content)} bytes)")
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find the TOC (Table of Contents) section
            toc = soup.find('div', {'class': 'toc'})
            
            if not toc:
                print(f"No TOC found for {game_name}, trying alternative approach...")
                return self.scrape_alternative_method(game_name, soup)
            
            print(f"Found TOC for {game_name}")
            
            for category_li in toc.find_all('li', class_='toclevel-1'):
                category_span = category_li.find('span', class_='toctext')
                if not category_span:
                    continue
                
                category_name = category_span.get_text().strip()
                
                # Skip non-weapon categories
                skip_categories = ['cast', 'crew', 'trivia', 'gallery', 'references', 'see also']
                if any(skip in category_name.lower() for skip in skip_categories):
                    continue
                
                print(f"  Processing category: {category_name}")
                
                # Find weapons in this category (toclevel-2)
                weapon_count = 0
                for weapon_li in category_li.find_all('li', class_='toclevel-2'):
                    weapon_span = weapon_li.find('span', class_='toctext')
                    if weapon_span:
                        toc_weapon_name = weapon_span.get_text().strip()
                        
                        # Try to get both real-world and in-game names
                        real_world, ingame = self.extract_weapon_info(soup, toc_weapon_name)
                        
                        # If we didn't find specific in-game name, use the TOC name as fallback
                        if not ingame:
                            ingame = toc_weapon_name
                        
                        weapons.append({
                            "Game": game_name,
                            "Category": category_name,
                            "TOC Name": toc_weapon_name,
                            "Real-World Name": real_world,
                            "In-Game Name": ingame
                        })
                        weapon_count += 1
                
                print(f"    Found {weapon_count} weapons in {category_name}")
            
            print(f"Total weapons found for {game_name}: {len(weapons)}")
            
        except requests.RequestException as e:
            print(f"Error scraping {game_name}: {e}")
            if "403" in str(e):
                print("Tip: IMFDB may be blocking automated requests. Try:")
                print("1. Using a VPN")
                print("2. Increasing delay between requests")
                print("3. Running the script at different times")
        except Exception as e:
            print(f"Unexpected error for {game_name}: {e}")
        
        return weapons
    
    def scrape_alternative_method(self, game_name, soup):
        """Alternative scraping method when TOC is not available"""
        weapons = []
        
        # Look for weapon headings directly
        headings = soup.find_all(['h2', 'h3'], string=re.compile(r'.*(rifle|pistol|gun|weapon|grenade|launcher).*', re.IGNORECASE))
        
        for heading in headings:
            toc_weapon_name = heading.get_text().strip()
            # Try to determine category from heading level or content
            category = "Unknown"
            
            # Try to extract weapon info
            real_world, ingame = self.extract_weapon_info(soup, toc_weapon_name)
            
            if not ingame:
                ingame = toc_weapon_name
            
            weapons.append({
                "Game": game_name,
                "Category": category,
                "TOC Name": toc_weapon_name,
                "Real-World Name": real_world,
                "In-Game Name": ingame
            })
        
        return weapons
    
    def scrape_all_games(self, urls):
        """Scrape weapons from all provided URLs"""
        all_weapons = []
        
        for game, url in urls.items():
            weapons = self.scrape_game_weapons(game, url)
            all_weapons.extend(weapons)
            
            # Be respectful with delays
            if self.delay > 0:
                print(f"Waiting {self.delay} seconds before next request...")
                time.sleep(self.delay)
        
        return all_weapons
    
    def save_data(self, weapons, base_filename="weapons"):
        """Save the scraped data to CSV and Markdown files"""
        if not weapons:
            print("No weapons data to save")
            return
        
        df = pd.DataFrame(weapons)
        
        # Save to CSV
        csv_filename = f"{base_filename}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")
        
        # Save to Markdown
        md_filename = f"{base_filename}.md"
        df.to_markdown(md_filename, index=False)
        print(f"Data saved to {md_filename}")
        
        # Display summary statistics
        print(f"\n=== SUMMARY ===")
        print(f"Total weapons found: {len(weapons)}")
        print(f"Games: {df['Game'].nunique()}")
        print(f"Categories: {df['Category'].nunique()}")
        print(f"\nWeapons per game:")
        print(df['Game'].value_counts())
        print(f"\nWeapons per category:")
        print(df['Category'].value_counts())
        
        return df

# Main execution
if __name__ == "__main__":
    # URLs to scrape
    urls = {
        "MWII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)",
        "MWIII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_III_(2023)",
        "Ready_or_Not": "https://www.imfdb.org/wiki/Ready_or_Not"
    }
    
    # Create scraper instance with longer delay
    scraper = IMFDBScraper(delay=3)
    
    # Scrape all games
    weapons_data = scraper.scrape_all_games(urls)
    
    # Save the data
    df = scraper.save_data(weapons_data, "all_weapons")
    
    # Show sample of the data
    if not df.empty:
        print(f"\n=== SAMPLE DATA ===")
        print(df.head(10))
        
        # Show weapons with real-world names found
        real_world_found = df[df['Real-World Name'] != '']
        if not real_world_found.empty:
            print(f"\n=== WEAPONS WITH REAL-WORLD NAMES FOUND ===")
            print(real_world_found[['TOC Name', 'Real-World Name', 'In-Game Name']].head())
        
        # Show weapons where in-game name differs from TOC name
        different_names = df[df['TOC Name'] != df['In-Game Name']]
        if not different_names.empty:
            print(f"\n=== WEAPONS WITH DIFFERENT IN-GAME NAMES ===")
            print(different_names[['TOC Name', 'In-Game Name']].head())