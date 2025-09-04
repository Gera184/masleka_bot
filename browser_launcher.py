#!/usr/bin/env python3
"""
Browser launcher module for opening Chromium and fallback browsers.
"""

import webbrowser
import subprocess
from browser_finder import find_chromium


class BrowserLauncher:
    """Class to handle browser launching operations."""
    
    def __init__(self, default_url="https://distributor.swiftness.co.il/he-IL/Account/Login#/"):
        """Initialize the browser launcher with a default URL."""
        self.default_url = default_url
    
    def open_chromium(self, url=None):
        """Open Chromium browser with the specified URL."""
        if url is None:
            url = self.default_url
            
        try:
            # Find Chromium installation
            chromium_path = find_chromium()
            
            if chromium_path:
                print(f"🚀 Opening Chromium from: {chromium_path}")
                # Use subprocess to directly launch Chromium
                subprocess.Popen([chromium_path, url])
                print(f"✅ Chromium opened successfully with URL: {url}")
                return True
            else:
                print("❌ Chromium not found, trying to use default browser...")
                return self._open_fallback_browser(url)
                
        except Exception as e:
            print(f"❌ Error opening Chromium: {e}")
            return self._open_fallback_browser(url)
    
    def _open_fallback_browser(self, url):
        """Open fallback browser when Chromium is not available."""
        try:
            # Try to unregister chrome and register chromium
            try:
                webbrowser.unregister('chrome')
            except:
                pass
            
            # Fallback to default browser
            webbrowser.open(url)
            print(f"✅ Default browser opened successfully with URL: {url}")
            return True
            
        except Exception as e:
            print(f"❌ Error opening default browser: {e}")
            return False
    
    def open_url(self, url):
        """Open any URL with the best available browser."""
        return self.open_chromium(url)
