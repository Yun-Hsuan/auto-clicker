"""
Main window view
GUI interface component
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QLineEdit,
    QFormLayout,
    QSplitter,
    QScrollArea,
    QCheckBox,
    QGroupBox,
    QTabWidget,
    QStackedWidget,
    QSpinBox,
    QComboBox,
    QPlainTextEdit,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QIcon
from frontend.controllers.clicker_controller import ClickerController
from frontend.utils.icon_manager import IconManager
from frontend.utils.font_manager import FontManager
from frontend.utils.theme_manager import ThemeManager
from frontend.utils.paths import get_icon_path
from frontend.i18n.translation_manager import t, TranslationManager
from frontend.components.profile_card import ProfileCard
from frontend.components.status_badge import StatusBadge
from frontend.components.profile_name_group import ProfileNameGroup
from frontend.components.hotkey_group import HotkeyGroup
from frontend.components.cursor_position_tab import CursorPositionTab
from frontend.components.click_path_tab import ClickPathTab
from backend.services.config_manager import ConfigManager
from backend.services.click_path_hotkey_service import ClickPathHotkeyService
from backend.services.profile_service import ProfileService
from backend.services.cursor_clicker_service import CursorClickerService
from backend.services.profile_hotkey_service import ProfileHotkeyService
from backend.services.click_path_executor_service import ClickPathExecutorService
from frontend.i18n.translation_manager import TranslationManager
from frontend.utils.ui_log_handler import UILogHandler
import random
import uuid
import logging


class MainWindow(QMainWindow):
    """Main window class"""
    
    # Signals to marshal global hotkey callbacks back to the GUI thread
    request_start_click_path_recording = Signal()
    request_stop_click_path_recording = Signal()
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        self.controller = ClickerController()
        
        # Initialize config manager (automatically creates config directory on first run)
        self.config_manager = ConfigManager()
        
        # Load configuration
        config = self.config_manager.load_config()
        
        # Load app settings
        app_settings = config.get("app_settings", {})
        self.current_theme = app_settings.get("theme", "light")
        current_language = app_settings.get("language", "en")
        TranslationManager.set_language(current_language, fallback_lang="en")
        self.debug_mode = app_settings.get("debug_mode", False)
        
        # Restore window geometry
        window_geometry = app_settings.get("window_geometry", {})
        if window_geometry:
            self.setGeometry(
                window_geometry.get("x", 100),
                window_geometry.get("y", 100),
                window_geometry.get("width", 800),
                window_geometry.get("height", 600)
            )
        
        self.profiles = []  # Store profile data: [{"name": "Profile 1", "start_hotkey": "", "end_hotkey": "", "is_active": False, "cursor_interval": 100, "cursor_button": "left", "cursor_count": 0, "click_path": [], "card": ProfileCard}, ...]
        self.current_profile_index = -1  # Currently selected profile index
        
        # Initialize hotkey service for Click Path recording
        self.hotkey_service = ClickPathHotkeyService()
        # Initialize state: no profile selected initially
        self.hotkey_service.set_profile_selected(False)
        
        # Initialize cursor clicker service for Cursor Position clicking
        self.cursor_clicker_service = CursorClickerService()
        
        # Initialize Click Path Executor Service
        self.click_path_executor_service = ClickPathExecutorService()
        
        # Initialize profile hotkey service (manages hotkeys for each profile)
        # Pass both cursor clicker and click path executor services
        self.profile_hotkey_service = ProfileHotkeyService(
            self.cursor_clicker_service,
            self.click_path_executor_service
        )
        
        # Initialize logger
        self._logger = logging.getLogger(__name__)
        
        self.init_ui()
        
        # Load profiles from config (after UI is initialized)
        self._load_profiles_from_config(config)
        
        # Register global hotkeys after UI is initialized
        self._register_global_hotkeys()
    
    def init_ui(self):
        """Initialize user interface"""
        # Set window title and size
        self.setWindowTitle(t("app.title", default="Orange Clicker"))
        self.setGeometry(100, 100, 800, 600)

        # Create menu bar with Settings, View, and Help menus (in that order)
        menu_bar = self.menuBar()

        # Settings menu (first)
        self.settings_menu = menu_bar.addMenu("")
        self.settings_preferences_action = self.settings_menu.addAction("")
        self.settings_preferences_action.triggered.connect(self.on_open_settings)

        # Language submenu under Settings
        self.language_menu = self.settings_menu.addMenu("")
        # Set minimum width for language menu to accommodate "Traditional Chinese" text
        self.language_menu.setMinimumWidth(180)
        self.language_en_action = self.language_menu.addAction("")
        self.language_en_action.triggered.connect(self.on_set_language_en)

        self.language_zh_tw_action = self.language_menu.addAction("")
        self.language_zh_tw_action.triggered.connect(self.on_set_language_zh_tw)
        
        # Debug Mode toggle (checkable action)
        self.settings_menu.addSeparator()
        self.debug_mode_action = self.settings_menu.addAction("")
        self.debug_mode_action.setCheckable(True)
        self.debug_mode_action.triggered.connect(self.on_toggle_debug_mode)

        # View menu (second)
        self.view_menu = menu_bar.addMenu("")

        # Theme submenu under View
        self.theme_menu = self.view_menu.addMenu("")
        self.theme_light_action = self.theme_menu.addAction("")
        self.theme_light_action.triggered.connect(self.on_set_theme_light)
        
        self.theme_dark_action = self.theme_menu.addAction("")
        self.theme_dark_action.triggered.connect(self.on_set_theme_dark)

        # Help menu (third)
        self.help_menu = menu_bar.addMenu("")
        self.help_user_guide_action = self.help_menu.addAction("")
        self.help_user_guide_action.triggered.connect(self.on_open_user_guide)

        self.help_about_action = self.help_menu.addAction("")
        self.help_about_action.triggered.connect(self.on_about)
        
        # Set window icon (use 256x256, system will auto-scale)
        app_icon = IconManager.get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        # Create central widget with splitter (left-right layout)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # Create splitter for resizable left-right panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # === Left Panel: Profile List (Card-based) ===
        self.left_panel = QWidget()
        self.left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)
        self.left_panel.setLayout(left_layout)
        
        # Add Profile button
        self.add_profile_button = QPushButton()
        self.add_profile_button.setObjectName("AddProfileButton")
        self.add_profile_button.clicked.connect(self.on_add_profile)
        left_layout.addWidget(self.add_profile_button)
        
        # Scroll area for profile cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container widget for cards
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)  # Spacing between cards
        self.cards_layout.addStretch()  # Push cards to top
        self.cards_container.setLayout(self.cards_layout)
        
        scroll_area.setWidget(self.cards_container)
        left_layout.addWidget(scroll_area)
        
        splitter.addWidget(self.left_panel)
        
        # === Right Panel: Profile Settings ===
        self.right_panel = QWidget()
        self.right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        self.right_panel.setLayout(right_layout)
        
        # Use QStackedWidget to switch between welcome and settings
        self.right_stacked = QStackedWidget()
        right_layout.addWidget(self.right_stacked)
        
        # === Welcome Page (shown when no profile is selected) ===
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_layout.setContentsMargins(40, 40, 40, 40)
        welcome_layout.setSpacing(24)
        self.welcome_page.setLayout(welcome_layout)
        
        # Add stretch before content to push it to center
        welcome_layout.addStretch()
        
        # Orange icon (256x256)
        self.welcome_icon_label = QLabel()
        icon = IconManager.get_icon_by_size(256)
        if not icon.isNull():
            pixmap = icon.pixmap(256, 256)
            self.welcome_icon_label.setPixmap(pixmap)
        self.welcome_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(self.welcome_icon_label)
        
        # Welcome message (random blessing)
        self.welcome_message_label = QLabel()
        self.welcome_message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_message_label.setWordWrap(True)
        self.welcome_message_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        welcome_layout.addWidget(self.welcome_message_label)
        
        # Add stretch after content to center it vertically
        welcome_layout.addStretch()
        
        self.right_stacked.addWidget(self.welcome_page)
        
        # === Settings Page (shown when profile is selected) ===
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(16, 16, 16, 16)
        settings_layout.setSpacing(16)
        self.settings_page.setLayout(settings_layout)
        
        # === Status Badge (above Profile Name) ===
        self.status_badge = StatusBadge()
        self.status_badge.set_theme(self.current_theme)
        settings_layout.addWidget(self.status_badge)
        
        # === Block 1: Profile Name Group + Hotkey Group (same row) ===
        # Use a horizontal layout so that Profile Name and Hotkey each take half width and share the same height.
        top_row_layout = QHBoxLayout()
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(16)
        # Align both groups to the top so their content lines up visually
        top_row_layout.setAlignment(Qt.AlignTop)

        # Profile Name Group
        self.profile_name_group = ProfileNameGroup()
        self.profile_name_group.name_changed.connect(self.on_profile_name_changed)
        
        # Hotkey Group
        self.hotkey_group = HotkeyGroup()
        self.hotkey_group.start_hotkey_changed.connect(self.on_profile_start_hotkey_changed)
        self.hotkey_group.end_hotkey_changed.connect(self.on_profile_end_hotkey_changed)

        # Ensure both groups have the same minimum height so they look visually balanced
        hotkey_height = self.hotkey_group.sizeHint().height()
        self.profile_name_group.setMinimumHeight(hotkey_height)

        top_row_layout.addWidget(self.profile_name_group, 1, Qt.AlignTop)
        top_row_layout.addWidget(self.hotkey_group, 1, Qt.AlignTop)

        settings_layout.addLayout(top_row_layout)
        
        # === Block 3: Tabs (Cursor Position / Click Path / Coming Soon) ===
        self.tab_widget = QTabWidget()
        
        # Tab 1: Cursor Position (Component)
        self.tab_cursor = CursorPositionTab()
        self.tab_cursor.interval_changed.connect(self.on_cursor_interval_changed)
        self.tab_cursor.click_button_changed.connect(self.on_cursor_button_changed)
        self.tab_cursor.click_count_changed.connect(self.on_cursor_count_changed)
        
        # Tab 2: Click Path Recording (Component)
        self.tab_path = ClickPathTab()
        self.tab_path.path_changed.connect(self.on_click_path_changed)
        # Listen for Click Path recording state changes (Ctrl+W / Ctrl+Q)
        self.tab_path.recording_state_changed.connect(self._on_click_path_recording_changed)
        
        # Set initial debug mode state for Click Path Tab
        self.tab_path.set_debug_mode(self.debug_mode)
        
        # Set reference for global hotkey handlers
        self._click_path_tab_ref = self.tab_path
        
        # Connect hotkey signals to UI-thread handlers
        self.request_start_click_path_recording.connect(self._start_click_path_recording_on_ui)
        self.request_stop_click_path_recording.connect(self._stop_click_path_recording_on_ui)
        
        # Tab 3: Visual Detection (Coming Soon placeholder)
        self.tab_visual = QWidget()
        visual_layout = QVBoxLayout()
        visual_layout.setContentsMargins(0, 32, 0, 0)
        visual_layout.setSpacing(16)
        self.tab_visual.setLayout(visual_layout)

        # Icon
        visual_icon_label = QLabel()
        visual_icon_label.setAlignment(Qt.AlignCenter)
        look_icon_path = get_icon_path("orange_lookfoward.png")
        if look_icon_path.exists():
            pixmap = QPixmap(str(look_icon_path))
            # Scale to a reasonable size while keeping aspect ratio
            scaled = pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            visual_icon_label.setPixmap(scaled)
        visual_layout.addWidget(visual_icon_label)

        # "Coming Soon" text
        visual_text_label = QLabel()
        visual_text_label.setAlignment(Qt.AlignCenter)
        visual_text_label.setText(
            t("main.profile.tab.visual.coming_soon", default="Coming Soon ~")
        )
        visual_text_label.setObjectName("VisualComingSoonLabel")
        visual_layout.addWidget(visual_text_label)

        # Add tabs
        self.tab_widget.addTab(self.tab_cursor, t("main.profile.tab.cursor", default="Cursor Position"))
        self.tab_widget.addTab(self.tab_path, t("main.profile.tab.path", default="Click Path"))
        self.tab_widget.addTab(self.tab_visual, t("main.profile.tab.visual", default="Visual Click"))
        
        # Connect tab change signal to track which tab is active
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Initialize hotkey service state: Click Path tab is not active initially
        self.hotkey_service.set_click_path_tab_active(False)
        
        settings_layout.addWidget(self.tab_widget, 1)  # Take remaining space
        
        # === Debug Log Area (only visible when Debug Mode is enabled) ===
        self.debug_log_area = QPlainTextEdit()
        self.debug_log_area.setObjectName("DebugLogArea")
        self.debug_log_area.setReadOnly(True)
        self.debug_log_area.setMaximumHeight(200)  # Limit height
        self.debug_log_area.setPlaceholderText(t("main.debug.log.placeholder", default="Debug logs will appear here when Debug Mode is enabled..."))
        self.debug_log_area.setVisible(self.debug_mode)  # Initially hidden unless debug mode is on
        settings_layout.addWidget(self.debug_log_area)
        
        # === Action Buttons (Reset and Save) ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(12)
        buttons_layout.addStretch()  # Push buttons to the right
        
        # Reset button
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("ResetButton")
        self.reset_button.clicked.connect(self.on_reset_clicked)
        buttons_layout.addWidget(self.reset_button)
        
        # Save button
        self.save_button = QPushButton()
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.on_save_clicked)
        buttons_layout.addWidget(self.save_button)
        
        settings_layout.addLayout(buttons_layout)
        
        self.right_stacked.addWidget(self.settings_page)
        
        # Show welcome page by default
        self.right_stacked.setCurrentWidget(self.welcome_page)
        
        splitter.addWidget(self.right_panel)
        
        # Set splitter sizes (left: 200px, right: flexible)
        splitter.setSizes([200, 400])

        # Apply initial translations to all UI elements
        self.apply_translations()
        
        # Apply initial theme (light mode by default)
        self.apply_theme(self.current_theme)
        
        # Show random welcome message
        self.update_welcome_message()
        
        # Set up timer to periodically check clicking status
        # This ensures UI updates when clicking stops due to count limit
        self._clicking_status_timer = QTimer()
        self._clicking_status_timer.timeout.connect(self._check_clicking_status)
        self._clicking_status_timer.start(500)  # Check every 500ms
        
        # Set up debug mode UI state
        if hasattr(self, 'debug_mode_action'):
            self.debug_mode_action.setChecked(self.debug_mode)
        
        # Initialize debug mode for services
        if hasattr(self, 'cursor_clicker_service'):
            import backend.services.cursor_clicker_service as cursor_service
            cursor_service.DEBUG_MODE = self.debug_mode
        if hasattr(self, 'click_path_executor_service'):
            import backend.services.click_path_executor_service as path_executor_service
            path_executor_service.DEBUG_MODE = self.debug_mode
        
        # Set up custom logging handler for UI
        self._setup_logging_handler()
    
    def apply_theme(self, theme_name: str) -> None:
        """Apply theme to the window."""
        self.current_theme = theme_name
        ThemeManager.apply_theme(self, theme_name)
    

    # ---- Menu actions ----

    def apply_translations(self) -> None:
        """Apply translations to all translatable UI elements."""
        # Window title
        self.setWindowTitle(t("app.title", default="Auto-Clicker"))

        # View menu
        self.view_menu.setTitle(t("menu.view", default="View"))
        self.theme_menu.setTitle(t("menu.view.theme", default="Theme"))
        self.theme_light_action.setText(
            t("menu.view.theme.light", default="Light Mode")
        )
        self.theme_dark_action.setText(
            t("menu.view.theme.dark", default="Dark Mode")
        )

        # Settings menu
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
        self.add_profile_button.setText(
            t("main.profile.add", default="Add Profile")
        )
        
        # Update profile name label
        if hasattr(self, 'profile_name_label'):
            self.profile_name_label.setText(
                t("main.profile.name", default="Profile Name") + ":"
            )
        
        # Update components translations
        if hasattr(self, 'profile_name_group'):
            self.profile_name_group.update_translations()
        if hasattr(self, 'hotkey_group'):
            self.hotkey_group.update_translations()
        if hasattr(self, 'tab_cursor'):
            self.tab_cursor.update_translations()
        if hasattr(self, 'tab_path'):
            self.tab_path.update_translations()
        
        # Update tab labels
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setTabText(0, t("main.profile.tab.cursor", default="Cursor Position"))
            self.tab_widget.setTabText(1, t("main.profile.tab.path", default="Click Path"))
            if self.tab_widget.count() > 2:
                self.tab_widget.setTabText(2, t("main.profile.tab.visual", default="Visual Click"))
        
        # Update button labels
        if hasattr(self, 'reset_button'):
            self.reset_button.setText(t("main.profile.button.reset", default="Reset"))
        if hasattr(self, 'save_button'):
            self.save_button.setText(t("main.profile.button.save", default="Save"))
        
        # Update status badge text
        if hasattr(self, 'status_badge'):
            self.update_status_badge()
        
        # Update welcome message
        self.update_welcome_message()
        
        # Update debug mode action text
        if hasattr(self, 'debug_mode_action'):
            self.debug_mode_action.setText(
                t("menu.settings.debug_mode", default="Debug Mode")
            )

    def on_open_settings(self):
        """Open settings dialog (placeholder with cute goose message)."""
        # Create custom message box with goose_laydown icon
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(t("menu.settings", default="Settings"))

        # Set goose_laydown icon
        goose_icon_path = get_icon_path("goose_laydown.png")
        if goose_icon_path.exists():
            pixmap = QPixmap(str(goose_icon_path))
            # Scale to appropriate size for message box (80x80)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            msg_box.setIconPixmap(scaled_pixmap)

        # Set cute message
        msg_box.setText(
            t("dialog.settings.message", default="吶～實在不知道要設定什麼阿？")
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)

        # Apply theme styling with custom message box styles (reuse the same style as user guide/about)
        theme_stylesheet = ThemeManager.get_theme(self.current_theme)
        custom_msgbox_style = f"""
            QMessageBox {{
                background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 14px;
                font-weight: bold;
            }}
            QMessageBox QLabel {{
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton {{
                min-width: 80px;
                padding: 6px 12px;
                border-radius: 6px;
            }}
        """
        msg_box.setStyleSheet(theme_stylesheet + "\n" + custom_msgbox_style)

        msg_box.exec()
    
    def on_toggle_debug_mode(self, checked: bool):
        """
        Handle Debug Mode toggle.
        
        Args:
            checked: True if Debug Mode is enabled, False otherwise
        """
        self.debug_mode = checked
        
        # Update UI visibility
        if hasattr(self, 'debug_log_area'):
            self.debug_log_area.setVisible(checked)
        
        # Update Click Path Tab debug mode (show/hide Load Test Data button)
        if hasattr(self, 'tab_path'):
            self.tab_path.set_debug_mode(checked)
        
        # Update logging level
        self._update_logging_level()
        
        # Update cursor clicker service debug mode
        if hasattr(self, 'cursor_clicker_service'):
            # Import and update DEBUG_MODE in cursor_clicker_service
            import backend.services.cursor_clicker_service as cursor_service
            cursor_service.DEBUG_MODE = checked
        
        # Update click path executor service debug mode
        if hasattr(self, 'click_path_executor_service'):
            # Import and update DEBUG_MODE in click_path_executor_service
            import backend.services.click_path_executor_service as path_executor_service
            path_executor_service.DEBUG_MODE = checked
        
        # Save to config
        self._save_config()
    
    def _setup_logging_handler(self):
        """Set up custom logging handler to capture logs in UI."""
        # Create UI log handler
        self.ui_log_handler = UILogHandler(self)
        self.ui_log_handler.log_message.connect(self._append_log_message)
        
        # Add handler to root logger (captures all loggers)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.ui_log_handler)
        
        # Set level based on debug mode
        self._update_logging_level()
    
    def _update_logging_level(self):
        """Update logging level based on debug mode."""
        root_logger = logging.getLogger()
        if self.debug_mode:
            root_logger.setLevel(logging.DEBUG)
        else:
            root_logger.setLevel(logging.WARNING)  # Only show warnings and errors when debug is off
    
    def _append_log_message(self, message: str):
        """
        Append a log message to the debug log area.
        
        Args:
            message: Log message string
        """
        if hasattr(self, 'debug_log_area') and self.debug_log_area.isVisible():
            self.debug_log_area.appendPlainText(message)
            # Auto-scroll to bottom
            scrollbar = self.debug_log_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def on_open_user_guide(self):
        """Open user guide (placeholder)."""
        # Create custom message box with goose_laydown icon
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(t("menu.help.user_guide", default="User Guide"))
        
        # Set goose_laydown icon
        goose_icon_path = get_icon_path("goose_laydown.png")
        if goose_icon_path.exists():
            pixmap = QPixmap(str(goose_icon_path))
            # Scale to appropriate size for message box (80x80)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            msg_box.setIconPixmap(scaled_pixmap)
        
        # Set cute message
        msg_box.setText(t("dialog.user_guide.message", default="讓鵝鵝鵝鵝鵝鵝躺平一下~"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # Apply theme styling with custom message box styles
        theme_stylesheet = ThemeManager.get_theme(self.current_theme)
        # Add custom styling for message box to make it more beautiful
        custom_msgbox_style = f"""
            QMessageBox {{
                background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 14px;
                font-weight: bold;
            }}
            QMessageBox QLabel {{
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {'#2196f3' if self.current_theme == 'light' else '#64b5f6'};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {'#1976d2' if self.current_theme == 'light' else '#90caf9'};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {'#1565c0' if self.current_theme == 'light' else '#42a5f5'};
            }}
        """
        msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
        
        msg_box.exec()

    def on_about(self):
        """Show About dialog."""
        # Create custom message box with goose_laydown icon
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(t("dialog.about.title", default="About Orange Clicker"))
        
        # Set goose_laydown icon
        goose_icon_path = get_icon_path("goose_laydown.png")
        if goose_icon_path.exists():
            pixmap = QPixmap(str(goose_icon_path))
            # Scale to appropriate size for message box (80x80)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            msg_box.setIconPixmap(scaled_pixmap)
        
        # Set cute message
        msg_box.setText(t("dialog.about.message", default="讓鵝鵝鵝鵝鵝鵝躺平一下~"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # Apply theme styling with custom message box styles
        theme_stylesheet = ThemeManager.get_theme(self.current_theme)
        # Add custom styling for message box to make it more beautiful
        custom_msgbox_style = f"""
            QMessageBox {{
                background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 14px;
                font-weight: bold;
            }}
            QMessageBox QLabel {{
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {'#2196f3' if self.current_theme == 'light' else '#64b5f6'};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {'#1976d2' if self.current_theme == 'light' else '#90caf9'};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {'#1565c0' if self.current_theme == 'light' else '#42a5f5'};
            }}
        """
        msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
        
        msg_box.exec()

    def on_set_language_en(self):
        """Switch UI language to English."""
        TranslationManager.set_language("en", fallback_lang="en")
        self.apply_translations()

    def on_set_language_zh_tw(self):
        """Switch UI language to Traditional Chinese."""
        TranslationManager.set_language("zh-TW", fallback_lang="en")
        self.apply_translations()

    def apply_theme(self, theme_name: str) -> None:
        """Apply theme to the window."""
        self.current_theme = theme_name
        ThemeManager.apply_theme(self, theme_name)
        
        # Update components themes
        if hasattr(self, 'profile_name_group'):
            self.profile_name_group.set_theme(theme_name)
        if hasattr(self, 'hotkey_group'):
            self.hotkey_group.set_theme(theme_name)
        if hasattr(self, 'tab_cursor'):
            self.tab_cursor.set_theme(theme_name)
        if hasattr(self, 'tab_path'):
            self.tab_path.set_theme(theme_name)
        
        # Update status badge theme
        if hasattr(self, 'status_badge'):
            self.status_badge.set_theme(theme_name)
            self.update_status_badge()
        
        # Get panel colors and apply to left/right panels
        panel_colors = ThemeManager.get_panel_colors(theme_name)
        left_panel_style = f"""
            QWidget#LeftPanel {{
                background-color: {panel_colors["left"]};
            }}
        """
        right_panel_style = f"""
            QWidget#RightPanel {{
                background-color: {panel_colors["right"]};
            }}
        """
        if hasattr(self, 'left_panel'):
            self.left_panel.setStyleSheet(left_panel_style)
        if hasattr(self, 'right_panel'):
            self.right_panel.setStyleSheet(right_panel_style)
        
        # Apply blue color scheme to Add Profile button
        blue_colors = ThemeManager.get_blue_colors()
        button_style = f"""
            QPushButton#AddProfileButton {{
                background-color: {blue_colors["primary"]};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton#AddProfileButton:hover {{
                background-color: {blue_colors["hover"]};
            }}
            QPushButton#AddProfileButton:pressed {{
                background-color: {blue_colors["pressed"]};
            }}
        """
        if hasattr(self, 'add_profile_button'):
            self.add_profile_button.setStyleSheet(button_style)
        
        # Update all profile cards with theme (using blue for ProfileCardContainer)
        for profile in self.profiles:
            if "card" in profile:
                profile["card"].set_theme(theme_name, primary_color="blue")
        
        # Apply theme to action buttons
        if hasattr(self, 'reset_button') and hasattr(self, 'save_button'):
            blue_colors = ThemeManager.get_blue_colors()
            # Gray colors for disabled state
            gray_colors = {
                "light": {"disabled": "#cccccc", "disabled_text": "#888888"},
                "dark": {"disabled": "#555555", "disabled_text": "#888888"}
            }
            gray = gray_colors.get(theme_name, gray_colors["light"])
            
            button_style = f"""
                QPushButton#ResetButton, QPushButton#SaveButton {{
                    background-color: {blue_colors["primary"]};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton#ResetButton:hover, QPushButton#SaveButton:hover {{
                    background-color: {blue_colors["hover"]};
                }}
                QPushButton#ResetButton:pressed, QPushButton#SaveButton:pressed {{
                    background-color: {blue_colors["pressed"]};
                }}
                QPushButton#ResetButton:disabled, QPushButton#SaveButton:disabled {{
                    background-color: {gray["disabled"]};
                    color: {gray["disabled_text"]};
                }}
            """
            self.reset_button.setStyleSheet(button_style)
            self.save_button.setStyleSheet(button_style)

    def on_set_theme_light(self):
        """Switch to light theme."""
        self.apply_theme("light")

    def on_set_theme_dark(self):
        """Switch to dark theme."""
        self.apply_theme("dark")

    # ---- Profile management ----

    def on_add_profile(self):
        """Add a new profile card."""
        profile_count = len(self.profiles) + 1
        default_name = f"Profile {profile_count}"
        default_start_hotkey = "#"
        default_end_hotkey = "#"
        default_hotkey_text = f"Start {default_start_hotkey} End {default_end_hotkey}"
        
        # Create profile card
        card = ProfileCard(
            profile_name=default_name,
            hotkey=default_hotkey_text,
            is_active=False
        )
        card.clicked.connect(lambda: self.on_card_clicked(card))
        card.active_changed.connect(lambda active: self.on_card_active_changed(card, active))
        card.delete_requested.connect(lambda: self.on_card_delete_requested(card))
        
        # Apply current theme to the new card (using blue for ProfileCardContainer)
        card.set_theme(self.current_theme, primary_color="blue")
        
        # Insert card before the stretch
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
        # Store profile data
        profile_data = {
            "id": str(uuid.uuid4()),  # Generate unique ID
            "name": default_name,
            "start_hotkey": "#",
            "end_hotkey": "#",
            "is_active": False,
            "is_saved": False,  # Track if profile has been saved
            "cursor_interval": 100,  # Default 100ms
            "cursor_button": "left",  # Default left button
            "cursor_count": 0,  # Default infinite (0)
            "click_path": [],  # Default empty click path
            "card": card
        }
        self.profiles.append(profile_data)
        
        # Select the newly added card
        self.current_profile_index = len(self.profiles) - 1
        self.select_profile(self.current_profile_index)

    def on_card_clicked(self, card: ProfileCard):
        """Handle card click."""
        # Reset swipe on other cards
        for profile in self.profiles:
            if profile["card"] != card:
                profile["card"].reset_swipe()
        
        # Find the profile index
        for i, profile in enumerate(self.profiles):
            if profile["card"] == card:
                self.select_profile(i)
                break
    
    def on_card_active_changed(self, card: ProfileCard, active: bool):
        """Handle card active state change."""
        # Find the profile and update
        for profile in self.profiles:
            if profile["card"] == card:
                profile_name = profile.get("name", "Unknown")
                profile_id = profile.get("id", "Unknown")
                
                self._logger.info(f"🔄 [MainWindow] 🔄🔴 Toggle switch changed for profile: {profile_name} (ID: {profile_id})")
                self._logger.info(f"🔄 [MainWindow]   - New active state: {active}")
                self._logger.info(f"🔄 [MainWindow]   - Profile is_saved: {profile.get('is_saved', False)}")
                self._logger.info(f"🔄 [MainWindow]   - Profile click_path type: {type(profile.get('click_path'))}")
                self._logger.info(f"🔄 [MainWindow]   - Profile click_path length: {len(profile.get('click_path', []))}")
                if profile.get("click_path"):
                    self._logger.info(f"🔄 [MainWindow]   - Profile click_path (first 3): {profile.get('click_path', [])[:3]}")
                
                # Only allow state change if profile is saved
                if profile.get("is_saved", False):
                    # IMPORTANT: Before registering hotkeys, verify the profile data is up-to-date
                    # Reload profile data from config to ensure we have the latest saved data
                    profile_id = profile.get("id")
                    
                    # DEBUG: Check profile_id before loading config
                    self._logger.debug(f"🔍 [MainWindow] 🔍 DEBUG: Checking profile_id before loading config")
                    self._logger.debug(f"🔍 [MainWindow]   - profile_id type: {type(profile_id)}")
                    self._logger.debug(f"🔍 [MainWindow]   - profile_id value: {profile_id}")
                    self._logger.debug(f"🔍 [MainWindow]   - profile_id is None: {profile_id is None}")
                    self._logger.debug(f"🔍 [MainWindow]   - profile_id is empty string: {profile_id == ''}")
                    self._logger.debug(f"🔍 [MainWindow]   - profile_id is truthy: {bool(profile_id)}")
                    
                    if profile_id:
                        self._logger.debug(f"🔍 [MainWindow] ✅ profile_id exists, loading config...")
                        config = self.config_manager.load_config()
                        profiles_data = config.get("profiles", [])
                        
                        # DEBUG: Check profiles_data from config
                        self._logger.debug(f"🔍 [MainWindow] 🔍 DEBUG: Checking profiles_data from config")
                        self._logger.debug(f"🔍 [MainWindow]   - profiles_data type: {type(profiles_data)}")
                        self._logger.debug(f"🔍 [MainWindow]   - profiles_data length: {len(profiles_data) if profiles_data else 0}")
                        
                        # DEBUG: Log all profile IDs in config for comparison
                        config_profile_ids = []
                        for idx, saved_profile_data in enumerate(profiles_data):
                            saved_id = saved_profile_data.get("id")
                            config_profile_ids.append(saved_id)
                            self._logger.debug(f"🔍 [MainWindow]   - Config profile[{idx}] ID: {saved_id} (type: {type(saved_id)})")
                        
                        self._logger.debug(f"🔍 [MainWindow]   - All config profile IDs: {config_profile_ids}")
                        self._logger.debug(f"🔍 [MainWindow]   - Looking for profile_id: {profile_id} (type: {type(profile_id)})")
                        
                        # Search for matching profile
                        found_match = False
                        for saved_profile_data in profiles_data:
                            saved_id = saved_profile_data.get("id")
                            
                            # DEBUG: Detailed comparison logging
                            self._logger.debug(f"🔍 [MainWindow] 🔍 DEBUG: Comparing profile IDs")
                            self._logger.debug(f"🔍 [MainWindow]   - Target profile_id: {profile_id} (type: {type(profile_id)})")
                            self._logger.debug(f"🔍 [MainWindow]   - Config saved_id: {saved_id} (type: {type(saved_id)})")
                            self._logger.debug(f"🔍 [MainWindow]   - IDs are equal (==): {saved_id == profile_id}")
                            self._logger.debug(f"🔍 [MainWindow]   - IDs are identical (is): {saved_id is profile_id}")
                            
                            if saved_profile_data.get("id") == profile_id:
                                found_match = True
                                self._logger.debug(f"🔍 [MainWindow] ✅ MATCH FOUND! Profile ID matched in config")
                                
                                # Deserialize and update profile with latest saved data
                                saved_profile = ProfileService.deserialize_profile(saved_profile_data)
                                
                                # DEBUG: Check deserialized profile data
                                self._logger.debug(f"🔍 [MainWindow] 🔍 DEBUG: Deserialized profile data")
                                self._logger.debug(f"🔍 [MainWindow]   - saved_profile['id']: {saved_profile.get('id')}")
                                self._logger.debug(f"🔍 [MainWindow]   - saved_profile['name']: {saved_profile.get('name')}")
                                self._logger.debug(f"🔍 [MainWindow]   - saved_profile click_path length: {len(saved_profile.get('click_path', []))}")
                                
                                # Update the profile in memory with saved data
                                profile.update(saved_profile)
                                # IMPORTANT: Keep the current active state (user just toggled it)
                                profile["is_active"] = active
                                # Keep the card reference
                                if "card" not in profile:
                                    profile["card"] = card
                                
                                self._logger.info(f"🔄 [MainWindow] ✅ Reloaded profile data from config for: {profile_name}")
                                break
                        
                        # DEBUG: Check if match was found
                        if not found_match:
                            self._logger.warning(f"🔍 [MainWindow] ⚠️  WARNING: Profile ID '{profile_id}' NOT FOUND in config!")
                            self._logger.warning(f"🔍 [MainWindow]   - Available profile IDs in config: {config_profile_ids}")
                            self._logger.warning(f"🔍 [MainWindow]   - This profile will use current memory data instead of config data")
                    else:
                        # If no profile_id, just update is_active directly
                        self._logger.warning(f"🔍 [MainWindow] ⚠️  WARNING: profile_id is empty/None! Cannot reload from config.")
                        self._logger.warning(f"🔍 [MainWindow]   - profile_id value: {profile_id}")
                        self._logger.warning(f"🔍 [MainWindow]   - This profile will use current memory data only")
                        profile["is_active"] = active
                    
                    self._logger.info(f"🔄 [MainWindow] ✅ Profile {profile_name} is saved, updating active state to {active}")
                    
                    self._logger.info(f"🔄 [MainWindow] 📋 Profile data after reloading from config:")
                    self._logger.info(f"🔄 [MainWindow]   - is_active: {profile.get('is_active', False)}")
                    self._logger.info(f"🔄 [MainWindow]   - name: {profile.get('name', 'N/A')}")
                    self._logger.info(f"🔄 [MainWindow]   - start_hotkey: {profile.get('start_hotkey', 'N/A')}")
                    self._logger.info(f"🔄 [MainWindow]   - end_hotkey: {profile.get('end_hotkey', 'N/A')}")
                    self._logger.info(f"🔄 [MainWindow]   - click_path type: {type(profile.get('click_path'))}")
                    self._logger.info(f"🔄 [MainWindow]   - click_path length: {len(profile.get('click_path', []))}")
                    if profile.get("click_path"):
                        self._logger.info(f"🔄 [MainWindow]   - click_path (first 3): {profile.get('click_path', [])[:3]}")
                    
                    # IMPORTANT: Update UI components with the latest profile data
                    # Update ProfileCard display (name, hotkey)
                    card.set_profile_name(profile.get("name", ""))
                    end_hotkey = profile.get("end_hotkey", "#")
                    hotkey_text = f"Start {profile.get('start_hotkey', '#')}" if profile.get("start_hotkey") else "Start #"
                    if end_hotkey and end_hotkey != "#":
                        hotkey_text += f" End {end_hotkey}"
                    card.set_hotkey(hotkey_text)
                    
                    # If this is the currently selected profile, update the right panel UI
                    if self.current_profile_index >= 0 and profile == self.profiles[self.current_profile_index]:
                        # Update Profile Name input
                        if hasattr(self, 'profile_name_group'):
                            self.profile_name_group.set_name(profile.get("name", ""))
                        
                        # Update Hotkey inputs
                        if hasattr(self, 'hotkey_group'):
                            self.hotkey_group.set_start_hotkey(profile.get("start_hotkey", "#"))
                            self.hotkey_group.set_end_hotkey(profile.get("end_hotkey", "#"))
                        
                        # Update Cursor Position Tab
                        if hasattr(self, 'tab_cursor'):
                            self.tab_cursor.set_interval(profile.get("cursor_interval", 100))
                            self.tab_cursor.set_click_button(profile.get("cursor_button", "left"))
                            self.tab_cursor.set_click_count(profile.get("cursor_count", 0))
                        
                        # Update Click Path Tab
                        if hasattr(self, 'tab_path'):
                            profile_id = profile.get("id")
                            if profile_id:
                                self.tab_path.set_current_profile_id(profile_id)
                            self.tab_path.set_path_data(profile.get("click_path", []))
                        
                        # Update status badge
                        self.update_status_badge()
                    
                    # Update hotkeys based on active state
                    self._logger.info(f"🔄 [MainWindow] 📝 Calling register_profile_hotkeys for profile: {profile_name}")
                    self.profile_hotkey_service.register_profile_hotkeys(profile)
                    
                    # IMPORTANT: Update toggle switch state to match profile's is_active
                    card.set_active(profile.get("is_active", False))
                    
                    # Save the updated is_active state to config
                    self._save_config()
                else:
                    # If not saved, revert the toggle switch
                    self._logger.warning(f"🔄 [MainWindow] ⚠️  Profile {profile_name} is not saved, reverting toggle switch")
                    card.set_active(False)
                break
    
    def on_card_delete_requested(self, card: ProfileCard):
        """
        Handle card delete request.
        
        Removes the profile from:
        1. UI (removes ProfileCard from layout)
        2. Memory (removes from self.profiles list)
        3. Config file (saves updated config to disk)
        """
        # Find the profile index
        for i, profile in enumerate(self.profiles):
            if profile["card"] == card:
                # Remove card from layout
                self.cards_layout.removeWidget(card)
                card.setParent(None)
                card.deleteLater()
                
                # Remove from profiles list
                self.profiles.pop(i)
                
                # Always return to welcome page after deletion
                self.current_profile_index = -1
                
                # Update hotkey service: no profile selected
                self.hotkey_service.set_profile_selected(False)
                
                # Clear right panel and show welcome page
                # Make sure to switch to welcome page first
                if hasattr(self, 'right_stacked') and hasattr(self, 'welcome_page'):
                    self.right_stacked.setCurrentWidget(self.welcome_page)
                
                # Clear form fields
                if hasattr(self, 'profile_name_group'):
                    self.profile_name_group.set_name("")
                if hasattr(self, 'hotkey_group'):
                    self.hotkey_group.set_start_hotkey("#")
                    self.hotkey_group.set_end_hotkey("#")
                
                # Update status badge
                if hasattr(self, 'status_badge'):
                    self.update_status_badge()
                
                # Update welcome message with random blessing
                self.update_welcome_message()
                
                # Unregister profile hotkeys before deletion
                profile_id = profile.get("id")
                if profile_id:
                    self.profile_hotkey_service.unregister_profile_hotkeys(profile_id)
                
                # Save configuration to file (removes deleted profile from config)
                self._save_config()
                
                break

    def select_profile(self, index: int):
        """Select a profile by index."""
        if 0 <= index < len(self.profiles):
            self.current_profile_index = index
            profile = self.profiles[index]
            
            # Update hotkey service: profile is selected
            self.hotkey_service.set_profile_selected(True)
            
            # Ensure we have the necessary widgets
            if not hasattr(self, 'right_stacked') or not hasattr(self, 'settings_page'):
                return
            
            # Switch to settings page (force update)
            self.right_stacked.setCurrentWidget(self.settings_page)
            self.right_stacked.update()  # Force update to ensure visibility
            
            # Update right panel with profile data
            if hasattr(self, 'profile_name_group'):
                self.profile_name_group.set_name(profile["name"])
            if hasattr(self, 'hotkey_group'):
                self.hotkey_group.set_start_hotkey(profile.get("start_hotkey", "#"))
                self.hotkey_group.set_end_hotkey(profile.get("end_hotkey", "#"))
            
            # Update cursor position tab
            if hasattr(self, 'tab_cursor'):
                self.tab_cursor.set_interval(profile.get("cursor_interval", 100))
                self.tab_cursor.set_click_button(profile.get("cursor_button", "left"))
                self.tab_cursor.set_click_count(profile.get("cursor_count", 0))
            
            # Update click path tab
            if hasattr(self, 'tab_path'):
                # Set the current profile ID (UUID) so ClickPathTab knows which profile it belongs to
                profile_id = profile.get("id")
                self.tab_path.set_current_profile_id(profile_id)
                # Load the profile's click path data
                self.tab_path.set_path_data(profile.get("click_path", []))
            
            # Update status badge and toggle switch based on saved state
            is_saved = profile.get("is_saved", False)
            if "card" in profile:
                # Enable/disable toggle switch based on saved state
                profile["card"].set_enabled(is_saved)
            
            # Update status badge
            self.update_status_badge()
        else:
            # No profile selected, show welcome page
            self.current_profile_index = -1
            
            # Update hotkey service: no profile selected
            self.hotkey_service.set_profile_selected(False)
            
            if hasattr(self, 'right_stacked') and hasattr(self, 'welcome_page'):
                self.right_stacked.setCurrentWidget(self.welcome_page)
                self.right_stacked.update()  # Force update to ensure visibility
            # Update welcome message with random blessing
            self.update_welcome_message()

    def on_profile_name_changed(self, new_name: str):
        """Handle profile name change from right panel."""
        if self.current_profile_index >= 0 and self.current_profile_index < len(self.profiles):
            profile = self.profiles[self.current_profile_index]
            # Update stored name
            profile["name"] = new_name
            # Update card
            profile["card"].set_profile_name(new_name)

    def on_profile_start_hotkey_changed(self, new_hotkey: str):
        """Handle profile start hotkey change from right panel."""
        if self.current_profile_index >= 0 and self.current_profile_index < len(self.profiles):
            profile = self.profiles[self.current_profile_index]
            # Update stored hotkey
            profile["start_hotkey"] = new_hotkey
            # Update card hotkey display (combine start and end)
            end_hotkey = profile.get("end_hotkey", "#")
            hotkey_text = f"Start {new_hotkey}" if new_hotkey else "Start #"
            if end_hotkey:
                hotkey_text += f" End {end_hotkey}"
            profile["card"].set_hotkey(hotkey_text)
    
    def on_profile_end_hotkey_changed(self, new_hotkey: str):
        """Handle profile end hotkey change from right panel."""
        if self.current_profile_index >= 0 and self.current_profile_index < len(self.profiles):
            profile = self.profiles[self.current_profile_index]
            # Update stored hotkey
            profile["end_hotkey"] = new_hotkey
            # Update card hotkey display (combine start and end)
            start_hotkey = profile.get("start_hotkey", "#")
            hotkey_text = f"Start {start_hotkey}" if start_hotkey else "Start #"
            if new_hotkey:
                hotkey_text += f" End {new_hotkey}"
            profile["card"].set_hotkey(hotkey_text)
    
    def update_welcome_message(self):
        """Update welcome message with random blessing."""
        # Get random blessing message
        blessing_key = f"welcome.blessing.{random.randint(1, 20)}"
        blessing_text = t(blessing_key, default="Welcome to Auto-Clicker!")
        if hasattr(self, 'welcome_message_label'):
            self.welcome_message_label.setText(blessing_text)
    
    def update_status_badge(self):
        """Update status badge based on current profile's saved and active state."""
        if not hasattr(self, 'status_badge'):
            return
        
        if 0 <= self.current_profile_index < len(self.profiles):
            profile = self.profiles[self.current_profile_index]
            is_saved = profile.get("is_saved", False)
            is_active = profile.get("is_active", False)
            
            if not is_saved:
                # Unsaved state: gray background, "Setting" status
                self.status_badge.set_status("unsaved")
                status_text = t("main.profile.status.setting", default="Setting")
            else:
                # Saved state: show active or stopped
                if is_active:
                    self.status_badge.set_status("active")
                    status_text = t("main.profile.status.active", default="Active")
                else:
                    self.status_badge.set_status("stopped")
                    status_text = t("main.profile.status.stopped", default="Stopped")
            
            self.status_badge.set_text(status_text)
            
            # Safety feature: Disable Reset, Save, and all input fields when profile is active
            self._update_input_fields_enabled(not is_active)
        else:
            # No profile selected, hide badge or show default
            self.status_badge.set_status("unsaved")
            self.status_badge.set_text(t("main.profile.status.setting", default="Setting"))
            # Enable all fields when no profile is selected
            self._update_input_fields_enabled(True)
    
    def on_reset_clicked(self):
        """
        Handle reset button click.
        
        Shows confirmation dialog, then resets all fields to the last saved state
        (reloads from the profile's stored data).
        """
        if not (0 <= self.current_profile_index < len(self.profiles)):
            return
        
        # Safety feature: Prevent Reset when profile is active
        profile = self.profiles[self.current_profile_index]
        if profile.get("is_active", False):
            return
        
        # Create confirmation dialog with orange_shock icon
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(t("main.profile.reset.confirm.title", default="重置確認"))
        
        # Set orange_shock icon
        shock_icon_path = get_icon_path("orange_shock.png")
        if shock_icon_path.exists():
            pixmap = QPixmap(str(shock_icon_path))
            # Scale to appropriate size for message box (80x80)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            msg_box.setIconPixmap(scaled_pixmap)
        
        # Set cute message
        msg_box.setText(t("main.profile.reset.confirm.message", default="你確定～確定要重置嗎？"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Apply theme styling with custom message box styles
        theme_stylesheet = ThemeManager.get_theme(self.current_theme)
        custom_msgbox_style = f"""
            QMessageBox {{
                background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 14px;
                font-weight: bold;
            }}
            QMessageBox QLabel {{
                color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {'#2196f3' if self.current_theme == 'light' else '#64b5f6'};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {'#1976d2' if self.current_theme == 'light' else '#90caf9'};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {'#1565c0' if self.current_theme == 'light' else '#42a5f5'};
            }}
        """
        msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # User confirmed reset - reload from config file (saved state)
            profile = self.profiles[self.current_profile_index]
            profile_id = profile.get("id")
            
            # Reload saved data from config file
            config = self.config_manager.load_config()
            profiles_data = config.get("profiles", [])
            
            # Find the saved profile data by ID
            saved_profile_data = None
            for saved_profile in profiles_data:
                if saved_profile.get("id") == profile_id:
                    saved_profile_data = saved_profile
                    break
            
            # If found saved data, use it; otherwise use current profile data
            if saved_profile_data:
                # Deserialize the saved profile data
                saved_profile = ProfileService.deserialize_profile(saved_profile_data)
                
                # Update the profile in memory with saved data
                profile["name"] = saved_profile["name"]
                profile["start_hotkey"] = saved_profile["start_hotkey"]
                profile["end_hotkey"] = saved_profile["end_hotkey"]
                profile["cursor_interval"] = saved_profile["cursor_interval"]
                profile["cursor_button"] = saved_profile["cursor_button"]
                profile["cursor_count"] = saved_profile["cursor_count"]
                profile["click_path"] = saved_profile["click_path"]
                profile["is_active"] = saved_profile["is_active"]
                profile["is_saved"] = saved_profile["is_saved"]
            
            # Reset all UI fields to the saved state
            if hasattr(self, 'profile_name_group'):
                self.profile_name_group.set_name(profile.get("name", ""))
            
            if hasattr(self, 'hotkey_group'):
                self.hotkey_group.set_start_hotkey(profile.get("start_hotkey", "#"))
                self.hotkey_group.set_end_hotkey(profile.get("end_hotkey", "#"))
            
            # Reset cursor position tab to saved values
            if hasattr(self, 'tab_cursor'):
                self.tab_cursor.set_interval(profile.get("cursor_interval", 100))
                self.tab_cursor.set_click_button(profile.get("cursor_button", "left"))
                self.tab_cursor.set_click_count(profile.get("cursor_count", 0))
            
            # Reset click path tab to saved values
            if hasattr(self, 'tab_path'):
                self.tab_path.set_path_data(profile.get("click_path", []))
            
            # Update ProfileCard to reflect saved state
            if "card" in profile:
                profile["card"].set_profile_name(profile["name"])
                end_hotkey = profile.get("end_hotkey", "#")
                hotkey_text = f"Start {profile['start_hotkey']}" if profile.get("start_hotkey") else "Start #"
                if end_hotkey:
                    hotkey_text += f" End {end_hotkey}"
                profile["card"].set_hotkey(hotkey_text)
                profile["card"].set_active(profile.get("is_active", False))
                profile["card"].set_enabled(profile.get("is_saved", False))
            
            # Update status badge based on saved state
            self.update_status_badge()
    
    def on_save_clicked(self):
        """Handle save button click."""
        if 0 <= self.current_profile_index < len(self.profiles):
            profile = self.profiles[self.current_profile_index]
            
            # Safety feature: Prevent Save when profile is active
            if profile.get("is_active", False):
                return
            
            # Step 1: Validate required fields BEFORE asking for save type
            profile_name = self.profile_name_group.get_name().strip()
            start_hotkey = self.hotkey_group.get_start_hotkey().strip()
            end_hotkey = self.hotkey_group.get_end_hotkey().strip()
            
            # Validation: Profile Name is required
            if not profile_name:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle(t("dialog.save.warning.title", default="警告"))
                
                # Set orange_shock icon
                shock_icon_path = get_icon_path("orange_shock.png")
                if shock_icon_path.exists():
                    pixmap = QPixmap(str(shock_icon_path))
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    msg_box.setIconPixmap(scaled_pixmap)
                
                msg_box.setText(t("dialog.save.warning.name_required", default="Profile Name 是必填欄位，請輸入名稱！"))
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                
                # Apply theme styling
                theme_stylesheet = ThemeManager.get_theme(self.current_theme)
                custom_msgbox_style = f"""
                    QMessageBox {{
                        background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                        color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QMessageBox QLabel {{
                        color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {'#ff9800' if self.current_theme == 'light' else '#ff9800'};
                        color: #ffffff;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 24px;
                        font-size: 14px;
                        font-weight: bold;
                        min-width: 80px;
                    }}
                    QMessageBox QPushButton:hover {{
                        background-color: {'#f57c00' if self.current_theme == 'light' else '#f57c00'};
                    }}
                    QMessageBox QPushButton:pressed {{
                        background-color: {'#e65100' if self.current_theme == 'light' else '#e65100'};
                    }}
                """
                msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
                msg_box.exec()
                return  # Don't save if validation fails
            
            # Validation: Start Hotkey is required (cannot be "#" or empty)
            if not start_hotkey or start_hotkey == "#":
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle(t("dialog.save.warning.title", default="警告"))
                
                # Set orange_shock icon
                shock_icon_path = get_icon_path("orange_shock.png")
                if shock_icon_path.exists():
                    pixmap = QPixmap(str(shock_icon_path))
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    msg_box.setIconPixmap(scaled_pixmap)
                
                msg_box.setText(t("dialog.save.warning.start_hotkey_required", default="Start Hotkey 是必填欄位，請設定快捷鍵！"))
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                
                # Apply theme styling
                theme_stylesheet = ThemeManager.get_theme(self.current_theme)
                custom_msgbox_style = f"""
                    QMessageBox {{
                        background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                        color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QMessageBox QLabel {{
                        color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px;
                    }}
                    QMessageBox QPushButton {{
                        background-color: {'#ff9800' if self.current_theme == 'light' else '#ff9800'};
                        color: #ffffff;
                        border: none;
                        border-radius: 8px;
                        padding: 8px 24px;
                        font-size: 14px;
                        font-weight: bold;
                        min-width: 80px;
                    }}
                    QMessageBox QPushButton:hover {{
                        background-color: {'#f57c00' if self.current_theme == 'light' else '#f57c00'};
                    }}
                    QMessageBox QPushButton:pressed {{
                        background-color: {'#e65100' if self.current_theme == 'light' else '#e65100'};
                    }}
                """
                msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
                msg_box.exec()
                return  # Don't save if validation fails
            
            # Step 2: Ask user which type to save (Cursor Position or Click Path)
            save_type_dialog = QMessageBox(self)
            save_type_dialog.setIcon(QMessageBox.Icon.Question)
            save_type_dialog.setWindowTitle(t("dialog.save.type.title", default="選擇儲存類型"))
            
            # Set orange icon
            orange_icon = IconManager.get_icon_by_size(64)
            if not orange_icon.isNull():
                pixmap = orange_icon.pixmap(80, 80)
                save_type_dialog.setIconPixmap(pixmap)
            
            # Set message
            save_type_dialog.setText(t("dialog.save.type.message", default="請選擇要儲存的類型："))
            save_type_dialog.setInformativeText(t("dialog.save.type.info", default="Cursor Position 和 Click Path 只能選擇一種儲存，否則會衝突。"))
            
            # Add buttons
            cursor_btn = save_type_dialog.addButton(
                t("dialog.save.type.cursor_position", default="Cursor Position"),
                QMessageBox.ButtonRole.AcceptRole
            )
            click_path_btn = save_type_dialog.addButton(
                t("dialog.save.type.click_path", default="Click Path"),
                QMessageBox.ButtonRole.AcceptRole
            )
            cancel_btn = save_type_dialog.addButton(
                QMessageBox.StandardButton.Cancel
            )
            save_type_dialog.setDefaultButton(cursor_btn)
            
            # Apply theme styling
            theme_stylesheet = ThemeManager.get_theme(self.current_theme)
            custom_msgbox_style = f"""
                QMessageBox {{
                    background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                    color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                    font-size: 14px;
                    font-weight: bold;
                }}
                QMessageBox QLabel {{
                    color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                }}
                QMessageBox QPushButton {{
                    background-color: {'#2196f3' if self.current_theme == 'light' else '#64b5f6'};
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 100px;
                }}
                QMessageBox QPushButton:hover {{
                    background-color: {'#1976d2' if self.current_theme == 'light' else '#90caf9'};
                }}
                QMessageBox QPushButton:pressed {{
                    background-color: {'#1565c0' if self.current_theme == 'light' else '#42a5f5'};
                }}
            """
            save_type_dialog.setStyleSheet(theme_stylesheet + custom_msgbox_style)
            
            result = save_type_dialog.exec()
            
            # Determine which type was selected
            save_cursor_position = False
            save_click_path = False
            
            if save_type_dialog.clickedButton() == cursor_btn:
                save_cursor_position = True
            elif save_type_dialog.clickedButton() == click_path_btn:
                save_click_path = True
            else:
                # User cancelled
                return
            
            # Save current values (always save name and hotkeys)
            profile["name"] = profile_name
            profile["start_hotkey"] = start_hotkey
            profile["end_hotkey"] = end_hotkey if end_hotkey else "#"
            
            # Step 2: Save based on selected type
            if save_cursor_position:
                # Save Cursor Position settings
                if hasattr(self, 'tab_cursor'):
                    profile["cursor_interval"] = self.tab_cursor.get_interval()
                    profile["cursor_button"] = self.tab_cursor.get_click_button()
                    profile["cursor_count"] = self.tab_cursor.get_click_count()
                
                # Clear Click Path data (to avoid conflicts)
                profile["click_path"] = []
                
                # Validation: Check if Click Count is Infinite (0) and End hotkey is not set
                click_count = profile.get("cursor_count", 0)
                end_hotkey = profile.get("end_hotkey", "#")
                
                if click_count == 0 and (not end_hotkey or end_hotkey == "#"):
                    # Show warning dialog
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Icon.Warning)
                    msg_box.setWindowTitle(t("dialog.save.warning.title", default="警告"))
                    
                    # Set orange_shock icon
                    shock_icon_path = get_icon_path("orange_shock.png")
                    if shock_icon_path.exists():
                        pixmap = QPixmap(str(shock_icon_path))
                        scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        msg_box.setIconPixmap(scaled_pixmap)
                    
                    # Set warning message
                    msg_box.setText(t("dialog.save.warning.infinite_no_end", default="Click Count 設為 Infinite 時，必須設定 End 快捷鍵才能停止點擊！"))
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    
                    # Apply theme styling
                    theme_stylesheet = ThemeManager.get_theme(self.current_theme)
                    custom_msgbox_style = f"""
                        QMessageBox {{
                            background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                            color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                            font-size: 14px;
                            font-weight: bold;
                        }}
                        QMessageBox QLabel {{
                            color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                            font-size: 16px;
                            font-weight: bold;
                            padding: 10px;
                        }}
                        QMessageBox QPushButton {{
                            background-color: {'#ff9800' if self.current_theme == 'light' else '#ff9800'};
                            color: #ffffff;
                            border: none;
                            border-radius: 8px;
                            padding: 8px 24px;
                            font-size: 14px;
                            font-weight: bold;
                            min-width: 80px;
                        }}
                        QMessageBox QPushButton:hover {{
                            background-color: {'#f57c00' if self.current_theme == 'light' else '#f57c00'};
                        }}
                        QMessageBox QPushButton:pressed {{
                            background-color: {'#e65100' if self.current_theme == 'light' else '#e65100'};
                        }}
                    """
                    msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
                    msg_box.exec()
                    return  # Don't save if validation fails
            
            elif save_click_path:
                # Save Click Path settings
                if hasattr(self, 'tab_path'):
                    click_path_data = self.tab_path.get_path_data()
                    profile["click_path"] = click_path_data
                    self._logger.debug(f"[MainWindow] Saved Click Path: {len(click_path_data)} steps")
                    if click_path_data:
                        self._logger.debug(f"[MainWindow] Click Path first step: {click_path_data[0] if len(click_path_data) > 0 else 'N/A'}")
                else:
                    self._logger.warning("[MainWindow] tab_path not found when saving Click Path")
                    profile["click_path"] = []
                
                # Clear Cursor Position data (to avoid conflicts)
                profile["cursor_interval"] = 100  # Reset to default
                profile["cursor_button"] = "left"  # Reset to default
                profile["cursor_count"] = 0  # Reset to default
                
                # No End Hotkey validation needed for Click Path
            
            # Mark profile as saved
            profile["is_saved"] = True
            
            # NOTE: We don't register hotkeys here. Hotkeys will be registered when the user
            # clicks the toggle switch to activate the profile. This ensures we always use
            # the latest profile data (including click_path) when registering.
            
            # Enable toggle switch now that profile is saved
            if "card" in profile:
                profile["card"].set_enabled(True)
                profile["card"].set_profile_name(profile["name"])
                end_hotkey = profile.get("end_hotkey", "#")
                hotkey_text = f"Start {profile['start_hotkey']}" if profile.get("start_hotkey") else "Start #"
                if end_hotkey:
                    hotkey_text += f" End {end_hotkey}"
                profile["card"].set_hotkey(hotkey_text)
            
            # Update status badge to reflect saved state
            self.update_status_badge()
            
            # Save to config file
            self._save_config()
            
            # Create custom success message box with orange icon
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle(t("dialog.save.success.title", default="儲存成功"))
            
            # Set orange icon (use 64x64 for message box - larger and more visible)
            orange_icon = IconManager.get_icon_by_size(64)
            if not orange_icon.isNull():
                # Use a larger pixmap for better visibility
                pixmap = orange_icon.pixmap(80, 80)
                msg_box.setIconPixmap(pixmap)
            
            # Set friendly message with larger font
            msg_box.setText(t("dialog.save.success.message", default="儲存成功啦！"))
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            
            # Apply theme styling with custom message box styles
            theme_stylesheet = ThemeManager.get_theme(self.current_theme)
            # Add custom styling for message box to make it more beautiful
            custom_msgbox_style = f"""
                QMessageBox {{
                    background-color: {'#ffffff' if self.current_theme == 'light' else '#1e1e1e'};
                    color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                    font-size: 14px;
                    font-weight: bold;
                }}
                QMessageBox QLabel {{
                    color: {'#000000' if self.current_theme == 'light' else '#ffffff'};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                }}
                QMessageBox QPushButton {{
                    background-color: {'#2196f3' if self.current_theme == 'light' else '#64b5f6'};
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QMessageBox QPushButton:hover {{
                    background-color: {'#1976d2' if self.current_theme == 'light' else '#90caf9'};
                }}
                QMessageBox QPushButton:pressed {{
                    background-color: {'#1565c0' if self.current_theme == 'light' else '#42a5f5'};
                }}
            """
            msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
            
            msg_box.exec()
    
    def _update_input_fields_enabled(self, enabled: bool):
        """
        Enable or disable all input fields based on profile active state.
        
        Safety feature: Disable all input fields and buttons when profile is active.
        
        Args:
            enabled: True to enable fields, False to disable
        """
        # Disable/Enable Reset and Save buttons
        if hasattr(self, 'reset_button'):
            self.reset_button.setEnabled(enabled)
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(enabled)
        
        # Disable/Enable Profile Name input
        if hasattr(self, 'profile_name_group'):
            if hasattr(self.profile_name_group, 'name_input'):
                self.profile_name_group.name_input.setEnabled(enabled)
        
        # Disable/Enable Hotkey inputs
        if hasattr(self, 'hotkey_group'):
            if hasattr(self.hotkey_group, 'start_input'):
                self.hotkey_group.start_input.setEnabled(enabled)
            if hasattr(self.hotkey_group, 'end_input'):
                self.hotkey_group.end_input.setEnabled(enabled)
        
        # Disable/Enable Cursor Position Tab inputs
        if hasattr(self, 'tab_cursor'):
            # Find all input widgets in tab_cursor
            for widget in self.tab_cursor.findChildren(QSpinBox):
                widget.setEnabled(enabled)
            for widget in self.tab_cursor.findChildren(QComboBox):
                widget.setEnabled(enabled)
        
        # Disable/Enable Click Path Tab inputs
        if hasattr(self, 'tab_path'):
            # Find all input widgets in tab_path
            for widget in self.tab_path.findChildren(QSpinBox):
                widget.setEnabled(enabled)
            for widget in self.tab_path.findChildren(QComboBox):
                widget.setEnabled(enabled)
            for widget in self.tab_path.findChildren(QLineEdit):
                widget.setEnabled(enabled)
            # Disable/Enable buttons in Click Path Tab
            for widget in self.tab_path.findChildren(QPushButton):
                widget.setEnabled(enabled)
    
    def on_cursor_interval_changed(self, interval: int):
        """Handle cursor interval change."""
        if 0 <= self.current_profile_index < len(self.profiles):
            self.profiles[self.current_profile_index]["cursor_interval"] = interval
    
    def on_cursor_button_changed(self, button: str):
        """Handle cursor button change."""
        if 0 <= self.current_profile_index < len(self.profiles):
            self.profiles[self.current_profile_index]["cursor_button"] = button
    
    def on_cursor_count_changed(self, count: int):
        """Handle cursor count change."""
        if 0 <= self.current_profile_index < len(self.profiles):
            self.profiles[self.current_profile_index]["cursor_count"] = count
    
    def on_click_path_changed(self, path_data: list):
        """
        Handle click path change.
        
        Uses profile ID (UUID) to find the correct profile, not profile index,
        because profile names can be changed.
        """
        # Get the profile ID from ClickPathTab
        if hasattr(self, 'tab_path'):
            profile_id = self.tab_path.get_current_profile_id()
            if profile_id:
                # Find profile by ID (UUID)
                for profile in self.profiles:
                    if profile.get("id") == profile_id:
                        profile["click_path"] = path_data
                        self._logger.debug(f"[MainWindow] Updated click_path for profile ID: {profile_id}")
                        return
                self._logger.warning(f"[MainWindow] Profile ID {profile_id} not found when updating click_path")
            else:
                self._logger.warning("[MainWindow] No profile ID set in ClickPathTab when click_path changed")
    
    def _register_global_hotkeys(self):
        """
        Register global hotkeys for Click Path recording.
        
        Delegates to HotkeyService for business logic.
        """
        # IMPORTANT: Always register Click Path hotkeys (Ctrl+W, Ctrl+Q) first
        # These are global hotkeys that should always be available
        self.hotkey_service.register_click_path_hotkeys(
            start_callback=self._on_start_recording_hotkey,
            stop_callback=self._on_stop_recording_hotkey
        )
        
        # Register hotkeys only for saved AND active profiles
        # Hotkeys are only available when Badge Status is "active"
        for profile in self.profiles:
            if profile.get("is_saved", False) and profile.get("is_active", False):
                self.profile_hotkey_service.register_profile_hotkeys(profile)
    
    def _on_tab_changed(self, index: int):
        """
        Handle tab change event.
        
        Args:
            index: Index of the newly selected tab
                0 = Cursor Position tab
                1 = Click Path tab
        """
        # Update hotkey service state
        is_click_path_active = (index == 1)
        self.hotkey_service.set_click_path_tab_active(is_click_path_active)
        
        # Important: When switching to Click Path tab, ensure profile_selected state is correct
        # and pass the current profile's UUID to ClickPathTab
        if is_click_path_active:
            # Check if a profile is currently selected
            if 0 <= self.current_profile_index < len(self.profiles):
                profile = self.profiles[self.current_profile_index]
                profile_id = profile.get("id")
                # Profile is selected, ensure HotkeyService knows
                self.hotkey_service.set_profile_selected(True)
                # Pass the current profile's UUID to ClickPathTab
                if hasattr(self, 'tab_path') and profile_id:
                    self.tab_path.set_current_profile_id(profile_id)
            else:
                # No profile selected, ensure HotkeyService knows
                self.hotkey_service.set_profile_selected(False)
                # Clear ClickPathTab's profile ID
                if hasattr(self, 'tab_path'):
                    self.tab_path.set_current_profile_id(None)
        
        # If switching away from Click Path tab, stop any ongoing recording
        if index != 1 and hasattr(self, '_click_path_tab_ref') and self._click_path_tab_ref:
            # Stop recording if currently recording
            if hasattr(self._click_path_tab_ref, '_is_recording') and self._click_path_tab_ref._is_recording:
                self._click_path_tab_ref.stop_recording()
    
    def _on_start_recording_hotkey(self):
        """
        Handle Ctrl+W hotkey to start recording.
        
        Called by HotkeyService when conditions are met.
        """
        # IMPORTANT: This method is called from the keyboard listener worker thread.
        # We must not touch Qt widgets directly here. Instead, emit a signal that
        # will be handled on the GUI thread.
        self.request_start_click_path_recording.emit()
    
    def _on_stop_recording_hotkey(self):
        """
        Handle Ctrl+Q hotkey to stop recording.
        
        Called by HotkeyService.
        """
        # IMPORTANT: Same as start hotkey – marshal to GUI thread via signal.
        self.request_stop_click_path_recording.emit()
    
    def _check_clicking_status(self):
        """Periodically check if clicking has stopped and update UI."""
        if hasattr(self, 'profile_hotkey_service'):
            self.profile_hotkey_service.check_clicking_status()
    
    def _start_click_path_recording_on_ui(self):
        """
        UI-thread handler for starting Click Path recording (Ctrl+W).
        """
        print("[MainWindow] Ctrl+W pressed - start recording")
        # Check if ClickPathTab reference exists
        if hasattr(self, '_click_path_tab_ref') and self._click_path_tab_ref:
            print("[MainWindow] Starting recording...")
            self._click_path_tab_ref.start_recording()
        else:
            print("[MainWindow] Warning: _click_path_tab_ref not found")
    
    def _stop_click_path_recording_on_ui(self):
        """
        UI-thread handler for stopping Click Path recording (Ctrl+Q).
        """
        print("[MainWindow] Ctrl+Q pressed - stop recording")
        # Check if ClickPathTab reference exists
        if hasattr(self, '_click_path_tab_ref') and self._click_path_tab_ref:
            # Check if currently recording
            if hasattr(self._click_path_tab_ref, '_is_recording') and self._click_path_tab_ref._is_recording:
                print("[MainWindow] Stopping recording...")
                self._click_path_tab_ref.stop_recording()
            else:
                print("[MainWindow] Not currently recording")
        else:
            print("[MainWindow] Warning: _click_path_tab_ref not found")
    
    def _on_click_path_recording_changed(self, is_recording: bool):
        """
        Handle Click Path recording state changes.
        
        When recording is active via Ctrl+W / Ctrl+Q:
        - Disable Save and Reset buttons
        - Rely on theme/Qt disabled state to show gray visual
        """
        # Determine whether current profile is active (for safety rules)
        profile_active = False
        if 0 <= self.current_profile_index < len(self.profiles):
            profile = self.profiles[self.current_profile_index]
            profile_active = profile.get("is_active", False)
        
        # Save/Reset only可操作在「未啟用 profile 且沒有正在錄製 Click Path」時
        can_edit = (not is_recording) and (not profile_active)
        
        if hasattr(self, 'reset_button'):
            self.reset_button.setEnabled(can_edit)
        if hasattr(self, 'save_button'):
            self.save_button.setEnabled(can_edit)
    
    def closeEvent(self, event):
        """Handle window close event - auto-save config before closing."""
        # Stop status checking timer
        if hasattr(self, '_clicking_status_timer'):
            self._clicking_status_timer.stop()
        
        # Remove UI log handler
        if hasattr(self, 'ui_log_handler'):
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.ui_log_handler)
        
        # Stop any ongoing recording
        if hasattr(self, '_click_path_tab_ref') and self._click_path_tab_ref:
            if hasattr(self._click_path_tab_ref, '_is_recording') and self._click_path_tab_ref._is_recording:
                self._click_path_tab_ref.stop_recording()
        
        # Unregister global hotkeys
        if hasattr(self, 'hotkey_service'):
            self.hotkey_service.unregister_all_hotkeys()
        
        # Stop cursor clicking and unregister all profile hotkeys
        if hasattr(self, 'profile_hotkey_service'):
            self.profile_hotkey_service.unregister_all_hotkeys()
        
        # Save configuration before closing
        self._save_config()
        event.accept()
    
    def _save_config(self):
        """
        Save current configuration to file.
        
        Delegates to backend services for data serialization.
        """
        try:
            # Build config dictionary using ProfileService for serialization
            config = {
                "version": "1.0.0",
                "app_settings": {
                    "language": TranslationManager.get_current_language(),
                    "theme": self.current_theme,
                    "debug_mode": getattr(self, 'debug_mode', False),
                    "window_geometry": {
                        "x": self.geometry().x(),
                        "y": self.geometry().y(),
                        "width": self.geometry().width(),
                        "height": self.geometry().height()
                    }
                },
                "profiles": ProfileService.serialize_profiles(self.profiles)
            }
            
            # Save to file using ConfigManager
            self.config_manager.save_config(config)
        except Exception as e:
            # Log error but don't show to user (silent fail on auto-save)
            print(f"Failed to save config: {e}")
    
    def _load_profiles_from_config(self, config: dict):
        """
        Load Profile data from config and rebuild UI.
        
        Uses ProfileService for deserialization, then rebuilds UI components.
        
        Args:
            config: Configuration dictionary from ConfigManager
        """
        profiles_data = config.get("profiles", [])
        
        # Use ProfileService to deserialize profiles
        deserialized_profiles = ProfileService.deserialize_profiles(profiles_data)
        
        # Rebuild UI for each profile
        for profile in deserialized_profiles:
            # Extract data
            profile_id = profile["id"]
            name = profile["name"]
            start_hotkey = profile["start_hotkey"]
            end_hotkey = profile["end_hotkey"]
            is_active = profile["is_active"]
            is_saved = profile["is_saved"]
            cursor_interval = profile["cursor_interval"]
            cursor_button = profile["cursor_button"]
            cursor_count = profile["cursor_count"]
            click_path = profile["click_path"]
            
            # Debug logging for loaded profile data
            self._logger.info(f"📂 [MainWindow] Loading profile: {name} (ID: {profile_id})")
            self._logger.debug(f"📂 [MainWindow]   - is_saved: {is_saved}, is_active: {is_active}")
            self._logger.debug(f"📂 [MainWindow]   - click_path type: {type(click_path)}")
            self._logger.debug(f"📂 [MainWindow]   - click_path length: {len(click_path) if click_path else 0}")
            if click_path:
                self._logger.debug(f"📂 [MainWindow]   - click_path content (first 3 items): {click_path[:3]}")
                # Validate click_path structure
                for i, item in enumerate(click_path[:3]):
                    self._logger.debug(f"📂 [MainWindow]     - Item {i}: type={type(item)}, content={item}")
            
            # Create ProfileCard (UI component)
            hotkey_text = f"Start {start_hotkey}" if start_hotkey else "Start #"
            if end_hotkey:
                hotkey_text += f" End {end_hotkey}"
            
            card = ProfileCard(
                profile_name=name,
                hotkey=hotkey_text,
                is_active=is_active
            )
            card.clicked.connect(lambda checked=False, c=card: self.on_card_clicked(c))
            card.active_changed.connect(lambda active, c=card: self.on_card_active_changed(c, active))
            card.delete_requested.connect(lambda c=card: self.on_card_delete_requested(c))
            
            # Apply current theme
            card.set_theme(self.current_theme, primary_color="blue")
            
            # Set enabled state based on saved status
            card.set_enabled(is_saved)
            
            # Insert card before the stretch
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            
            # Store profile data with card reference
            profile["card"] = card
            self.profiles.append(profile)
            
            # Register hotkeys only for saved AND active profiles
            # Hotkeys are only available when Badge Status is "active"
            if is_saved and is_active:
                self.profile_hotkey_service.register_profile_hotkeys(profile)


