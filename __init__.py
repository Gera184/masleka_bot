#!/usr/bin/env python3
"""
Masleka Bot - A Python project for opening Chromium browser.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "A Python project that opens Chromium browser programmatically"

from .browser_launcher import BrowserLauncher
from .browser_finder import find_chromium, get_system_info
from .utils import print_status, get_platform, validate_url
from .web_automation import WebAutomation

__all__ = [
    'BrowserLauncher',
    'find_chromium',
    'get_system_info',
    'print_status',
    'get_platform',
    'validate_url',
    'WebAutomation'
]
