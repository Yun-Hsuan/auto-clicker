"""
Profile Card Widget
A custom widget for displaying profile information in a card format.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal, QEvent, QPropertyAnimation, QEasingCurve, QRect, Property, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QIcon, QPainterPath
from frontend.utils.theme_manager import ThemeManager


class ToggleSwitch(QWidget):
    """Custom toggle switch widget with sliding animation."""
    
    toggled = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self._knob_position = 0
        self._enabled = True
        self._animation = QPropertyAnimation(self, b"knobPosition")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.setFixedSize(40, 20)  # Smaller size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_knob_position()
    
    def setEnabled(self, enabled: bool):
        """Enable or disable the toggle switch.
        
        Args:
            enabled: Whether the toggle switch should be enabled
        """
        self._enabled = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
    
    def knobPosition(self):
        return self._knob_position
    
    def setKnobPosition(self, value):
        self._knob_position = value
        self.update()
    
    knobPosition = Property(int, knobPosition, setKnobPosition)
    
    def isChecked(self):
        return self._checked
    
    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self._update_knob_position()
            self.toggled.emit(self._checked)
    
    def _update_knob_position(self):
        target = 18 if self._checked else 0  # Adjusted for smaller size
        self._animation.setStartValue(self._knob_position)
        self._animation.setEndValue(target)
        self._animation.start()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background color (Tiffany Blue when checked, orange when unchecked)
        orange_colors = ThemeManager.get_orange_colors()
        tiffany_colors = ThemeManager.get_tiffany_colors()
        
        if not self._enabled:
            # Disabled state: gray background
            bg_color = QColor("#cccccc")
        elif self._checked:
            # Use Tiffany Blue for checked state
            tiffany_blue = tiffany_colors["toggle_checked"]
            bg_color = QColor(tiffany_blue)
        else:
            # Use orange for unchecked state
            bg_color = QColor(orange_colors["toggle_unchecked"])
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        # Knob (white circle)
        knob_size = 16
        knob_x = self._knob_position + 2
        knob_y = 2
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(knob_x, knob_y, knob_size, knob_size)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._enabled:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)


class ProfileCard(QWidget):
    """Custom card widget for displaying profile information."""
    
    # Signals
    clicked = Signal()  # Emitted when card is clicked
    active_changed = Signal(bool)  # Emitted when active state changes
    delete_requested = Signal()  # Emitted when delete is requested
    
    def __init__(self, profile_name: str = "", hotkey: str = "", is_active: bool = False, parent=None):
        """Initialize profile card.
        
        Args:
            profile_name: Name of the profile
            hotkey: Hotkey string (e.g., "Start: F10 End: F9")
            is_active: Whether the profile is active
            parent: Parent widget
        """
        super().__init__(parent)
        self.profile_name = profile_name
        self.hotkey = hotkey
        self.is_active = is_active
        
        # Swipe-to-delete state
        self._swipe_offset = 0
        self._is_dragging = False
        self._drag_start_pos = QPoint()
        self._delete_button_width = 40
        
        # Theme state
        self._current_theme = "light"  # "light" or "dark"
        self._primary_color = "blue"  # "blue" or "orange" - ProfileCardContainer uses blue
        self._is_clicking = False  # Whether clicking is currently active
        
        # Set object name for styling
        self.setObjectName("ProfileCard")
        
        # Enable auto-fill background so styles can be applied
        self.setAutoFillBackground(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        # Use absolute positioning for swipe effect
        self.setMinimumHeight(80)
        
        # Outer container layout (contains delete button and swipeable card)
        # No layout, use absolute positioning
        
        # Delete button (fixed on the right side, always there but hidden behind card)
        self.delete_button = QPushButton()
        self.delete_button.setParent(self)
        self.delete_button.setFixedWidth(self._delete_button_width)
        self.delete_button.setFixedHeight(self.height())
        # Add border-radius to match ProfileCardContainer (8px)
        # Use orange color scheme from ThemeManager
        orange_colors = ThemeManager.get_orange_colors()
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {orange_colors["primary"]};
                color: white;
                border: none;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {orange_colors["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {orange_colors["pressed"]};
            }}
        """)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        # Position delete button on the right side with slight overlap
        # Move it slightly left to overlap with container (about 4px overlap)
        overlap = 4
        self.delete_button.move(self.width() - self._delete_button_width + overlap, 0)
        # Ensure delete button is below container (so it's covered initially)
        self.delete_button.lower()
        # Disable mouse events when hidden to prevent blocking drag
        self.delete_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        # Create flat trash icon using QPainter
        self._create_trash_icon()
        
        # Swipeable container widget (this will have the background and border)
        # Initially covers the delete button, moves left when swiped
        self.container_widget = QWidget(self)
        self.container_widget.setObjectName("ProfileCardContainer")
        self.container_widget.setAutoFillBackground(True)
        self.container_widget.resize(self.width(), self.height())
        self.container_widget.move(0, 0)  # Initially at position 0, covering delete button
        # Ensure container is above delete button
        self.container_widget.raise_()
        
        # Container layout (horizontal: left content, right toggle)
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(16)
        self.container_widget.setLayout(container_layout)
        
        # Left side: Content layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Profile title label (top row)
        self.title_label = QLabel(self.profile_name)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        content_layout.addWidget(self.title_label)
        
        # Hotkey label (bottom row)
        self.hotkey_label = QLabel(self.hotkey if self.hotkey else "")
        self.hotkey_label.setStyleSheet("font-size: 12px; color: #666;")
        content_layout.addWidget(self.hotkey_label)
        
        # Add content layout to container (left side, takes remaining space)
        container_layout.addLayout(content_layout, 1)
        
        # Right side: Toggle switch (vertically centered)
        self.toggle_switch = ToggleSwitch()
        self.toggle_switch.setChecked(self.is_active)
        self.toggle_switch.toggled.connect(self.on_active_changed)
        container_layout.addWidget(self.toggle_switch, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Apply card style (light green background with border)
        self.update_style()
    
    def resizeEvent(self, event):
        """Handle resize event to update widget positions."""
        super().resizeEvent(event)
        self.container_widget.resize(self.width(), self.height())
        if hasattr(self, 'delete_button'):
            self.delete_button.setFixedHeight(self.height())
            # Position delete button on the right side with slight overlap
            overlap = 4
            self.delete_button.move(self.width() - self._delete_button_width + overlap, 0)
    
    def update_style(self):
        """Update card style based on theme, primary color, and clicking state."""
        # If clicking, use pinkish red colors; otherwise use normal colors
        if self._is_clicking:
            scheme = ThemeManager.get_clicking_colors(self._current_theme)
        else:
            scheme = ThemeManager.get_color_scheme(self._current_theme, self._primary_color)
        
        # Apply style to the container widget
        container_style = f"""
            QWidget#ProfileCardContainer {{
                background-color: {scheme["bg"]};
                border: 1px solid {scheme["border"]};
                border-radius: 4px;
            }}
        """
        self.container_widget.setStyleSheet(container_style)
        
        # Update text colors
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: 16px; color: {scheme['text']};")
        self.hotkey_label.setStyleSheet(f"font-size: 12px; color: {scheme['text_secondary']};")
    
    def set_theme(self, theme_name: str, primary_color: str = "blue"):
        """
        Set theme and primary color for the card.
        
        Args:
            theme_name: "light" or "dark"
            primary_color: "blue" or "orange"
        """
        self._current_theme = theme_name
        self._primary_color = primary_color
        self.update_style()
    
    def set_profile_name(self, name: str):
        """Update profile name."""
        self.profile_name = name
        self.title_label.setText(name)
    
    def set_hotkey(self, hotkey: str):
        """Update hotkey."""
        self.hotkey = hotkey
        self.hotkey_label.setText(hotkey if hotkey else "")
    
    def on_active_changed(self, checked):
        """Handle toggle switch state change."""
        self.is_active = checked
        self.active_changed.emit(self.is_active)
    
    def set_active(self, active: bool):
        """Update active state."""
        self.is_active = active
        self.toggle_switch.setChecked(active)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the toggle switch.
        
        Args:
            enabled: Whether the toggle switch should be enabled
        """
        self.toggle_switch.setEnabled(enabled)
    
    def set_clicking(self, is_clicking: bool):
        """
        Set clicking state to show visual feedback.
        
        When clicking is active, the card will show pinkish red colors.
        When stopped, it will return to normal blue colors.
        
        Args:
            is_clicking: True if clicking is active, False otherwise
        """
        if self._is_clicking != is_clicking:
            self._is_clicking = is_clicking
            self.update_style()
    
    def mousePressEvent(self, event):
        """Handle mouse press event for swipe detection."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on toggle switch
            toggle_pos = self.container_widget.mapToParent(self.toggle_switch.pos())
            toggle_rect = QRect(toggle_pos, self.toggle_switch.size())
            if toggle_rect.contains(event.pos()):
                return super().mousePressEvent(event)
            
            # Check if clicking on delete button (only when it's visible and enabled)
            if (self._swipe_offset < 0 and 
                not self.delete_button.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) and
                self.delete_button.geometry().contains(event.pos())):
                return super().mousePressEvent(event)
            
            # Start dragging
            self._is_dragging = True
            self._drag_start_pos = event.pos()
            self._swipe_start_offset = self._swipe_offset
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move event for swipe gesture."""
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            # Calculate swipe offset (left swipe = negative delta_x)
            delta_x = event.pos().x() - self._drag_start_pos.x()
            new_offset = self._swipe_start_offset + delta_x
            
            # Limit swipe to the left (negative values)
            # Allow slight overlap (4px) so container and delete button overlap nicely
            # Max offset is delete button width minus overlap
            max_offset = -(self._delete_button_width - 8)
            self._swipe_offset = max(max_offset, min(0, new_offset))
            # Update position immediately to show delete button
            self._update_swipe_position()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event to complete or cancel swipe."""
        if self._is_dragging:
            self._is_dragging = False
            
            # Check if this was just a click (no significant movement)
            # If swipe offset hasn't changed much, treat it as a click
            if abs(self._swipe_offset - self._swipe_start_offset) < 5:
                # This was a click, not a swipe - emit clicked signal
                # But only if we're not clicking on toggle or delete button
                if (self._swipe_offset >= 0 and 
                    not self.delete_button.geometry().contains(event.pos())):
                    # Check if clicking on toggle switch
                    toggle_pos = self.container_widget.mapToParent(self.toggle_switch.pos())
                    toggle_rect = QRect(toggle_pos, self.toggle_switch.size())
                    if not toggle_rect.contains(event.pos()):
                        # Regular click on card - emit clicked signal
                        self.clicked.emit()
            else:
                # This was a swipe - handle swipe logic
                # Calculate max offset with overlap
                max_offset = -(self._delete_button_width - 4)
                # If swiped more than half, snap to delete position
                if abs(self._swipe_offset) > abs(max_offset) / 2:
                    self._animate_swipe(max_offset)
                else:
                    # Snap back to original position
                    self._animate_swipe(0)
        super().mouseReleaseEvent(event)
    
    def _update_swipe_position(self):
        """Update the visual position of the card based on swipe offset."""
        # When swiping left (negative offset), move card left to reveal delete button on right
        # Container widget moves left, naturally revealing the delete button that's fixed on the right
        self.container_widget.move(self._swipe_offset, 0)
        
        # Delete button is always there, fixed on the right side
        # When container moves left (negative offset), delete button naturally becomes visible
        # We don't need to show/hide or change z-order, it's already positioned correctly
        if self._swipe_offset < 0:
            # Enable mouse events when visible
            self.delete_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        else:
            # Disable mouse events when hidden to prevent blocking drag
            self.delete_button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    
    def _animate_swipe(self, target_offset):
        """Animate swipe to target position."""
        animation = QPropertyAnimation(self, b"swipeOffset")
        animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(self._swipe_offset)
        animation.setEndValue(target_offset)
        animation.start()
        self._swipe_offset = target_offset
    
    def swipeOffset(self):
        """Property getter for swipe offset."""
        return self._swipe_offset
    
    def setSwipeOffset(self, value):
        """Property setter for swipe offset."""
        self._swipe_offset = value
        self._update_swipe_position()
    
    swipeOffset = Property(int, swipeOffset, setSwipeOffset)
    
    def _create_trash_icon(self):
        """Create a flat trash icon for the delete button."""
        # Create a pixmap for the icon
        from PySide6.QtGui import QPixmap
        icon_size = 24
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        
        # Draw flat trash icon (simplified design)
        # Trash can body (rectangle with rounded top)
        body_width = 14
        body_height = 12
        body_x = (icon_size - body_width) / 2
        body_y = icon_size - body_height - 4
        
        # Top lid
        painter.drawRoundedRect(body_x, body_y, body_width, 2, 1, 1)
        # Body
        painter.drawRect(body_x + 1, body_y + 2, body_width - 2, body_height - 2)
        
        # Handle (small rectangle on top)
        handle_width = 4
        handle_height = 2
        handle_x = (icon_size - handle_width) / 2
        handle_y = body_y - handle_height
        painter.drawRect(handle_x, handle_y, handle_width, handle_height)
        
        # Lines on body (to indicate it's a trash can)
        line_y1 = body_y + 5
        line_y2 = body_y + 8
        line_x = body_x + 3
        painter.drawLine(line_x, line_y1, line_x + body_width - 6, line_y1)
        painter.drawLine(line_x, line_y2, line_x + body_width - 6, line_y2)
        
        painter.end()
        
        # Set icon to button
        icon = QIcon(pixmap)
        self.delete_button.setIcon(icon)
        self.delete_button.setIconSize(pixmap.size())
    
    def on_delete_clicked(self):
        """Handle delete button click."""
        self.delete_requested.emit()
    
    def reset_swipe(self):
        """Reset swipe position to original."""
        self._animate_swipe(0)
