# Static Assets Directory

This directory contains static asset files used by the frontend.

## Directory Structure

```
assets/
├── icons/      # Icon files (.ico, .png, .svg, etc.)
├── images/     # Image files (.png, .jpg, .svg, etc.)
└── fonts/      # Font files (.ttf, .otf, etc.)
```

## Usage

When referencing resource files in your code, it's recommended to use relative or absolute paths:

### Method 1: Using Relative Path (Recommended)

```python
import os
from pathlib import Path

# Get project root directory
BASE_DIR = Path(__file__).parent.parent.parent.parent
ICON_PATH = BASE_DIR / "frontend" / "public" / "assets" / "icons" / "app_icon.ico"
```

### Method 2: Using Resource System (PySide6)

```python
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon

icon_path = "frontend/public/assets/icons/app_icon.ico"
icon = QIcon(icon_path)
```

## File Naming Conventions

- Use lowercase letters and underscores: `app_icon.ico`
- Use descriptive names: `button_click.png` instead of `img1.png`
- Prefer SVG format (scalable) or high-resolution PNG for icons

## Notes

- For large files (> 1MB), consider using an external CDN or resource server
- Compress images to reduce application size
- Prefer vector formats (SVG) for icons to support multiple resolutions


