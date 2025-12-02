"""
Font Manager Module
Provides font loading and management functionality.
"""

from pathlib import Path
from PySide6.QtGui import QFont, QFontDatabase
from frontend.utils.paths import get_font_path


class FontManager:
    """Font manager for loading and managing custom fonts."""
    
    _loaded_fonts: dict[str, int] = {}  # Store loaded font IDs
    
    # Common font paths for quick access
    FONT_PATHS = {
        # Noto Sans TC (Traditional Chinese)
        'noto_tc_regular': 'Noto_Sans_TC/static/NotoSansTC-Regular.ttf',
        'noto_tc_bold': 'Noto_Sans_TC/static/NotoSansTC-Bold.ttf',
        'noto_tc_medium': 'Noto_Sans_TC/static/NotoSansTC-Medium.ttf',
        'noto_tc_light': 'Noto_Sans_TC/static/NotoSansTC-Light.ttf',
        'noto_tc_semibold': 'Noto_Sans_TC/static/NotoSansTC-SemiBold.ttf',
        
        # Roboto
        'roboto_regular': 'Roboto/static/Roboto-Regular.ttf',
        'roboto_bold': 'Roboto/static/Roboto-Bold.ttf',
        'roboto_medium': 'Roboto/static/Roboto-Medium.ttf',
        'roboto_light': 'Roboto/static/Roboto-Light.ttf',
    }
    
    @staticmethod
    def load_font(filename: str) -> int:
        """
        Load a font file and return its font ID.
        
        Args:
            filename: Font filename (e.g., "Roboto-Regular.ttf")
            
        Returns:
            int: Font ID if successful, -1 if failed
        """
        if filename in FontManager._loaded_fonts:
            return FontManager._loaded_fonts[filename]
        
        font_path = get_font_path(filename)
        if not font_path.exists():
            print(f"Warning: Font file not found: {font_path}")
            return -1
        
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            FontManager._loaded_fonts[filename] = font_id
            print(f"Font loaded successfully: {filename}")
        else:
            print(f"Failed to load font: {filename}")
        
        return font_id
    
    @staticmethod
    def get_font_family(filename: str) -> str | None:
        """
        Get the font family name from a font file.
        
        Args:
            filename: Font filename
            
        Returns:
            str: Font family name if successful, None if failed
        """
        font_id = FontManager.load_font(filename)
        if font_id == -1:
            return None
        
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            return font_families[0]
        return None
    
    @staticmethod
    def create_font(
        font_family: str | None = None,
        font_filename: str | None = None,
        point_size: int = 10,
        weight: int = QFont.Weight.Normal,
        italic: bool = False
    ) -> QFont:
        """
        Create a QFont object.
        
        Args:
            font_family: Font family name (if None, will try to load from font_filename)
            font_filename: Font filename to load (e.g., "Roboto-Regular.ttf")
            point_size: Font size in points
            weight: Font weight (QFont.Weight.Normal, QFont.Weight.Bold, etc.)
            italic: Whether the font is italic
            
        Returns:
            QFont: Font object
        """
        # 如果提供了字體文件名，先加載並獲取字體族名
        if font_filename:
            family = FontManager.get_font_family(font_filename)
            if family:
                font_family = family
        
        # 創建字體對象
        if font_family:
            font = QFont(font_family, point_size, weight, italic)
        else:
            # 如果沒有指定字體，使用系統默認字體
            font = QFont()
            font.setPointSize(point_size)
            font.setWeight(weight)
            font.setItalic(italic)
        
        return font
    
    @staticmethod
    def get_default_font(point_size: int = 10) -> QFont:
        """
        Get the default system font.
        
        Args:
            point_size: Font size in points
            
        Returns:
            QFont: Default font object
        """
        font = QFont()
        font.setPointSize(point_size)
        return font
    
    @staticmethod
    def preload_fonts(*font_filenames: str) -> dict[str, bool]:
        """
        Preload multiple font files.
        
        Args:
            *font_filenames: Font filenames to load (can use predefined names or paths)
                            Examples:
                            - "noto_tc_regular" (predefined name)
                            - "Noto_Sans_TC/static/NotoSansTC-Regular.ttf" (full path)
                            
        Returns:
            dict: Dictionary mapping filename to success status
        """
        results = {}
        for filename in font_filenames:
            # Check if it's a predefined font name
            actual_path = FontManager.FONT_PATHS.get(filename, filename)
            font_id = FontManager.load_font(actual_path)
            results[filename] = font_id != -1
        return results
    
    @staticmethod
    def get_font_by_name(name: str, point_size: int = 10, weight: int = QFont.Weight.Normal) -> QFont:
        """
        Get a font by predefined name.
        
        Args:
            name: Predefined font name (e.g., "noto_tc_regular", "roboto_bold")
            point_size: Font size in points
            weight: Font weight (optional, will use font file's weight if available)
            
        Returns:
            QFont: Font object
        """
        if name not in FontManager.FONT_PATHS:
            print(f"Warning: Unknown font name '{name}'. Available: {list(FontManager.FONT_PATHS.keys())}")
            return FontManager.get_default_font(point_size)
        
        font_path = FontManager.FONT_PATHS[name]
        return FontManager.create_font(font_filename=font_path, point_size=point_size, weight=weight)
    
    @staticmethod
    def get_noto_tc_font(weight: str = 'regular', point_size: int = 10) -> QFont:
        """
        Convenience method to get Noto Sans TC font.
        
        Args:
            weight: Font weight ('regular', 'bold', 'medium', 'light', 'semibold')
            point_size: Font size in points
            
        Returns:
            QFont: Noto Sans TC font object
        """
        weight_map = {
            'regular': 'noto_tc_regular',
            'bold': 'noto_tc_bold',
            'medium': 'noto_tc_medium',
            'light': 'noto_tc_light',
            'semibold': 'noto_tc_semibold',
        }
        
        font_name = weight_map.get(weight.lower(), 'noto_tc_regular')
        return FontManager.get_font_by_name(font_name, point_size=point_size)
    
    @staticmethod
    def get_roboto_font(weight: str = 'regular', point_size: int = 10) -> QFont:
        """
        Convenience method to get Roboto font.
        
        Args:
            weight: Font weight ('regular', 'bold', 'medium', 'light')
            point_size: Font size in points
            
        Returns:
            QFont: Roboto font object
        """
        weight_map = {
            'regular': 'roboto_regular',
            'bold': 'roboto_bold',
            'medium': 'roboto_medium',
            'light': 'roboto_light',
        }
        
        font_name = weight_map.get(weight.lower(), 'roboto_regular')
        return FontManager.get_font_by_name(font_name, point_size=point_size)

