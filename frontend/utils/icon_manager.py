"""
Icon Manager Module
Provides icon loading and management functionality.
"""

from pathlib import Path
from PySide6.QtGui import QIcon
from frontend.utils.paths import get_icon_path


class IconManager:
    """Icon manager for handling icons of various sizes."""
    
    # Define available icon sizes
    SIZES = {
        'tiny': 16,           # Tiny icons
        'small': 32,          # Menu / Explorer small
        'small_alt': 48,      # Small icons
        'medium': 64,         # Medium icons
        'desktop': 128,       # Desktop icon
        'taskbar': 256,       # Taskbar / Start Menu
    }
    
    @staticmethod
    def get_icon_path_by_size(size: int) -> Path:
        """
        Get icon path by size.
        
        Args:
            size: Icon size (16, 32, 48, 64, 128, 256)
            
        Returns:
            Path: Path to the icon file
        """
        filename = f"orange_clicker_icon_{size}x{size}.png"
        return get_icon_path(filename)
    
    @staticmethod
    def get_icon_by_size(size: int) -> QIcon:
        """
        Get QIcon object by size.
        
        Args:
            size: Icon size (16, 32, 48, 64, 128, 256)
            
        Returns:
            QIcon: Icon object
        """
        icon_path = IconManager.get_icon_path_by_size(size)
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()
    
    @staticmethod
    def get_app_icon() -> QIcon:
        """
        Get the main application icon (uses the largest size, system will auto-scale).
        
        Returns:
            QIcon: Application icon
        """
        # Use 256x256 as the main app icon
        return IconManager.get_icon_by_size(IconManager.SIZES['taskbar'])
    
    @staticmethod
    def get_icon_by_name(name: str) -> QIcon:
        """
        Get icon by predefined size name.
        
        Args:
            name: Icon size name ('tiny', 'small', 'small_alt', 'medium', 'desktop', 'taskbar')
            
        Returns:
            QIcon: Icon object
        """
        if name in IconManager.SIZES:
            return IconManager.get_icon_by_size(IconManager.SIZES[name])
        return QIcon()
    
    @staticmethod
    def get_all_icons() -> dict[str, QIcon]:
        """
        Get all icons of available sizes.
        
        Returns:
            dict: A dictionary containing all icon sizes
        """
        icons = {}
        for name, size in IconManager.SIZES.items():
            icons[name] = IconManager.get_icon_by_size(size)
        return icons

