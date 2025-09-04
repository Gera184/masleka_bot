#!/usr/bin/env python3
"""
Driver setup module for web automation.
Exported from web_automation.py
"""

import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """Setup the webdriver with Chromium options."""
    try:
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configure download directory
        download_dir = Path.home() / "Desktop" / "maslekot"
        download_dir.mkdir(exist_ok=True)
        
        # Set download preferences
        prefs = {
            "download.default_directory": str(download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Try to use existing Chromium installation
        from browser_finder import find_chromium
        chromium_path = find_chromium()
        
        if chromium_path:
            chrome_options.binary_location = chromium_path
            print(f"✅ Using Chromium at: {chromium_path}")
        else:
            print("⚠️ Chromium not found, using default Chrome driver")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        wait = WebDriverWait(driver, 30)
        return driver, wait, True
        
    except Exception as e:
        print(f"❌ Error setting up webdriver: {e}")
        return None, None, False


if __name__ == "__main__":
    # Test the function
    driver, wait, success = setup_driver()
    if success:
        print("✅ Driver setup successful!")
        driver.quit()
    else:
        print("❌ Driver setup failed!")
