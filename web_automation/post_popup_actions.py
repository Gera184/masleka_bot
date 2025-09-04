#!/usr/bin/env python3
"""
Post-popup actions module for web automation.
"""

import time
import os
import shutil
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .page_operations import wait_for_element
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client_deatils _automation'))
from saver_products_processor import process_saver_products_with_navigation
# Download directory for PDFs
DOWNLOAD_DIR = Path.home() / "Desktop" / "maslekot"


def wait_for_new_pdf_download(timeout=30):
    """Wait for any new PDF file to appear in the download directory"""
    start_time = time.time()
    initial_files = set(DOWNLOAD_DIR.glob("*.pdf"))

    while time.time() - start_time < timeout:
        current_files = set(DOWNLOAD_DIR.glob("*.pdf"))
        new_files = current_files - initial_files

        for file in new_files:
            if not file.name.endswith(".crdownload"):
                return file
        time.sleep(1)
    return None


def create_identification_folder(identification_number, fullname_text=None):
    """Create a folder for the specific identification number or full name"""
    if fullname_text:
        # Use full name for folder, but sanitize it for filesystem compatibility
        folder_name = (
            fullname_text.replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace("*", "_")
            .replace("?", "_")
            .replace('"', "_")
            .replace("<", "_")
            .replace(">", "_")
            .replace("|", "_")
        )
    else:
        folder_name = f"ID_{identification_number}"

    subfolder = DOWNLOAD_DIR / folder_name
    subfolder.mkdir(exist_ok=True)
    return subfolder


def move_pdf_to_folder(pdf_file, target_folder, identification_number):
    """Move a downloaded PDF to its specific folder"""
    if pdf_file and pdf_file.exists():
        # Create a unique filename to avoid conflicts
        timestamp = int(time.time())
        new_filename = f"report_{identification_number}_{timestamp}.pdf"
        target_path = target_folder / new_filename

        try:
            shutil.move(str(pdf_file), str(target_path))
            print(f"✅ PDF moved to: {target_path}")
            return target_path
        except Exception as e:
            print(f"❌ Error moving PDF: {e}")
            return None
    return None


