#!/usr/bin/env python3
"""
Configuration module for the browser opener project.
"""

# Default URLs
DEFAULT_URL = "https://distributor.swiftness.co.il/he-IL/Account/Login#/"
FALLBACK_URL = "https://www.google.com"

# Browser names
CHROMIUM_NAME = "Chromium"
DEFAULT_BROWSER_NAME = "Default Browser"

# Status messages
MESSAGES = {
    'start': "🚀 Starting Python project...",
    'looking': "🌐 Looking for Chromium browser...",
    'success': "✅ Project started successfully!",
    'chromium_found': "Found Chromium at: {}",
    'chromium_opening': "🚀 Opening Chromium from: {}",
    'chromium_success': "✅ Chromium opened successfully with URL: {}",
    'chromium_not_found': "❌ Chromium not found, trying to use default browser...",
    'fallback_success': "✅ Default browser opened successfully with URL: {}",
    'error_chromium': "❌ Error opening Chromium: {}",
    'error_fallback': "❌ Error opening default browser: {}",
    'trying_fallback': "Trying to open default browser..."
}

# File paths for different platforms
CHROMIUM_PATHS = {
    'win32': [
        r"C:\Program Files\Chromium\Application\chrome.exe",
        r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Chromium\Application\chrome.exe",
        r"C:\Users\{}\AppData\Roaming\Chromium\Application\chrome.exe",
        r"C:\chromium\chrome.exe",
        r"C:\Program Files\chromium\chrome.exe",
        r"C:\Program Files (x86)\chromium\chrome.exe"
    ],
    'darwin': [
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser"
    ],
    'linux': [
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/snap/bin/chromium",
        "/usr/bin/google-chromium"
    ]
}
