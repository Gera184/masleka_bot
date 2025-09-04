#!/usr/bin/env python3
"""
Navigation operations module for web automation.
"""

from selenium.webdriver.common.by import By
from .page_operations import wait_for_element


def click_home_page_item1(driver):
    """Click on the div with id=homePageItem1."""
    try:
        print("🏠 Looking for homePageItem1 div...")
        
        # Wait for and click homePageItem1 div
        home_item = wait_for_element(driver, By.ID, "homePageItem1")
        if home_item:
            home_item.click()
            print("✅ homePageItem1 div clicked successfully")
            return True
        else:
            print("❌ homePageItem1 div not found")
            return False
            
    except Exception as e:
        print(f"❌ Error clicking homePageItem1 div: {e}")
        return False


def click_action_view(driver):
    """Click on the div with id=actionview."""
    try:
        print("👁️ Looking for actionview div...")
        
        # Wait for and click actionview div
        action_view = wait_for_element(driver, By.ID, "actionview")
        if action_view:
            action_view.click()
            print("✅ actionview div clicked successfully")
            return True
        else:
            print("❌ actionview div not found")
            return False
            
    except Exception as e:
        print(f"❌ Error clicking actionview div: {e}")
        return False
