from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os

# Setup Chrome
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Open the website
driver.get("https://perchance.org/ai-character-generator")

# Prompt user
prompt = input("Enter your character description: ")

# Wait for input box and insert description
desc_box = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='description']"))
)
desc_box.clear()
desc_box.send_keys(prompt)

# Click generate button
generate_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'generate')]")
generate_btn.click()

# Wait a bit for generation
time.sleep(5)

# Check for blocked image
blocked = driver.find_elements(By.XPATH, "//div[contains(text(),'Your safety settings have blocked this image.')]")
if blocked:
    print("[!] Image blocked. Updating settings...")

    # Click "change settings"
    change_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'change settings')]"))
    )
    change_btn.click()

    # Wait for dropdown and click to open
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "select"))
    )
    dropdown.click()

    # Select "Disable filter permanently"
    dropdown.send_keys("Disable filter permanently")

    # Check "I am over 18 years old"
    age_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and contains(@aria-label,'18')]")
    age_checkbox.click()

    # Save settings
    save_btn = driver.find_element(By.XPATH, "//button[text()='save']")
    save_btn.click()

    # Regenerate the image
    time.sleep(3)
    generate_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'generate')]")
    generate_btn.click()
    time.sleep(6)

# Find the image element (if not blocked)
try:
    image = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "img"))
    )
    image_url = image.get_attribute("src")

    # Download image
    if image_url.startswith("http"):
        img_data = requests.get(image_url).content
        os.makedirs("downloads", exist_ok=True)
        filename = f"downloads/{prompt.replace(' ', '_')[:30]}.png"
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        print(f"[+] Image saved to {filename}")
    else:
        print("[!] No valid image URL found.")
except Exception as e:
    print("[!] Error extracting image:", str(e))

# Close browser
driver.quit()
