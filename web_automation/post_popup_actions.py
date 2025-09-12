#!/usr/bin/env python3
"""
Post-popup actions module for web automation.
Optimized for better performance, maintainability, and error handling.
"""

import time
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from .page_operations import wait_for_element
import sys

# Configuration constants
DOWNLOAD_DIR = Path.home() / "Desktop" / "maslekot"
DEFAULT_TIMEOUT = 30
SHORT_TIMEOUT = 10
LONG_TIMEOUT = 100
SLEEP_SHORT = 1
SLEEP_MEDIUM = 2
SLEEP_LONG = 3
SLEEP_EXTRA_LONG = 5

# Element selectors
SELECTORS = {
    "filter_box": '[name="filterBoxFilter"]',
    "identification_input": '[ng-model="IdentificationNumber"]',
    "filter_button": "//div[contains(@class, 'sw-filter')]//input[@type='button']",
    "fullname_element": "td.table-cell span[ng-bind='dataItem.FullName']",
    "watch_cell": "td.table-cell.showDetailsCommand.k-command-cell img.watch-img",
    "radio_element": "RadioId21",
    "pdf_button": "btnShowPopup",
    "report_button": "btnCreateTaxesPdf",
    "tab_selectors": [
        'li.k-item.k-state-default[role="tab"] span.k-link',
        "li.k-item span.k-link",
        '[role="tab"] span.k-link',
        "li.k-item.k-state-default",
        'li[role="tab"]',
    ],
    "checkbox_selectors": {
        "first": "checkYtrotPitzuim",
        "second": '[ng-model="compensationReportChecked"]',
    },
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import saver_products_processor with error handling
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "client_deatils _automation")
)
try:
    from saver_products_processor import process_saver_products_with_navigation
except ImportError:
    logger.warning(
        "⚠️ Could not import saver_products_processor - some functionality may be limited"
    )

    def process_saver_products_with_navigation(*args, **kwargs):
        logger.warning("⚠️ process_saver_products_with_navigation not available")
        return False


