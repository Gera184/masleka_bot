#!/usr/bin/env python3
"""
Web automation package for handling form interactions after browser opens.
"""

from .driver_setup import setup_driver
from .page_operations import open_page, wait_for_element
from .login_operations import (
    fill_login_form, 
    get_code_token_from_user, 
    fill_code_token, 
    click_submit_button
)
from .navigation_operations import click_home_page_item1, click_action_view
from .popup_operations import handle_popup_with_text_input
from .post_popup_actions import handle_post_popup_actions
from .automation_orchestrator import automate_login, close_browser

# Define the WebAutomation class directly in the package
from config import DEFAULT_URL

class WebAutomation:
    """Class to handle web automation tasks."""
    
    def __init__(self, url=DEFAULT_URL):
        """Initialize the web automation with the target URL."""
        self.url = url
        self.driver = None
        self.wait = None
        
        # Login credentials
        self.username = "EFZO312387319"
        self.password = "Badboy2025!@"
        
    def setup_driver(self):
        """Setup the webdriver with Chromium options."""
        driver, wait, success = setup_driver()
        if success:
            self.driver = driver
            self.wait = wait
        return success
    
    def open_page(self):
        """Open the target page."""
        return open_page(self.driver, self.url)
    
    def wait_for_element(self, by, value, timeout=30):
        """Wait for an element to be present on the page."""
        return wait_for_element(self.driver, by, value, timeout)
    
    def fill_login_form(self):
        """Fill in the login form with credentials."""
        return fill_login_form(self.driver, self.username, self.password)
    
    def get_code_token_from_user(self):
        """Show a dialog to get the CodeToken from the user."""
        return get_code_token_from_user()
    
    def fill_code_token(self, code_token):
        """Fill in the CodeToken field."""
        return fill_code_token(self.driver, code_token)
    
    def click_submit_button(self):
        """Click the SubmitButton1 button."""
        return click_submit_button(self.driver)
    
    def click_home_page_item1(self):
        """Click on the div with id=homePageItem1."""
        return click_home_page_item1(self.driver)
    
    def click_action_view(self):
        """Click on the div with id=actionview."""
        return click_action_view(self.driver)

    def handle_popup_with_text_input(self):
        """Create and handle popup with text input, label ת"ז, and buttons הוספה/שליחה."""
        return handle_popup_with_text_input(self.driver)

    def handle_post_popup_actions(self, text_array):
        """Handle actions after popup is completed - loop through all items in text_array and process each one."""
        return handle_post_popup_actions(self.driver, self.wait, text_array)

    def automate_login(self):
        """Complete automation process."""
        return automate_login(self.url, self.username, self.password)
    
    def close_browser(self):
        """Close the browser."""
        close_browser(self.driver)

__all__ = [
    'setup_driver',
    'open_page',
    'wait_for_element',
    'fill_login_form',
    'get_code_token_from_user',
    'fill_code_token',
    'click_submit_button',
    'click_home_page_item1',
    'click_action_view',
    'handle_popup_with_text_input',
    'handle_post_popup_actions',
    'automate_login',
    'close_browser',
    'WebAutomation'
]
