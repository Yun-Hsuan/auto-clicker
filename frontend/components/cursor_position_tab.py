"""
Cursor Position Tab Component
A reusable component for cursor position clicking settings.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QSpinBox, QComboBox, QGroupBox
from PySide6.QtCore import Qt, Signal
from frontend.utils.theme_manager import ThemeManager
from frontend.i18n.translation_manager import t


class CursorPositionTab(QWidget):
    """Cursor position clicking settings tab component."""
    
    # Signals emitted when settings change
    interval_changed = Signal(int)  # Click interval in milliseconds
    click_button_changed = Signal(str)  # Mouse button: "left", "right", "middle"
    click_count_changed = Signal(int)  # Number of clicks (0 = infinite)
    
    def __init__(self, parent=None):
        """Initialize cursor position tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._current_theme = "light"
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 16, 12, 16)  # Left, Top, Right, Bottom margins
        layout.setSpacing(16)  # Spacing between groups
        self.setLayout(layout)
        
        # === Click Interval Group ===
        interval_group = QGroupBox()
        interval_group.setObjectName("ClickIntervalGroupBox")
        interval_layout = QVBoxLayout()
        interval_layout.setContentsMargins(12, 12, 12, 12)
        interval_layout.setSpacing(8)
        interval_group.setLayout(interval_layout)
        
        # Title label
        self.interval_title_label = QLabel()
        self.interval_title_label.setObjectName("ClickIntervalTitle")
        self.interval_title_label.setTextFormat(Qt.TextFormat.RichText)
        interval_layout.addWidget(self.interval_title_label)
        
        # Form layout for interval settings
        interval_form = QFormLayout()
        interval_form.setContentsMargins(0, 0, 0, 0)
        interval_form.setSpacing(12)
        
        # Click interval (milliseconds)
        self.interval_label = QLabel()
        self.interval_label.setObjectName("ClickIntervalLabel")
        self.interval_label.setTextFormat(Qt.TextFormat.RichText)
        
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)  # Minimum 1ms
        self.interval_spinbox.setMaximum(60000)  # Maximum 60 seconds
        self.interval_spinbox.setValue(100)  # Default 100ms
        self.interval_spinbox.setSuffix(" ms")
        self.interval_spinbox.valueChanged.connect(self.interval_changed.emit)
        
        interval_form.addRow(self.interval_label, self.interval_spinbox)
        interval_layout.addLayout(interval_form)
        
        layout.addWidget(interval_group)
        
        # === Click Settings Group ===
        click_settings_group = QGroupBox()
        click_settings_group.setObjectName("ClickSettingsGroupBox")
        click_settings_layout = QVBoxLayout()
        click_settings_layout.setContentsMargins(12, 12, 12, 12)
        click_settings_layout.setSpacing(8)
        click_settings_group.setLayout(click_settings_layout)
        
        # Title label
        self.click_settings_title_label = QLabel()
        self.click_settings_title_label.setObjectName("ClickSettingsTitle")
        self.click_settings_title_label.setTextFormat(Qt.TextFormat.RichText)
        click_settings_layout.addWidget(self.click_settings_title_label)
        
        # Form layout for click settings
        click_form = QFormLayout()
        click_form.setContentsMargins(0, 0, 0, 0)
        click_form.setSpacing(12)
        
        # Mouse button selection
        self.button_label = QLabel()
        self.button_label.setObjectName("ClickButtonLabel")
        self.button_label.setTextFormat(Qt.TextFormat.RichText)
        
        self.button_combo = QComboBox()
        self.button_combo.addItem(t("main.profile.cursor.button.left", default="Left Button"), "left")
        self.button_combo.addItem(t("main.profile.cursor.button.right", default="Right Button"), "right")
        self.button_combo.addItem(t("main.profile.cursor.button.middle", default="Middle Button"), "middle")
        self.button_combo.currentIndexChanged.connect(
            lambda: self.click_button_changed.emit(self.button_combo.currentData())
        )
        
        click_form.addRow(self.button_label, self.button_combo)
        
        # Click count (0 = infinite)
        self.count_label = QLabel()
        self.count_label.setObjectName("ClickCountLabel")
        self.count_label.setTextFormat(Qt.TextFormat.RichText)
        
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setMinimum(0)  # 0 = infinite
        self.count_spinbox.setMaximum(999999)  # Maximum clicks
        self.count_spinbox.setValue(0)  # Default: infinite
        self.count_spinbox.setSpecialValueText(t("main.profile.cursor.count.infinite", default="Infinite"))
        self.count_spinbox.valueChanged.connect(self.click_count_changed.emit)
        
        click_form.addRow(self.count_label, self.count_spinbox)
        
        click_settings_layout.addLayout(click_form)
        layout.addWidget(click_settings_group)
        
        # Add stretch to push content to top
        layout.addStretch()
        
        # Apply initial translations and theme
        self.update_translations()
        self.update_theme(self._current_theme)
    
    def set_theme(self, theme_name: str):
        """Set theme.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        if self._current_theme != theme_name:
            self._current_theme = theme_name
            self.update_theme(theme_name)
    
    def update_theme(self, theme_name: str):
        """Update theme colors.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        tiffany_colors = ThemeManager.get_tiffany_colors()
        
        # Get text color based on theme
        # In dark mode, use white; in light mode, use tiffany blue
        if theme_name == "dark":
            text_color = "#ffffff"  # White for dark mode
        else:
            text_color = tiffany_colors.get("light", "#0ABAB5")  # Tiffany blue for light mode
        
        # Update interval group title
        interval_title_text = t("main.profile.cursor.interval.title", default="Click Interval")
        interval_title_html = f'<span style="color: {text_color};">{interval_title_text}</span>'
        self.interval_title_label.setText(interval_title_html)
        
        # Update interval label
        interval_label_text = t("main.profile.cursor.interval", default="Interval")
        interval_label_html = f'<span style="color: {text_color};">{interval_label_text}</span>'
        self.interval_label.setText(interval_label_html)
        
        # Update click settings group title
        click_settings_title_text = t("main.profile.cursor.settings.title", default="Click Settings")
        click_settings_title_html = f'<span style="color: {text_color};">{click_settings_title_text}</span>'
        self.click_settings_title_label.setText(click_settings_title_html)
        
        # Update button label
        button_label_text = t("main.profile.cursor.button", default="Mouse Button")
        button_label_html = f'<span style="color: {text_color};">{button_label_text}</span>'
        self.button_label.setText(button_label_html)
        
        # Update count label
        count_label_text = t("main.profile.cursor.count", default="Click Count")
        count_label_html = f'<span style="color: {text_color};">{count_label_text}</span>'
        self.count_label.setText(count_label_html)
    
    def update_translations(self):
        """Update translations."""
        # Update combo box items
        self.button_combo.clear()
        self.button_combo.addItem(t("main.profile.cursor.button.left", default="Left Button"), "left")
        self.button_combo.addItem(t("main.profile.cursor.button.right", default="Right Button"), "right")
        self.button_combo.addItem(t("main.profile.cursor.button.middle", default="Middle Button"), "middle")
        
        # Update spinbox special value text
        self.count_spinbox.setSpecialValueText(t("main.profile.cursor.count.infinite", default="Infinite"))
        
        # Update theme (which updates labels)
        self.update_theme(self._current_theme)
    
    def set_interval(self, interval_ms: int):
        """Set click interval.
        
        Args:
            interval_ms: Click interval in milliseconds
        """
        self.interval_spinbox.setValue(interval_ms)
    
    def get_interval(self) -> int:
        """Get click interval.
        
        Returns:
            int: Click interval in milliseconds
        """
        return self.interval_spinbox.value()
    
    def set_click_button(self, button: str):
        """Set mouse button.
        
        Args:
            button: Mouse button ("left", "right", or "middle")
        """
        index = self.button_combo.findData(button)
        if index >= 0:
            self.button_combo.setCurrentIndex(index)
    
    def get_click_button(self) -> str:
        """Get mouse button.
        
        Returns:
            str: Mouse button ("left", "right", or "middle")
        """
        return self.button_combo.currentData()
    
    def set_click_count(self, count: int):
        """Set click count.
        
        Args:
            count: Number of clicks (0 = infinite)
        """
        self.count_spinbox.setValue(count)
    
    def get_click_count(self) -> int:
        """Get click count.
        
        Returns:
            int: Number of clicks (0 = infinite)
        """
        return self.count_spinbox.value()

