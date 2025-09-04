#!/usr/bin/env python3
"""
Page operations module for web automation.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def open_page(driver, url):
    """Open the target page."""
    try:
        print(f"🌐 Opening page: {url}")
        driver.get(url)
        print("✅ Page opened successfully")
        return True
    except Exception as e:
        print(f"❌ Error opening page: {e}")
        return False


def wait_for_element(driver, by, value, timeout=30):
    """Wait for an element to be present on the page."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"❌ Timeout waiting for element: {value}")
        # Add debugging information
        try:
            print(f"🔍 Current page URL: {driver.current_url}")
            print(f"🔍 Page title: {driver.title}")
            
            # Try to find similar elements
            if by == By.ID:
                # Look for elements with similar IDs
                similar_elements = driver.find_elements(By.CSS_SELECTOR, f"[id*='{value.lower()}']")
                if similar_elements:
                    print(f"🔍 Found {len(similar_elements)} elements with similar IDs:")
                    for elem in similar_elements[:5]:  # Show first 5
                        try:
                            print(f"   - {elem.get_attribute('id')} (text: '{elem.text[:50]}...')")
                        except:
                            print(f"   - {elem.get_attribute('id')} (text: not readable)")
            
            # Look for elements with similar text content
            all_elements = driver.find_elements(By.TAG_NAME, "*")
            matching_elements = []
            for elem in all_elements:
                try:
                    if value.lower() in elem.text.lower() or value.lower() in (elem.get_attribute('id') or '').lower():
                        matching_elements.append(elem)
                except:
                    continue
            
            if matching_elements:
                print(f"🔍 Found {len(matching_elements)} elements with similar content:")
                for elem in matching_elements[:5]:  # Show first 5
                    try:
                        elem_id = elem.get_attribute('id') or 'no-id'
                        elem_text = elem.text[:30] or 'no-text'
                        print(f"   - ID: {elem_id}, Text: '{elem_text}...'")
                    except:
                        print(f"   - Element (details not readable)")
            
        except Exception as debug_error:
            print(f"⚠️ Could not gather debugging info: {debug_error}")
        
        return None
