#!/usr/bin/env python3
"""
Browser finder module for detecting Chromium installation paths.
"""

import sys
import os


def find_chromium():
    """Find Chromium installation path."""
    if sys.platform == "win32":
        # Windows paths for Chromium
        possible_paths = [
            r"C:\Program Files\Chromium\Application\chrome.exe",
            r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Chromium\Application\chrome.exe".format(os.getenv('USERNAME')),
            r"C:\Users\{}\AppData\Roaming\Chromium\Application\chrome.exe".format(os.getenv('USERNAME')),
            # Also check for portable Chromium
            r"C:\chromium\chrome.exe",
            r"C:\Program Files\chromium\chrome.exe",
            r"C:\Program Files (x86)\chromium\chrome.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found Chromium at: {path}")
                return path
                
    elif sys.platform == "darwin":
        # macOS paths for Chromium
        possible_paths = [
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found Chromium at: {path}")
                return path
    else:
        # Linux paths for Chromium
        possible_paths = [
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/snap/bin/chromium",
            "/usr/bin/google-chromium"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found Chromium at: {path}")
                return path
    
    return None


def get_system_info():
    """Get information about the current system."""
    return {
        'platform': sys.platform,
        'username': os.getenv('USERNAME'),
        'home': os.path.expanduser('~')
    }
