#!/usr/bin/env python3
"""
SaverMyProducts processing module for client details automation.
Handles extraction, processing, and file management for client product data.

FLOW OVERVIEW:
=============

1. ENTRY POINT:
   - process_saver_products_with_navigation() - Main function called from external modules

2. DATA EXTRACTION PHASE:
   - SaverProductsExtractor.__init__() - Initialize extractor with driver and wait
   - SaverProductsExtractor.extract_saver_products_data() - Main extraction method
     ├── ElementFinder.wait_for_element() - Find SaverMyProducts element
     ├── SaverProductsExtractor._get_product_rows() - Get all product rows
     └── SaverProductsExtractor._process_all_product_rows() - Process each row
         └── ProductDataProcessor.process_product_row() - Process individual product
             ├── ProductDataProcessor._extract_product_name() - Get product name
             └── ProductDataProcessor._process_detail_boxes_with_policies() - Process detail boxes
                 ├── DetailBoxExtractor.extract_all_detail_box_data() - Extract box data
                 │   ├── DetailBoxExtractor._extract_basic_elements() - Extract div/span elements
                 │   ├── DetailBoxExtractor._extract_currency_elements() - Extract .shekel elements
                 │   ├── DetailBoxExtractor._extract_percentage_elements() - Extract .precentage elements
                 │   └── DetailBoxExtractor._extract_link_elements() - Extract anchor elements
                 └── ProductDataProcessor._get_policy_data_for_number() - Get policy data
                     ├── ProductDataProcessor._navigate_back_to_main_page() - Open new tab
                     ├── ProductDataProcessor._click_product_details_tab() - Click "פירוט מוצרים" tab
                     ├── ProductDataProcessor._find_policy_link_by_number() - Find policy link
                     └── ProductDataProcessor._click_specific_tabs() - Click policy tabs
                         ├── ProductDataProcessor._find_tab_by_text() - Find tab by text
                         ├── ProductDataProcessor._extract_liens_data() - Extract "שעבודים ועיקולים" data
                         └── ProductDataProcessor._extract_loans_data() - Extract "הלוואות" data

3. FILE SAVING PHASE:
   - DataFileManager.save_extracted_data() - Save extracted data to PDF file with Hebrew support

4. NAVIGATION & PDF DOWNLOAD PHASE:
   - NavigationHandler.__init__() - Initialize navigator
   - NavigationHandler.navigate_via_pdf_icon() - Handle PDF icon navigation
     ├── ElementFinder.wait_for_element() - Find PDF icon
     └── NavigationHandler._handle_pdf_download() - Handle PDF download
         ├── PDFManager.wait_for_new_pdf_download() - Wait for PDF download
         └── PDFManager.move_pdf_to_folder() - Move PDF to client folder

UTILITY CLASSES:
===============
- PDFManager: Handles PDF file operations (download monitoring, file movement)
- ElementFinder: Handles element finding and waiting operations
- DetailBoxExtractor: Handles extraction of data from detail boxes
- ProductDataProcessor: Handles processing of individual product data
- DataFileManager: Handles saving extracted data to files
- SaverProductsExtractor: Main class for extracting SaverMyProducts data
- NavigationHandler: Handles navigation operations including PDF icon clicking

EXECUTION ORDER:
===============
1. Extract SaverMyProducts data from current page
2. For each product row:
   a. Extract product name
   b. For each detail box in the row:
      - Extract all data from the box
      - If policy number found, navigate to policy details
      - Extract data from "שעבודים ועיקולים" and "הלוואות" tabs
3. Save all extracted data to PDF file with Hebrew text support
4. Navigate back via PDF icon and download PDF report
5. Move PDF to client-specific folder
"""

import time
import shutil
import logging
import functools
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import black, red, blue, green

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
DOWNLOAD_DIR = Path.home() / "Desktop" / "maslekot"
DEFAULT_TIMEOUT = 30
SLEEP_INTERVAL = 1
MAIN_PAGE_URL = (
    "https://distributor.swiftness.co.il/he-IL/MaintenanceInterface/MainPage"
)

# CSS Selectors - Pre-compiled for better performance
SELECTORS = {
    "saver_products": ".SaverMyProducts",
    "product_rows": "div[ng-repeat='item in GroupedData']",
    "product_name": "div.productName",
    "details_box": "div.details-box",
    "pdf_icon": 'input[type="image"][src="/Images/Icons/pdf-icon.png"][name="pdf"]',
    "policy_links": "a[ng-click='PolicyClicked(details)']",
    "product_details_tab": "li.k-item.k-state-default[role='tab'][aria-controls='tabstrip-2'] span.k-link",
    "liens_content": "#PolicyConfiscationContent",
    "loans_table": "table.PolicyLoanGrid",
    "tab_links": "li.k-item span.k-link",
    "currency_elements": ".shekel",
    "percentage_elements": ".precentage",
    "link_elements": "a",
    "basic_elements": "div, span",
}

# Hebrew text constants
HEBREW_TEXTS = {
    "product_details_tab": "פירוט מוצרים",
    "liens_tab": "שעבודים ועיקולים",
    "loans_tab": "הלוואות",
}


# Hebrew font configuration
def configure_hebrew_fonts():
    """Configure Hebrew fonts for PDF generation."""
    try:
        # Try to register Hebrew-supporting fonts in order of preference
        hebrew_fonts = [
            ("Arial", "arial.ttf"),  # Arial usually has Hebrew support
            ("Tahoma", "tahoma.ttf"),  # Tahoma has excellent Hebrew support
            ("Calibri", "calibri.ttf"),  # Calibri has good Hebrew support
            ("TimesNewRoman", "times.ttf"),  # Times New Roman has Hebrew support
        ]

        # Common font paths for Hebrew fonts
        font_paths = [
            "C:/Windows/Fonts/",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/times.ttf",
            "/System/Library/Fonts/",
            "/usr/share/fonts/truetype/",
            "/usr/share/fonts/TTF/",
        ]

        for font_name, font_file in hebrew_fonts:
            try:
                # Try different font file extensions
                font_extensions = [".ttf", ".otf", ""]

                for ext in font_extensions:
                    full_font_file = (
                        font_file
                        if font_file.endswith((".ttf", ".otf"))
                        else f"{font_file}{ext}"
                    )

                    for font_path in font_paths:
                        full_path = Path(font_path) / full_font_file
                        if full_path.exists():
                            try:
                                pdfmetrics.registerFont(
                                    TTFont(font_name, str(full_path))
                                )
                                logger.info(
                                    f"Registered Hebrew font: {font_name} from {full_path}"
                                )
                                return font_name
                            except Exception as font_error:
                                logger.debug(
                                    f"Failed to register {font_name}: {font_error}"
                                )
                                continue

            except Exception as e:
                logger.debug(f"Could not register font {font_name}: {e}")
                continue

        # If no Hebrew font found, use default
        logger.warning("No Hebrew font found, using default font")
        return "Helvetica"

    except Exception as e:
        logger.error(f"Error configuring Hebrew fonts: {e}")
        return "Helvetica"


