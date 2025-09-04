# Masleka Bot - Chromium Browser Opener with Login Automation

A well-organized Python project that opens Chromium browser programmatically and automates login processes with cross-platform support.

## Features

- Opens Chromium browser automatically
- Cross-platform support (Windows, macOS, Linux)
- Fallback to default browser if Chromium is not found
- **NEW**: Automated login form filling
- **NEW**: Interactive CodeToken input dialog
- **NEW**: Automatic form submission
- **NEW**: Automated PDF download and organization
- **NEW**: Individual folders for each identification number
- Error handling and user feedback
- Modular and organized code structure
- Command-line interface support
- Configurable URLs and settings

## Project Structure

```
masleka_bot/
├── __init__.py           # Package initialization
├── main.py              # Main application entry point (with automation)
├── cli.py               # Command-line interface
├── browser_finder.py    # Browser detection and path finding
├── browser_launcher.py  # Browser launching functionality
├── web_automation.py    # Web automation and form handling
├── config.py            # Configuration and constants
├── utils.py             # Utility functions
├── requirements.txt     # Project dependencies
├── test_example.py      # Example usage and testing
└── README.md           # This file
```

## Requirements

- Python 3.6 or higher
- Chromium browser (optional - will fallback to default browser)
- **NEW**: Selenium WebDriver (automatically managed)

## Installation

1. Clone or download this project
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (with Automation)

Run the main script for full automation:

```bash
python main.py
```

This will:
1. Open Chromium browser
2. Navigate to the login page
3. Fill in Username and Password automatically
4. Show a dialog for CodeToken input
5. Click the Submit button
6. Keep the browser open for manual interaction

### Command Line Interface

Use the CLI for more options:

```bash
# Run full automation (default)
python cli.py

# Just open browser without automation
python cli.py --browser-only

# Open with custom URL and automation
python cli.py -u https://example.com

# Enable verbose output
python cli.py -v

# Show help
python cli.py --help
```

### Programmatic Usage

You can also use the modules in your own code:

```python
from web_automation import WebAutomation

# Create automation instance
automation = WebAutomation("https://example.com")

# Run full automation
```

## PDF Download and Organization

The bot now includes automated PDF download and organization functionality:

### Directory Structure

PDFs are automatically organized in the following structure:
```
Desktop/
└── maslekot/
    ├── ID_123456789/
    │   ├── report_123456789_1703123456.pdf
    │   └── report_123456789_1703123457.pdf
    ├── ID_987654321/
    │   ├── report_987654321_1703123458.pdf
    │   └── report_987654321_1703123459.pdf
    └── ...
```

### Features

- **Automatic Download Directory**: Creates `~/Desktop/maslekot/` folder
- **Individual Folders**: Each identification number gets its own folder (`ID_[number]`)
- **Unique Filenames**: PDFs are renamed with timestamps to avoid conflicts
- **Download Monitoring**: Automatically detects when PDFs are downloaded
- **Error Handling**: Graceful handling of download failures

### How It Works

1. When processing each identification number, the bot:
   - Creates a dedicated folder for that ID
   - Monitors the download directory for new PDF files
   - Moves downloaded PDFs to the appropriate folder
   - Renames files with timestamps for uniqueness

2. The download process:
   - Configures Chrome to download PDFs to the maslekot folder
   - Waits for PDF downloads to complete
   - Automatically organizes files into individual folders
   - Provides detailed logging of the process

### Testing the PDF Functionality

You can test the PDF download structure using the provided test script:

```bash
python test_download_structure.py
```

This will create test folders and verify that the file organization works correctly.
success = automation.automate_login()

# Or use individual methods
automation.setup_driver()
automation.open_page()
automation.fill_login_form()
# ... etc
```

## Modules Overview

### `web_automation.py` (NEW)
- `WebAutomation` class: Handles web automation and form interactions
- Automatic form filling with hardcoded credentials
- Interactive CodeToken input dialog
- Automatic button clicking
- Selenium WebDriver integration

### `browser_finder.py`
- `find_chromium()`: Detects Chromium installation paths
- `get_system_info()`: Gets system information

### `browser_launcher.py`
- `BrowserLauncher` class: Handles browser launching operations
- Cross-platform browser detection and fallback

### `config.py`
- Configuration constants and settings
- Status messages and file paths

### `utils.py`
- Utility functions for common operations
- Platform detection and URL validation

### `cli.py`
- Command-line interface with argument parsing
- Support for both automation and browser-only modes

## Automation Features

### Login Credentials
The automation uses these hardcoded credentials:
- **Username**: `EFZO206264152`
- **Password**: `Badboy2025!@`
- **CodeToken**: User input via dialog

### Form Elements
The automation looks for these form elements:
- `UserName` (ID)
- `Password` (ID) 
- `CodeToken` (ID)
- `SubmitButton1` (name attribute)

### Process Flow
1. Opens Chromium browser
2. Navigates to the target URL
3. Waits for page to load
4. Fills Username and Password automatically
5. Shows dialog for CodeToken input
6. Fills CodeToken field
7. Clicks SubmitButton1
8. Keeps browser open for manual interaction

## Customization

### Changing Default URL

Edit `config.py`:

```python
DEFAULT_URL = "https://your-preferred-website.com"
```

### Modifying Credentials

Edit `web_automation.py`:

```python
def __init__(self, url=DEFAULT_URL):
    # ...
    self.username = "your_username"
    self.password = "your_password"
```

### Adding New Browser Paths

Edit `config.py` in the `CHROMIUM_PATHS` section:

```python
CHROMIUM_PATHS = {
    'win32': [
        # Add your custom paths here
        r"C:\Custom\Path\To\Chromium\chrome.exe",
        # ... existing paths
    ]
}
```

## Troubleshooting

- If Chromium doesn't open, the script will automatically try your default browser
- Make sure Chromium is installed in one of the standard locations
- Check that you have permission to execute the script
- Use verbose mode (`-v`) for detailed output
- **NEW**: If automation fails, check that the form elements exist with the expected IDs
- **NEW**: Ensure you have internet connection for Selenium WebDriver download

## Development

### Adding New Features

1. Create new modules in separate files
2. Import them in `__init__.py` if they should be part of the public API
3. Update documentation and tests

### Code Organization

- Keep related functionality in the same module
- Use clear, descriptive function and variable names
- Add docstrings to all functions and classes
- Follow PEP 8 style guidelines

## License

This project is open source and available under the MIT License.

