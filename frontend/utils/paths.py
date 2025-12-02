"""
Path Utility Module
Provides helper functions for resource file paths.
"""

from pathlib import Path


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path: Path to the project root directory.
    """
    # Traverse upwards from the current file location until 'main.py' is found
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "main.py").exists():
            return current
        current = current.parent
    # If not found, return the parent of the parent of the current file
    # (frontend/utils -> frontend -> root)
    return Path(__file__).resolve().parent.parent.parent


def get_assets_path() -> Path:
    """
    Get the assets directory path.

    Returns:
        Path: Path to the assets directory.
    """
    root = get_project_root()
    return root / "frontend" / "public" / "assets"


def get_icon_path(filename: str) -> Path:
    """
    Get the path to an icon file.

    Args:
        filename: Icon file name (e.g. "app_icon.ico")

    Returns:
        Path: Full path to the icon file.
    """
    return get_assets_path() / "icons" / filename


def get_image_path(filename: str) -> Path:
    """
    Get the path to an image file.

    Args:
        filename: Image file name (e.g. "logo.png")

    Returns:
        Path: Full path to the image file.
    """
    return get_assets_path() / "images" / filename


def get_font_path(filename: str) -> Path:
    """
    Get the path to a font file.
    Supports subdirectory paths (e.g., "Noto_Sans_TC/static/NotoSansTC-Regular.ttf").
    
    Args:
        filename: Font file name or path relative to fonts directory
                  Examples:
                  - "NotoSansTC-Regular.ttf" (direct file)
                  - "Noto_Sans_TC/static/NotoSansTC-Regular.ttf" (subdirectory)
                  - "Roboto/static/Roboto-Regular.ttf" (subdirectory)
        
    Returns:
        Path: Full path to the font file.
    """
    return get_assets_path() / "fonts" / filename