def fix_hebrew_text_direction(text: str) -> str:
    """
    Fix Hebrew text direction and encoding for proper PDF display.

    Args:
        text: Input text that may contain Hebrew characters

    Returns:
        Text with proper Hebrew direction and encoding
    """
    try:
        # Ensure text is properly encoded
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="ignore")

        # Check if text contains Hebrew characters
        hebrew_chars = any("\u0590" <= char <= "\u05ff" for char in text)

        if hebrew_chars:
            # For Hebrew text, clean up any problematic direction markers
            text = text.strip()

            # Special handling for specific keys where only the key should be reversed, not the value
            special_keys = ["סהכ חסכון", "מספר פוליסה", "יתרה לתשלום"]

            for special_key in special_keys:
                if text.startswith(special_key + ":"):
                    # Split into key and value
                    key_part = special_key + ":"
                    value_part = text[len(key_part) :].strip()

                    # Only reverse the key part, keep value unchanged
                    reversed_key = key_part[::-1]
                    result = value_part + " " + reversed_key

                    print(f"DEBUG: Special key handling - Original: {repr(text)}")
                    print(f"DEBUG: Special key handling - Result: {repr(result)}")
                    return result

            # For all other Hebrew text, reverse the entire text
            text = text[::-1]
            print(f"DEBUG: Reversed Hebrew text: {repr(text)}")

        return text

    except Exception as e:
        logger.warning(f"Error fixing Hebrew text direction: {e}")
        return text


def is_hebrew_text(text: str) -> bool:
    """
    Check if text contains Hebrew characters.

    Args:
        text: Text to check

    Returns:
        True if text contains Hebrew characters, False otherwise
    """
    try:
        return any("\u0590" <= char <= "\u05ff" for char in text)
    except Exception:
        return False


def get_text_color_for_line(line: str) -> str:
    """
    Determine the color for a text line based on its content.

    Args:
        line: Text line to analyze

    Returns:
        Color name for the text
    """
    try:
        print(f"DEBUG: Analyzing line: '{line}'")

        # Check for specific Hebrew patterns that should be colored
        hebrew_patterns = {
            "שם חברה מנהלת": blue,  # Company name - blue
            "סך הכל חסכון": green,  # Total savings - green
            "סטטוס": black,  # Status - black (default)
        }

        print(
            f"DEBUG: Available colors - blue: {blue}, green: {green}, red: {red}, black: {black}"
        )

        # Check for patterns that should be red if answer is "כן" (Yes)
        red_condition_patterns = [
            "האם הוטל שיעבוד על הפוליסה/חשבון",
            "האם הוטל עיקול על הפוליסה/חשבון",
            "האם קיימת הלוואה",
        ]

        # Check for specific product types that should be red
        red_product_types = [
            "פנסיה ותיקה מקיפה",  # Old Comprehensive Pension
        ]

        # Check for specific product types that should be red
        for product_type in red_product_types:
            if product_type in line:
                print(f"DEBUG: Found red product type '{product_type}' - using red")
                return red

        # Check if line contains any of the red condition patterns
        for pattern in red_condition_patterns:
            if pattern in line:
                # If the line contains "כן" (Yes), make it red
                if "כן" in line:
                    print(
                        f"DEBUG: Found red pattern '{pattern}' with answer 'כן' - using red"
                    )
                    return red
                else:
                    # If it's not "כן", keep it black
                    print(
                        f"DEBUG: Found red pattern '{pattern}' but answer is not 'כן' - using black"
                    )
                    return black

        # Check for other Hebrew patterns (more flexible matching)
        for pattern, color in hebrew_patterns.items():
            if pattern in line:
                print(f"DEBUG: Found pattern '{pattern}' - using {color}")
                return color

        # Additional flexible pattern matching
        if "סטטוס" in line:
            print("DEBUG: Found 'סטטוס' pattern - using black")
            return black
        elif "סך הכל חסכון" in line or "סהכ חסכון" in line:
            print("DEBUG: Found savings pattern - using green")
            return green
        elif "שם חברה מנהלת" in line:
            print("DEBUG: Found company name pattern - using blue")
            return blue
        elif "פנסיה ותיקה מקיפה" in line:
            print("DEBUG: Found old comprehensive pension pattern - using red")
            return red

        # Default color
        print(f"DEBUG: No pattern found for line: {line[:50]}... - using black")
        return black

    except Exception as e:
        logger.warning(f"Error determining text color: {e}")
        return black


# Performance monitoring decorator
def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.2f} seconds: {e}"
            )
            raise

    return wrapper


