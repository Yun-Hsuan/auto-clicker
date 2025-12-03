"""
Orange Clicker Main Application Entry Point
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from frontend.views.main_window import MainWindow
from frontend.utils.icon_manager import IconManager
from frontend.utils.font_manager import FontManager
from frontend.i18n.translation_manager import TranslationManager

# Configure logging to show debug messages in terminal
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


def main():
    """Main function to launch the application."""
    # Create the application instance
    app = QApplication(sys.argv)

    # Set up i18n (default to English, fallback to English)
    # TODO: later load language from a config file or settings UI
    TranslationManager.set_language("en", fallback_lang="en")

    # Preload fonts at app startup so the entire application can use them
    # Using predefined font names (recommended)
    FontManager.preload_fonts(
        "noto_tc_regular",  # Noto Sans TC Regular (for Chinese)
        "noto_tc_bold",     # Noto Sans TC Bold
        "roboto_regular",   # Roboto Regular (for English)
    )
    
    # Set the application icon (used for taskbar, system tray, etc.)
    app_icon = IconManager.get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Set the application's default font (optional)
    # This will be used as the default font for all widgets
    default_font = FontManager.get_noto_tc_font("regular", point_size=10)
    app.setFont(default_font)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application's event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
