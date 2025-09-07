# wkhtmltopdf Installation Guide

## Overview
The SaverMyProducts processor now uses `pdfkit` with `wkhtmltopdf` for HTML to PDF conversion. This provides excellent Hebrew RTL support and works reliably on Windows.

## Installation Steps

### 1. Install Python Dependencies
```bash
py -m pip install pdfkit>=1.0.0
```

### 2. Install wkhtmltopdf

#### Option A: Download from Official Website (Recommended)
1. Go to: https://wkhtmltopdf.org/downloads.html
2. Download the Windows installer (64-bit recommended)
3. Run the installer and follow the setup wizard
4. The installer will add wkhtmltopdf to your system PATH

#### Option B: Using Chocolatey (if you have it installed)
```bash
choco install wkhtmltopdf
```

#### Option C: Using Scoop (if you have it installed)
```bash
scoop install wkhtmltopdf
```

### 3. Verify Installation
After installation, test if wkhtmltopdf is working:

```bash
wkhtmltopdf --version
```

You should see output like:
```
wkhtmltopdf 0.12.6 (with patched qt)
```

## Configuration

### Automatic Detection
pdfkit will automatically detect wkhtmltopdf if it's in your system PATH.

### Manual Configuration (if needed)
If wkhtmltopdf is not in your PATH, you can configure pdfkit manually:

```python
import pdfkit

# Configure the path to wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')

# Use it in your code
pdfkit.from_string(html_content, 'output.pdf', configuration=config)
```

## Benefits of wkhtmltopdf

### 1. **Excellent Hebrew Support**
- Native RTL text direction support
- Proper Hebrew font rendering
- Correct text alignment

### 2. **Windows Compatibility**
- Works reliably on Windows
- No complex system dependencies
- Easy installation process

### 3. **High Quality Output**
- Professional PDF generation
- Good typography and layout
- Consistent rendering across platforms

## Troubleshooting

### Common Issues

#### 1. "wkhtmltopdf not found" Error
**Solution**: Make sure wkhtmltopdf is installed and in your PATH
- Check installation: `wkhtmltopdf --version`
- If not found, reinstall or add to PATH manually

#### 2. "Permission Denied" Error
**Solution**: Run your Python script as administrator or check file permissions

#### 3. "Encoding Error" with Hebrew Text
**Solution**: Make sure your HTML includes proper UTF-8 encoding:
```html
<meta charset="UTF-8">
```

### Testing Your Setup

Create a simple test script to verify everything works:

```python
import pdfkit

# Test HTML with Hebrew text
html_content = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>Test</title>
</head>
<body>
    <h1>שלום עולם</h1>
    <p>זהו טקסט בעברית לבדיקה</p>
</body>
</html>
"""

try:
    pdfkit.from_string(html_content, 'test_hebrew.pdf')
    print("✅ Hebrew PDF generation successful!")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Alternative Solutions

If you encounter issues with wkhtmltopdf, here are some alternatives:

### 1. **WeasyPrint** (Linux/macOS)
- Better for Linux and macOS
- More complex Windows setup
- Requires additional system libraries

### 2. **ReportLab** (Direct PDF)
- No external dependencies
- More complex Hebrew text handling
- Requires manual text reversal

### 3. **Playwright/Selenium PDF**
- Uses browser engine for PDF generation
- Excellent rendering quality
- Requires browser installation

## Performance Notes

- **First Run**: May be slower due to font loading
- **Subsequent Runs**: Fast PDF generation
- **Memory Usage**: Moderate, suitable for most systems
- **File Size**: Optimized PDF output

## Support

If you encounter issues:
1. Check the wkhtmltopdf documentation
2. Verify your HTML is valid
3. Test with simple Hebrew text first
4. Check system PATH configuration

The combination of pdfkit + wkhtmltopdf provides the best balance of Hebrew support, Windows compatibility, and ease of use for your SaverMyProducts processor.
