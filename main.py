#!/usr/bin/env python3
"""
Main file for the Python project that opens Chromium browser and automates login.
"""

from web_automation import WebAutomation
from utils import print_status


def main():
    """Main function to run the application."""
    print_status('start')
    print_status('looking')
    
    # Create web automation instance
    automation = WebAutomation()
    
    # Run the complete automation process
    success = automation.automate_login()
    
    if success:
        print_status('success')
        print("🤖 Automation completed! The browser will remain open.")
        print("💡 You can now interact with the page manually.")
        print("💡 If some steps failed, you can complete them manually.")
        
        # Keep the script running until user closes browser
        try:
            input("Press Enter to close the browser...")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            automation.close_browser()
    else:
        print("❌ Automation failed. Please check the error messages above.")
        print("💡 The browser will remain open so you can try manual steps.")
        
        # Keep browser open even if automation failed
        try:
            input("Press Enter to close the browser...")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            automation.close_browser()


if __name__ == "__main__":
    main()
