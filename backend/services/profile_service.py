"""
Profile Service for Orange Clicker

Handles serialization and deserialization of Profile data.
Separates business logic from UI components.
"""

from typing import Dict, List, Any
import uuid


class ProfileService:
    """
    Service for managing Profile data serialization and deserialization.
    
    This service handles:
    - Converting Profile data (with UI components) to serializable format
    - Converting serialized Profile data back to application format
    - Data validation and transformation
    """
    
    @staticmethod
    def serialize_profiles(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Serialize Profile data (excluding UI component references).
        
        Args:
            profiles: List of profile dictionaries from main_window.profiles
                     Each profile may contain a "card" (ProfileCard) reference
        
        Returns:
            List of serializable profile dictionaries (without UI components)
        """
        serialized = []
        for profile in profiles:
            # Exclude 'card' component reference, only save data
            click_path = profile.get("click_path", [])
            
            # Ensure click_path is a list (not None or other type)
            if click_path is None:
                click_path = []
            if not isinstance(click_path, list):
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"⚠️  [ProfileService] click_path is not a list when saving: type={type(click_path)}, value={click_path}")
                click_path = []
            
            # Determine profile type: Click Path or Cursor Position
            # If click_path has data, it's Click Path mode (don't save cursor_settings)
            # If click_path is empty, it's Cursor Position mode (save cursor_settings)
            is_click_path_mode = click_path and len(click_path) > 0
            
            profile_data = {
                "id": profile.get("id", str(uuid.uuid4())),  # Generate unique ID if missing
                "name": profile.get("name", ""),
                "start_hotkey": profile.get("start_hotkey", "#"),
                "end_hotkey": profile.get("end_hotkey", "#"),
                "is_active": profile.get("is_active", False),
                "is_saved": profile.get("is_saved", False),
                "click_path": click_path
            }
            
            # Only save cursor_settings if it's Cursor Position mode
            if not is_click_path_mode:
                profile_data["cursor_settings"] = {
                    "interval": profile.get("cursor_interval", 100),
                    "button": profile.get("cursor_button", "left"),
                    "count": profile.get("cursor_count", 0)
                }
            # If Click Path mode, don't include cursor_settings (or set to None)
            # This ensures we can distinguish between the two modes when loading
            
            serialized.append(profile_data)
        return serialized
    
    @staticmethod
    def deserialize_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize a single profile from config format to application format.
        
        Args:
            profile_data: Profile dictionary from config file
        
        Returns:
            Profile dictionary in application format (without "card" reference)
        """
        profile_id = profile_data.get("id", str(uuid.uuid4()))
        name = profile_data.get("name", "Unnamed Profile")
        start_hotkey = profile_data.get("start_hotkey", "#")
        end_hotkey = profile_data.get("end_hotkey", "#")
        is_active = profile_data.get("is_active", False)
        is_saved = profile_data.get("is_saved", False)
        
        # Click path - ensure it's always a list
        click_path = profile_data.get("click_path", [])
        if click_path is None:
            click_path = []
        # Ensure click_path is a list (not a string or other type)
        if not isinstance(click_path, list):
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️  [ProfileService] click_path is not a list: type={type(click_path)}, value={click_path}")
            click_path = []
        
        # Determine profile type: Click Path or Cursor Position
        # If click_path has data, it's Click Path mode (use default cursor settings)
        # If click_path is empty, it's Cursor Position mode (load cursor_settings)
        is_click_path_mode = click_path and len(click_path) > 0
        
        if is_click_path_mode:
            # Click Path mode: Use default cursor settings (not used, but needed for compatibility)
            cursor_interval = 100
            cursor_button = "left"
            cursor_count = 0
        else:
            # Cursor Position mode: Load cursor settings from config
            cursor_settings = profile_data.get("cursor_settings", {})
            cursor_interval = cursor_settings.get("interval", 100)
            cursor_button = cursor_settings.get("button", "left")
            cursor_count = cursor_settings.get("count", 0)
        
        # Return profile in application format (card will be added by UI layer)
        return {
            "id": profile_id,
            "name": name,
            "start_hotkey": start_hotkey,
            "end_hotkey": end_hotkey,
            "is_active": is_active,
            "is_saved": is_saved,
            "cursor_interval": cursor_interval,
            "cursor_button": cursor_button,
            "cursor_count": cursor_count,
            "click_path": click_path
        }
    
    @staticmethod
    def deserialize_profiles(profiles_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deserialize multiple profiles from config format.
        
        Args:
            profiles_data: List of profile dictionaries from config file
        
        Returns:
            List of profile dictionaries in application format (without "card" references)
        """
        return [ProfileService.deserialize_profile(profile_data) for profile_data in profiles_data]


