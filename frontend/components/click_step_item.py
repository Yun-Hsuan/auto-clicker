"""
Click Step Item Component
A reusable component for displaying and editing a single click step in the click path.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QComboBox, QGroupBox, QPushButton, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from frontend.utils.theme_manager import ThemeManager
from frontend.i18n.translation_manager import t


class ClickStepItem(QGroupBox):
    """Single click step item component."""
    
    # Signals emitted when step data changes
    position_changed = Signal(int, int)  # x, y
    button_changed = Signal(str)  # "left", "right", "middle"
    click_count_changed = Signal(int)  # Number of clicks
    delete_requested = Signal()  # Request to delete this step
    step_name_changed = Signal(str)  # Step name changed
    
    def __init__(self, step_index: int, parent=None):
        """Initialize click step item.
        
        Args:
            step_index: Index of this step (1-based, for display)
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("ClickStepItemGroupBox")
        self._current_theme = "light"
        self._step_index = step_index
        self._step_name = None  # Custom step name (None means use default "Step {index}")
        self._x = 0
        self._y = 0
        self._button = "left"
        self._click_count = 1
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Header: Step name (editable) and delete button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        # Editable step name
        self.step_name_edit = QLineEdit()
        self.step_name_edit.setObjectName("ClickStepNameEdit")
        self.step_name_edit.setPlaceholderText(t("main.profile.path.step", default="Step {index}").format(index=self._step_index))
        self.step_name_edit.textChanged.connect(self._on_step_name_changed)
        header_layout.addWidget(self.step_name_edit)
        
        header_layout.addStretch()
        
        # Delete button
        self.delete_button = QPushButton()
        self.delete_button.setObjectName("ClickStepDeleteButton")
        self.delete_button.setText("×")
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.clicked.connect(self.delete_requested.emit)
        header_layout.addWidget(self.delete_button)
        
        layout.addLayout(header_layout)
        
        # Form layout for step settings
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(8)
        
        # Position (x, y) - Read-only display
        position_layout = QHBoxLayout()
        position_layout.setContentsMargins(0, 0, 0, 0)
        position_layout.setSpacing(8)
        
        self.position_label = QLabel()
        self.position_label.setObjectName("ClickStepPositionLabel")
        self.position_label.setTextFormat(Qt.TextFormat.RichText)
        position_layout.addWidget(self.position_label)
        
        position_layout.addStretch()
        
        self.position_value_label = QLabel()
        self.position_value_label.setObjectName("ClickStepPositionValue")
        self.position_value_label.setText("(0, 0)")
        position_layout.addWidget(self.position_value_label)
        
        form_layout.addLayout(position_layout)
        
        # Mouse button selection
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        
        self.button_label = QLabel()
        self.button_label.setObjectName("ClickStepButtonLabel")
        self.button_label.setTextFormat(Qt.TextFormat.RichText)
        button_layout.addWidget(self.button_label)
        
        button_layout.addStretch()
        
        self.button_combo = QComboBox()
        self.button_combo.addItem(t("main.profile.cursor.button.left", default="Left Button"), "left")
        self.button_combo.addItem(t("main.profile.cursor.button.right", default="Right Button"), "right")
        self.button_combo.addItem(t("main.profile.cursor.button.middle", default="Middle Button"), "middle")
        self.button_combo.currentIndexChanged.connect(
            lambda: self.button_changed.emit(self.button_combo.currentData())
        )
        button_layout.addWidget(self.button_combo)
        
        form_layout.addLayout(button_layout)
        
        # Click count
        count_layout = QHBoxLayout()
        count_layout.setContentsMargins(0, 0, 0, 0)
        count_layout.setSpacing(8)
        
        self.count_label = QLabel()
        self.count_label.setObjectName("ClickStepCountLabel")
        self.count_label.setTextFormat(Qt.TextFormat.RichText)
        count_layout.addWidget(self.count_label)
        
        count_layout.addStretch()
        
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setMinimum(1)  # Minimum 1 click
        self.count_spinbox.setMaximum(999)  # Maximum 999 clicks
        self.count_spinbox.setValue(1)  # Default 1 click
        self.count_spinbox.valueChanged.connect(self.click_count_changed.emit)
        count_layout.addWidget(self.count_spinbox)
        
        form_layout.addLayout(count_layout)
        
        layout.addLayout(form_layout)
        
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
        # Get theme stylesheet from ThemeManager (includes ClickStepItem styles)
        theme_stylesheet = ThemeManager.get_theme(theme_name)
        self.setStyleSheet(theme_stylesheet)
        
        # Get colors for labels and other elements
        orange_colors = ThemeManager.get_orange_colors()
        tiffany_colors = ThemeManager.get_tiffany_colors()
        
        # Determine text color based on theme
        if theme_name == "dark":
            text_color = "#ffffff"
            label_color = "#ffffff"  # White for labels in dark mode
        else:
            text_color = "#000000"
            label_color = tiffany_colors.get("light", "#0ABAB5")  # Tiffany Blue for labels in light mode
        
        # Update step name edit placeholder
        default_step_name = t("main.profile.path.step", default="Step {index}").format(index=self._step_index)
        if self._step_name is None or self._step_name == "":
            self.step_name_edit.setPlaceholderText(default_step_name)
            self.step_name_edit.setText("")
        else:
            self.step_name_edit.setText(self._step_name)
        
        # Update labels with correct color (white in dark mode, Tiffany Blue in light mode)
        position_label_text = t("main.profile.path.position", default="Position")
        position_label_html = f'<span style="color: {label_color};">{position_label_text}</span>'
        self.position_label.setText(position_label_html)
        
        button_label_text = t("main.profile.cursor.button", default="Mouse Button")
        button_label_html = f'<span style="color: {label_color};">{button_label_text}</span>'
        self.button_label.setText(button_label_html)
        
        count_label_text = t("main.profile.cursor.count", default="Click Count")
        count_label_html = f'<span style="color: {label_color};">{count_label_text}</span>'
        self.count_label.setText(count_label_html)
        
        # Update delete button style (orange) - this is component-specific, so keep it here
        delete_button_style = f"""
            QPushButton#ClickStepDeleteButton {{
                background-color: {orange_colors["primary"]};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#ClickStepDeleteButton:hover {{
                background-color: {orange_colors["hover"]};
            }}
            QPushButton#ClickStepDeleteButton:pressed {{
                background-color: {orange_colors["pressed"]};
            }}
        """
        self.delete_button.setStyleSheet(delete_button_style)
    
    def update_translations(self):
        """Update translations."""
        # Update combo box items
        self.button_combo.clear()
        self.button_combo.addItem(t("main.profile.cursor.button.left", default="Left Button"), "left")
        self.button_combo.addItem(t("main.profile.cursor.button.right", default="Right Button"), "right")
        self.button_combo.addItem(t("main.profile.cursor.button.middle", default="Middle Button"), "middle")
        
        # Update theme (which updates labels)
        self.update_theme(self._current_theme)
    
    def _on_step_name_changed(self, text: str):
        """Handle step name change.
        
        Args:
            text: New step name
        """
        self._step_name = text if text else None
        self.step_name_changed.emit(text if text else "")
    
    def set_step_name(self, name: str):
        """Set custom step name.
        
        Args:
            name: Step name (empty string or None to use default)
        """
        if name is None or name == "":
            self._step_name = None
            self.step_name_edit.setText("")
        else:
            self._step_name = name
            self.step_name_edit.setText(name)
    
    def get_step_name(self) -> str:
        """Get step name.
        
        Returns:
            str: Step name (empty string if using default)
        """
        if self._step_name is None or self._step_name == "":
            return t("main.profile.path.step", default="Step {index}").format(index=self._step_index)
        return self._step_name
    
    def set_step_index(self, index: int):
        """Set step index (for display).
        
        Args:
            index: Step index (1-based)
        """
        self._step_index = index
        # Update placeholder if name is empty
        if self._step_name is None or self._step_name == "":
            default_step_name = t("main.profile.path.step", default="Step {index}").format(index=self._step_index)
            self.step_name_edit.setPlaceholderText(default_step_name)
        self.update_theme(self._current_theme)  # Update theme
    
    def set_position(self, x: int, y: int):
        """Set click position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self._x = x
        self._y = y
        self.position_value_label.setText(f"({x}, {y})")
        self.position_changed.emit(x, y)
    
    def get_position(self):
        """Get click position.
        
        Returns:
            tuple: (x, y) coordinates
        """
        return (self._x, self._y)
    
    def set_button(self, button: str):
        """Set mouse button.
        
        Args:
            button: Mouse button ("left", "right", or "middle")
        """
        self._button = button
        index = self.button_combo.findData(button)
        if index >= 0:
            self.button_combo.setCurrentIndex(index)
    
    def get_button(self) -> str:
        """Get mouse button.
        
        Returns:
            str: Mouse button ("left", "right", or "middle")
        """
        return self.button_combo.currentData()
    
    def set_click_count(self, count: int):
        """Set click count.
        
        Args:
            count: Number of clicks
        """
        self._click_count = count
        self.count_spinbox.setValue(count)
    
    def get_click_count(self) -> int:
        """Get click count.
        
        Returns:
            int: Number of clicks
        """
        return self.count_spinbox.value()
    
    def get_step_data(self) -> dict:
        """Get all step data as a dictionary.
        
        Returns:
            dict: Step data with keys: x, y, button, click_count, name
        """
        return {
            "x": self._x,
            "y": self._y,
            "button": self.get_button(),
            "click_count": self.get_click_count(),
            "name": self.get_step_name()
        }
    
    def set_step_data(self, data: dict):
        """Set all step data from a dictionary.
        
        Args:
            data: Step data with keys: x, y, button, click_count, name
        """
        if "x" in data and "y" in data:
            self.set_position(data["x"], data["y"])
        if "button" in data:
            self.set_button(data["button"])
        if "click_count" in data:
            self.set_click_count(data["click_count"])
        if "name" in data:
            self.set_step_name(data["name"])

