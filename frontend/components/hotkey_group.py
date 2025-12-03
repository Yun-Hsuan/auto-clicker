"""
Hotkey Group Component
A reusable component for hotkey settings with blue theme.
"""

from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QPixmap
from frontend.utils.theme_manager import ThemeManager
from frontend.utils.paths import get_icon_path
from frontend.i18n.translation_manager import t


class HotkeyGroup(QGroupBox):
    """Hotkey settings group component."""
    
    # Signals emitted when hotkeys change
    start_hotkey_changed = Signal(str)
    end_hotkey_changed = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize hotkey group.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("HotkeyGroupBox")
        self._current_theme = "light"
        
        # Hotkey capture state
        self._capturing_start = False
        self._capturing_end = False
        
        # Store previous hotkey values to revert if validation fails
        self._previous_start_hotkey = "#"
        self._previous_end_hotkey = "#"
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Custom title label with blue text
        self.title_label = QLabel()
        self.title_label.setObjectName("HotkeyTitle")
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.title_label)
        
        # Form layout for hotkey inputs
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)
        
        # Start Hotkey (Required) - Blue text with orange asterisk
        self.start_label = QLabel()
        self.start_label.setObjectName("HotkeyStartLabel")
        self.start_label.setTextFormat(Qt.TextFormat.RichText)
        
        self.start_input = QLineEdit()
        self.start_input.setText("#")  # Default value
        self.start_input.textChanged.connect(self.start_hotkey_changed.emit)
        # Install event filter for hotkey capture
        self.start_input.installEventFilter(self)
        self.start_input.setPlaceholderText(t("main.profile.hotkey.click_to_set", default="Click here and press a key combination"))
        
        form_layout.addRow(self.start_label, self.start_input)
        
        # End Hotkey - Blue text only (no asterisk, not required)
        self.end_label = QLabel()
        self.end_label.setObjectName("HotkeyEndLabel")
        self.end_label.setTextFormat(Qt.TextFormat.RichText)
        
        self.end_input = QLineEdit()
        self.end_input.setText("#")  # Default value
        self.end_input.textChanged.connect(self.end_hotkey_changed.emit)
        # Install event filter for hotkey capture
        self.end_input.installEventFilter(self)
        self.end_input.setPlaceholderText(t("main.profile.hotkey.click_to_set", default="Click here and press a key combination"))
        
        form_layout.addRow(self.end_label, self.end_input)
        
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
        # Update title
        hotkey_text = t("main.profile.hotkey", default="Hotkey")
        blue_colors = ThemeManager.get_blue_colors()
        hotkey_title_html = f'<span style="color: {blue_colors["primary"]};">{hotkey_text}</span>'
        self.title_label.setText(hotkey_title_html)
        
        # Update labels
        start_text = t("main.profile.hotkey.start", default="Start")
        orange_colors = ThemeManager.get_orange_colors()
        start_html = f'<span style="color: {blue_colors["primary"]};">{start_text}</span> <span style="color: {orange_colors["primary"]};">*</span>'
        self.start_label.setText(start_html)
        
        end_text = t("main.profile.hotkey.end", default="End")
        end_html = f'<span style="color: {blue_colors["primary"]};">{end_text}</span>'
        self.end_label.setText(end_html)
    
    def update_translations(self):
        """Update translations."""
        self.update_theme(self._current_theme)
    
    def set_start_hotkey(self, hotkey: str):
        """Set start hotkey.
        
        Args:
            hotkey: Start hotkey value
        """
        self.start_input.setText(hotkey)
    
    def get_start_hotkey(self) -> str:
        """Get start hotkey.
        
        Returns:
            str: Start hotkey value
        """
        return self.start_input.text()
    
    def set_end_hotkey(self, hotkey: str):
        """Set end hotkey.
        
        Args:
            hotkey: End hotkey value
        """
        self.end_input.setText(hotkey)
    
    def get_end_hotkey(self) -> str:
        """Get end hotkey.
        
        Returns:
            str: End hotkey value
        """
        return self.end_input.text()
    
    def eventFilter(self, obj, event):
        """
        Event filter to capture hotkey combinations.
        
        Args:
            obj: Object that received the event
            event: Event object
        
        Returns:
            bool: True if event was handled, False otherwise
        """
        # Only handle events for our input fields
        if obj not in (self.start_input, self.end_input):
            return super().eventFilter(obj, event)
        
        # Handle focus in: start capturing
        if event.type() == event.Type.FocusIn:
            if obj == self.start_input:
                self._capturing_start = True
                # Save current value as previous value before user starts typing
                self._previous_start_hotkey = self.start_input.text()
                self.start_input.setPlaceholderText(t("main.profile.hotkey.press_keys", default="Press key combination..."))
            elif obj == self.end_input:
                self._capturing_end = True
                # Save current value as previous value before user starts typing
                self._previous_end_hotkey = self.end_input.text()
                self.end_input.setPlaceholderText(t("main.profile.hotkey.press_keys", default="Press key combination..."))
            return False
        
        # Handle focus out: stop capturing
        if event.type() == event.Type.FocusOut:
            if obj == self.start_input:
                self._capturing_start = False
                self.start_input.setPlaceholderText(t("main.profile.hotkey.click_to_set", default="Click here and press a key combination"))
            elif obj == self.end_input:
                self._capturing_end = False
                self.end_input.setPlaceholderText(t("main.profile.hotkey.click_to_set", default="Click here and press a key combination"))
            return False
        
        # Handle key press: capture hotkey
        if event.type() == event.Type.KeyPress:
            # Check if we're capturing
            is_capturing = False
            if obj == self.start_input and self._capturing_start:
                is_capturing = True
            elif obj == self.end_input and self._capturing_end:
                is_capturing = True
            
            if is_capturing:
                hotkey_str = self._format_hotkey(event)
                if hotkey_str:
                    # ⭐ 防呆功能：检查 Start 和 End hotkey 是否相同
                    if obj == self.start_input:
                        # Setting start hotkey - check if it matches end hotkey
                        end_hotkey = self.end_input.text()
                        if hotkey_str == end_hotkey and hotkey_str != "#" and end_hotkey != "#":
                            # Show cute warning message box
                            self._show_duplicate_hotkey_warning()
                            # Revert to previous value
                            obj.setText(self._previous_start_hotkey)
                            return True  # Event handled, don't update
                        else:
                            # Update previous value
                            self._previous_start_hotkey = hotkey_str
                            # Update the input field
                            obj.setText(hotkey_str)
                            # Emit signal
                            self.start_hotkey_changed.emit(hotkey_str)
                    else:
                        # Setting end hotkey - check if it matches start hotkey
                        start_hotkey = self.start_input.text()
                        if hotkey_str == start_hotkey and hotkey_str != "#" and start_hotkey != "#":
                            # Show cute warning message box
                            self._show_duplicate_hotkey_warning()
                            # Revert to previous value
                            obj.setText(self._previous_end_hotkey)
                            return True  # Event handled, don't update
                        else:
                            # Update previous value
                            self._previous_end_hotkey = hotkey_str
                            # Update the input field
                            obj.setText(hotkey_str)
                            # Emit signal
                            self.end_hotkey_changed.emit(hotkey_str)
                    # Clear focus to stop capturing
                    obj.clearFocus()
                return True  # Event handled
        
        return super().eventFilter(obj, event)
    
    def _format_hotkey(self, event: QKeyEvent) -> str:
        """
        Format a key event into a hotkey string.
        
        Args:
            event: QKeyEvent object
        
        Returns:
            str: Formatted hotkey string (e.g., "Ctrl+W", "F1", "Ctrl+Shift+A")
                 Returns empty string if only modifier keys are pressed
        """
        modifiers = []
        key = event.key()
        
        # Ignore if only modifier keys are pressed (Ctrl, Alt, Shift, Meta)
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift, 
                   Qt.Key.Key_Meta, Qt.Key.Key_AltGr):
            return ""
        
        # Check for modifier keys
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifiers.append("Ctrl")
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifiers.append("Alt")
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifiers.append("Shift")
        if event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            modifiers.append("Meta")
        
        # Get the key name
        key_name = None
        
        # Function keys (F1-F12)
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            key_name = f"F{key - Qt.Key.Key_F1 + 1}"
        # Special keys
        elif key == Qt.Key.Key_Escape:
            key_name = "Esc"
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            key_name = "Enter"
        elif key == Qt.Key.Key_Space:
            key_name = "Space"
        elif key == Qt.Key.Key_Tab:
            key_name = "Tab"
        elif key == Qt.Key.Key_Backspace:
            key_name = "Backspace"
        elif key == Qt.Key.Key_Delete:
            key_name = "Delete"
        elif key == Qt.Key.Key_Insert:
            key_name = "Insert"
        elif key == Qt.Key.Key_Home:
            key_name = "Home"
        elif key == Qt.Key.Key_End:
            key_name = "End"
        elif key == Qt.Key.Key_PageUp:
            key_name = "PageUp"
        elif key == Qt.Key.Key_PageDown:
            key_name = "PageDown"
        elif key == Qt.Key.Key_Up:
            key_name = "Up"
        elif key == Qt.Key.Key_Down:
            key_name = "Down"
        elif key == Qt.Key.Key_Left:
            key_name = "Left"
        elif key == Qt.Key.Key_Right:
            key_name = "Right"
        # Regular keys (letters, numbers, etc.)
        elif Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            # Get the letter (A-Z)
            key_name = chr(ord('A') + (key - Qt.Key.Key_A))
        elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            # Get the number (0-9)
            key_name = chr(ord('0') + (key - Qt.Key.Key_0))
        else:
            # Try to get text representation
            text = event.text()
            if text and text.isprintable() and not text.isspace():
                key_name = text.upper()
        
        # If we couldn't determine the key, return empty string
        if not key_name:
            return ""
        
        # Combine modifiers and key
        if modifiers:
            return "+".join(modifiers) + "+" + key_name
        else:
            return key_name
    
    def _show_duplicate_hotkey_warning(self):
        """
        Show cute warning message box when Start and End hotkeys are the same.
        
        ⭐ 防呆功能：显示可爱的提示信息。
        """
        # Get parent widget for message box
        parent = self.parent()
        while parent and not hasattr(parent, 'current_theme'):
            parent = parent.parent()
        
        # Create cute warning message box
        msg_box = QMessageBox(parent if parent else None)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(t("dialog.hotkey.duplicate.title", default="快捷鍵重複"))
        
        # Set orange_shock icon
        shock_icon_path = get_icon_path("orange_shock.png")
        if shock_icon_path.exists():
            pixmap = QPixmap(str(shock_icon_path))
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            msg_box.setIconPixmap(scaled_pixmap)
        
        # Set cute message
        msg_box.setText(t("dialog.hotkey.duplicate.message", default="噓～這兩個不可以一樣唷～"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # Apply theme styling
        if parent and hasattr(parent, 'current_theme'):
            theme_name = parent.current_theme
        else:
            theme_name = self._current_theme
        
        theme_stylesheet = ThemeManager.get_theme(theme_name)
        custom_msgbox_style = f"""
            QMessageBox {{
                background-color: {'#ffffff' if theme_name == 'light' else '#1e1e1e'};
                color: {'#000000' if theme_name == 'light' else '#ffffff'};
                font-size: 14px;
                font-weight: bold;
            }}
            QMessageBox QLabel {{
                color: {'#000000' if theme_name == 'light' else '#ffffff'};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {'#ff9800' if theme_name == 'light' else '#ff9800'};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {'#f57c00' if theme_name == 'light' else '#f57c00'};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {'#e65100' if theme_name == 'light' else '#e65100'};
            }}
        """
        msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
        msg_box.exec()
    
    def set_start_hotkey(self, hotkey: str):
        """Set start hotkey.
        
        Args:
            hotkey: Start hotkey value
        """
        # Save current value as previous value before updating
        self._previous_start_hotkey = self.start_input.text()
        self.start_input.setText(hotkey)
        # Update previous value to the new value after setting
        self._previous_start_hotkey = hotkey
    
    def set_end_hotkey(self, hotkey: str):
        """Set end hotkey.
        
        Args:
            hotkey: End hotkey value
        """
        # Save current value as previous value before updating
        self._previous_end_hotkey = self.end_input.text()
        self.end_input.setText(hotkey)
        # Update previous value to the new value after setting
        self._previous_end_hotkey = hotkey

