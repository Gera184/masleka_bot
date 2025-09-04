# Client Details Automation

This package contains modules for processing client details and financial products data from web automation.

## Modules

### saver_products_processor.py

This module handles the extraction and processing of SaverMyProducts data from web pages.

#### Functions

##### `extract_saver_products_data(driver, wait, identification_folder, identification_number)`

Extracts data from the SaverMyProducts element and saves it to a text file.

**Parameters:**
- `driver`: Selenium WebDriver instance
- `wait`: WebDriverWait instance  
- `identification_folder`: Path to the folder where data should be saved
- `identification_number`: The identification number being processed

**Returns:**
- `bool`: True if successful, False otherwise

**Features:**
- Finds and processes all product rows in SaverMyProducts
- Extracts product names, policy numbers, company names, product types, status, and balances
- Saves comprehensive data to timestamped text files
- Handles errors gracefully and continues processing

##### `process_saver_products_with_navigation(driver, wait, identification_folder, identification_number)`

Processes SaverMyProducts data and handles navigation back to the main page.

**Parameters:**
- `driver`: Selenium WebDriver instance
- `wait`: WebDriverWait instance
- `identification_folder`: Path to the folder where data should be saved  
- `identification_number`: The identification number being processed

**Returns:**
- `bool`: True if successful, False otherwise

**Features:**
- Calls `extract_saver_products_data()` to extract and save data
- Handles navigation back to the main page using PDF icon
- Navigates to Events InfoRequest page
- Comprehensive error handling

##### `wait_for_element(driver, by, value, timeout=30)`

Utility function to wait for an element to be present on the page.

**Parameters:**
- `driver`: Selenium WebDriver instance
- `by`: Selenium By strategy
- `value`: Element selector value
- `timeout`: Maximum time to wait in seconds (default: 30)

**Returns:**
- `WebElement` or `None`: The found element or None if not found

## Data Extraction

The module extracts the following information from SaverMyProducts:

- **Product Names**: Names of financial products (pension funds, insurance, etc.)
- **Policy Numbers**: All policy numbers associated with each product
- **Company Names**: Financial institutions managing the products
- **Product Types**: Type of financial product
- **Status**: Current status of each policy
- **Balances**: Accumulated balances and forecasts
- **Management Fees**: Fee structures for each product

## Output Files

Data is saved to text files with the following format:
```
saver_products_data_{identification_number}_{timestamp}.txt
```

The files contain:
- Header with identification number and extraction date
- Product-by-product breakdown
- Policy numbers for each product
- Detailed financial information
- Error logs for any failed extractions

## Usage

```python
from client_deatils_automation.saver_products_processor import process_saver_products_with_navigation

# Process SaverMyProducts data and handle navigation
success = process_saver_products_with_navigation(
    driver, 
    wait, 
    identification_folder, 
    identification_number
)
```

## Error Handling

The module includes comprehensive error handling:
- Graceful handling of missing elements
- Detailed error logging
- Continues processing even if individual elements fail
- Returns success/failure status for integration with main automation flow
