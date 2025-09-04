#!/usr/bin/env python3
"""
Installation script for Masleka Bot dependencies.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install project dependencies."""
    print("🚀 Installing Masleka Bot dependencies...\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️ Failed to upgrade pip, continuing anyway...")
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    print("\n✅ All dependencies installed successfully!")
    return True


def test_installation():
    """Test if the installation was successful."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test importing selenium
        import selenium
        print("✅ Selenium imported successfully")
        
        # Test importing webdriver-manager
        import webdriver_manager
        print("✅ WebDriver Manager imported successfully")
        
        # Test importing our modules
        from browser_finder import find_chromium
        print("✅ Browser finder module imported successfully")
        
        from web_automation import WebAutomation
        print("✅ Web automation module imported successfully")
        
        print("\n🎉 Installation test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False


def main():
    """Main installation function."""
    print("=" * 50)
    print("🤖 Masleka Bot - Installation Script")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("=" * 50)
    print("\nYou can now run the bot with:")
    print("  python main.py")
    print("\nOr use the CLI:")
    print("  python cli.py --help")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
