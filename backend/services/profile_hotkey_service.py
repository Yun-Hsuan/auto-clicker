"""
Profile Hotkey Service

Manages hotkeys for individual profiles (Cursor Position clicking and Click Path execution).
Inherits from HotkeyService for shared keyboard listener.
Handles registration, unregistration, and click triggering for each profile.
"""

import logging
from typing import Dict, Optional
from backend.services.hotkey_service import HotkeyService
from backend.services.cursor_clicker_service import CursorClickerService
from backend.services.click_path_executor_service import ClickPathExecutorService

logger = logging.getLogger(__name__)


class ProfileHotkeyService(HotkeyService):
    """
    Service for managing profile-specific hotkeys for Cursor Position clicking and Click Path execution.
    
    This service handles:
    - Registering/unregistering hotkeys for each profile
    - Triggering cursor clicking based on profile settings
    - Managing active profile hotkeys
    - Executing click paths when profile hotkeys are pressed
    """
    
    def __init__(self, cursor_clicker_service: CursorClickerService, click_path_executor_service: ClickPathExecutorService):
        """
        Initialize profile hotkey service.
        
        Args:
            cursor_clicker_service: CursorClickerService instance for performing cursor position clicks
            click_path_executor_service: ClickPathExecutorService instance for executing click paths
        """
        super().__init__()
        self._cursor_clicker_service = cursor_clicker_service
        self._click_path_executor_service = click_path_executor_service
        
        # Track registered profile hotkeys
        # Format: {profile_id: {"start_hotkey": str, "end_hotkey": str, "profile": dict}}
        self._active_profile_hotkeys: Dict[str, dict] = {}
        
        # Track which profile is currently clicking (for UI updates)
        self._clicking_profile_id: Optional[str] = None
    
    def register_profile_hotkeys(self, profile: dict):
        """
        Register hotkeys for a profile.
        
        Args:
            profile: Profile dictionary containing:
                - id: Profile ID
                - start_hotkey: Start hotkey string (e.g., "Ctrl+W")
                - end_hotkey: End hotkey string (e.g., "Ctrl+Q")
                - is_saved: Whether profile is saved
                - is_active: Whether profile is active
                - cursor_interval: Click interval in milliseconds
                - cursor_button: Mouse button ("left", "right", "middle")
                - cursor_count: Number of clicks per interval (0 = infinite total)
        """
        profile_id = profile.get("id")
        profile_name = profile.get("name", "Unknown")
        
        logger.info(f"🔑 [Profile Hotkey] Attempting to register hotkeys for profile: {profile_name} (ID: {profile_id})")
        logger.debug(f"🔑 [Profile Hotkey] Profile data: is_saved={profile.get('is_saved', False)}, is_active={profile.get('is_active', False)}")
        logger.debug(f"🔑 [Profile Hotkey] Start hotkey: {profile.get('start_hotkey', '#')}, End hotkey: {profile.get('end_hotkey', '#')}")
        logger.debug(f"🔑 [Profile Hotkey] Click path: type={type(profile.get('click_path'))}, length={len(profile.get('click_path', []))}")
        if profile.get("click_path"):
            logger.debug(f"🔑 [Profile Hotkey] Click path content (first 3 items): {profile.get('click_path', [])[:3]}")
        
        if not profile_id:
            logger.warning(f"🔑 [Profile Hotkey] ❌ Cannot register hotkeys: profile missing ID")
            return
        
        # Unregister existing hotkeys for this profile first
        self.unregister_profile_hotkeys(profile_id)
        
        # Only register if profile is saved and active
        if not profile.get("is_saved", False) or not profile.get("is_active", False):
            logger.info(f"🔑 [Profile Hotkey] ⏭️  Profile {profile_name} not saved or not active, skipping hotkey registration")
            logger.debug(f"🔑 [Profile Hotkey]   - is_saved: {profile.get('is_saved', False)}")
            logger.debug(f"🔑 [Profile Hotkey]   - is_active: {profile.get('is_active', False)}")
            return
        
        start_hotkey = profile.get("start_hotkey", "#")
        end_hotkey = profile.get("end_hotkey", "#")
        
        # Skip if hotkeys are not set
        if not start_hotkey or start_hotkey == "#":
            logger.warning(f"🔑 [Profile Hotkey] ❌ Profile {profile_name} has no start hotkey, skipping registration")
            return
        
        # Store hotkey info with profile reference
        # NOTE: We store the profile reference directly. When the toggle switch is activated,
        # the profile data is already up-to-date (including click_path), so we can use it directly.
        self._active_profile_hotkeys[profile_id] = {
            "start_hotkey": start_hotkey,
            "end_hotkey": end_hotkey,
            "profile": profile
        }
        
        # Log for debugging
        logger.info(f"🔑 [Profile Hotkey] ✅ Stored profile data: click_path length={len(profile.get('click_path', []))}")
        if profile.get("click_path"):
            logger.debug(f"🔑 [Profile Hotkey]   - Click path first item: {profile.get('click_path', [])[0] if len(profile.get('click_path', [])) > 0 else 'N/A'}")
        
        # Register start hotkey
        def on_start_hotkey():
            """Handle profile start hotkey press."""
            logger.info(f"🎯 [Profile Hotkey] ⚡⚡⚡ START HOTKEY PRESSED ⚡⚡⚡")
            logger.info(f"🎯 [Profile Hotkey]   - Profile ID: {profile_id}")
            logger.info(f"🎯 [Profile Hotkey]   - Hotkey: {start_hotkey}")
            
            # STEP 1: Check if profile exists in active hotkeys
            hotkey_info = self._active_profile_hotkeys.get(profile_id)
            if not hotkey_info:
                logger.error(f"🎯 [Profile Hotkey] ❌ STEP 1 FAILED: Profile {profile_id} not found in active hotkeys!")
                logger.error(f"🎯 [Profile Hotkey]   - Available profile IDs: {list(self._active_profile_hotkeys.keys())}")
                return
            
            logger.info(f"🎯 [Profile Hotkey] ✅ STEP 1 PASSED: Profile found in active hotkeys")
            
            # STEP 2: Get stored profile
            stored_profile = hotkey_info.get("profile")
            if not stored_profile:
                logger.error(f"🎯 [Profile Hotkey] ❌ STEP 2 FAILED: No profile data in hotkey_info!")
                logger.error(f"🎯 [Profile Hotkey]   - hotkey_info keys: {list(hotkey_info.keys())}")
                return
            
            logger.info(f"🎯 [Profile Hotkey] ✅ STEP 2 PASSED: Profile data retrieved")
            logger.info(f"🎯 [Profile Hotkey]   - Profile name: {stored_profile.get('name', 'Unknown')}")
            logger.info(f"🎯 [Profile Hotkey]   - is_active: {stored_profile.get('is_active', False)}")
            logger.info(f"🎯 [Profile Hotkey]   - is_saved: {stored_profile.get('is_saved', False)}")
            
            # STEP 3: Check if profile is active and saved
            if not stored_profile.get("is_active", False) or not stored_profile.get("is_saved", False):
                logger.warning(f"🎯 [Profile Hotkey] ⏭️  STEP 3 FAILED: Profile is not active or not saved")
                logger.warning(f"🎯 [Profile Hotkey]   - is_active: {stored_profile.get('is_active', False)}")
                logger.warning(f"🎯 [Profile Hotkey]   - is_saved: {stored_profile.get('is_saved', False)}")
                return
            
            logger.info(f"🎯 [Profile Hotkey] ✅ STEP 3 PASSED: Profile is active and saved")
            
            # STEP 4: Get click_path data
            click_path = stored_profile.get("click_path", [])
            logger.info(f"🎯 [Profile Hotkey] 📊 STEP 4: Checking click_path data")
            logger.info(f"🎯 [Profile Hotkey]   - click_path type: {type(click_path)}")
            logger.info(f"🎯 [Profile Hotkey]   - click_path is None: {click_path is None}")
            logger.info(f"🎯 [Profile Hotkey]   - click_path length: {len(click_path) if click_path else 0}")
            logger.info(f"🎯 [Profile Hotkey]   - click_path is truthy: {bool(click_path)}")
            logger.info(f"🎯 [Profile Hotkey]   - click_path and len > 0: {click_path and len(click_path) > 0}")
            
            if click_path:
                logger.info(f"🎯 [Profile Hotkey]   - Click path content (first 3 items): {click_path[:3]}")
                # Validate click_path structure
                if isinstance(click_path, list) and len(click_path) > 0:
                    first_item = click_path[0]
                    logger.info(f"🎯 [Profile Hotkey]   - First item type: {type(first_item)}")
                    if isinstance(first_item, dict):
                        logger.info(f"🎯 [Profile Hotkey]   - First item keys: {list(first_item.keys())}")
                        logger.info(f"🎯 [Profile Hotkey]   - First item content: {first_item}")
                    else:
                        logger.error(f"🎯 [Profile Hotkey]   - ❌ First item is not a dict: {first_item}")
            else:
                logger.info(f"🎯 [Profile Hotkey]   - click_path is empty or None")
            
            if click_path and len(click_path) > 0:
                # Click Path mode: Execute recorded click path
                logger.info(f"🎯 [Profile Hotkey] 🛤️  CLICK PATH MODE - Profile '{stored_profile.get('name', profile_id)}' ({len(click_path)} steps)")
                logger.debug(f"🎯 [Profile Hotkey]   - Calling _click_path_executor_service.start_execution()")
                try:
                    self._click_path_executor_service.start_execution(click_path)
                    logger.info(f"🎯 [Profile Hotkey] ✅ Click Path execution started successfully")
                except Exception as e:
                    logger.error(f"🎯 [Profile Hotkey] ❌ Error starting Click Path execution: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                # Cursor Position mode: Continuous clicking at current position
                interval = stored_profile.get("cursor_interval", 100)
                button = stored_profile.get("cursor_button", "left")
                click_count = stored_profile.get("cursor_count", 0)
                
                logger.info(f"🎯 [Profile Hotkey] 🖱️  CURSOR POSITION MODE - Profile '{stored_profile.get('name', profile_id)}'")
                logger.debug(f"🎯 [Profile Hotkey]   - interval: {interval}ms")
                logger.debug(f"🎯 [Profile Hotkey]   - button: {button}")
                logger.debug(f"🎯 [Profile Hotkey]   - click_count: {click_count}")
                if not click_path or len(click_path) == 0:
                    logger.debug(f"🎯 [Profile Hotkey]   - Click path is empty or None, using Cursor Position mode")
                
                try:
                    self._cursor_clicker_service.start_clicking(
                        interval_ms=interval,
                        button=button,
                        click_count=click_count
                    )
                    logger.info(f"🎯 [Profile Hotkey] ✅ Cursor Position clicking started successfully")
                except Exception as e:
                    logger.error(f"🎯 [Profile Hotkey] ❌ Error starting Cursor Position clicking: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # Track which profile is clicking
            self._clicking_profile_id = profile_id
            logger.debug(f"🎯 [Profile Hotkey]   - Set _clicking_profile_id to: {profile_id}")
            
            # Update ProfileCard visual state to show clicking
            if "card" in stored_profile:
                stored_profile["card"].set_clicking(True)
                logger.debug(f"🎯 [Profile Hotkey]   - Updated ProfileCard visual state to clicking=True")
            else:
                logger.warning(f"🎯 [Profile Hotkey] ⚠️  No 'card' reference in stored profile")
        
        logger.info(f"🔑 [Profile Hotkey] 📝 Registering start hotkey '{start_hotkey}' with KeyboardListener")
        try:
            self.register_hotkey(start_hotkey, on_start_hotkey)
            logger.info(f"🔑 [Profile Hotkey] ✅ Successfully registered start hotkey '{start_hotkey}' for profile {profile_name} (ID: {profile_id})")
        except Exception as e:
            logger.error(f"🔑 [Profile Hotkey] ❌ Failed to register start hotkey '{start_hotkey}': {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Register end hotkey (if set)
        if end_hotkey and end_hotkey != "#":
            def on_end_hotkey():
                """Handle profile end hotkey press."""
                # Stop both cursor clicking and click path execution
                self._cursor_clicker_service.stop_clicking()
                self._click_path_executor_service.stop_execution()
                logger.info(f"Profile {profile.get('name', profile_id)} end hotkey pressed - stopped clicking")
                
                # Clear clicking profile tracking
                self._clicking_profile_id = None
                
                # Update ProfileCard visual state to stop showing clicking
                stored_profile = self._active_profile_hotkeys.get(profile_id, {}).get("profile")
                if stored_profile and "card" in stored_profile:
                    stored_profile["card"].set_clicking(False)
            
            self.register_hotkey(end_hotkey, on_end_hotkey)
            logger.info(f"Registered end hotkey '{end_hotkey}' for profile {profile_id}")
    
    def unregister_profile_hotkeys(self, profile_id: str):
        """
        Unregister hotkeys for a profile.
        
        Args:
            profile_id: Profile ID
        """
        if profile_id not in self._active_profile_hotkeys:
            return
        
        hotkey_info = self._active_profile_hotkeys[profile_id]
        start_hotkey = hotkey_info.get("start_hotkey")
        end_hotkey = hotkey_info.get("end_hotkey")
        
        # Unregister hotkeys
        if start_hotkey and start_hotkey != "#":
            self.unregister_hotkey(start_hotkey)
            logger.debug(f"Unregistered start hotkey '{start_hotkey}' for profile {profile_id}")
        
        if end_hotkey and end_hotkey != "#":
            self.unregister_hotkey(end_hotkey)
            logger.debug(f"Unregistered end hotkey '{end_hotkey}' for profile {profile_id}")
        
        # Remove from tracking
        del self._active_profile_hotkeys[profile_id]
        
        # Stop clicking if this profile was active
        self._cursor_clicker_service.stop_clicking()
        self._click_path_executor_service.stop_execution()
        
        # Clear clicking profile tracking and update UI
        if self._clicking_profile_id == profile_id:
            self._clicking_profile_id = None
            # Update ProfileCard visual state to stop showing clicking
            hotkey_info = self._active_profile_hotkeys.get(profile_id, {})
            stored_profile = hotkey_info.get("profile")
            if stored_profile and "card" in stored_profile:
                stored_profile["card"].set_clicking(False)
        
        logger.info(f"Unregistered all hotkeys for profile {profile_id}")
    
    def unregister_all_hotkeys(self):
        """Unregister all profile hotkeys."""
        # Clear clicking state for all profiles
        if self._clicking_profile_id:
            profile_id = self._clicking_profile_id
            hotkey_info = self._active_profile_hotkeys.get(profile_id, {})
            stored_profile = hotkey_info.get("profile")
            if stored_profile and "card" in stored_profile:
                stored_profile["card"].set_clicking(False)
            self._clicking_profile_id = None
        
        profile_ids = list(self._active_profile_hotkeys.keys())
        for profile_id in profile_ids:
            self.unregister_profile_hotkeys(profile_id)
        logger.info("Unregistered all profile hotkeys")
    
    def check_clicking_status(self):
        """
        Check if clicking has stopped and update UI accordingly.
        This should be called periodically to handle cases where clicking stops
        due to count limit or other reasons.
        """
        if self._clicking_profile_id:
            # Check both cursor clicking and click path execution
            cursor_clicking = self._cursor_clicker_service.is_clicking()
            path_executing = self._click_path_executor_service.is_executing()
            
            if not cursor_clicking and not path_executing:
                # Both have stopped, update UI
                profile_id = self._clicking_profile_id
                hotkey_info = self._active_profile_hotkeys.get(profile_id, {})
                stored_profile = hotkey_info.get("profile")
                if stored_profile and "card" in stored_profile:
                    stored_profile["card"].set_clicking(False)
                self._clicking_profile_id = None
    
    def update_profile(self, profile: dict):
        """
        Update hotkeys for a profile (re-register if needed).
        
        Args:
            profile: Updated profile dictionary
        """
        profile_id = profile.get("id")
        if not profile_id:
            return
        
        # Re-register hotkeys with updated profile data
        self.register_profile_hotkeys(profile)
    
    def is_profile_registered(self, profile_id: str) -> bool:
        """
        Check if a profile's hotkeys are registered.
        
        Args:
            profile_id: Profile ID
        
        Returns:
            bool: True if registered, False otherwise
        """
        return profile_id in self._active_profile_hotkeys

