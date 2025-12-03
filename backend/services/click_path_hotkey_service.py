"""
Click Path Hotkey Service

Manages global hotkeys for Click Path recording (Ctrl+W, Ctrl+Q).
Inherits from HotkeyService for shared keyboard listener.
"""

from typing import Callable, Optional
from backend.services.hotkey_service import HotkeyService


class ClickPathHotkeyService(HotkeyService):
    """
    Service for managing global hotkeys for Click Path recording.
    
    This service handles:
    - Registering/unregistering global hotkeys (Ctrl+W, Ctrl+Q)
    - Business logic for when hotkeys should respond
    - Managing hotkey state for Click Path recording
    """
    
    def __init__(self):
        """Initialize click path hotkey service."""
        super().__init__()
        self._start_recording_callback: Optional[Callable[[], None]] = None
        self._stop_recording_callback: Optional[Callable[[], None]] = None
        
        # State tracking
        self._is_profile_selected = False
        self._is_click_path_tab_active = False
    
    def register_click_path_hotkeys(
        self,
        start_callback: Callable[[], None],
        stop_callback: Callable[[], None]
    ):
        """
        Register global hotkeys for Click Path recording.
        
        Args:
            start_callback: Function to call when Ctrl+W is pressed (start recording)
            stop_callback: Function to call when Ctrl+Q is pressed (stop recording)
        """
        self._start_recording_callback = start_callback
        self._stop_recording_callback = stop_callback
        
        # Register Ctrl+W to start recording
        self.register_hotkey("ctrl+w", self._on_start_recording_hotkey)
        
        # Register Ctrl+Q to stop recording
        self.register_hotkey("ctrl+q", self._on_stop_recording_hotkey)
    
    def unregister_all_hotkeys(self):
        """Unregister all click path hotkeys."""
        self.unregister_hotkey("ctrl+w")
        self.unregister_hotkey("ctrl+q")
        self._start_recording_callback = None
        self._stop_recording_callback = None
    
    def set_profile_selected(self, is_selected: bool):
        """
        Update whether a profile is currently selected.
        
        Args:
            is_selected: True if a profile is selected, False otherwise
        """
        self._is_profile_selected = is_selected
    
    def set_click_path_tab_active(self, is_active: bool):
        """
        Update whether the Click Path tab is currently active.
        
        Args:
            is_active: True if Click Path tab is active, False otherwise
        """
        self._is_click_path_tab_active = is_active
    
    def _on_start_recording_hotkey(self):
        """
        Handle Ctrl+W hotkey to start recording.
        
        Only works when:
        1. A profile is selected (to know which profile to save the recording to)
        2. The Click Path tab is active
        """
        print(f"[ClickPathHotkeyService] Ctrl+W pressed - profile_selected={self._is_profile_selected}, tab_active={self._is_click_path_tab_active}")
        # Business logic: Only start recording if conditions are met
        if not self._is_profile_selected:
            print("[ClickPathHotkeyService] Ignored: No profile selected")
            return
        
        if not self._is_click_path_tab_active:
            print("[ClickPathHotkeyService] Ignored: Click Path tab not active")
            return
        
        # Call the callback if registered
        if self._start_recording_callback:
            print("[ClickPathHotkeyService] Calling start_recording_callback")
            self._start_recording_callback()
        else:
            print("[ClickPathHotkeyService] Warning: start_recording_callback not registered")
    
    def _on_stop_recording_hotkey(self):
        """
        Handle Ctrl+Q hotkey to stop recording.
        
        Works regardless of tab selection (allows stopping from any tab).
        """
        print("[ClickPathHotkeyService] Ctrl+Q pressed - stop recording")
        # Business logic: Always allow stopping (safety feature)
        if self._stop_recording_callback:
            print("[ClickPathHotkeyService] Calling stop_recording_callback")
            self._stop_recording_callback()
        else:
            print("[ClickPathHotkeyService] Warning: stop_recording_callback not registered")

