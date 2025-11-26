import cloudscraper
from bs4 import BeautifulSoup
import pandas
redundant

test_url = "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)"

scraper = cloudscraper.create_scraper()
response = scraper.get(test_url)

print("RESPONSE:", response.text[:100000])  # print first 1000 chars

soup = BeautifulSoup(response.content, "html.parser")
# print ("SOUP:", soup.prettify()[:100000])  # Print first 1000 characters of prettified HTML

toc = soup.find("div", id="toc")
# IMFDB typically lists weapons in 'wikitable' class tables or in 'li' lists under headings
weapon_names = []

if toc:
    # TOC links are in <li> elements with nested <a> tags
    for li in toc.find_all("li"):
        a_tag = li.find("a")
        if a_tag:
            # Remove section numbers and whitespace
            name = a_tag.get_text(strip=True)
            # Often formatted as "1 Weapon Name" — remove leading numbers
            name = " ".join(name.split()[1:]) if name.split()[0].replace(".", "").isdigit() else name
            weapon_names.append(name)

# Clean duplicates and sort
weapon_names = sorted(list(set(weapon_names)))

print("Weapons from navigation:", weapon_names)
