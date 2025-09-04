#!/usr/bin/env python3
"""
Client Details Automation Package

This package contains modules for processing client details and financial products data.
"""

from .saver_products_processor import (
    extract_saver_products_data,
    process_saver_products_with_navigation,
    wait_for_element
)

__all__ = [
    'extract_saver_products_data',
    'process_saver_products_with_navigation', 
    'wait_for_element'
]

__version__ = '1.0.0'
__author__ = 'Automation Team'
