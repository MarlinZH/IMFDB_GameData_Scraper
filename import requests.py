import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL to scrape
urls = {
    "MWII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)",
    "MWIII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_III_(2023)",
    "Ready_or_Not": "https://www.imfdb.org/wiki/Ready_or_Not"
}

weapons = []

for game, url in urls.items():
    print(f"Scraping {game} from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the TOC (Table of Contents) section
    toc = soup.find('div', {'class': 'toc'})
    print(f"TOC found for {game}: {toc is not None}")
    if toc:
        print(f"Found TOC for {game}")
        for category_li in toc.findall('li', class='toclevel-1'):
            category = categoryli.find('span', class='toctext')
            if not category:
                continue
            category_name = category.get_text().strip()
            # Find all weapons under this category
            for weapon_li in category_li.findall('li', class='toclevel-2'):
                weapon_span = weaponli.find('span', class='toctext')
                if weapon_span:
                    weapon_name = weapon_span.get_text().strip()
                    weapons.append({
                        "Game": game,
                        "Category": category_name,
                        "In-Game Name": weapon_name,
                        "Real-World Equivalent": ""  # You can enhance this if needed
                    })

df = pd.DataFrame(weapons)
df.to_csv("all_weapons.csv", index=False)
df.to_markdown("all_weapons.md", index=False)

df.head()

print(f"Total weapons found: {len(weapons)}")
print(weapons[:5])  # Show a sample
# print(soup.prettify()[:1000])