# Performance optimization: Cache for frequently accessed elements
class ElementCache:
    """Simple cache for frequently accessed elements to improve performance."""

    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, WebElement] = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[WebElement]:
        """Get element from cache."""
        return self.cache.get(key)

    def set(self, key: str, element: WebElement) -> None:
        """Set element in cache with size limit."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = element

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()


class PDFManager:
    """Handles PDF file operations including download monitoring and file movement."""

    @staticmethod
    def wait_for_new_pdf_download(timeout: int = DEFAULT_TIMEOUT) -> Optional[Path]:
        """
        Wait for any new PDF file to appear in the download directory.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Path to the new PDF file or None if timeout
        """
        start_time = time.time()
        initial_files = set(DOWNLOAD_DIR.glob("*.pdf"))

        logger.info(f"Waiting for PDF download (timeout: {timeout}s)")

        while time.time() - start_time < timeout:
            current_files = set(DOWNLOAD_DIR.glob("*.pdf"))
            new_files = current_files - initial_files

            for file in new_files:
                if not file.name.endswith(".crdownload"):
                    logger.info(f"PDF download detected: {file}")
                    return file
            time.sleep(SLEEP_INTERVAL)

        logger.warning("PDF download timeout reached")
        return None

    @staticmethod
    def move_pdf_to_folder(
        pdf_file: Path, target_folder: Path, identification_number: str
    ) -> Optional[Path]:
        """Move a downloaded PDF to its specific folder."""
        if not pdf_file or not pdf_file.exists():
            return None

        try:
            # Create a unique filename to avoid conflicts
            timestamp = int(time.time())
            new_filename = f"דוח_מאוחד_{identification_number}_{timestamp}.pdf"
            target_path = target_folder / new_filename

            shutil.move(str(pdf_file), str(target_path))
            logger.info(f"✅ PDF moved to: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"❌ Error moving PDF: {e}")
            return None


class ElementFinder:
    """Handles element finding and waiting operations."""

    @staticmethod
    def wait_for_element(
        driver: WebDriver, by: By, value: str, timeout: int = DEFAULT_TIMEOUT
    ) -> Optional[WebElement]:
        """
        Wait for an element to be present on the page.

        Args:
            driver: Selenium WebDriver instance
            by: Selenium By strategy
            value: Element selector value
            timeout: Maximum time to wait in seconds

        Returns:
            WebElement or None if not found
        """
        try:
            wait = WebDriverWait(driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            logger.debug(f"Element found: {value}")
            return element
        except TimeoutException:
            logger.warning(f"Element not found within timeout: {value}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for element {value}: {e}")
            return None

    @staticmethod
    def find_elements_safe(
        driver: WebDriver, by: By, value: str, timeout: int = 5
    ) -> List[WebElement]:
        """
        Safely find multiple elements with timeout.

        Args:
            driver: Selenium WebDriver instance
            by: Selenium By strategy
            value: Element selector value
            timeout: Maximum time to wait in seconds

        Returns:
            List of WebElements (empty if none found)
        """
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.presence_of_element_located((by, value)))
            elements = driver.find_elements(by, value)
            logger.debug(f"Found {len(elements)} elements: {value}")
            return elements
        except TimeoutException:
            logger.debug(f"No elements found: {value}")
            return []
        except Exception as e:
            logger.error(f"Error finding elements {value}: {e}")
            return []


class DetailBoxExtractor:
    """Handles extraction of data from detail boxes."""

    @staticmethod
    def extract_all_detail_box_data(
        detail_box: WebElement, detail_index: int
    ) -> Dict[str, str]:
        """
        Extract ALL available data from a detail box by finding all elements with data.

        Args:
            detail_box: The detail box WebElement
            detail_index: Index of the detail box for logging

        Returns:
            Dictionary containing all extracted data
        """
        detail_data = {}

        try:
            # Extract all element types in parallel for better performance
            extraction_methods = [
                DetailBoxExtractor._extract_basic_elements,
                DetailBoxExtractor._extract_currency_elements,
                DetailBoxExtractor._extract_percentage_elements,
                DetailBoxExtractor._extract_link_elements,
            ]

            for method in extraction_methods:
                try:
                    method(detail_box, detail_data, detail_index)
                except Exception as method_error:
                    logger.warning(f"Error in {method.__name__}: {method_error}")

            logger.info(
                f"Detail box {detail_index + 1}: {len(detail_data)} data points extracted"
            )

        except Exception as e:
            logger.error(f"Error extracting detail box data: {e}")
            detail_data["Error"] = f"Failed to extract data: {e}"

        return detail_data

    @staticmethod
    def _extract_basic_elements(
        detail_box: WebElement, detail_data: Dict[str, str], detail_index: int
    ) -> None:
        """Extract data from basic div and span elements."""
        all_elements = detail_box.find_elements(
            By.CSS_SELECTOR, SELECTORS["basic_elements"]
        )
        logger.debug(
            f"Found {len(all_elements)} basic elements in detail box {detail_index + 1}"
        )

        for element_index, element in enumerate(all_elements):
            try:
                text = element.text.strip()
                if not text:
                    continue

                key = DetailBoxExtractor._generate_element_key(element, element_index)
                detail_data[key] = text
                logger.debug(f"Extracted: {key}: {text}")

            except Exception as element_error:
                logger.warning(
                    f"Error processing element {element_index}: {element_error}"
                )

    @staticmethod
    def _generate_element_key(element: WebElement, element_index: int) -> str:
        """Generate a meaningful key for an element based on its attributes."""
        element_name = element.get_attribute("name") or ""
        element_ng_bind = element.get_attribute("ng-bind") or ""
        element_class = element.get_attribute("class") or ""

        if element_name:
            key = element_name
        elif element_ng_bind:
            ng_bind_clean = element_ng_bind.replace(
                "details.vw_HoldingsShow_SavingProductsDetails.", ""
            )
            key = ng_bind_clean
        elif element_class and "ng-binding" in element_class:
            key = f"element_{element_index}"
        else:
            key = f"element_{element_index}"

        return key.replace(" ", "_").replace("-", "_")

    @staticmethod
    def _extract_currency_elements(
        detail_box: WebElement, detail_data: Dict[str, str], detail_index: int
    ) -> None:
        """Extract currency values from elements with shekel class."""
        try:
            currency_elements = detail_box.find_elements(
                By.CSS_SELECTOR, SELECTORS["currency_elements"]
            )
            for i, currency_elem in enumerate(currency_elements):
                try:
                    currency_text = currency_elem.text.strip()
                    if currency_text:
                        currency_name = (
                            currency_elem.get_attribute("name") or f"currency_{i}"
                        )
                        detail_data[currency_name] = currency_text
                        logger.debug(f"Currency: {currency_name}: {currency_text}")
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error extracting currency data: {e}")

    @staticmethod
    def _extract_percentage_elements(
        detail_box: WebElement, detail_data: Dict[str, str], detail_index: int
    ) -> None:
        """Extract percentage values from elements with precentage class."""
        try:
            percentage_elements = detail_box.find_elements(
                By.CSS_SELECTOR, SELECTORS["percentage_elements"]
            )
            for i, percent_elem in enumerate(percentage_elements):
                try:
                    percent_text = percent_elem.text.strip()
                    if percent_text:
                        percent_name = (
                            percent_elem.get_attribute("name") or f"percentage_{i}"
                        )
                        detail_data[percent_name] = percent_text
                        logger.debug(f"Percentage: {percent_name}: {percent_text}")
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error extracting percentage data: {e}")

    @staticmethod
    def _extract_link_elements(
        detail_box: WebElement, detail_data: Dict[str, str], detail_index: int
    ) -> None:
        """Extract link text from anchor elements."""
        try:
            link_elements = detail_box.find_elements(
                By.CSS_SELECTOR, SELECTORS["link_elements"]
            )
            for i, link_elem in enumerate(link_elements):
                try:
                    link_text = link_elem.text.strip()
                    if link_text:
                        link_name = link_elem.get_attribute("name") or f"link_{i}"
                        detail_data[link_name] = link_text
                        logger.debug(f"Link: {link_name}: {link_text}")
                except Exception:
                    continue
        except Exception as e:
            logger.warning(f"Error extracting link data: {e}")


class ProductDataProcessor:
    """Handles processing of individual product data."""

    @staticmethod
    def process_product_row(
        product_row: WebElement, row_index: int, total_rows: int, driver: WebDriver
    ) -> List[str]:
        """
        Process a single product row and extract all relevant data.

        Args:
            product_row: The product row WebElement
            row_index: Index of the current row
            total_rows: Total number of rows
            driver: WebDriver instance for navigation operations

        Returns:
            List of extracted data strings
        """
        extracted_data = []

        try:
            print(f"\n🔄 Processing product row {row_index + 1}/{total_rows}")

            # Extract product name
            product_name = ProductDataProcessor._extract_product_name(
                product_row, row_index
            )
            print(f"📋 Product: {product_name}")

            # Add product header
            extracted_data.append(f"*{product_name}*")
            extracted_data.append(" ")  # Add space after product name

            # Process each detail box individually with its policy data
            detail_boxes_data = (
                ProductDataProcessor._process_detail_boxes_with_policies(
                    product_row, driver
                )
            )
            extracted_data.extend(detail_boxes_data)

            # Add separator
            # extracted_data.extend(["", "=" * 60, ""])

        except Exception as row_error:
            print(f"❌ Error processing product row {row_index + 1}: {row_error}")
            extracted_data.extend(
                [f"PRODUCT {row_index + 1}: ERROR - {row_error}", "=" * 60, ""]
            )

        return extracted_data

    @staticmethod
    def _extract_product_name(product_row: WebElement, row_index: int) -> str:
        """Extract the product name from a product row."""
        try:
            product_name_element = product_row.find_element(
                By.CSS_SELECTOR, SELECTORS["product_name"]
            )
            return (
                product_name_element.text
                if product_name_element
                else f"Product {row_index + 1}"
            )
        except Exception as e:
            logger.warning(f"Error extracting product name: {e}")
            return f"Product {row_index + 1}"

    @staticmethod
    def _navigate_back_to_main_page(driver: WebDriver) -> str:
        """
        Open the main page URL in a new tab.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            New window handle if successful, None otherwise
        """
        try:
            print("🔄 Opening main page in new tab...")

            # Store the current window handle
            original_window = driver.current_window_handle

            # Open new tab
            driver.execute_script("window.open('');")

            # Switch to the new tab
            new_window = None
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    new_window = window_handle
                    break

            if not new_window:
                print("    ❌ Could not find new tab")
                return None

            # Switch to new tab
            driver.switch_to.window(new_window)

            # Navigate to the main page URL in the new tab
            driver.get(MAIN_PAGE_URL)

            logger.info(f"Opened main page in new tab: {MAIN_PAGE_URL}")

            return new_window

        except Exception as e:
            print(f"❌ Error opening main page in new tab: {e}")
            # Try to switch back to original window if there was an error
            try:
                if "original_window" in locals():
                    driver.switch_to.window(original_window)
            except Exception:
                pass
            return None

    @staticmethod
    def _find_policy_link_by_number(
        driver: WebDriver, policy_number: str
    ) -> Optional[WebElement]:
        """
        Find a policy link element by its policy number in the current tab.

        Args:
            driver: Selenium WebDriver instance
            policy_number: The policy number to search for

        Returns:
            WebElement if found, None otherwise
        """
        try:
            print(f"🔍 Looking for policy link with number: {policy_number}")

            # Find all policy links in the current tab
            policy_links = driver.find_elements(
                By.CSS_SELECTOR, SELECTORS["policy_links"]
            )

            logger.info(f"Found {len(policy_links)} policy links in new tab")

            # Look for the policy link with the matching number
            for link in policy_links:
                link_text = link.text.strip()
                if link_text == policy_number:
                    print(f"    ✅ Found policy link: {policy_number}")
                    return link

            print(f"❌ Policy link with number {policy_number} not found")
            return None

        except Exception as e:
            print(f"❌ Error finding policy link: {e}")
            return None

    @staticmethod
    def _click_product_details_tab(driver: WebDriver) -> bool:
        """
        Find and click on the "פירוט מוצרים" (Product Details) tab.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            True if successful, False otherwise
        """
        try:
            print("🔍 Looking for 'פירוט מוצרים' tab...")

            # Try multiple selectors to find the element
            selectors = [
                SELECTORS["product_details_tab"],
                "li.k-item[aria-controls='tabstrip-2'] span.k-link",
                "li.k-item.k-state-default[role='tab'] span.k-link",
                "li.k-item span.k-link",
                "span.k-link",
                "li[role='tab'] span.k-link",
            ]

            # Try to find the element with the Hebrew text
            target_text = HEBREW_TEXTS["product_details_tab"]

            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(
                        f"🔍 Found {len(elements)} elements with selector: {selector}"
                    )

                    for element in elements:
                        element_text = element.text.strip()
                        print(f"📝 Element text: '{element_text}'")

                        if target_text in element_text:
                            print(
                                f"✅ Found target element with text: '{element_text}'"
                            )

                            # Click the element
                            driver.execute_script("arguments[0].click();", element)
                            print("✅ Clicked on 'פירוט מוצרים' tab")

                            # Wait for policy links to be available after tab click
                            try:
                                wait = WebDriverWait(driver, 60)
                                wait.until(
                                    EC.presence_of_element_located(
                                        (By.CSS_SELECTOR, SELECTORS["policy_links"])
                                    )
                                )
                                print("✅ Policy links are now available")
                            except TimeoutException:
                                print(
                                    "⚠️ Timeout waiting for policy links, but continuing..."
                                )

                            return True

                except Exception as selector_error:
                    print(f"⚠️ Error with selector '{selector}': {selector_error}")
                    continue

            print(f"❌ Could not find element with text: '{target_text}'")
            return False

        except Exception as e:
            print(f"❌ Error clicking 'פירוט מוצרים' tab: {e}")
            return False

    @staticmethod
    def _process_detail_boxes_with_policies(
        product_row: WebElement, driver: WebDriver
    ) -> List[str]:
        """
        Process each detail box individually and include its policy data right after it.
        This ensures the data is organized in the correct format.

        Args:
            product_row: The product row WebElement
            driver: WebDriver instance for navigation

        Returns:
            List of extracted data strings organized by detail box
        """
        all_data = []

        try:
            details_boxes = product_row.find_elements(
                By.CSS_SELECTOR, SELECTORS["details_box"]
            )

            for detail_index, detail_box in enumerate(details_boxes):
                try:
                    print(
                        f"🔍 Processing detail box {detail_index + 1} with policy data"
                    )

                    # Extract basic detail box information
                    box_data = DetailBoxExtractor.extract_all_detail_box_data(
                        detail_box, detail_index
                    )

                    # Add detail box information
                    for key, value in box_data.items():
                        if key == "element_0":
                            all_data.append(f"שם חברה מנהלת: {value}")
                        elif key == f"productTypeName{detail_index}":
                            all_data.append(f"סוג מוצר: {value}")
                        elif key == f"poliyStatusName{detail_index}":
                            all_data.append(f"סטטוס: {value}")
                        elif key == "element_11":
                            all_data.append(f"סהכ חסכון: {value}")

                    # Check if this detail box has a policy number and get its data
                    if "element_4" in box_data:
                        policy_number = box_data["element_4"]
                        print(f"🔍 Found policy number: {policy_number}")

                        # Get policy data for this specific policy
                        policy_data = ProductDataProcessor._get_policy_data_for_number(
                            driver, policy_number
                        )

                        if policy_data:
                            all_data.extend(policy_data)
                            print(f"✅ Added policy data for {policy_number}")

                    # Add empty line for separation between detail boxes
                    all_data.append("")

                except Exception as detail_error:
                    print(
                        f"⚠️ Error processing detail box {detail_index + 1}: {detail_error}"
                    )
                    all_data.append(
                        f"Detail Box {detail_index + 1}: ERROR - {detail_error}"
                    )
                    all_data.append("")

        except Exception as e:
            print(f"⚠️ Error processing detail boxes with policies: {e}")
            all_data.append("DETAILS: ERROR - Failed to extract")

        return all_data

    @staticmethod
    def _get_policy_data_for_number(driver: WebDriver, policy_number: str) -> List[str]:
        """
        Get policy data for a specific policy number.

        Args:
            driver: WebDriver instance for navigation
            policy_number: The policy number to get data for

        Returns:
            List of extracted data strings for the policy
        """
        policy_data = []

        try:
            # Navigate to main page and find policy link
            new_window = ProductDataProcessor._navigate_back_to_main_page(driver)
            if new_window:
                if ProductDataProcessor._click_product_details_tab(driver):
                    policy_link = ProductDataProcessor._find_policy_link_by_number(
                        driver, policy_number
                    )
                    if policy_link:
                        print(f"✅ Found and clicked policy link for: {policy_number}")
                        policy_link.click()

                        # Add policy header
                        policy_data.append(f"מספר פוליסה: {policy_number}")

                        # Click on specific tabs and extract data
                        tabs_data = ProductDataProcessor._click_specific_tabs(driver)
                        policy_data.extend(tabs_data)

                        # Close the current tab and switch back to the original tab
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        print("✅ Returned to original tab")
                    else:
                        # Close tab and return to original if policy link not found
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                else:
                    # Close tab and return to original if tab click failed
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            else:
                print(f"⚠️ Could not open new tab for policy {policy_number}")

        except Exception as e:
            print(f"⚠️ Error getting policy data for {policy_number}: {e}")
            # Try to return to original window if there was an error
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except Exception:
                pass

        return policy_data

    @staticmethod
    def _wait_for_table_data_loaded(driver: WebDriver, timeout: int = 60) -> bool:
        """
        Wait for table data to be fully loaded by checking for various indicators.

        Args:
            driver: WebDriver instance
            timeout: Maximum time to wait in seconds

        Returns:
            True if data is loaded, False if timeout
        """
        try:
            print("⏳ Waiting for table data to be fully loaded...")

            wait = WebDriverWait(driver, timeout)

            # Wait for any loading indicators to disappear
            try:
                # Check for common loading indicators and wait for them to disappear
                loading_selectors = [
                    "div[class*='loading']",
                    "div[class*='spinner']",
                    "div[class*='loader']",
                    "img[src*='loading']",
                    "img[src*='spinner']",
                    ".k-loading-mask",
                    ".loading-overlay",
                ]

                for selector in loading_selectors:
                    try:
                        loading_elements = driver.find_elements(
                            By.CSS_SELECTOR, selector
                        )
                        if loading_elements:
                            print(f"    🔍 Found loading indicator: {selector}")
                            # Wait for loading elements to be hidden or removed
                            wait.until(
                                EC.invisibility_of_element_located(
                                    (By.CSS_SELECTOR, selector)
                                )
                            )
                            print(f"    ✅ Loading indicator disappeared: {selector}")
                    except TimeoutException:
                        # Loading indicator might not exist, continue
                        pass
                    except Exception:
                        # Other exceptions, continue
                        pass

            except Exception as e:
                print(f"⚠️ Error checking loading indicators: {e}")

            # Wait for table content to be present and populated
            try:
                # Wait for at least one data row to be present
                wait.until(
                    lambda driver: len(
                        driver.find_elements(By.CSS_SELECTOR, "tbody tr, div.row-fluid")
                    )
                    > 0
                )
                print("    ✅ Found data rows")

                # Additional wait to ensure data is fully rendered
                time.sleep(2)

                # Check if rows have actual content (not just empty cells)
                rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr, div.row-fluid")
                if rows:
                    # Wait for at least one row to have meaningful content
                    wait.until(
                        lambda driver: any(
                            row.find_elements(By.CSS_SELECTOR, "td, div")
                            and any(
                                cell.text.strip()
                                for cell in row.find_elements(
                                    By.CSS_SELECTOR, "td, div"
                                )
                            )
                            for row in driver.find_elements(
                                By.CSS_SELECTOR, "tbody tr, div.row-fluid"
                            )
                        )
                    )
                    print("    ✅ Data rows contain content")

            except TimeoutException:
                print("    ⚠️ Timeout waiting for table data to load")
                return False
            except Exception as e:
                print(f"    ⚠️ Error waiting for table data: {e}")
                return False

            print("    ✅ Table data is fully loaded")
            return True

        except Exception as e:
            print(f"    ⚠️ Error in _wait_for_table_data_loaded: {e}")
            return False

    @staticmethod
    def _click_specific_tabs(driver: WebDriver) -> List[str]:
        """
        Click on specific tabs: שעבודים ועיקולים (Liens and Foreclosures) and הלוואות (Loans).
        Extract data from both tabs and return it for inclusion in the text file.

        Args:
            driver: WebDriver instance for navigation

        Returns:
            List of extracted data strings from both tabs
        """
        extracted_data = []

        try:
            print("🔍 Looking for specific tabs to click...")

            # Wait for the page to load
            time.sleep(3)

            # Click on שעבודים ועיקולים tab (Liens and Foreclosures)
            print("🔍 Looking for 'שעבודים ועיקולים' tab...")
            liens_tab = ProductDataProcessor._find_tab_by_text(
                driver, "שעבודים ועיקולים"
            )
            if liens_tab:
                print("✅ Found 'שעבודים ועיקולים' tab, clicking...")
                driver.execute_script("arguments[0].click();", liens_tab)
                print("✅ Clicked on 'שעבודים ועיקולים' tab")

                # Wait for table data to be fully loaded
                if ProductDataProcessor._wait_for_table_data_loaded(driver):
                    print("✅ Table data loaded for 'שעבודים ועיקולים' tab")
                    # Extract data from שעבודים ועיקולים tab
                    liens_data = ProductDataProcessor._extract_liens_data(driver)
                    extracted_data.extend(liens_data)
                else:
                    print(
                        "⚠️ Timeout waiting for 'שעבודים ועיקולים' table data, proceeding anyway..."
                    )
                    liens_data = ProductDataProcessor._extract_liens_data(driver)
                    extracted_data.extend(liens_data)
            else:
                print("❌ 'שעבודים ועיקולים' tab not found")

            # Click on הלוואות tab (Loans)
            print("🔍 Looking for 'הלוואות' tab...")
            loans_tab = ProductDataProcessor._find_tab_by_text(driver, "הלוואות")
            if loans_tab:
                print("✅ Found 'הלוואות' tab, clicking...")
                driver.execute_script("arguments[0].click();", loans_tab)
                print("✅ Clicked on 'הלוואות' tab")

                # Wait for table data to be fully loaded
                if ProductDataProcessor._wait_for_table_data_loaded(driver):
                    print("✅ Table data loaded for 'הלוואות' tab")
                    # Extract data from הלוואות tab
                    loans_data = ProductDataProcessor._extract_loans_data(driver)
                    extracted_data.extend(loans_data)
                else:
                    print(
                        "⚠️ Timeout waiting for 'הלוואות' table data, proceeding anyway..."
                    )
                    loans_data = ProductDataProcessor._extract_loans_data(driver)
                    extracted_data.extend(loans_data)
            else:
                print("❌ 'הלוואות' tab not found")

        except Exception as e:
            print(f"⚠️ Error clicking specific tabs: {e}")

        return extracted_data

    @staticmethod
    def _extract_liens_data(driver: WebDriver) -> List[str]:
        """
        Extract data from the שעבודים ועיקולים (Liens and Foreclosures) tab.

        Args:
            driver: WebDriver instance

        Returns:
            List of extracted data strings
        """
        extracted_data = []

        try:
            print("🔍 Extracting data from 'שעבודים ועיקולים' tab...")

            # Wait for table data to be fully loaded before extracting
            if not ProductDataProcessor._wait_for_table_data_loaded(driver, timeout=60):
                print(
                    "⚠️ Timeout waiting for liens table data, proceeding with extraction..."
                )

            # Look for the PolicyConfiscationContent div
            liens_content = driver.find_element(
                By.CSS_SELECTOR, SELECTORS["liens_content"]
            )
            if liens_content:
                print("✅ Found liens content section")

                # Add section header
                extracted_data.append("")
                extracted_data.append("שעבודים ועיקולים")

                # Extract all row-fluid divs
                rows = liens_content.find_elements(By.CSS_SELECTOR, "div.row-fluid")

                for row in rows:
                    try:
                        # Find label and value elements
                        label_elem = row.find_element(
                            By.CSS_SELECTOR, "div.boldStyle label"
                        )
                        value_elem = row.find_element(
                            By.CSS_SELECTOR, "div:not(.boldStyle)"
                        )

                        if label_elem and value_elem:
                            label_text = label_elem.text.strip()
                            value_text = value_elem.text.strip()

                            if label_text and value_text:
                                extracted_data.append(f"    {label_text}: {value_text}")
                                print(f"    ✅ Extracted: {label_text}: {value_text}")

                    except Exception as row_error:
                        print(f"⚠️ Error processing row: {row_error}")
                        continue

                print(f"📋 Total liens data points extracted: {len(extracted_data)}")
            else:
                print("❌ Liens content section not found")

        except Exception as e:
            print(f"⚠️ Error extracting liens data: {e}")
            extracted_data.append("ERROR - Failed to extract data")

        return extracted_data

    @staticmethod
    def _extract_loans_data(driver: WebDriver) -> List[str]:
        """
        Extract data from the הלוואות (Loans) tab.

        Args:
            driver: WebDriver instance

        Returns:
            List of extracted data strings
        """
        extracted_data = []

        try:
            print("🔍 Extracting data from 'הלוואות' tab...")

            # Wait for table data to be fully loaded before extracting
            if not ProductDataProcessor._wait_for_table_data_loaded(driver, timeout=60):
                print(
                    "⚠️ Timeout waiting for loans table data, proceeding with extraction..."
                )

            # Look for the PolicyLoanGrid table
            loans_table = driver.find_element(By.CSS_SELECTOR, SELECTORS["loans_table"])
            if loans_table:
                print("✅ Found loans table")

                # Add section header
                extracted_data.append("")
                extracted_data.append("הלוואות")

                # Extract table headers
                headers = []
                header_elements = loans_table.find_elements(
                    By.CSS_SELECTOR, "thead th.k-header"
                )
                for header in header_elements:
                    header_text = header.text.strip()
                    if header_text:
                        headers.append(header_text)

                print(f"📊 Table headers: {headers}")

                # Extract table rows data
                rows = loans_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                print(f"📊 Found {len(rows)} loan rows")

                for row_index, row in enumerate(rows):
                    try:
                        cells = row.find_elements(By.CSS_SELECTOR, "td")
                        row_data = []

                        for cell_index, cell in enumerate(cells):
                            cell_text = cell.text.strip()
                            if cell_text and cell_index < len(headers):
                                if headers[cell_index] == "האם קיימת הלוואה":
                                    row_data.append(
                                        f"{headers[cell_index]}: {cell_text}"
                                    )

                                if headers[cell_index] == "יתרה לתשלום (₪)":
                                    clean_header = headers[cell_index].replace(
                                        " (₪)", ""
                                    )
                                    row_data.append(f"{clean_header}: {cell_text}")

                        if row_data:
                            extracted_data.extend([f"{item}" for item in row_data])
                            extracted_data.append("")  # Empty line for separation

                    except Exception as row_error:
                        print(
                            f"    ⚠️ Error processing loan row {row_index + 1}: {row_error}"
                        )
                        continue

                print(f"📋 Total loans data points extracted: {len(extracted_data)}")
            else:
                print("❌ Loans table not found")

        except Exception as e:
            print(f"⚠️ Error extracting loans data: {e}")
            extracted_data.append("    ERROR - Failed to extract data")

        return extracted_data

    @staticmethod
    def _store_tabs_data(tabs_data: List[str]) -> None:
        """
        Store the extracted tabs data for later inclusion in the text file.
        This is a simple storage mechanism that can be extended later.

        Args:
            tabs_data: List of extracted data strings from tabs
        """
        try:
            # For now, we'll just print the data
            # In a future implementation, this could store to a class variable
            # or pass the data back through the call chain
            if tabs_data:
                print("📋 Extracted tabs data:")
                for data_item in tabs_data:
                    print(f"{data_item}")
            else:
                print("📋 No tabs data extracted")

        except Exception as e:
            print(f"⚠️ Error storing tabs data: {e}")

    @staticmethod
    def _find_tab_by_text(driver: WebDriver, tab_text: str) -> Optional[WebElement]:
        """
        Find a tab element by its text content.

        Args:
            driver: WebDriver instance
            tab_text: The text to search for in the tab

        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Look for tabs with the specific text
            tab_elements = driver.find_elements(By.CSS_SELECTOR, SELECTORS["tab_links"])

            for tab in tab_elements:
                if tab_text in tab.text.strip():
                    print(f"    ✅ Found tab with text: '{tab.text.strip()}'")
                    return tab

            print(f"    ❌ Tab with text '{tab_text}' not found")
            return None

        except Exception as e:
            print(f"    ⚠️ Error finding tab with text '{tab_text}': {e}")
            return None

    @staticmethod
    def _collect_detail_box_values(product_row: WebElement) -> Dict[str, str]:
        """Collect and merge raw key/value pairs from all detail boxes for a product row."""
        merged: Dict[str, str] = {}
        try:
            details_boxes = product_row.find_elements(
                By.CSS_SELECTOR, SELECTORS["details_box"]
            )
            for detail_index, detail_box in enumerate(details_boxes):
                try:
                    box_data = DetailBoxExtractor.extract_all_detail_box_data(
                        detail_box, detail_index
                    )
                    merged.update(box_data)
                except Exception:
                    continue
        except Exception:
            pass
        return merged


