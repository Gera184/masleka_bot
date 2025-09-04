# Web Automation Package

This package contains modular web automation functions organized by functionality.

## Structure

```
web_automation/
├── __init__.py                 # Package initialization and exports
├── driver_setup.py            # WebDriver setup and configuration
├── page_operations.py         # Basic page operations (open, wait for elements)
├── login_operations.py        # Login form handling and authentication
├── navigation_operations.py   # Navigation and clicking operations
├── popup_operations.py        # Popup creation and handling
├── post_popup_actions.py      # Complex post-popup processing
├── automation_orchestrator.py # Main automation coordination
└── README.md                  # This file
```

## Modules

### `driver_setup.py`
- **`setup_driver()`**: Sets up Chrome/Chromium WebDriver with anti-detection options
- Returns: `(driver, wait, success)` tuple

### `page_operations.py`
- **`open_page(driver, url)`**: Opens a web page
- **`wait_for_element(driver, by, value, timeout=30)`**: Waits for element with debugging info

### `login_operations.py`
- **`fill_login_form(driver, username, password)`**: Fills login credentials
- **`get_code_token_from_user()`**: Shows dialog for user input
- **`fill_code_token(driver, code_token)`**: Fills code token field
- **`click_submit_button(driver)`**: Clicks submit button

### `navigation_operations.py`
- **`click_home_page_item1(driver)`**: Clicks homePageItem1 div
- **`click_action_view(driver)`**: Clicks actionview div

### `popup_operations.py`
- **`handle_popup_with_text_input(driver)`**: Creates and handles text input popup

### `post_popup_actions.py`
- **`handle_post_popup_actions(driver, wait, text_array)`**: Processes text array items

### `automation_orchestrator.py`
- **`automate_login(url, username, password)`**: Complete automation workflow
- **`close_browser(driver)`**: Closes browser

## Usage

### Import individual functions:
```python
from web_automation import setup_driver, open_page, fill_login_form
```

### Use the main automation function:
```python
from web_automation import automate_login

success = automate_login(url, username, password)
```

### Use the WebAutomation class (from main web_automation.py):
```python
from web_automation import WebAutomation

automation = WebAutomation()
success = automation.automate_login()
```

## Benefits

1. **Modularity**: Each function is in its own file for easy maintenance
2. **Reusability**: Functions can be imported and used independently
3. **Testability**: Individual functions can be tested in isolation
4. **Maintainability**: Changes to specific functionality only affect one file
5. **Clarity**: Clear separation of concerns by functionality

## Dependencies

- `selenium`: Web automation
- `tkinter`: User dialogs
- `browser_finder`: Chromium detection
- `config`: Default URL configuration
