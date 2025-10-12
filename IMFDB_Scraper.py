import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin

# URL to scrape
urls = {
    --"MWII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)",
    "MWIII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_III_(2023)",
    "Ready_or_Not": "https://www.imfdb.org/wiki/Ready_or_Not",
    "Delta Force": "https://www.imfdb.org/wiki/Delta_Force_(2024_VG)"
}

weapons = []

for game, url in urls.items():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    current_category = ""

    for tag in soup.find_all(['h2', 'h3', 'h4', 'p']):
        if tag.name == 'h2':
            current_category = tag.get_text().strip()
        elif tag.name in ['h3', 'h4']:
            weapon_name = tag.get_text().strip()
            real_world_equiv = ""

            if "(" in weapon_name and ")" in weapon_name:
                real_world_equiv = weapon_name.split("(")[-1].split(")")[0].strip()
                weapon_name = weapon_name.split("(")[0].strip()

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
            # weapons = self.scrape_game_weapons(game, url)
            # all_weapons.extend(weapons)
            
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
        "MWII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)"
        # ,
        # "MWIII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_III_(2023)",
        # "Ready_or_Not": "https://www.imfdb.org/wiki/Ready_or_Not"
    }
    for game, url in urls.items():
        print(f"Scraping {game} from {url}")
        response = requests.get(url)
        print("RESPONSE:",response.content)
        soup = BeautifulSoup(response.content, "html.parser")
        print("SOUP:",soup.prettify()[:1000])  # Print first 1000 characters of prettified HTML
        print(f"Successfully retrieved {game} page ({len(response.content)} bytes)")
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