class DataFileManager:
    """Handles saving extracted data to PDF files."""

    @staticmethod
    def save_extracted_data(
        extracted_data: List[str],
        identification_folder: Path,
        identification_number: str,
    ) -> bool:
        """
        Save extracted data to a PDF file with Hebrew text support.

        Args:
            extracted_data: List of data strings to save
            identification_folder: Folder to save the file in
            identification_number: Client identification number

        Returns:
            True if successful, False otherwise
        """
        timestamp = int(time.time())
        filename = f"עיקולים_הלוואות{identification_number}_{timestamp}.pdf"
        file_path = identification_folder / filename

        try:
            # Configure Hebrew fonts
            hebrew_font = configure_hebrew_fonts()
            print(f"DEBUG: Using font: {hebrew_font}")

            # Create PDF document
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Define styles for Hebrew text
            styles = getSampleStyleSheet()

            # Header style - try left alignment for Hebrew text
            header_style = ParagraphStyle(
                "HebrewHeader",
                parent=styles["Heading2"],
                fontName=hebrew_font,
                fontSize=18,  # Increased from 14 to 18
                alignment=TA_RIGHT,  # Try left alignment instead of right
                spaceAfter=12,
                spaceBefore=12,
                fontWeight="bolder",  # Added bold weight
                leading=12,  # Line height for better readability
            )

            # Normal text style - try left alignment for Hebrew text
            normal_style = ParagraphStyle(
                "HebrewNormal",
                parent=styles["Normal"],
                fontName=hebrew_font,
                fontSize=10,
                alignment=TA_RIGHT,  # Try left alignment instead of right
                spaceAfter=6,
                textColor=black,  # Default color
                leading=12,  # Line height for better readability
            )

            # Build PDF content
            story = []

            # Process and add data
            for line in extracted_data:
                if not line.strip():
                    story.append(Spacer(1, 6))
                    continue

                # Check if line is a header (starts with *)
                if line.startswith("*") and line.endswith("*"):
                    # Remove asterisks and format as header
                    header_text = line[1:-1]

                    # Determine color for header BEFORE fixing text direction
                    header_color = get_text_color_for_line(header_text)

                    # Fix Hebrew text direction
                    header_text = fix_hebrew_text_direction(header_text)

                    # Create dynamic header style with color
                    dynamic_header_style = ParagraphStyle(
                        "DynamicHeaderStyle",
                        parent=header_style,
                        textColor=header_color,
                        fontWeight="bolder",
                        fontSize=20,  # Increased from 16 to 20 for even bigger product names
                        leading=12,  # Line height for product names
                    )

                    story.append(Paragraph(header_text, dynamic_header_style))
                elif line.startswith("="):
                    # Skip separator lines
                    continue
                else:
                    # Regular text line
                    # Determine color BEFORE fixing text direction (so patterns match)
                    text_color = get_text_color_for_line(line)

                    # Fix Hebrew text direction
                    fixed_line = fix_hebrew_text_direction(line)
                    # Escape special characters for PDF
                    escaped_line = DataFileManager._escape_text_for_pdf(fixed_line)

                    # Create dynamic style with the determined color
                    dynamic_style = ParagraphStyle(
                        "DynamicStyle",
                        parent=normal_style,
                        textColor=text_color,
                        leading=12,  # Line height for regular text
                    )

                    story.append(Paragraph(escaped_line, dynamic_style))

            # Build PDF
            doc.build(story)

            print(f"✅ SaverMyProducts data saved to PDF: {file_path}")
            return True

        except Exception as save_error:
            print(f"❌ Error saving data to PDF file: {save_error}")
            return False

    @staticmethod
    def _escape_text_for_pdf(text: str) -> str:
        """
        Escape special characters for PDF generation while preserving Hebrew text.

        Args:
            text: Text to escape

        Returns:
            Escaped text safe for PDF
        """
        try:
            # Ensure text is properly encoded as UTF-8
            if isinstance(text, bytes):
                text = text.decode("utf-8", errors="ignore")

            # Replace special characters that might cause issues in PDF
            replacements = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#x27;",
            }

            for char, replacement in replacements.items():
                text = text.replace(char, replacement)

            # Ensure Hebrew text is properly handled
            if is_hebrew_text(text):
                # Remove any problematic characters that might interfere with Hebrew rendering
                text = text.replace("\u200e", "")  # Left-to-right mark
                text = text.replace("\u200f", "")  # Right-to-left mark
                text = text.replace("\u202e", "")  # RTL override
                text = text.replace("\u202d", "")  # LTR override

            return text

        except Exception as e:
            logger.warning(f"Error escaping text for PDF: {e}")
            return str(text)


