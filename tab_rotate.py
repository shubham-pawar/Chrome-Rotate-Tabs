import time
import chromedriver_autoinstaller
from selenium import webdriver

# Automatically install the ChromeDriver
chromedriver_autoinstaller.install()

# Create a new instance of Chrome
driver = webdriver.Chrome()

# Open the first URL directly in the first tab
urls = [
    "https://www.youtube.com",
    "https://www.apple.com",
    "https://www.github.com",
    "https://www.wikipedia.org"
]

# Open the first URL
driver.get(urls[0])
time.sleep(1)  # Wait for the page to load

# Open the remaining URLs in new tabs
for url in urls[1:]:
    driver.execute_script("window.open(arguments[0], '_blank');", url)
    time.sleep(1)  # Wait a bit for each page to load

# Function to rotate tabs
def rotate_tabs(interval):
    while True:
        for index in range(len(driver.window_handles)):
            driver.switch_to.window(driver.window_handles[index])
            time.sleep(interval)  # Wait for the specified interval

# Rotate tabs every 10 seconds
rotate_tabs(10) 
