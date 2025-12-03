"""
Theme Manager Module
Provides theme management functionality for light and dark modes.
"""

from typing import Dict, Literal


class ThemeManager:
    """Theme manager for light and dark mode styles."""
    
    # Color schemes for ProfileCard and other components
    COLOR_SCHEMES = {
        "light": {
            "blue": {
                "bg": "#e3f2fd",      # Light blue background
                "border": "#90caf9",   # Blue border
                "text": "#000000",     # Black text
                "text_secondary": "#666666"  # Gray text
            },
            "orange": {
                "bg": "#fff3e0",      # Light orange background
                "border": "#ffb74d",   # Orange border
                "text": "#000000",     # Black text
                "text_secondary": "#666666"  # Gray text
            }
        },
        "dark": {
            "blue": {
                "bg": "#1e3a5f",      # Dark blue background
                "border": "#64b5f6",   # Light blue border
                "text": "#ffffff",     # White text
                "text_secondary": "#b0b0b0"  # Light gray text
            },
            "orange": {
                "bg": "#5d4037",      # Dark orange background
                "border": "#ff9800",   # Orange border
                "text": "#ffffff",     # White text
                "text_secondary": "#b0b0b0"  # Light gray text
            }
        }
    }
    
    # Orange color palette for buttons and switches
    ORANGE_COLORS = {
        "primary": "#ff9800",      # Main orange
        "hover": "#f57c00",        # Darker orange on hover
        "pressed": "#e65100",      # Even darker orange when pressed
        "toggle_unchecked": "#ff9800"  # Orange for toggle switch (unchecked)
    }
    
    # Blue color palette for buttons
    BLUE_COLORS = {
        "primary": "#2196f3",      # Main blue
        "hover": "#1976d2",        # Darker blue on hover
        "pressed": "#1565c0",      # Even darker blue when pressed
    }
    
    # Gray color palette for buttons (default state)
    GRAY_COLORS = {
        "light": {
            "default": "#cccccc",   # Light gray for default state
            "text": "#666666",      # Gray text
        },
        "dark": {
            "default": "#555555",   # Dark gray for default state
            "text": "#888888",      # Light gray text
        }
    }
    
    # Tiffany Blue (Cyan-Green) color palette for active status
    TIFFANY_COLORS = {
        "light": "#0ABAB5",        # Tiffany Blue for light mode
        "dark": "#0A9B96",          # Darker Tiffany Blue for dark mode
        "toggle_checked": "#0ABAB5",  # Tiffany Blue for toggle switch (checked/active)
        # Light backgrounds for ClickStepItem
        "bg_light": "#E0F7F6",     # Very light Tiffany Blue for light mode background
        "bg_dark": "#0A5A55",      # Darker Tiffany Blue for dark mode background
    }
    
    # Pink/Red color palette for clicking state (not too red, more pinkish)
    CLICKING_COLORS = {
        "light": {
            "bg": "#FFE5E5",       # Light pink background for light mode
            "border": "#FFB3BA",   # Pink border for light mode
            "text": "#000000",     # Black text
            "text_secondary": "#666666"  # Gray text
        },
        "dark": {
            "bg": "#5A2A2A",       # Dark pink/red background for dark mode
            "border": "#FF8A95",   # Pink border for dark mode
            "text": "#ffffff",     # White text
            "text_secondary": "#b0b0b0"  # Light gray text
        }
    }
    
    # Panel background colors for left and right panels
    PANEL_COLORS = {
        "light": {
            "left": "#f5f5f5",     # Slightly gray for left panel
            "right": "#fafafa"     # Slightly lighter for right panel
        },
        "dark": {
            "left": "#252526",     # Darker for left panel
            "right": "#2d2d2d"     # Slightly lighter for right panel
        }
    }

    # Light theme stylesheet
    LIGHT_THEME = """
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        QWidget {
            background-color: #ffffff;
            color: #000000;
        }
        QLabel {
            background-color: transparent;
            color: #000000;
        }
        QPushButton {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: bold;
        }
        QGroupBox#ProfileNameGroupBox {
            border: 2px solid #2196f3;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            background-color: #f8f9fa;
        }
        QGroupBox#HotkeyGroupBox {
            border: 2px solid #2196f3;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            background-color: #f8f9fa;
        }
        /* ClickIntervalGroupBox and ClickSettingsGroupBox - Tiffany Blue Theme - Light Mode */
        QGroupBox#ClickIntervalGroupBox, QGroupBox#ClickSettingsGroupBox {
            background-color: #E0F7F6;
            border: 2px solid #0ABAB5;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            color: #000000;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
        }
        /* Modern QLineEdit */
        QLineEdit {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px 12px;
            background-color: #ffffff;
            font-size: 13px;
            selection-background-color: #2196f3;
            selection-color: #ffffff;
        }
        QLineEdit:focus {
            border: 2px solid #2196f3;
            background-color: #ffffff;
        }
        QLineEdit:hover {
            border: 2px solid #90caf9;
        }
        /* Modern QComboBox */
        QComboBox {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px 32px 8px 12px;
            background-color: #ffffff;
            font-size: 13px;
            min-height: 20px;
        }
        QComboBox:hover {
            border: 2px solid #90caf9;
        }
        QComboBox:focus {
            border: 2px solid #2196f3;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            background-color: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #666666;
            width: 0;
            height: 0;
            margin-right: 8px;
        }
        QComboBox::down-arrow:hover {
            border-top-color: #2196f3;
        }
        QComboBox QAbstractItemView {
            border: 2px solid #2196f3;
            border-radius: 8px;
            background-color: #ffffff;
            selection-background-color: #e3f2fd;
            selection-color: #1976d2;
            padding: 4px;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 12px;
            border-radius: 4px;
            min-height: 20px;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #e3f2fd;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #2196f3;
            color: #ffffff;
        }
        /* Modern QSpinBox */
        QSpinBox {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px 12px;
            background-color: #ffffff;
            font-size: 13px;
            min-height: 20px;
        }
        QSpinBox:hover {
            border: 2px solid #90caf9;
        }
        QSpinBox:focus {
            border: 2px solid #2196f3;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            border: none;
            background-color: transparent;
            width: 20px;
            border-radius: 4px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #e3f2fd;
        }
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
            background-color: #bbdefb;
        }
        QSpinBox::up-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 5px solid #666666;
            width: 0;
            height: 0;
            margin: 2px;
        }
        QSpinBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid #666666;
            width: 0;
            height: 0;
            margin: 2px;
        }
        QSpinBox::up-arrow:hover {
            border-bottom-color: #2196f3;
        }
        QSpinBox::down-arrow:hover {
            border-top-color: #2196f3;
        }
        QLabel#ProfileNameTitle, QLabel#HotkeyTitle, QLabel#ClickIntervalTitle, QLabel#ClickSettingsTitle {
            font-weight: bold;
            font-size: 14px;
        }
        QLabel#HotkeyStartLabel, QLabel#HotkeyEndLabel {
            font-weight: bold;
            font-size: 13px;
        }
        /* ClickStepItem Styles - Light Mode */
        QGroupBox#ClickStepItemGroupBox {
            background-color: #E0F7F6;
            border: 2px solid #0ABAB5;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            color: #000000;
        }
        QLineEdit#ClickStepNameEdit {
            color: #000000;
            background-color: transparent;
            border: 2px solid #0ABAB5;
            border-radius: 6px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 13px;
        }
        QLineEdit#ClickStepNameEdit:focus {
            border: 2px solid #0ABAB5;
            background-color: #E0F7F6;
        }
        QLabel#ClickStepPositionLabel, QLabel#ClickStepButtonLabel, QLabel#ClickStepCountLabel {
            /* Slightly deeper Tiffany Blue in light mode for better readability */
            color: #0A9B96;
            font-weight: bold;
        }
        QLabel#ClickStepPositionValue {
            color: #000000;
        }
        QTabWidget::pane {
            border: 2px solid #2196f3;
            border-top-left-radius: 0px;
            border-top-right-radius: 4px;
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #666666;
            padding: 8px 16px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
            border: none;
        }
        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #1565c0;
            border: 2px solid #2196f3;
            border-bottom: none;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background-color: #f0f0f0;
            color: #888888;
        }
        QMenuBar {
            background-color: #f5f5f5;
            color: #000000;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
        }
        QMenu::item:selected {
            background-color: #e0e0e0;
        }
        /* Modern flat scrollbar */
        QScrollBar:vertical {
            background-color: #f5f5f5;
            width: 12px;
            border: none;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background-color: #c0c0c0;
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #a0a0a0;
        }
        QScrollBar::handle:vertical:pressed {
            background-color: #808080;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            border: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
        QScrollBar:horizontal {
            background-color: #f5f5f5;
            height: 12px;
            border: none;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background-color: #c0c0c0;
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #a0a0a0;
        }
        QScrollBar::handle:horizontal:pressed {
            background-color: #808080;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
            border: none;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: transparent;
        }
    """

    # Dark theme stylesheet
    DARK_THEME = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLabel {
            background-color: transparent;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QPushButton:pressed {
            background-color: #2d2d2d;
        }
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: bold;
            color: #ffffff;
        }
        QGroupBox#ProfileNameGroupBox {
            border: 2px solid #64b5f6;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            background-color: #252526;
        }
        QGroupBox#HotkeyGroupBox {
            border: 2px solid #64b5f6;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            background-color: #252526;
        }
        /* ClickIntervalGroupBox and ClickSettingsGroupBox - Tiffany Blue Theme - Dark Mode */
        QGroupBox#ClickIntervalGroupBox, QGroupBox#ClickSettingsGroupBox {
            background-color: #0A5A55;
            border: 2px solid #0A9B96;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            color: #ffffff;
        }
        /* QComboBox and QSpinBox within ClickIntervalGroupBox and ClickSettingsGroupBox - Dark Mode */
        QGroupBox#ClickIntervalGroupBox QComboBox, QGroupBox#ClickSettingsGroupBox QComboBox {
            color: #ffffff;
        }
        QGroupBox#ClickIntervalGroupBox QComboBox QAbstractItemView {
            color: #ffffff;
        }
        QGroupBox#ClickIntervalGroupBox QSpinBox, QGroupBox#ClickSettingsGroupBox QSpinBox {
            color: #ffffff;
        }
        /* Labels within ClickIntervalGroupBox and ClickSettingsGroupBox - Dark Mode */
        QGroupBox#ClickIntervalGroupBox QLabel, QGroupBox#ClickSettingsGroupBox QLabel {
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
        }
        /* Modern QLineEdit */
        QLineEdit {
            border: 2px solid #555555;
            border-radius: 8px;
            padding: 8px 12px;
            background-color: #2d2d2d;
            color: #ffffff;
            font-size: 13px;
            selection-background-color: #64b5f6;
            selection-color: #ffffff;
        }
        QLineEdit:focus {
            border: 2px solid #64b5f6;
            background-color: #2d2d2d;
        }
        QLineEdit:hover {
            border: 2px solid #90caf9;
        }
        /* Modern QComboBox */
        QComboBox {
            border: 2px solid #555555;
            border-radius: 8px;
            padding: 8px 32px 8px 12px;
            background-color: #2d2d2d;
            color: #ffffff;
            font-size: 13px;
            min-height: 20px;
        }
        QComboBox:hover {
            border: 2px solid #90caf9;
        }
        QComboBox:focus {
            border: 2px solid #64b5f6;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
            background-color: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #b0b0b0;
            width: 0;
            height: 0;
            margin-right: 8px;
        }
        QComboBox::down-arrow:hover {
            border-top-color: #64b5f6;
        }
        QComboBox QAbstractItemView {
            border: 2px solid #64b5f6;
            border-radius: 8px;
            background-color: #2d2d2d;
            selection-background-color: #1565c0;
            selection-color: #ffffff;
            padding: 4px;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 12px;
            border-radius: 4px;
            min-height: 20px;
            color: #ffffff;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #3c3c3c;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #64b5f6;
            color: #ffffff;
        }
        /* Modern QSpinBox */
        QSpinBox {
            border: 2px solid #555555;
            border-radius: 8px;
            padding: 8px 12px;
            background-color: #2d2d2d;
            color: #ffffff;
            font-size: 13px;
            min-height: 20px;
        }
        QSpinBox:hover {
            border: 2px solid #90caf9;
        }
        QSpinBox:focus {
            border: 2px solid #64b5f6;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            border: none;
            background-color: transparent;
            width: 20px;
            border-radius: 4px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #3c3c3c;
        }
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
            background-color: #4a4a4a;
        }
        QSpinBox::up-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 5px solid #b0b0b0;
            width: 0;
            height: 0;
            margin: 2px;
        }
        QSpinBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid #b0b0b0;
            width: 0;
            height: 0;
            margin: 2px;
        }
        QSpinBox::up-arrow:hover {
            border-bottom-color: #64b5f6;
        }
        QSpinBox::down-arrow:hover {
            border-top-color: #64b5f6;
        }
        QLabel#ProfileNameTitle, QLabel#HotkeyTitle, QLabel#ClickIntervalTitle, QLabel#ClickSettingsTitle {
            font-weight: bold;
            font-size: 14px;
        }
        QLabel#HotkeyStartLabel, QLabel#HotkeyEndLabel {
            font-weight: bold;
            font-size: 13px;
        }
        /* ClickStepItem Styles - Dark Mode */
        QGroupBox#ClickStepItemGroupBox {
            background-color: #0A5A55;
            border: 2px solid #0A9B96;
            border-radius: 12px;
            margin-top: 8px;
            padding-top: 8px;
            color: #ffffff;
        }
        QLineEdit#ClickStepNameEdit {
            color: #ffffff;
            background-color: transparent;
            border: 2px solid #0A9B96;
            border-radius: 6px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 13px;
        }
        QLineEdit#ClickStepNameEdit:focus {
            border: 2px solid #0A9B96;
            background-color: #0A5A55;
        }
        QLabel#ClickStepPositionLabel, QLabel#ClickStepButtonLabel, QLabel#ClickStepCountLabel {
            color: #ffffff;
            font-weight: bold;
        }
        QLabel#ClickStepPositionValue {
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 2px solid #64b5f6;
            border-top-left-radius: 0px;
            border-top-right-radius: 4px;
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            background-color: #1e1e1e;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #b0b0b0;
            padding: 8px 16px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
            border: none;
        }
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            color: #64b5f6;
            border: 2px solid #64b5f6;
            border-bottom: none;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background-color: #4a4a4a;
            color: #d0d0d0;
        }
        QMenuBar {
            background-color: #252526;
            color: #ffffff;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #3c3c3c;
        }
        QMenu {
            background-color: #252526;
            color: #ffffff;
            border: 1px solid #3c3c3c;
        }
        QMenu::item:selected {
            background-color: #3c3c3c;
        }
        /* Modern flat scrollbar */
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
            border: none;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background-color: #505050;
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #606060;
        }
        QScrollBar::handle:vertical:pressed {
            background-color: #707070;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            border: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
            border: none;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background-color: #505050;
            min-width: 30px;
            border-radius: 6px;
            margin: 2px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #606060;
        }
        QScrollBar::handle:horizontal:pressed {
            background-color: #707070;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
            border: none;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: transparent;
        }
    """

    @staticmethod
    def get_theme(theme_name: str) -> str:
        """
        Get theme stylesheet by name.

        Args:
            theme_name: Theme name ('light' or 'dark')

        Returns:
            str: Theme stylesheet
        """
        themes: Dict[str, str] = {
            'light': ThemeManager.LIGHT_THEME,
            'dark': ThemeManager.DARK_THEME,
        }
        return themes.get(theme_name.lower(), ThemeManager.LIGHT_THEME)

    @staticmethod
    def apply_theme(widget, theme_name: str) -> None:
        """
        Apply theme to a widget.

        Args:
            widget: QWidget to apply theme to
            theme_name: Theme name ('light' or 'dark')
        """
        stylesheet = ThemeManager.get_theme(theme_name)
        widget.setStyleSheet(stylesheet)
    
    @staticmethod
    def get_color_scheme(theme_name: str, primary_color: Literal["blue", "orange"] = "blue") -> Dict[str, str]:
        """
        Get color scheme for a specific theme and primary color.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
            primary_color: Primary color ('blue' or 'orange')
            
        Returns:
            dict: Color scheme dictionary with keys: bg, border, text, text_secondary
        """
        theme = theme_name.lower()
        color = primary_color.lower()
        
        if theme in ThemeManager.COLOR_SCHEMES and color in ThemeManager.COLOR_SCHEMES[theme]:
            return ThemeManager.COLOR_SCHEMES[theme][color]
        
        # Fallback to light blue
        return ThemeManager.COLOR_SCHEMES["light"]["blue"]
    
    @staticmethod
    def get_orange_colors() -> Dict[str, str]:
        """
        Get orange color palette for buttons and switches.
        
        Returns:
            dict: Orange color dictionary with keys: primary, hover, pressed, toggle_unchecked
        """
        return ThemeManager.ORANGE_COLORS.copy()
    
    @staticmethod
    def get_blue_colors() -> Dict[str, str]:
        """
        Get blue color palette for buttons.
        
        Returns:
            dict: Blue color dictionary with keys: primary, hover, pressed
        """
        return ThemeManager.BLUE_COLORS.copy()
    
    @staticmethod
    def get_panel_colors(theme_name: str) -> Dict[str, str]:
        """
        Get panel background colors for left and right panels.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
            
        Returns:
            dict: Panel color dictionary with keys: left, right
        """
        theme = theme_name.lower()
        if theme in ThemeManager.PANEL_COLORS:
            return ThemeManager.PANEL_COLORS[theme].copy()
        # Fallback to light theme
        return ThemeManager.PANEL_COLORS["light"].copy()
    
    @staticmethod
    def get_tiffany_colors() -> Dict[str, str]:
        """
        Get Tiffany Blue color palette for active status and toggles.
        
        Returns:
            dict: Tiffany Blue color dictionary with keys: light, dark, toggle_checked
        """
        return ThemeManager.TIFFANY_COLORS.copy()
    
    @staticmethod
    def get_clicking_colors(theme_name: Literal["light", "dark"]) -> Dict[str, str]:
        """
        Get clicking state colors (pinkish red) for a specific theme.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        
        Returns:
            dict: Clicking color dictionary with keys: bg, border, text, text_secondary
        """
        theme = theme_name.lower()
        if theme in ThemeManager.CLICKING_COLORS:
            return ThemeManager.CLICKING_COLORS[theme].copy()
        # Fallback to light theme
        return ThemeManager.CLICKING_COLORS["light"].copy()
    
    @staticmethod
    def get_gray_colors(theme_name: Literal["light", "dark"]) -> Dict[str, str]:
        """
        Get gray color palette for buttons (default state).
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        
        Returns:
            dict: Gray color dictionary with keys: default, text
        """
        theme = theme_name.lower()
        if theme in ThemeManager.GRAY_COLORS:
            return ThemeManager.GRAY_COLORS[theme].copy()
        # Fallback to light theme
        return ThemeManager.GRAY_COLORS["light"].copy()

