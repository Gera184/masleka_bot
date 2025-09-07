#!/usr/bin/env python3
"""
Installation script for required dependencies.
Run this script to install the necessary packages for the SaverMyProducts processor.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all required dependencies."""
    print("🔧 Installing required dependencies for SaverMyProducts processor...")
    print("=" * 60)
    
    # Required packages
    packages = [
        "selenium>=4.0.0",
        "pdfkit>=1.0.0"
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Installation Summary:")
    print(f"   Successfully installed: {success_count}/{total_packages} packages")
    
    if success_count == total_packages:
        print("✅ All dependencies installed successfully!")
        print("\n🎉 You can now run the SaverMyProducts processor with HTML to PDF conversion support.")
        print("📝 Note: You may need to install wkhtmltopdf separately for pdfkit to work.")
        print("   Download from: https://wkhtmltopdf.org/downloads.html")
    else:
        print("⚠️ Some packages failed to install. Please check the errors above.")
        print("You may need to install them manually or check your Python environment.")

if __name__ == "__main__":
    main()