def handle_post_popup_actions(driver, wait, text_array):
    """Handle actions after popup is completed - loop through all items in text_array and process each one."""
    try:
        print(f"🔍 Handling post-popup actions for {len(text_array)} items...")

        # Ensure download directory exists
        DOWNLOAD_DIR.mkdir(exist_ok=True)
        print(f"📁 Download directory: {DOWNLOAD_DIR}")

        if not text_array or len(text_array) == 0:
            print("❌ No text available from popup array")
            return False

        # Process each item in the text_array
        for index, identification_number in enumerate(text_array):
            print(
                f"\n🔄 Processing item {index + 1}/{len(text_array)}: {identification_number}"
            )

            try:
                # Find and click the div with name="filterBoxFilter"
                print("🔍 Looking for filterBoxFilter div...")
                filter_box = wait_for_element(
                    driver, By.CSS_SELECTOR, '[name="filterBoxFilter"]', timeout=30
                )
                if not filter_box:
                    print("❌ filterBoxFilter div not found")
                    print("⏭️ Continuing to next item...")
                    continue

                # Try to click using JavaScript for better reliability
                driver.execute_script("arguments[0].click();", filter_box)
                print("✅ filterBoxFilter div clicked successfully using JavaScript")

                # Wait for the input to be available
                time.sleep(1)

                # Find the input with ng-model="IdentificationNumber"
                print("🔍 Looking for IdentificationNumber input...")
                identification_input = wait_for_element(
                    driver,
                    By.CSS_SELECTOR,
                    '[ng-model="IdentificationNumber"]',
                    timeout=30,
                )
                if not identification_input:
                    print("❌ IdentificationNumber input not found")
                    print("⏭️ Continuing to next item...")
                    continue

                # Clear and fill the input using JavaScript with better error handling
                try:
                    # Sanitize the identification number to prevent JavaScript injection
                    safe_identification_number = (
                        str(identification_number)
                        .replace("'", "\\'")
                        .replace('"', '\\"')
                    )

                    # Clear the input
                    driver.execute_script(
                        "arguments[0].value = '';", identification_input
                    )

                    # Fill the input with sanitized value
                    driver.execute_script(
                        f"arguments[0].value = '{safe_identification_number}';",
                        identification_input,
                    )

                    # Trigger input events to ensure the form recognizes the change
                    driver.execute_script(
                        """
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """,
                        identification_input,
                    )

                    print(
                        f"✅ IdentificationNumber input filled with: {identification_number}"
                    )
                except Exception as fill_error:
                    print(f"❌ Error filling identification input: {fill_error}")
                    continue

                # Click filter button
                try:
                    print("🔍 Looking for filter button...")
                    filter_button = wait.until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "//div[contains(@class, 'sw-filter')]//input[@type='button']",
                            )
                        )
                    )

                    filter_button.click()
                    time.sleep(2)
                    print("✅ Filter button clicked successfully")

                except Exception as e:
                    print(f"❌ Error with filter button: {e}")
                    continue

                # Wait for the table to load with results
                print("⏳ Waiting for table results to load...")
                time.sleep(3)

                # Find and extract the FullName text from the table cell
                try:
                    print("🔍 Looking for FullName in table cell...")
                    fullname_element = wait_for_element(
                        driver,
                        By.CSS_SELECTOR,
                        "td.table-cell span[ng-bind='dataItem.FullName']",
                        timeout=10,
                    )

                    if fullname_element:
                        fullname_text = fullname_element.text
                        print(f"✅ Found FullName: {fullname_text}")
                    else:
                        print("❌ FullName element not found")
                        fullname_text = None

                except Exception as e:
                    print(f"❌ Error extracting FullName: {e}")
                    fullname_text = None

                # Create folder using fullname if available, otherwise use identification number
                identification_folder = create_identification_folder(
                    identification_number, fullname_text
                )
                print(f"📁 Created folder: {identification_folder}")

                # Find and click the table cell with watch image
                print("🔍 Looking for table cell with watch image...")
                watch_cell = wait_for_element(
                    driver,
                    By.CSS_SELECTOR,
                    "td.table-cell.showDetailsCommand.k-command-cell img.watch-img",
                    timeout=30,
                )
                if not watch_cell:
                    print("❌ Watch image not found in table cell")
                    print("⏭️ Continuing to next item...")
                    continue

                # Try to click using JavaScript
                driver.execute_script("arguments[0].click();", watch_cell)
                print("✅ Watch image clicked successfully using JavaScript")

                # Wait for modal to open
                print("⏳ Waiting for modal to open...")
                time.sleep(3)

                # Find and click the element with id="RadioId21"
                print("🔍 Looking for RadioId21 element...")
                radio_element = wait_for_element(
                    driver, By.ID, "RadioId21", timeout=100
                )
                if not radio_element:
                    print("❌ RadioId21 element not found in modal")
                    continue

                # Check if element is visible and clickable
                if not radio_element.is_displayed():
                    print(
                        "⚠️ RadioId21 element is not visible, trying to scroll to it..."
                    )
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", radio_element
                    )
                    time.sleep(1)

                # Try to click using JavaScript if regular click fails
                try:
                    driver.execute_script("arguments[0].click();", radio_element)
                    print("✅ RadioId21 element clicked successfully using JavaScript")
                except Exception as js_click_error:
                    print(f"❌ JavaScript click failed: {js_click_error}")
                    continue

                # Wait for the tab to be available
                print("⏳ Waiting for tabs to load...")
                time.sleep(5)

                # Find and click the "פירוט מוצרים" (Product Details) tab
                print("🔍 Looking for פירוט מוצרים tab...")
                try:
                    # Try multiple selector strategies to find the tab
                    tab_selectors = [
                        'li.k-item.k-state-default[role="tab"] span.k-link',
                        "li.k-item span.k-link",
                        '[role="tab"] span.k-link',
                        "li.k-item.k-state-default",
                        'li[role="tab"]',
                    ]

                    product_details_tab = None
                    used_selector = None

                    for selector in tab_selectors:
                        try:
                            print(f"🔍 Trying selector: {selector}")
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            print(
                                f"📊 Found {len(elements)} elements with selector: {selector}"
                            )

                            for element in elements:
                                try:
                                    element_text = element.text.strip()
                                    print(f"📝 Element text: '{element_text}'")
                                    if "פירוט מוצרים" in element_text:
                                        product_details_tab = element
                                        used_selector = selector
                                        print(
                                            f"✅ Found פירוט מוצרים tab with selector: {selector}"
                                        )
                                        break
                                except Exception as text_error:
                                    print(
                                        f"⚠️ Could not get text for element: {text_error}"
                                    )
                                    continue

                            if product_details_tab:
                                break
                        except Exception as selector_error:
                            print(f"⚠️ Selector failed: {selector} - {selector_error}")
                            continue

                    if not product_details_tab:
                        print("❌ פירוט מוצרים tab not found with any selector")
                        print("🔍 Available tabs on page:")
                        try:
                            # Try to find any tabs and show their text
                            all_tabs = driver.find_elements(
                                By.CSS_SELECTOR,
                                'li[role="tab"], .k-item, [class*="tab"]',
                            )
                            for i, tab in enumerate(all_tabs):
                                try:
                                    tab_text = tab.text.strip()
                                    if tab_text:
                                        print(f"  Tab {i + 1}: '{tab_text}'")
                                except:
                                    print(f"  Tab {i + 1}: [text not readable]")
                        except Exception as debug_error:
                            print(f"⚠️ Could not debug available tabs: {debug_error}")
                        print("⏭️ Continuing to next item...")
                        continue

                    # Click the found tab using JavaScript
                    driver.execute_script("arguments[0].click();", product_details_tab)
                    print(
                        f"✅ פירוט מוצרים tab clicked successfully using JavaScript (selector: {used_selector})"
                    )

                except Exception as e:
                    print(f"❌ Error clicking פירוט מוצרים tab: {e}")
                    print("⏭️ Continuing to next item...")
                    continue

                # Wait for the tab content to load
                print("⏳ Waiting for tab content to load...")
                time.sleep(2)

                # Find and click the PDF icon button
                print("🔍 Looking for PDF icon button...")
                pdf_button = wait_for_element(driver, By.ID, "btnShowPopup", timeout=30)
                if not pdf_button:
                    print("❌ PDF icon button not found")
                    print("⏭️ Continuing to next item...")
                    continue

                # Wait for popup to appear
                print("⏳ Waiting for popup to appear after clicking PDF button...")
                time.sleep(3)

                # Loop to handle checkbox + report button click twice
                for i in range(2):
                    # Click the PDF icon button via JS
                    driver.execute_script("arguments[0].click();", pdf_button)
                    print("✅ PDF icon button clicked successfully using JavaScript")

                    try:
                        # Determine which checkbox to use
                        if i == 0:
                            checkbox_selector = (By.ID, "checkYtrotPitzuim")
                        else:
                            checkbox_selector = (
                                By.CSS_SELECTOR,
                                '[ng-model="compensationReportChecked"]',
                            )

                        # Wait for the checkbox
                        checkbox = wait.until(
                            EC.element_to_be_clickable(checkbox_selector)
                        )

                        # Click the checkbox using JS for better reliability
                        driver.execute_script("arguments[0].click();", checkbox)
                        print(f"✅ Checkbox clicked for attempt {i + 1}")

                        # Wait a moment to let the report button become enabled
                        time.sleep(1)

                        # Wait for and click the "create report" button
                        report_button = wait.until(
                            EC.element_to_be_clickable((By.ID, "btnCreateTaxesPdf"))
                        )
                        report_button.click()
                        print(f"✅ Report button clicked for attempt {i + 1}")

                        # Wait for PDF download and move it to the identification folder
                        print(f"⏳ Waiting for PDF download for attempt {i + 1}...")
                        downloaded_pdf = wait_for_new_pdf_download(timeout=30)
                        if downloaded_pdf:
                            moved_pdf = move_pdf_to_folder(
                                downloaded_pdf,
                                identification_folder,
                                identification_number,
                            )
                            if moved_pdf:
                                print(f"✅ PDF {i + 1} saved to: {moved_pdf}")
                            else:
                                print(f"❌ Failed to move PDF {i + 1}")
                        else:
                            print(f"❌ PDF download {i + 1} not detected")

                        # Wait between attempts
                        time.sleep(3)

                    except Exception as e:
                        print(f"❌ Error during report attempt {i + 1}: {e}")
                        print("⏭️ Continuing to next attempt...")
                        continue

                # Process SaverMyProducts data and handle PDF icon navigation using the new module
                success = process_saver_products_with_navigation(
                    driver, 
                    wait, 
                    identification_folder, 
                    identification_number
                )
                
                if not success:
                    print("⚠️ Failed to process SaverMyProducts, but continuing with navigation")
                
                # Navigate to Events InfoRequest page (kept in main file as requested)
                driver.get(
                    "https://distributor.swiftness.co.il/he-IL/Agent#/Desktop/Events/InfoRequest"
                )
                print("✅ Successfully navigated to Events InfoRequest page")

                # Continue the loop from the beginning for the next item
                continue

                # Wait a bit before processing the next item
                time.sleep(2)

            except Exception as item_error:
                print(
                    f"❌ Error processing item {index + 1} ({identification_number}): {item_error}"
                )
                continue

        print(f"✅ Post-popup actions completed for all {len(text_array)} items!")
        return True

    except Exception as e:
        print(f"❌ Error handling post-popup actions: {e}")
        return False
