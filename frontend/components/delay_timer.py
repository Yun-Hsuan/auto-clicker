"""
Delay Timer Component
A reusable component for displaying and editing delay between click steps.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QColor
from frontend.utils.theme_manager import ThemeManager
from frontend.i18n.translation_manager import t


class DashedLineWidget(QWidget):
    """Custom widget for drawing a vertical dashed line."""
    
    def __init__(self, parent=None, theme="light"):
        """Initialize dashed line widget.
        
        Args:
            parent: Parent widget
            theme: Current theme ('light' or 'dark')
        """
        super().__init__(parent)
        self._theme = theme
        self.setMinimumWidth(0)
        self.setFixedHeight(80)  # Match DelayTimer height
        
        # Make background transparent so the line is visible
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAutoFillBackground(False)
    
    def set_theme(self, theme_name: str):
        """Set theme.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        if self._theme != theme_name:
            self._theme = theme_name
            self.update()
    
    def paintEvent(self, event):
        """Draw vertical dashed line."""
        if self.width() <= 0 or self.height() <= 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get Tiffany blue color from theme manager
        tiffany_colors = ThemeManager.get_tiffany_colors()
        if self._theme == "dark":
            line_color = QColor(tiffany_colors.get("dark", "#0A9B96"))
        else:
            line_color = QColor(tiffany_colors.get("light", "#0ABAB5"))
        
        # Draw dashed vertical line in the center
        center_x = self.width() // 2
        
        pen = QPen(line_color, 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([4, 4])  # 4px dash, 4px gap
        painter.setPen(pen)
        
        top_margin = 10
        bottom_margin = 10
        
        painter.drawLine(
            center_x, top_margin,
            center_x, self.height() - bottom_margin
        )


class DelayTimer(QWidget):
    """Delay timer component between click steps."""
    
    # Signal emitted when delay changes
    delay_changed = Signal(int)  # Delay in milliseconds
    
    def __init__(self, parent=None):
        """Initialize delay timer.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._current_theme = "light"
        self._delay = 10  # Default 10ms delay
        self.setFixedHeight(80)  # Fixed height for consistent layout
        
        # Enable paint events and ensure widget is visible
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAutoFillBackground(False)  # Transparent background
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components with 3-section horizontal layout."""
        # Main horizontal layout: 3 equal parts (left empty, middle line, right controls)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # No margins to match ClickStepItem spacing
        main_layout.setSpacing(0)  # No spacing between sections
        self.setLayout(main_layout)
        
        # === Left Section: Empty (1/3 width) ===
        left_widget = QWidget()
        left_widget.setMinimumWidth(0)
        main_layout.addWidget(left_widget, 1)  # 1/3 of space
        
        # === Middle Section: Vertical dashed line (1/3 width) ===
        # Custom widget for drawing the dashed line
        self.middle_widget = DashedLineWidget(self, self._current_theme)
        self.middle_widget.setMinimumWidth(0)
        main_layout.addWidget(self.middle_widget, 1)  # 1/3 of space
        
        # === Right Section: Delay settings (1/3 width) ===
        # Container with Tiffany Blue background
        self.right_container = QWidget()
        self.right_container.setObjectName("DelayTimerContainer")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(12, 8, 12, 8)  # Padding for container
        right_layout.setSpacing(4)
        self.right_container.setLayout(right_layout)
        
        # Delay input with label
        delay_layout = QHBoxLayout()
        delay_layout.setContentsMargins(0, 0, 0, 0)
        delay_layout.setSpacing(8)
        
        self.delay_label = QLabel()
        self.delay_label.setObjectName("DelayTimerLabel")
        self.delay_label.setTextFormat(Qt.TextFormat.RichText)
        delay_layout.addWidget(self.delay_label)
        
        delay_layout.addStretch()
        
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(0)  # Minimum 0ms (no delay)
        self.delay_spinbox.setMaximum(60000)  # Maximum 60 seconds
        self.delay_spinbox.setValue(10)  # Default 10ms
        self.delay_spinbox.setSuffix(" ms")
        self.delay_spinbox.valueChanged.connect(self._on_delay_changed)
        delay_layout.addWidget(self.delay_spinbox)
        
        right_layout.addStretch()  # Push to center vertically
        right_layout.addLayout(delay_layout)
        right_layout.addStretch()  # Push to center vertically
        
        main_layout.addWidget(self.right_container, 1)  # 1/3 of space
        
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
        
        # Update middle widget theme
        if hasattr(self, 'middle_widget'):
            self.middle_widget.set_theme(theme_name)
    
    def update_theme(self, theme_name: str):
        """Update theme colors.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        tiffany_colors = ThemeManager.get_tiffany_colors()
        
        # Get colors from theme manager
        if theme_name == "dark":
            bg_color = tiffany_colors.get("dark", "#0A9B96")
            line_color = tiffany_colors.get("dark", "#0A9B96")
        else:
            bg_color = tiffany_colors.get("light", "#0ABAB5")
            line_color = tiffany_colors.get("light", "#0ABAB5")
        
        # Update label (white text for contrast on Tiffany blue background)
        delay_label_text = t("main.profile.path.delay", default="Delay")
        delay_label_html = f'<span style="color: #ffffff; font-weight: bold;">{delay_label_text}</span>'
        self.delay_label.setText(delay_label_html)
        
        # Update container background (Tiffany Blue)
        container_style = f"""
            QWidget#DelayTimerContainer {{
                background-color: {bg_color};
                border-radius: 8px;
                border: none;
            }}
        """
        if hasattr(self, 'right_container'):
            self.right_container.setStyleSheet(container_style)
        
        # Update middle widget (dashed line) theme
        if hasattr(self, 'middle_widget'):
            self.middle_widget.set_theme(theme_name)
    
    def update_translations(self):
        """Update translations."""
        # Update theme (which updates labels)
        self.update_theme(self._current_theme)
    
    def _on_delay_changed(self, value: int):
        """Handle delay value change.
        
        Args:
            value: New delay value in milliseconds
        """
        self._delay = value
        self.delay_changed.emit(value)
    
    def set_delay(self, delay_ms: int):
        """Set delay value.
        
        Args:
            delay_ms: Delay in milliseconds
        """
        self._delay = delay_ms
        self.delay_spinbox.setValue(delay_ms)
    
    def get_delay(self) -> int:
        """Get delay value.
        
        Returns:
            int: Delay in milliseconds
        """
        return self._delay