class SaverProductsExtractor:
    """Main class for extracting SaverMyProducts data."""

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait

    def extract_saver_products_data(
        self, identification_folder: Path, identification_number: str
    ) -> bool:
        """
        Extract data from SaverMyProducts element and save to text file.

        Args:
            identification_folder: Path to the folder where data should be saved
            identification_number: The identification number being processed

        Returns:
            True if successful, False otherwise
        """
        try:
            print("🔍 Looking for SaverMyProducts element...")

            saver_products = ElementFinder.wait_for_element(
                self.driver,
                By.CSS_SELECTOR,
                SELECTORS["saver_products"],
                timeout=DEFAULT_TIMEOUT,
            )

            if not saver_products:
                print("❌ SaverMyProducts element not found")
                return False

            print("✅ Found SaverMyProducts element")

            # Extract product rows
            product_rows = self._get_product_rows(saver_products)
            if not product_rows:
                print("❌ No product rows found")
                return False

            # Process all product rows
            extracted_data = self._process_all_product_rows(
                product_rows, identification_number
            )

            # Save data to file
            return DataFileManager.save_extracted_data(
                extracted_data, identification_folder, identification_number
            )

        except Exception as saver_error:
            print(f"❌ Error processing SaverMyProducts: {saver_error}")
            return False

    def _get_product_rows(self, saver_products: WebElement) -> List[WebElement]:
        """Get all product rows from the SaverMyProducts element."""
        try:
            product_rows = saver_products.find_elements(
                By.CSS_SELECTOR, SELECTORS["product_rows"]
            )
            logger.info(f"Found {len(product_rows)} product rows in SaverMyProducts")
            return product_rows
        except Exception as e:
            logger.error(f"Error getting product rows: {e}")
            return []

    def _process_all_product_rows(
        self, product_rows: List[WebElement], identification_number: str
    ) -> List[str]:
        """Process all product rows and collect extracted data."""
        extracted_data: List[str] = []

        for row_index, product_row in enumerate(product_rows):
            row_data = ProductDataProcessor.process_product_row(
                product_row, row_index, len(product_rows), self.driver
            )
            extracted_data.extend(row_data)

        return extracted_data

    def _create_header_data(
        self, identification_number: str, total_products: int
    ) -> List[str]:
        """Create header data for the extracted file."""
        return [
            f"=== SAVER PRODUCTS DATA FOR ID: {identification_number} ===",
            f"Extraction Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Products Found: {total_products}",
            "=" * 60,
            "",
        ]


