"""
Main window view
GUI interface component
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PySide6.QtCore import Qt
from frontend.controllers.clicker_controller import ClickerController
from frontend.utils.icon_manager import IconManager
from frontend.utils.font_manager import FontManager
from frontend.i18n.translation_manager import t, TranslationManager


class MainWindow(QMainWindow):
    """Main window class"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        self.controller = ClickerController()
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Set window title and size
        self.setWindowTitle(t("app.title", default="Orange Clicker"))
        self.setGeometry(100, 100, 400, 300)

        # Create menu bar with Settings, Language and Help menus
        menu_bar = self.menuBar()

        # Settings menu
        self.settings_menu = menu_bar.addMenu("")
        self.settings_preferences_action = self.settings_menu.addAction("")
        self.settings_preferences_action.triggered.connect(self.on_open_settings)

        # Language submenu under Settings
        self.language_menu = self.settings_menu.addMenu("")
        self.language_en_action = self.language_menu.addAction("")
        self.language_en_action.triggered.connect(self.on_set_language_en)

        self.language_zh_tw_action = self.language_menu.addAction("")
        self.language_zh_tw_action.triggered.connect(self.on_set_language_zh_tw)

        # Help menu
        self.help_menu = menu_bar.addMenu("")
        self.help_user_guide_action = self.help_menu.addAction("")
        self.help_user_guide_action.triggered.connect(self.on_open_user_guide)

        self.help_about_action = self.help_menu.addAction("")
        self.help_about_action.triggered.connect(self.on_about)
        
        # Set window icon (use 256x256, system will auto-scale)
        app_icon = IconManager.get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create label
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set label font (if you have custom font files, you can use them like this)
        # label_font = FontManager.create_font(font_filename="your_font.ttf", point_size=12)
        # self.label.setFont(label_font)
        layout.addWidget(self.label)
        
        # Create button
        self.button = QPushButton()
        # Set button icon (uses medium size)
        button_icon = IconManager.get_icon_by_name('medium')
        if not button_icon.isNull():
            self.button.setIcon(button_icon)
        # Set button font (if you have custom font files, you can use them like this)
        # button_font = FontManager.create_font(font_filename="your_font.ttf", point_size=11)
        # self.button.setFont(button_font)
        self.button.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.button)
        
        # Add stretchable space
        layout.addStretch()

        # Apply initial translations to all UI elements
        self.apply_translations()
    
    def on_button_clicked(self):
        """Button click event handler"""
        # Get message from controller
        message = self.controller.handle_button_click()
        
        # Show message box
        QMessageBox.information(
            self,
            t("dialog.message.title", default="Message"),
            message,
        )
        
        # Update label as well
        self.label.setText(message)

    # ---- Menu actions ----

    def apply_translations(self) -> None:
        """Apply translations to all translatable UI elements."""
        # Window title
        self.setWindowTitle(t("app.title", default="Orange Clicker"))

        # Menus and actions
        self.settings_menu.setTitle(t("menu.settings", default="Settings"))
        self.settings_preferences_action.setText(
            t("menu.settings.preferences", default="Preferences")
        )

        self.language_menu.setTitle(
            t("menu.settings.language", default="Language")
        )
        self.language_en_action.setText(
            t("menu.settings.language.en", default="English")
        )
        self.language_zh_tw_action.setText(
            t("menu.settings.language.zh-TW", default="Traditional Chinese")
        )

        self.help_menu.setTitle(t("menu.help", default="Help"))
        self.help_user_guide_action.setText(
            t("menu.help.user_guide", default="User Guide")
        )
        self.help_about_action.setText(
            t("menu.help.about", default="About")
        )

        # Main content
        self.label.setText(
            t(
                "main.label.message",
                default="Click the button to show a message",
            )
        )
        self.button.setText(
            t("main.button.click", default="Click Me")
        )

    def on_open_settings(self):
        """Open settings dialog (placeholder)."""
        QMessageBox.information(
            self,
            t("menu.settings", default="Settings"),
            "Settings dialog is not implemented yet.",
        )

    def on_open_user_guide(self):
        """Open user guide (placeholder)."""
        QMessageBox.information(
            self,
            t("menu.help.user_guide", default="User Guide"),
            "User guide is not implemented yet.",
        )

    def on_about(self):
        """Show About dialog."""
        QMessageBox.information(
            self,
            t("dialog.about.title", default="About Orange Clicker"),
            "Orange Clicker\nA simple auto-clicker demo built with PySide6.",
        )

    def on_set_language_en(self):
        """Switch UI language to English."""
        TranslationManager.set_language("en", fallback_lang="en")
        self.apply_translations()

    def on_set_language_zh_tw(self):
        """Switch UI language to Traditional Chinese."""
        TranslationManager.set_language("zh-TW", fallback_lang="en")
        self.apply_translations()

