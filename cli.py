#!/usr/bin/env python3
"""
Command Line Interface module for the browser opener project.
"""

import argparse
import sys
from browser_launcher import BrowserLauncher
from web_automation import WebAutomation
from utils import print_status, validate_url
from config import DEFAULT_URL


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Open Chromium browser with optional login automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run full automation with login
  python cli.py --browser-only      # Just open browser without automation
  python cli.py -u https://google.com --browser-only  # Open custom URL
  python cli.py --automate          # Run automation (default)
  python cli.py -v --automate       # Run automation with verbose output
        """
    )
    
    parser.add_argument(
        '-u', '--url',
        type=str,
        default=DEFAULT_URL,
        help=f'URL to open (default: {DEFAULT_URL})'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--browser-only',
        action='store_true',
        help='Only open browser without automation'
    )
    
    parser.add_argument(
        '--automate',
        action='store_true',
        help='Run full automation with login (default)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def main_cli():
    """Main CLI function."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate URL
    if not validate_url(args.url):
        print(f"❌ Invalid URL: {args.url}")
        print("URL must start with http:// or https://")
        sys.exit(1)
    
    if args.verbose:
        print(f"🔍 Verbose mode enabled")
        print(f"🌐 Target URL: {args.url}")
    
    # Determine mode
    if args.browser_only:
        # Just open browser without automation
        if args.verbose:
            print("🌐 Opening browser only (no automation)")
        
        launcher = BrowserLauncher(args.url)
        success = launcher.open_chromium()
        
        if not success:
            print("❌ Failed to open browser")
            sys.exit(1)
        
        if args.verbose:
            print("✅ Browser opened successfully")
    else:
        # Run full automation (default)
        if args.verbose:
            print("🤖 Running full automation with login")
        
        automation = WebAutomation(args.url)
        success = automation.automate_login()
        
        if not success:
            print("❌ Automation failed")
            sys.exit(1)
        
        if args.verbose:
            print("✅ Automation completed successfully")
        
        # Keep browser open for manual interaction
        print("🌐 Browser will remain open for manual interaction")
        try:
            input("Press Enter to close the browser...")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            automation.close_browser()


if __name__ == "__main__":
    main_cli()
