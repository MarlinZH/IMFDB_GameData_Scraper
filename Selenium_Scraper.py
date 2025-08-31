from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = Options()

# Critical flags for container environments
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=9222")

# Only set this if you *know* your Chromium is at that path
# options.binary_location = "/usr/bin/chromium-browser"

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=options
)

url = "https://www.imfdb.org/wiki/Call_of_Duty:_Modern_Warfare_II_(2022)"
driver.get(url)

print("Page title:", driver.title)

element = driver.find_element(By.TAG_NAME, "h1")
print("First header:", element.text)

driver.quit()
