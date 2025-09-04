#!/usr/bin/env python3
"""
Login operations module for web automation.
"""

import tkinter as tk
from tkinter import simpledialog
from selenium.webdriver.common.by import By
from .page_operations import wait_for_element


def fill_login_form(driver, username, password):
    """Fill in the login form with credentials."""
    try:
        print("📝 Filling login form...")
        
        # Wait for and fill username
        username_field = wait_for_element(driver, By.ID, "UserName")
        if username_field:
            username_field.clear()
            username_field.send_keys(username)
            print(f"✅ Username filled: {username}")
        else:
            print("❌ Username field not found")
            return False
        
        # Wait for and fill password
        password_field = wait_for_element(driver, By.ID, "Password")
        if password_field:
            password_field.clear()
            password_field.send_keys(password)
            print(f"✅ Password filled: {password}")
        else:
            print("❌ Password field not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error filling login form: {e}")
        return False


def get_code_token_from_user():
    """Show a dialog to get the CodeToken from the user."""
    try:
        # Create a simple dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Center the dialog
        root.geometry("0x0+{}+{}".format(
            root.winfo_screenwidth() // 2,
            root.winfo_screenheight() // 2
        ))
        
        # Show input dialog
        code_token = simpledialog.askstring(
            "Code Token Required",
            "Please enter the Code Token:",
            parent=root
        )
        
        root.destroy()
        
        if code_token:
            print(f"✅ Code Token received: {code_token}")
            return code_token
        else:
            print("❌ No Code Token provided")
            return None
            
    except Exception as e:
        print(f"❌ Error getting Code Token: {e}")
        return None


def fill_code_token(driver, code_token):
    """Fill in the CodeToken field."""
    try:
        print("🔑 Filling Code Token...")
        
        # Wait for and fill CodeToken
        code_token_field = wait_for_element(driver, By.ID, "CodeToken")
        if code_token_field:
            code_token_field.clear()
            code_token_field.send_keys(code_token)
            print(f"✅ Code Token filled: {code_token}")
            return True
        else:
            print("❌ Code Token field not found")
            return False
            
    except Exception as e:
        print(f"❌ Error filling Code Token: {e}")
        return False


def click_submit_button(driver):
    """Click the SubmitButton1 button."""
    try:
        print("🔘 Looking for SubmitButton1...")
        
        # Wait for and click submit button
        submit_button = wait_for_element(driver, By.NAME, "SubmitButton1")
        if submit_button:
            submit_button.click()
            print("✅ Submit button clicked successfully")
            return True
        else:
            print("❌ Submit button not found")
            return False
            
    except Exception as e:
        print(f"❌ Error clicking submit button: {e}")
        return False
