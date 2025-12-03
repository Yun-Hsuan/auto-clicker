"""
Click Path Tab Component
A reusable component for recording and managing click sequences.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon, QPixmap
from frontend.utils.theme_manager import ThemeManager
from frontend.i18n.translation_manager import t
from frontend.components.click_step_item import ClickStepItem
from frontend.components.delay_timer import DelayTimer
from frontend.components.status_badge import StatusBadge
from frontend.utils.mouse_listener import MouseListener
from frontend.utils.paths import get_icon_path
import platform
import logging
import time
from typing import Optional


class ClickPathTab(QWidget):
    """Click path recording tab component."""
    
    # Signals emitted when path data changes
    path_changed = Signal(list)  # List of step data dictionaries
    
    # Signal emitted when mouse click is detected (from background thread)
    mouse_click_detected = Signal(int, int, str)  # x, y, button
    
    # Signal emitted when recording state changes (True = recording, False = stopped)
    recording_state_changed = Signal(bool)
    
    def __init__(self, parent=None):
        """Initialize click path tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._current_theme = "light"
        self._is_recording = False
        self._items = []  # List of widgets (ClickStepItem or DelayTimer) in alternating order
        self._mouse_listener = MouseListener()
        self._logger = logging.getLogger(__name__)
        self._recording_start_time = None  # Track recording start time for debug logs
        self._current_profile_id: Optional[str] = None  # UUID of the current profile
        
        self.init_ui()
    
    def set_current_profile_id(self, profile_id: Optional[str]):
        """
        Set the current profile ID (UUID).
        
        This identifies which profile the click path recording belongs to.
        Profile ID is used instead of name because profile names can be changed.
        
        Args:
            profile_id: UUID of the current profile, or None if no profile is selected
        """
        self._current_profile_id = profile_id
        if profile_id:
            self._logger.debug(f"[Click Path] Current profile ID set to: {profile_id}")
        else:
            self._logger.debug("[Click Path] Current profile ID cleared (no profile selected)")
    
    def get_current_profile_id(self) -> Optional[str]:
        """
        Get the current profile ID (UUID).
        
        Returns:
            UUID of the current profile, or None if no profile is selected
        """
        return self._current_profile_id
    
    def set_debug_mode(self, enabled: bool):
        """
        Set debug mode state and update UI visibility.
        
        Args:
            enabled: True to enable debug mode, False to disable
        """
        if hasattr(self, 'load_test_button'):
            self.load_test_button.setVisible(enabled)
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, '_mouse_listener'):
            self._mouse_listener.stop_listening()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 16, 0, 0)  # Top margin: 16px
        layout.setSpacing(16)
        self.setLayout(layout)
        
        # === Top Control Container (3 columns) ===
        top_container = QWidget()
        top_container_layout = QHBoxLayout()
        top_container_layout.setContentsMargins(12, 8, 12, 8)  # Left, Top, Right, Bottom padding
        top_container_layout.setSpacing(12)
        top_container.setLayout(top_container_layout)
        
        # Left: Status Badge
        self.recording_badge = StatusBadge()
        self.recording_badge.set_status("unsaved")  # Default: orange status badge
        top_container_layout.addWidget(self.recording_badge, 1)  # 1/3 width
        
        # Middle: Load Test Data button (only visible in debug mode)
        self.load_test_button = QPushButton()
        self.load_test_button.setObjectName("ClickPathLoadTestButton")
        self.load_test_button.clicked.connect(self._load_test_data)
        self.load_test_button.setVisible(False)  # Hidden by default, shown only in debug mode
        top_container_layout.addWidget(self.load_test_button, 1)  # 1/3 width
        
        # Right: Clear All button
        self.clear_button = QPushButton()
        self.clear_button.setObjectName("ClickPathClearButton")
        self.clear_button.clicked.connect(self.clear_steps)
        top_container_layout.addWidget(self.clear_button, 1)  # 1/3 width
        
        layout.addWidget(top_container)
        
        # === Steps List (Scrollable) ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container widget for steps
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout()
        self.steps_layout.setContentsMargins(0, 0, 0, 0)
        self.steps_layout.setSpacing(12)
        self.steps_layout.addStretch()  # Push steps to top
        self.steps_container.setLayout(self.steps_layout)
        
        scroll_area.setWidget(self.steps_container)
        layout.addWidget(scroll_area)
        
        # Connect mouse click signal (for thread-safe communication)
        self.mouse_click_detected.connect(self._on_mouse_click_safe)
        
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
            
        # Update all items (steps and delays)
        for item in self._items:
            if hasattr(item, 'set_theme'):
                item.set_theme(theme_name)
    
    def update_theme(self, theme_name: str):
        """Update theme colors.
        
        Args:
            theme_name: Theme name ('light' or 'dark')
        """
        blue_colors = ThemeManager.get_blue_colors()
        gray_colors = ThemeManager.get_gray_colors(theme_name)
        
        # Update recording badge theme
        if hasattr(self, 'recording_badge'):
            self.recording_badge.set_theme(theme_name)
            self._update_recording_badge()
        
        # Update load test button style (blue, for testing)
        load_test_button_style = f"""
            QPushButton#ClickPathLoadTestButton {{
                background-color: {blue_colors["primary"]};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton#ClickPathLoadTestButton:hover {{
                background-color: {blue_colors["hover"]};
            }}
            QPushButton#ClickPathLoadTestButton:pressed {{
                background-color: {blue_colors["pressed"]};
            }}
        """
        self.load_test_button.setStyleSheet(load_test_button_style)
        
        # Update clear button style (gray by default, blue on hover)
        clear_button_style = f"""
            QPushButton#ClickPathClearButton {{
                background-color: {gray_colors["default"]};
                color: {gray_colors["text"]};
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton#ClickPathClearButton:hover {{
                background-color: {blue_colors["primary"]};
                color: white;
            }}
            QPushButton#ClickPathClearButton:pressed {{
                background-color: {blue_colors["pressed"]};
                color: white;
            }}
        """
        self.clear_button.setStyleSheet(clear_button_style)
    
    def update_translations(self):
        """Update translations."""
        # Update button texts
        self.clear_button.setText(t("main.profile.path.clear", default="Clear All"))
        self.load_test_button.setText(t("main.profile.path.load_test", default="Load Test Data"))
        
        # Update recording badge text
        self._update_recording_badge()
        
        # Update theme (which updates labels)
        self.update_theme(self._current_theme)
    
    def _update_recording_badge(self):
        """Update recording badge text and status."""
        if not hasattr(self, 'recording_badge'):
            return
        
        if self._is_recording:
            # Recording: red status
            self.recording_badge.set_status("recording")
            status_text = t("main.profile.path.recording.badge", default="记录中，按Ctrl+Q 停止")
        else:
            # Not recording: orange status
            self.recording_badge.set_status("stopped")  # Use "stopped" status (orange)
            status_text = t("main.profile.path.ready.badge", default="按Ctrl+W 开始记录")
        
        self.recording_badge.set_text(status_text)
    
    def start_recording(self):
        """Start recording mouse clicks."""
        if self._is_recording:
            return
        
        self._is_recording = True
        self._recording_start_time = time.time()  # Track start time for debug logs
        self.update_translations()
        self.update_theme(self._current_theme)
        
        # Notify listeners (e.g., MainWindow) that recording has started
        try:
            self.recording_state_changed.emit(True)
        except Exception as e:
            self._logger.error(f"Error emitting recording_state_changed(True): {e}")
        
        # Start global mouse listener
        self._mouse_listener.start_listening(self._on_mouse_click)
        
        # Log recording start
        self._logger.info("🎬 [Click Path] 開始記錄點擊路徑 (使用 Windows Hook API)")
    
    def stop_recording(self):
        """Stop recording mouse clicks."""
        if not self._is_recording:
            return
        
        try:
            self._is_recording = False
            
            # Update UI (with error handling)
            try:
                self.update_translations()
                self.update_theme(self._current_theme)
            except Exception as e:
                self._logger.error(f"Error updating UI in stop_recording: {e}")
            
            # Stop global mouse listener (with comprehensive error handling)
            try:
                if self._mouse_listener and self._mouse_listener.is_listening():
                    self._mouse_listener.stop_listening()
            except Exception as e:
                self._logger.error(f"Error stopping mouse listener: {e}", exc_info=True)
                # Continue even if stopping listener fails
            
            # Remove last DelayTimer if it exists (last step doesn't need a delay)
            # Only if there are items and the last one is a DelayTimer
            # Important: Check list is not empty before accessing [-1]
            if self._items and len(self._items) > 0:
                try:
                    last_item = self._items[-1]
                    if isinstance(last_item, DelayTimer):
                        # Safely remove the last DelayTimer
                        self.steps_layout.removeWidget(last_item)
                        last_item.setParent(None)
                        last_item.deleteLater()
                        # Remove from list (use index to avoid issues if item appears multiple times)
                        del self._items[-1]
                except (IndexError, AttributeError) as e:
                    self._logger.error(f"Error removing last DelayTimer (list may be empty or corrupted): {e}")
                except Exception as e:
                    self._logger.error(f"Error removing last DelayTimer: {e}", exc_info=True)
            
            # IMPORTANT: Always emit path_changed signal after stopping recording
            # This ensures the path data is updated and saved to the profile
            # Wrap in try-except to prevent crashes
            try:
                self._on_path_changed()
            except Exception as e:
                self._logger.error(f"Error in _on_path_changed during stop_recording: {e}", exc_info=True)
                # Try to emit empty path as fallback
                try:
                    self.path_changed.emit([])
                except Exception as e2:
                    self._logger.error(f"Error emitting path_changed signal: {e2}")
            
            # Log recording stop
            try:
                step_count = sum(1 for item in self._items if isinstance(item, ClickStepItem))
                self._logger.info(f"🛑 [Click Path] 停止記錄，共記錄 {step_count} 個點擊步驟")
            except Exception as e:
                self._logger.error(f"Error counting steps: {e}")
            
            # Reset recording start time
            self._recording_start_time = None
            
        except Exception as e:
            self._logger.error(f"Critical error in stop_recording: {e}", exc_info=True)
            # Ensure recording state is reset even if there's an error
            self._is_recording = False
            try:
                if self._mouse_listener and self._mouse_listener.is_listening():
                    self._mouse_listener.stop_listening()
            except Exception as e2:
                self._logger.error(f"Error stopping mouse listener in exception handler: {e2}")
        finally:
            # Always notify listeners that recording has stopped
            try:
                self.recording_state_changed.emit(False)
            except Exception as e:
                self._logger.error(f"Error emitting recording_state_changed(False): {e}")
    
    def _on_mouse_click(self, x: int, y: int, button: str):
        """
        Handle mouse click event from listener.
        
        This method is called from a background thread (pynput listener).
        We emit a signal to safely pass the event to the main GUI thread.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ("left", "right", or "middle")
        """
        # Emit signal (thread-safe, will be handled on main thread)
        self.mouse_click_detected.emit(x, y, button)
    
    def _on_mouse_click_safe(self, x: int, y: int, button: str):
        """
        Safely handle mouse click on the main GUI thread.
        
        This method is called via signal from the background thread.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ("left", "right", or "middle")
        """
        if self._is_recording:
            # Calculate reaction time (time since recording started or last click)
            current_time = time.time()
            if self._recording_start_time:
                reaction_time = (current_time - self._recording_start_time) * 1000  # Convert to ms
            else:
                reaction_time = 0
            
            # Log click event (similar to Cursor Position debug logs)
            self._logger.info(
                f"🖱️ [Click Path] 記錄點擊: "
                f"位置 ({x}, {y}), "
                f"按鈕: {button}, "
                f"反應時間: {reaction_time:.2f}ms, "
                f"監聽方式: Windows Hook API"
            )
            
            # Add click step
            self.add_click_step(x, y, button)
            
            # Update recording start time for next click's reaction time calculation
            self._recording_start_time = current_time
    
    def add_click_step(self, x: int, y: int, button: str = "left"):
        """Add a new click step with delay timer.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ("left", "right", or "middle")
        """
        # Calculate step index (number of steps, not items)
        step_count = sum(1 for item in self._items if isinstance(item, ClickStepItem))
        step_index = step_count + 1
        
        # Create step item
        step_item = ClickStepItem(step_index, self)
        step_item.set_position(x, y)
        step_item.set_button(button)
        step_item.set_theme(self._current_theme)
        
        # Connect signals
        step_item.position_changed.connect(lambda x, y: self._on_path_changed())
        step_item.button_changed.connect(lambda: self._on_path_changed())
        step_item.click_count_changed.connect(lambda: self._on_path_changed())
        step_item.step_name_changed.connect(lambda: self._on_path_changed())
        step_item.delete_requested.connect(lambda: self._remove_step(step_item))
        
        # Insert step before stretch
        insert_index = self.steps_layout.count() - 1
        self.steps_layout.insertWidget(insert_index, step_item)
        self._items.append(step_item)
        
        # Add delay timer after step (default 10ms delay)
        delay_timer = DelayTimer(self)
        delay_timer.set_delay(10)  # Default 10ms
        delay_timer.set_theme(self._current_theme)
        delay_timer.delay_changed.connect(lambda: self._on_path_changed())
        
        # Insert delay after the step
        self.steps_layout.insertWidget(insert_index + 1, delay_timer)
        self._items.append(delay_timer)
        
        # Update step indices
        self._update_step_indices()
        
        # Emit path changed signal
        self._on_path_changed()
    
    def _remove_step(self, step_item: ClickStepItem):
        """Remove a click step and its associated delay timers.
        
        Args:
            step_item: Step item to remove
        """
        if step_item not in self._items:
            return
        
        step_index = self._items.index(step_item)
        
        # Remove the step
        self.steps_layout.removeWidget(step_item)
        step_item.setParent(None)
        step_item.deleteLater()
        self._items.remove(step_item)
        
        # Remove associated delay timers
        # If not the first item, remove the delay before it
        if step_index > 0 and isinstance(self._items[step_index - 1], DelayTimer):
            delay = self._items[step_index - 1]
            self.steps_layout.removeWidget(delay)
            delay.setParent(None)
            delay.deleteLater()
            self._items.remove(delay)
        
        # If not the last item, remove the delay after it
        if step_index < len(self._items) and isinstance(self._items[step_index], DelayTimer):
            delay = self._items[step_index]
            self.steps_layout.removeWidget(delay)
            delay.setParent(None)
            delay.deleteLater()
            self._items.remove(delay)
        
        # Update step indices
        self._update_step_indices()
        
        # Emit path changed signal
        self._on_path_changed()
    
    def _update_step_indices(self):
        """Update step indices for all steps."""
        step_number = 1
        for item in self._items:
            if isinstance(item, ClickStepItem):
                item.set_step_index(step_number)
                step_number += 1
    
    def clear_steps(self):
        """Clear all click steps and delays."""
        if not any(isinstance(item, ClickStepItem) for item in self._items):
            return
        
        # Create custom message box with orange_shock icon
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(t("main.profile.path.clear.confirm.title", default="清除全部"))
        
        # Set orange_shock icon
        shock_icon_path = get_icon_path("orange_shock.png")
        if shock_icon_path.exists():
            pixmap = QPixmap(str(shock_icon_path))
            # Scale to appropriate size for message box (80x80)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            msg_box.setIconPixmap(scaled_pixmap)
        
        # Set cute message
        msg_box.setText(t("main.profile.path.clear.confirm.message", default="你確定嗎？全部清除？"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Apply theme styling with custom message box styles
        theme_stylesheet = ThemeManager.get_theme(self._current_theme)
        # Add custom styling for message box to make it more beautiful
        custom_msgbox_style = f"""
            QMessageBox {{
                background-color: {'#ffffff' if self._current_theme == 'light' else '#1e1e1e'};
                color: {'#000000' if self._current_theme == 'light' else '#ffffff'};
                font-size: 14px;
                font-weight: bold;
            }}
            QMessageBox QLabel {{
                color: {'#000000' if self._current_theme == 'light' else '#ffffff'};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {'#2196f3' if self._current_theme == 'light' else '#64b5f6'};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {'#1976d2' if self._current_theme == 'light' else '#90caf9'};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {'#1565c0' if self._current_theme == 'light' else '#42a5f5'};
            }}
        """
        msg_box.setStyleSheet(theme_stylesheet + custom_msgbox_style)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove all items (steps and delays)
            for item in self._items[:]:  # Copy list to avoid modification during iteration
                if isinstance(item, ClickStepItem):
                    self._remove_step(item)
    
    def _on_path_changed(self):
        """Handle path data change."""
        try:
            # Collect all path data (steps with delays)
            path_data = []
            i = 0
            while i < len(self._items):
                item = self._items[i]
                if isinstance(item, ClickStepItem):
                    try:
                        step_data = item.get_step_data()
                        # Get delay after this step (if exists)
                        if i + 1 < len(self._items) and isinstance(self._items[i + 1], DelayTimer):
                            step_data["delay"] = self._items[i + 1].get_delay()
                        else:
                            step_data["delay"] = 0  # No delay for last step
                        path_data.append(step_data)
                    except Exception as e:
                        self._logger.error(f"Error getting step data for item {i}: {e}")
                i += 1
            
            # Emit signal (even if path_data is empty, which is valid)
            self.path_changed.emit(path_data)
        except Exception as e:
            self._logger.error(f"Error in _on_path_changed: {e}", exc_info=True)
            # Emit empty list as fallback to prevent crashes
            try:
                self.path_changed.emit([])
            except Exception as e2:
                self._logger.error(f"Error emitting path_changed signal: {e2}")
    
    def get_path_data(self) -> list:
        """Get all path data as a list of dictionaries.
        
        Returns:
            list: List of step data dictionaries with delay
        """
        path_data = []
        i = 0
        while i < len(self._items):
            item = self._items[i]
            if isinstance(item, ClickStepItem):
                step_data = item.get_step_data()
                # Get delay after this step (if exists)
                if i + 1 < len(self._items) and isinstance(self._items[i + 1], DelayTimer):
                    step_data["delay"] = self._items[i + 1].get_delay()
                else:
                    step_data["delay"] = 0  # No delay for last step
                path_data.append(step_data)
            i += 1
        return path_data
    
    def set_path_data(self, path_data: list):
        """Set path data from a list of dictionaries.
        
        Args:
            path_data: List of step data dictionaries with delay
        """
        # Clear existing items
        for item in self._items[:]:
            if isinstance(item, ClickStepItem):
                self._remove_step(item)
        
        # Add new steps with delays
        for step_data in path_data:
            x = step_data.get("x", 0)
            y = step_data.get("y", 0)
            button = step_data.get("button", "left")
            click_count = step_data.get("click_count", 1)
            delay = step_data.get("delay", 10)
            
            # Add step
            step_count = sum(1 for item in self._items if isinstance(item, ClickStepItem))
            step_index = step_count + 1
            
            step_item = ClickStepItem(step_index, self)
            step_item.set_position(x, y)
            step_item.set_button(button)
            step_item.set_click_count(click_count)
            # Set step name if provided
            if "name" in step_data:
                step_item.set_step_name(step_data["name"])
            step_item.set_theme(self._current_theme)
            
            # Connect signals
            step_item.position_changed.connect(lambda x, y: self._on_path_changed())
            step_item.button_changed.connect(lambda: self._on_path_changed())
            step_item.click_count_changed.connect(lambda: self._on_path_changed())
            step_item.delete_requested.connect(lambda: self._remove_step(step_item))
            
            # Insert step
            insert_index = self.steps_layout.count() - 1
            self.steps_layout.insertWidget(insert_index, step_item)
            self._items.append(step_item)
            
            # Add delay timer after step (if delay > 0)
            # Note: We add delay after each step except when delay is 0
            if delay > 0:
                delay_timer = DelayTimer(self)
                delay_timer.set_delay(delay)
                delay_timer.set_theme(self._current_theme)
                delay_timer.delay_changed.connect(lambda: self._on_path_changed())
                
                # Insert delay after the step
                self.steps_layout.insertWidget(insert_index + 1, delay_timer)
                self._items.append(delay_timer)
        
        # Update step indices
        self._update_step_indices()
        
        # Emit path changed signal
        self._on_path_changed()
    
    def _load_test_data(self):
        """Load test data for UI preview (temporary, remove after backend implementation)."""
        # Test data: 5 steps with 4 delays
        test_steps = [
            {"x": 100, "y": 200, "button": "left", "click_count": 1, "delay": 10},
            {"x": 300, "y": 400, "button": "left", "click_count": 2, "delay": 20},
            {"x": 500, "y": 300, "button": "right", "click_count": 1, "delay": 15},
            {"x": 700, "y": 500, "button": "left", "click_count": 3, "delay": 30},
            {"x": 900, "y": 100, "button": "middle", "click_count": 1, "delay": 0},  # Last step, delay 0
        ]
        
        # Use set_path_data to load test data (this will handle the layout correctly)
        self.set_path_data(test_steps)

