#!/usr/bin/env python3
"""
Automation orchestrator module for web automation.
"""

import time
from .driver_setup import setup_driver
from .page_operations import open_page
from .login_operations import (
    fill_login_form, 
    get_code_token_from_user, 
    fill_code_token, 
    click_submit_button
)
from .navigation_operations import click_home_page_item1, click_action_view
from .popup_operations import handle_popup_with_text_input
from .post_popup_actions import handle_post_popup_actions


def automate_login(url, username, password):
    """Complete automation process."""
    try:
        print("🤖 Starting web automation...")
        
        # Setup driver
        driver, wait, success = setup_driver()
        if not success:
            return False
        
        # Open page
        if not open_page(driver, url):
            return False
        
        # Wait a bit for page to load
        time.sleep(2)
        
        # Fill login form
        if not fill_login_form(driver, username, password):
            return False
        
        # Get CodeToken from user
        code_token = get_code_token_from_user()
        if not code_token:
            return False
        
        # Fill CodeToken
        if not fill_code_token(driver, code_token):
            return False
        
        # Click submit button
        if not click_submit_button(driver):
            return False
        
        # Wait for login to complete and page to load
        print("⏳ Waiting for login to complete...")
        time.sleep(3)
        
        # Click on homePageItem1 div
        if not click_home_page_item1(driver):
            return False
        
        # Wait for the div to load
        time.sleep(2)
        
        # Click on actionview div
        if not click_action_view(driver):
            return False
        
        # Wait for popup to appear
        print("⏳ Waiting for popup to appear...")
        time.sleep(3)
        
        # Handle the popup with text input
        if not handle_popup_with_text_input(driver):
            return False
        
        # Get the text array from the popup for use in post-popup actions
        text_array = driver.execute_script("return window.maslekaTextArray || [];")
        
        # Handle post-popup actions
        if not handle_post_popup_actions(driver, wait, text_array):
            return False
        
        print("✅ Automation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        return False
    finally:
        # Keep the browser open for user interaction
        print("🌐 Browser will remain open for manual interaction")


def close_browser(driver):
    """Close the browser."""
    if driver:
        driver.quit()
        print("   Browser closed")
