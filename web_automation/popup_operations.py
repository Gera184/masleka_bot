#!/usr/bin/env python3
"""
Popup operations module for web automation.
"""

import time
from selenium.webdriver.common.by import By
from .page_operations import wait_for_element


def handle_popup_with_text_input(driver):
    """Create and handle popup with text input, label ת"ז, and buttons הוספה/שליחה."""
    try:
        print("📝 Creating popup with text input...")
        
        # Create popup using JavaScript injection
        popup_script = """
        // Create popup container
        var popup = document.createElement('div');
        popup.id = 'masleka-popup';
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border: 2px solid #007bff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            min-width: 400px;
            font-family: Arial, sans-serif;
        `;
        
        // Create popup content
        popup.innerHTML = `
            <div style="margin-bottom: 15px;">
                <h3 style="margin: 0 0 15px 0; color: #333; text-align: center;">Enter ת"ז Information</h3>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label for="teudat-zehut" style="display: block; margin-bottom: 5px; font-weight: bold; color: #555;">ת"ז:</label>
                <input type="text" id="teudat-zehut" placeholder="Enter ת"ז number" style="
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                    box-sizing: border-box;
                ">
            </div>
            
            <div id="text-array-display" style="
                margin-bottom: 15px;
                max-height: 150px;
                overflow-y: auto;
                border: 1px solid #eee;
                padding: 10px;
                background: #f9f9f9;
                border-radius: 4px;
            ">
                <div style="font-weight: bold; margin-bottom: 5px; color: #666;">Added Texts:</div>
                <div id="text-list" style="font-size: 12px; color: #333;"></div>
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: center;">
                <button id="add-button" style="
                    padding: 8px 16px;
                    background: #28a745;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                ">הוספה</button>
                
                <button id="send-button" style="
                    padding: 8px 16px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                ">שליחה</button>
            </div>
        `;
        
        // Add popup to page
        document.body.appendChild(popup);
        
        // Initialize text array
        window.maslekaTextArray = [];
        
        // Get elements
        var textInput = document.getElementById('teudat-zehut');
        var addButton = document.getElementById('add-button');
        var sendButton = document.getElementById('send-button');
        var textList = document.getElementById('text-list');
        
        // Add button functionality
        addButton.addEventListener('click', function() {
            var text = textInput.value.trim();
            if (text) {
                window.maslekaTextArray.push(text);
                textInput.value = '';
                
                // Update display
                textList.innerHTML = window.maslekaTextArray.map(function(item, index) {
                    return '<div style="margin: 2px 0; padding: 2px 5px; background: white; border-radius: 2px;">' + 
                           (index + 1) + '. ' + item + '</div>';
                }).join('');
                
                console.log('Added text:', text);
                console.log('Text array:', window.maslekaTextArray);
            }
        });
        
        // Send button functionality
        sendButton.addEventListener('click', function() {
            console.log('Final text array:', window.maslekaTextArray);
            alert('שליחה completed! Text array: ' + JSON.stringify(window.maslekaTextArray));
            document.body.removeChild(popup);
        });
        
        // Enter key functionality
        textInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addButton.click();
            }
        });
        
        // Focus on input
        textInput.focus();
        
        console.log('Masleka popup created successfully');
        """
        
        # Execute the JavaScript to create the popup
        driver.execute_script(popup_script)
        print("✅ Popup created successfully")
        
        # Wait for popup to be visible
        time.sleep(1)
        
        # Now interact with the popup using Selenium
        print("📋 Popup is ready for user input...")
        
        # Find the text input field
        text_input = wait_for_element(driver, By.ID, "teudat-zehut")
        if not text_input:
            print("❌ Text input field not found in created popup")
            return False
        
        # Find the הוספה button
        add_button = wait_for_element(driver, By.ID, "add-button")
        if not add_button:
            print("❌ הוספה button not found in created popup")
            return False
        
        # Find the שליחה button
        send_button = wait_for_element(driver, By.ID, "send-button")
        if not send_button:
            print("❌ שליחה button not found in created popup")
            return False
        
        print("🎯 Popup is ready! User can now:")
        print("   - Type text in the ת\"ז input field")
        print("   - Click הוספה to add text to the array")
        print("   - Click שליחה when finished")
        print("   - Press Enter to quickly add text")
        
        # Wait for user to interact with the popup
        print("⏳ Waiting for user to complete text input...")
        
        # Keep the automation running while user interacts with popup
        # The user will manually interact with the popup
        # We'll wait for the popup to be closed (when שליחה is clicked)
        
        try:
            # Wait for the popup to be removed (when שליחה is clicked)
            while True:
                try:
                    # Check if popup still exists
                    popup_element = driver.find_element(By.ID, "masleka-popup")
                    if not popup_element.is_displayed():
                        break
                    time.sleep(0.5)
                except:
                    # Popup was closed
                    break
            
            print("✅ User completed text input and closed popup")
            
            # Handle any alert that might appear after שליחה is clicked
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"📋 Alert detected: {alert_text}")
                alert.accept()  # Click OK on the alert
                print("✅ Alert accepted successfully")
            except:
                # No alert present, continue normally
                pass
            
            # Get the final text array from JavaScript
            final_array = driver.execute_script("return window.maslekaTextArray || [];")
            print(f"📋 Final text array from user input: {final_array}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error waiting for user input: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error creating/handling popup: {e}")
        return False
