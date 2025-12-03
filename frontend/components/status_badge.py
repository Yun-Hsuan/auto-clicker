"""
Status Badge Widget
A custom badge widget for displaying profile status (Active/Stopped).
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from frontend.utils.theme_manager import ThemeManager


class StatusBadge(QWidget):
    """Custom badge widget for displaying status."""
    
    def __init__(self, parent=None):
        """Initialize status badge.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._is_active = False
        self._status = "unsaved"  # "unsaved", "active", "stopped"
        self._current_theme = "light"
        
        self.setObjectName("StatusBadge")
        # Enable auto-fill background so styles can be applied
        self.setAutoFillBackground(True)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        # Main layout (no margins, no spacing)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Container widget for background and border-radius
        self.container_widget = QWidget(self)
        self.container_widget.setObjectName("StatusBadgeContainer")
        self.container_widget.setAutoFillBackground(True)
        main_layout.addWidget(self.container_widget)
        
        # Container layout
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(12, 4, 12, 4)
        container_layout.setSpacing(0)
        self.container_widget.setLayout(container_layout)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("StatusBadgeLabel")
        container_layout.addWidget(self.status_label)
        
        # Apply initial style
        self.update_style()
    
    def set_status(self, status: str):
        """Set status.
        
        Args:
            status: Status string ("unsaved", "active", or "stopped")
        """
        if self._status != status:
            self._status = status
            self._is_active = (status == "active")
            self.update_style()
    
    def set_active(self, is_active: bool):
        """Set active state (for backward compatibility).
        
        Args:
            is_active: Whether the profile is active
        """
        if is_active:
            self.set_status("active")
        else:
            # Only set to stopped if not unsaved
            if self._status != "unsaved":
                self.set_status("stopped")
    
    def set_theme(self, theme_name: str):
        """Set theme.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        if self._current_theme != theme_name:
            self._current_theme = theme_name
            self.update_style()
    
    def update_style(self):
        """Update badge style based on status and theme."""
        orange_colors = ThemeManager.get_orange_colors()
        tiffany_colors = ThemeManager.get_tiffany_colors()
        
        if self._status == "active":
            # Active state: Tiffany Blue background with white text
            if self._current_theme == "dark":
                bg_color = tiffany_colors["dark"]  # Darker Tiffany Blue for dark mode
            else:
                bg_color = tiffany_colors["light"]  # Tiffany Blue for light mode
            text_color = "#ffffff"  # White text for both modes
        elif self._status == "stopped":
            # Stopped state: orange background with white text
            bg_color = orange_colors["primary"]  # Orange
            text_color = "#ffffff"  # White text for both modes
        elif self._status == "recording":
            # Recording state: red background with white text
            bg_color = "#ff0000"  # Red
            text_color = "#ffffff"  # White text
        else:
            # Unsaved state: gray background with white text
            if self._current_theme == "dark":
                bg_color = "#666666"  # Gray for dark mode
            else:
                bg_color = "#999999"  # Gray for light mode
            text_color = "#ffffff"  # White text for both modes
        
        # Apply style to container widget (background and border-radius)
        container_style = f"""
            QWidget#StatusBadgeContainer {{
                background-color: {bg_color};
                border-radius: 12px;
                min-height: 24px;
            }}
        """
        self.container_widget.setStyleSheet(container_style)
        
        # Apply style to label (text color)
        label_style = f"""
            QLabel#StatusBadgeLabel {{
                color: {text_color};
                font-weight: bold;
                font-size: 12px;
                background-color: transparent;
                border: none;
            }}
        """
        self.status_label.setStyleSheet(label_style)
    
    def set_text(self, text: str):
        """Set badge text.
        
        Args:
            text: Badge text
        """
        self.status_label.setText(text)

