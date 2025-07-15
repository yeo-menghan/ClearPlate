from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import time
import os
import requests

options = Options()
# Commented headless to show window
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.instagram.com/caifanbrother/")
time.sleep(5)

# Dismiss cookie banner
try:
    driver.find_element("xpath", "//button[text()='Only allow essential cookies']").click()
    print("Cookies dismissed.")
except NoSuchElementException:
    pass

# Dismiss login popup
try:
    driver.find_element("xpath", "//div[@role='dialog']//button[contains(text(), 'Not Now')]").click()
    print("Login modal dismissed.")
except NoSuchElementException:
    pass

# Scroll to load posts
last_height = driver.execute_script("return document.body.scrollHeight")
for i in range(20):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    print(f"Scrolled {i+1} times...")

# Parse and download
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()
img_tags = soup.find_all("img")
img_urls = list(set(tag["src"] for tag in img_tags if "src" in tag.attrs))

os.makedirs("ig_downloads", exist_ok=True)
for i, url in enumerate(img_urls):
    try:
        r = requests.get(url)
        with open(f"ig_downloads/post_{i+1}.jpg", "wb") as f:
            f.write(r.content)
        print(f"Downloaded post_{i+1}.jpg")
    except Exception as e:
        print(f"Error downloading image {i+1}: {e}")