class NavigationHandler:
    """Handles navigation operations including PDF icon clicking."""

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def navigate_via_pdf_icon(
        self, identification_folder: Path, identification_number: str
    ) -> bool:
        """
        Navigate back to the main page using PDF icon and handle PDF download.

        Args:
            identification_folder: Folder to save downloaded PDF
            identification_number: Client identification number

        Returns:
            True if successful, False otherwise
        """
        try:
            print("🔍 Looking for PDF icon to navigate back...")

            pdf_icon = ElementFinder.wait_for_element(
                self.driver,
                By.CSS_SELECTOR,
                SELECTORS["pdf_icon"],
                timeout=DEFAULT_TIMEOUT,
            )

            if not pdf_icon:
                print("❌ PDF icon not found for navigation")
                return False

            # Click PDF icon
            self.driver.execute_script("arguments[0].click();", pdf_icon)
            print("✅ PDF icon clicked for navigation")

            # Handle PDF download
            return self._handle_pdf_download(
                identification_folder, identification_number
            )

        except Exception as e:
            print(f"❌ Error in navigation via PDF icon: {e}")
            return False

    def _handle_pdf_download(
        self, identification_folder: Path, identification_number: str
    ) -> bool:
        """Handle PDF download and file movement."""
        try:
            print("⏳ Waiting for PDF download...")
            downloaded_pdf = PDFManager.wait_for_new_pdf_download(
                timeout=DEFAULT_TIMEOUT
            )

            if not downloaded_pdf:
                print("❌ PDF download not detected")
                return False

            moved_pdf = PDFManager.move_pdf_to_folder(
                downloaded_pdf, identification_folder, identification_number
            )

            if moved_pdf:
                print(f"✅ PDF saved to client folder: {moved_pdf}")
                time.sleep(2)  # Wait for any response
                return True
            else:
                print("❌ Failed to move PDF to client folder")
                return False

        except Exception as e:
            print(f"❌ Error handling PDF download: {e}")
            return False


def process_saver_products_with_navigation(
    driver: WebDriver,
    wait: WebDriverWait,
    identification_folder: Path,
    identification_number: str,
) -> bool:
    """
    Main function to process SaverMyProducts data and handle PDF icon navigation.

    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        identification_folder: Path to the folder where data should be saved
        identification_number: The identification number being processed

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Starting SaverMyProducts processing for ID: {identification_number}")

    try:
        # Extract SaverMyProducts data
        extractor = SaverProductsExtractor(driver, wait)
        success = extractor.extract_saver_products_data(
            identification_folder, identification_number
        )

        if not success:
            logger.warning(
                "Failed to extract SaverMyProducts data, but continuing with navigation"
            )

        # Handle navigation
        navigator = NavigationHandler(driver)
        navigation_success = navigator.navigate_via_pdf_icon(
            identification_folder, identification_number
        )

        logger.info(
            f"SaverMyProducts processing completed for ID: {identification_number}"
        )
        return navigation_success

    except Exception as e:
        logger.error(f"Error in process_saver_products_with_navigation: {e}")
        return False