class ElementHelper:
    """Helper class for common element operations."""

    @staticmethod
    def safe_click(driver: WebDriver, element, description: str = "element") -> bool:
        """Safely click an element using JavaScript."""
        try:
            driver.execute_script("arguments[0].click();", element)
            logger.info(f"✅ {description} clicked successfully using JavaScript")
            return True
        except Exception as e:
            logger.error(f"❌ Error clicking {description}: {e}")
            return False

    @staticmethod
    def safe_fill_input(
        driver: WebDriver, element, value: str, description: str = "input"
    ) -> bool:
        """Safely fill an input field with JavaScript."""
        try:
            # Sanitize the value to prevent JavaScript injection
            safe_value = str(value).replace("'", "\\'").replace('"', '\\"')

            # Clear and fill the input
            driver.execute_script("arguments[0].value = '';", element)
            driver.execute_script(f"arguments[0].value = '{safe_value}';", element)

            # Trigger input events
            driver.execute_script(
                """
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
                element,
            )

            logger.info(f"✅ {description} filled with: {value}")
            return True
        except Exception as e:
            logger.error(f"❌ Error filling {description}: {e}")
            return False

    @staticmethod
    def find_element_with_fallback(
        driver: WebDriver, selectors: List[Tuple], description: str = "element"
    ):
        """Find element using multiple selector strategies."""
        for selector_type, selector_value in selectors:
            try:
                if selector_type == By.ID:
                    element = driver.find_element(selector_type, selector_value)
                elif selector_type == By.CSS_SELECTOR:
                    element = driver.find_element(selector_type, selector_value)
                elif selector_type == By.XPATH:
                    element = driver.find_element(selector_type, selector_value)
                else:
                    continue

                if element:
                    logger.info(
                        f"✅ Found {description} with {selector_type}: {selector_value}"
                    )
                    return element
            except NoSuchElementException:
                continue
            except Exception as e:
                logger.warning(
                    f"⚠️ Selector failed: {selector_type} {selector_value} - {e}"
                )
                continue

        logger.error(f"❌ {description} not found with any selector")
        return None


class PDFManager:
    """Manages PDF download and file operations."""

    @staticmethod
    def wait_for_new_pdf_download(timeout: int = DEFAULT_TIMEOUT) -> Optional[Path]:
        """Wait for any new PDF file to appear in the download directory."""
        start_time = time.time()
        initial_files = set(DOWNLOAD_DIR.glob("*.pdf"))

        while time.time() - start_time < timeout:
            current_files = set(DOWNLOAD_DIR.glob("*.pdf"))
            new_files = current_files - initial_files

            for file in new_files:
                if not file.name.endswith(".crdownload"):
                    logger.info(f"✅ New PDF detected: {file.name}")
                    return file
            time.sleep(SLEEP_SHORT)

        logger.warning(f"⚠️ No PDF download detected within {timeout} seconds")
        return None

    @staticmethod
    def create_identification_folder(
        identification_number: str, fullname_text: Optional[str] = None
    ) -> Path:
        """Create a folder for the specific identification number or full name."""
        if fullname_text:
            # Sanitize folder name for filesystem compatibility
            invalid_chars = '/\\:*?"<>|'
            folder_name = fullname_text
            for char in invalid_chars:
                folder_name = folder_name.replace(char, "_")
        else:
            folder_name = f"ID_{identification_number}"

        subfolder = DOWNLOAD_DIR / folder_name
        subfolder.mkdir(exist_ok=True)
        logger.info(f"📁 Created folder: {subfolder}")
        return subfolder

    @staticmethod
    def move_pdf_to_folder(
        pdf_file: Path, target_folder: Path, identification_number: str
    ) -> Optional[Path]:
        """Move a downloaded PDF to its specific folder, adding keywords to the filename if found."""
        if not pdf_file or not pdf_file.exists():
            return None

        try:
            # Check for keywords in the original filename
            keyword = ""
            if "פיצויים" in pdf_file.name:
                keyword = "פיצויים"
            elif "תגמולים" in pdf_file.name:
                keyword = "תגמולים"

            # Create a unique filename to avoid conflicts
            timestamp = int(time.time())
            new_filename = f"{identification_number}"
            if keyword:
                new_filename += f"_{keyword}"
            new_filename += f"_{timestamp}.pdf"

            target_path = target_folder / new_filename

            shutil.move(str(pdf_file), str(target_path))
            logger.info(f"✅ PDF moved to: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"❌ Error moving PDF: {e}")
            return None


class ClientProcessor:
    """Handles processing of individual client identification numbers."""

    def __init__(self, driver: WebDriver, wait: WebDriverWait):
        self.driver = driver
        self.wait = wait
        self.element_helper = ElementHelper()

    def process_client(
        self, identification_number: str, index: int, total: int
    ) -> bool:
        """Process a single client identification number."""
        logger.info(
            f"\n🔄 Processing item {index + 1}/{total}: {identification_number}"
        )

        try:
            # Step 1: Search for client
            if not self._search_client(identification_number):
                return False

            # Step 2: Extract client name and create folder
            fullname_text = self._extract_client_name()
            identification_folder = PDFManager.create_identification_folder(
                identification_number, fullname_text
            )

            # Step 3: Navigate to client details
            if not self._navigate_to_client_details():
                return False

            # Step 4: Generate PDF reports
            if not self._generate_pdf_reports(
                identification_folder, identification_number
            ):
                logger.warning("⚠️ PDF generation failed, but continuing")

            # Step 5: Process SaverMyProducts data
            success = process_saver_products_with_navigation(
                self.driver, self.wait, identification_folder, identification_number
            )

            if not success:
                logger.warning("⚠️ Failed to process SaverMyProducts, but continuing")

            # Step 6: Navigate to Events InfoRequest page
            self._navigate_to_events_page()

            return True

        except Exception as e:
            logger.error(f"❌ Error processing client {identification_number}: {e}")
            return False

    def _search_client(self, identification_number: str) -> bool:
        """Search for client using identification number."""
        try:
            # Click filter box
            filter_box = wait_for_element(
                self.driver, By.CSS_SELECTOR, SELECTORS["filter_box"], DEFAULT_TIMEOUT
            )
            if not filter_box:
                logger.error("❌ filterBoxFilter div not found")
                return False

            if not self.element_helper.safe_click(
                self.driver, filter_box, "filterBoxFilter div"
            ):
                return False

            time.sleep(SLEEP_SHORT)

            # Fill identification input
            identification_input = wait_for_element(
                self.driver,
                By.CSS_SELECTOR,
                SELECTORS["identification_input"],
                DEFAULT_TIMEOUT,
            )
            if not identification_input:
                logger.error("❌ IdentificationNumber input not found")
                return False

            if not self.element_helper.safe_fill_input(
                self.driver,
                identification_input,
                identification_number,
                "IdentificationNumber input",
            ):
                return False

            # Click filter button
            try:
                filter_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, SELECTORS["filter_button"]))
                )
                filter_button.click()
                time.sleep(SLEEP_MEDIUM)
                logger.info("✅ Filter button clicked successfully")
            except Exception as e:
                logger.error(f"❌ Error with filter button: {e}")
                return False

            # Wait for table results
            logger.info("⏳ Waiting for table results to load...")
            time.sleep(SLEEP_LONG)

            return True

        except Exception as e:
            logger.error(f"❌ Error searching client: {e}")
            return False

    def _extract_client_name(self) -> Optional[str]:
        """Extract client name from table."""
        try:
            fullname_element = wait_for_element(
                self.driver,
                By.CSS_SELECTOR,
                SELECTORS["fullname_element"],
                SHORT_TIMEOUT,
            )

            if fullname_element:
                fullname_text = fullname_element.text
                logger.info(f"✅ Found FullName: {fullname_text}")
                return fullname_text
            else:
                logger.warning("❌ FullName element not found")
                return None

        except Exception as e:
            logger.error(f"❌ Error extracting FullName: {e}")
            return None

    def _navigate_to_client_details(self) -> bool:
        """Navigate to client details page."""
        try:
            # Click watch image
            watch_cell = wait_for_element(
                self.driver, By.CSS_SELECTOR, SELECTORS["watch_cell"], DEFAULT_TIMEOUT
            )
            if not watch_cell:
                logger.error("❌ Watch image not found in table cell")
                return False

            if not self.element_helper.safe_click(
                self.driver, watch_cell, "watch image"
            ):
                return False

            # Wait for modal
            logger.info("⏳ Waiting for modal to open...")
            time.sleep(SLEEP_LONG)

            # Click RadioId21
            radio_element = wait_for_element(
                self.driver, By.ID, SELECTORS["radio_element"], LONG_TIMEOUT
            )
            if not radio_element:
                logger.error("❌ RadioId21 element not found in modal")
                return False

            # Ensure element is visible
            if not radio_element.is_displayed():
                logger.info("⚠️ RadioId21 element is not visible, scrolling to it...")
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", radio_element
                )
                time.sleep(SLEEP_SHORT)

            if not self.element_helper.safe_click(
                self.driver, radio_element, "RadioId21 element"
            ):
                return False

            # Wait for tabs
            logger.info("⏳ Waiting for tabs to load...")
            time.sleep(SLEEP_EXTRA_LONG)

            # Click product details tab
            return self._click_product_details_tab()

        except Exception as e:
            logger.error(f"❌ Error navigating to client details: {e}")
            return False

    def _click_product_details_tab(self) -> bool:
        """Click the product details tab."""
        try:
            product_details_tab = None

            for selector in SELECTORS["tab_selectors"]:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(
                        f"📊 Found {len(elements)} elements with selector: {selector}"
                    )

                    for element in elements:
                        try:
                            element_text = element.text.strip()
                            if "פירוט מוצרים" in element_text:
                                product_details_tab = element
                                logger.info(
                                    f"✅ Found פירוט מוצרים tab with selector: {selector}"
                                )
                                break
                        except Exception:
                            continue

                    if product_details_tab:
                        break
                except Exception:
                    continue

            if not product_details_tab:
                logger.error("❌ פירוט מוצרים tab not found")
                self._debug_available_tabs()
                return False

            if not self.element_helper.safe_click(
                self.driver, product_details_tab, "פירוט מוצרים tab"
            ):
                return False

            time.sleep(SLEEP_MEDIUM)
            return True

        except Exception as e:
            logger.error(f"❌ Error clicking product details tab: {e}")
            return False

    def _debug_available_tabs(self):
        """Debug available tabs on the page."""
        try:
            all_tabs = self.driver.find_elements(
                By.CSS_SELECTOR, 'li[role="tab"], .k-item, [class*="tab"]'
            )
            logger.info("🔍 Available tabs on page:")
            for i, tab in enumerate(all_tabs):
                try:
                    tab_text = tab.text.strip()
                    if tab_text:
                        logger.info(f"  Tab {i + 1}: '{tab_text}'")
                except Exception:
                    logger.info(f"  Tab {i + 1}: [text not readable]")
        except Exception as e:
            logger.warning(f"⚠️ Could not debug available tabs: {e}")

    def _generate_pdf_reports(
        self, identification_folder: Path, identification_number: str
    ) -> bool:
        """Generate PDF reports for the client."""
        try:
            # Find PDF button
            pdf_button = wait_for_element(
                self.driver, By.ID, SELECTORS["pdf_button"], DEFAULT_TIMEOUT
            )
            if not pdf_button:
                logger.error("❌ PDF icon button not found")
                return False

            logger.info("⏳ Waiting for popup to appear after clicking PDF button...")
            time.sleep(SLEEP_LONG)

            # Generate two reports
            for i in range(2):
                if not self._generate_single_report(
                    pdf_button, i, identification_folder, identification_number
                ):
                    logger.warning(f"⚠️ Report {i + 1} generation failed")

            return True

        except Exception as e:
            logger.error(f"❌ Error generating PDF reports: {e}")
            return False

    def _generate_single_report(
        self,
        pdf_button,
        attempt: int,
        identification_folder: Path,
        identification_number: str,
    ) -> bool:
        """Generate a single PDF report."""
        try:
            # Click PDF button
            if not self.element_helper.safe_click(
                self.driver, pdf_button, f"PDF button (attempt {attempt + 1})"
            ):
                return False

            # Determine checkbox selector
            checkbox_id = (
                SELECTORS["checkbox_selectors"]["first"]
                if attempt == 0
                else SELECTORS["checkbox_selectors"]["second"]
            )
            checkbox_selector = (
                (By.ID, checkbox_id) if attempt == 0 else (By.CSS_SELECTOR, checkbox_id)
            )

            # Click checkbox
            checkbox = self.wait.until(EC.element_to_be_clickable(checkbox_selector))
            if not self.element_helper.safe_click(
                self.driver, checkbox, f"checkbox (attempt {attempt + 1})"
            ):
                return False

            time.sleep(SLEEP_SHORT)

            # Click report button
            report_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, SELECTORS["report_button"]))
            )
            report_button.click()
            logger.info(f"✅ Report button clicked for attempt {attempt + 1}")

            # Wait for PDF download
            logger.info(f"⏳ Waiting for PDF download for attempt {attempt + 1}...")
            downloaded_pdf = PDFManager.wait_for_new_pdf_download(DEFAULT_TIMEOUT)

            if downloaded_pdf:
                moved_pdf = PDFManager.move_pdf_to_folder(
                    downloaded_pdf, identification_folder, identification_number
                )
                if moved_pdf:
                    logger.info(f"✅ PDF {attempt + 1} saved to: {moved_pdf}")
                else:
                    logger.error(f"❌ Failed to move PDF {attempt + 1}")
            else:
                logger.error(f"❌ PDF download {attempt + 1} not detected")

            time.sleep(SLEEP_LONG)
            return True

        except Exception as e:
            logger.error(f"❌ Error during report attempt {attempt + 1}: {e}")
            return False

    def _navigate_to_events_page(self):
        """Navigate to Events InfoRequest page."""
        try:
            self.driver.get(
                "https://distributor.swiftness.co.il/he-IL/Agent#/Desktop/Events/InfoRequest"
            )
            logger.info("✅ Successfully navigated to Events InfoRequest page")
        except Exception as e:
            logger.error(f"❌ Error navigating to Events page: {e}")


def handle_post_popup_actions(
    driver: WebDriver, wait: WebDriverWait, text_array: List[str]
) -> bool:
    """
    Handle actions after popup is completed - loop through all items in text_array and process each one.

    Args:
        driver: WebDriver instance
        wait: WebDriverWait instance
        text_array: List of identification numbers to process

    Returns:
        bool: True if all items processed successfully, False otherwise
    """
    try:
        logger.info(f"🔍 Handling post-popup actions for {len(text_array)} items...")

        # Ensure download directory exists
        DOWNLOAD_DIR.mkdir(exist_ok=True)
        logger.info(f"📁 Download directory: {DOWNLOAD_DIR}")

        if not text_array or len(text_array) == 0:
            logger.error("❌ No text available from popup array")
            return False

        # Initialize client processor
        client_processor = ClientProcessor(driver, wait)

        # Process each client
        successful_count = 0
        for index, identification_number in enumerate(text_array):
            try:
                if client_processor.process_client(
                    identification_number, index, len(text_array)
                ):
                    successful_count += 1
                else:
                    logger.warning(
                        f"⚠️ Failed to process client {identification_number}"
                    )

                # Small delay between clients
                time.sleep(SLEEP_MEDIUM)

            except Exception as item_error:
                logger.error(
                    f"❌ Error processing item {index + 1} ({identification_number}): {item_error}"
                )
                continue

        logger.info(
            f"✅ Post-popup actions completed! Successfully processed {successful_count}/{len(text_array)} items"
        )
        return successful_count > 0

    except Exception as e:
        logger.error(f"❌ Error handling post-popup actions: {e}")
        return False


# Legacy function aliases for backward compatibility
def wait_for_new_pdf_download(timeout: int = DEFAULT_TIMEOUT) -> Optional[Path]:
    """Legacy function - use PDFManager.wait_for_new_pdf_download instead."""
    return PDFManager.wait_for_new_pdf_download(timeout)


def create_identification_folder(
    identification_number: str, fullname_text: Optional[str] = None
) -> Path:
    """Legacy function - use PDFManager.create_identification_folder instead."""
    return PDFManager.create_identification_folder(identification_number, fullname_text)


def move_pdf_to_folder(
    pdf_file: Path, target_folder: Path, identification_number: str
) -> Optional[Path]:
    """Legacy function - use PDFManager.move_pdf_to_folder instead."""
    return PDFManager.move_pdf_to_folder(pdf_file, target_folder, identification_number)
