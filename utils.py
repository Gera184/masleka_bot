#!/usr/bin/env python3
"""
Utilities module for common helper functions.
"""

import sys
import os
from config import MESSAGES


def print_status(message_key, *args):
    """Print a formatted status message."""
    message = MESSAGES.get(message_key, message_key)
    if args:
        print(message.format(*args))
    else:
        print(message)


def get_platform():
    """Get the current platform."""
    return sys.platform


def is_windows():
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_macos():
    """Check if running on macOS."""
    return sys.platform == "darwin"


def is_linux():
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


def get_username():
    """Get the current username."""
    return os.getenv('USERNAME') or os.getenv('USER')


def format_path_with_username(path_template):
    """Format a path template with the current username."""
    username = get_username()
    return path_template.format(username) if username else path_template


def validate_url(url):
    """Basic URL validation."""
    if not url:
        return False
    
    # Simple validation - check if it starts with http:// or https://
    return url.startswith(('http://', 'https://'))


def safe_file_exists(file_path):
    """Safely check if a file exists."""
    try:
        return os.path.exists(file_path)
    except (OSError, ValueError):
        return False
