"""
Profile Name Group Component
A reusable component for profile name input with blue theme.
"""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt, Signal
from frontend.utils.theme_manager import ThemeManager
from frontend.i18n.translation_manager import t


class ProfileNameGroup(QGroupBox):
    """Profile name input group component."""
    
    # Signal emitted when profile name changes
    name_changed = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize profile name group.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("ProfileNameGroupBox")
        self._current_theme = "light"
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        # Make the content visually closer to the top so it aligns better with HotkeyGroup
        layout.setContentsMargins(12, 4, 12, 12)
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Custom title label with blue text and orange asterisk
        self.title_label = QLabel()
        self.title_label.setObjectName("ProfileNameTitle")
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.title_label)
        
        # Profile name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            t("main.profile.name.placeholder", default="Enter profile name...")
        )
        self.name_input.textChanged.connect(self.name_changed.emit)
        layout.addWidget(self.name_input)

        # Invisible stretch to visually match HotkeyGroup height when sharing a row
        layout.addStretch(1)
        
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
        profile_name_text = t("main.profile.name", default="Profile Name")
        orange_colors = ThemeManager.get_orange_colors()
        blue_colors = ThemeManager.get_blue_colors()
        title_html = f'<span style="color: {blue_colors["primary"]};">{profile_name_text}</span> <span style="color: {orange_colors["primary"]};">*</span>'
        self.title_label.setText(title_html)
    
    def update_translations(self):
        """Update translations."""
        self.name_input.setPlaceholderText(
            t("main.profile.name.placeholder", default="Enter profile name...")
        )
        self.update_theme(self._current_theme)
    
    def set_name(self, name: str):
        """Set profile name.
        
        Args:
            name: Profile name
        """
        self.name_input.setText(name)
    
    def get_name(self) -> str:
        """Get profile name.
        
        Returns:
            str: Profile name
        """
        return self.name_input.text()

