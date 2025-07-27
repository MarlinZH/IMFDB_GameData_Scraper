import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL to scrape
urls = {
    "MWII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)",
    "MWIII": "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_III_(2023)",
    "Ready_or_Not": "https://www.imfdb.org/wiki/Ready_or_Not"
}

response = requests.get(urls)
soup = BeautifulSoup(response.content, "html.parser")

weapons = []
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
            "Category": current_category,
            "In-Game Name": weapon_name,
            "Real-World Equivalent": real_world_equiv
        })

df = pd.DataFrame(weapons)
df.to_csv("mwii_weapons.csv", index=False)
df.to_markdown("mwii_weapons.md", index=False)

df.head()
