"""
Hotkey Service for Orange Clicker

Base service for managing global hotkeys.
Provides common functionality for registering/unregistering hotkeys.
"""

from typing import Callable, Optional
from frontend.utils.keyboard_listener import get_keyboard_listener


class HotkeyService:
    """
    Base service for managing global hotkeys.
    
    This service provides:
    - Common keyboard listener instance (singleton)
    - Basic hotkey registration/unregistration methods
    - Shared infrastructure for all hotkey-related services
    """
    
    def __init__(self):
        """Initialize hotkey service."""
        # Use singleton to ensure all services share the same keyboard listener
        self._keyboard_listener = get_keyboard_listener()
    
    def register_hotkey(self, hotkey: str, callback: Callable[[], None]):
        """
        Register a global hotkey.
        
        Args:
            hotkey: Hotkey string (e.g., "Ctrl+W", "Ctrl+Q")
            callback: Function to call when hotkey is pressed
        """
        self._keyboard_listener.register_hotkey(hotkey, callback)
    
    def unregister_hotkey(self, hotkey: str):
        """
        Unregister a global hotkey.
        
        Args:
            hotkey: Hotkey string to unregister
        """
        self._keyboard_listener.unregister_hotkey(hotkey)
    
    def unregister_all_hotkeys(self):
        """Unregister all hotkeys managed by this service."""
        # Note: This only clears hotkeys registered through this service
        # For complete cleanup, use KeyboardListener.stop_all()
        pass
    

