"""
Global Keyboard Event Listener
Handles global keyboard hotkey events using Win32 API.

IMPORTANT: This class should be used as a singleton to avoid conflicts
when multiple services register hotkeys.

Uses Win32 RegisterHotKey API for maximum compatibility and performance.
"""

import platform
import ctypes
from ctypes import wintypes
import threading
import logging
from queue import Queue, Empty
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Global singleton instance
_global_keyboard_listener_instance = None


def get_keyboard_listener() -> 'KeyboardListener':
    """
    Get the global singleton KeyboardListener instance.
    
    Returns:
        KeyboardListener: The global singleton instance
    """
    global _global_keyboard_listener_instance
    if _global_keyboard_listener_instance is None:
        _global_keyboard_listener_instance = KeyboardListener()
    return _global_keyboard_listener_instance


# Windows API constants for RegisterHotKey
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

# Virtual key codes
VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_F4 = 0x73
VK_F5 = 0x74
VK_F6 = 0x75
VK_F7 = 0x76
VK_F8 = 0x77
VK_F9 = 0x78
VK_F10 = 0x79
VK_F11 = 0x7A
VK_F12 = 0x7B

# Virtual key code map
VK_CODE_MAP = {
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    'f1': VK_F1, 'f2': VK_F2, 'f3': VK_F3, 'f4': VK_F4,
    'f5': VK_F5, 'f6': VK_F6, 'f7': VK_F7, 'f8': VK_F8,
    'f9': VK_F9, 'f10': VK_F10, 'f11': VK_F11, 'f12': VK_F12,
}


def ui_to_win32_hotkey(ui_hotkey: str) -> tuple[int, int]:
    """
    Convert UI hotkey format to Win32 RegisterHotKey format.
    
    Args:
        ui_hotkey: Hotkey string in UI format (e.g., "Ctrl+W", "F1", "Ctrl+Shift+A")
    
    Returns:
        tuple: (modifiers, vk_code) for RegisterHotKey
        Returns (None, None) if conversion fails
    """
    if not ui_hotkey or ui_hotkey == "#":
        return None, None
    
    parts = ui_hotkey.split("+")
    modifiers = 0
    vk_code = None
    
    for part in parts:
        part = part.strip().lower()
        if not part:
            continue
        
        # Modifier keys
        if part == "ctrl":
            modifiers |= MOD_CONTROL
        elif part == "alt":
            modifiers |= MOD_ALT
        elif part == "shift":
            modifiers |= MOD_SHIFT
        elif part == "meta" or part == "win":
            modifiers |= MOD_WIN
        # Regular keys
        else:
            # Function keys
            if part.startswith("f") and len(part) > 1:
                try:
                    f_num = int(part[1:])
                    if 1 <= f_num <= 12:
                        vk_code = VK_F1 + (f_num - 1)
                except ValueError:
                    pass
            
            # Regular keys (letters, numbers)
            if vk_code is None and part in VK_CODE_MAP:
                vk_code = VK_CODE_MAP[part]
    
    if vk_code is None:
        return None, None
    
    return modifiers, vk_code


class KeyboardListener:
    """Global keyboard event listener for hotkeys using Win32 RegisterHotKey API."""
    
    def __init__(self):
        """Initialize keyboard listener."""
        # Hotkeys stored by UI string, e.g. "Ctrl+W"
        self._hotkeys: Dict[str, dict] = {}
        # Hotkeys stored by Win32 ID (for fast WM_HOTKEY lookup on worker thread)
        self._hotkeys_by_id: Dict[int, dict] = {}
        
        # Worker thread state
        self._is_listening = False
        self._message_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._command_queue: "Queue[Dict[str, Any]]" = Queue()
        self._next_hotkey_id = 1  # Unique ID for each hotkey (required by RegisterHotKey)
        
        # Load Windows DLLs (process-wide, safe to use from worker thread)
        if platform.system() == "Windows":
            self._user32 = ctypes.windll.user32
            self._kernel32 = ctypes.windll.kernel32
            
            # Define GetLastError function signature
            self._kernel32.GetLastError.argtypes = []
            self._kernel32.GetLastError.restype = wintypes.DWORD
            
            # Define RegisterHotKey function signature
            self._user32.RegisterHotKey.argtypes = [
                wintypes.HWND,    # hWnd
                ctypes.c_int,     # id
                ctypes.c_uint,    # fsModifiers
                ctypes.c_uint     # vk
            ]
            self._user32.RegisterHotKey.restype = wintypes.BOOL
            
            # Define UnregisterHotKey function signature
            self._user32.UnregisterHotKey.argtypes = [
                wintypes.HWND,    # hWnd
                ctypes.c_int      # id
            ]
            self._user32.UnregisterHotKey.restype = wintypes.BOOL
            
            # Define GetMessage function signature
            self._user32.GetMessageW.argtypes = [
                ctypes.POINTER(wintypes.MSG),  # lpMsg
                wintypes.HWND,                 # hWnd
                wintypes.UINT,                 # wMsgFilterMin
                wintypes.UINT                  # wMsgFilterMax
            ]
            self._user32.GetMessageW.restype = wintypes.BOOL
            
            # Define TranslateMessage function signature
            self._user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
            self._user32.TranslateMessage.restype = wintypes.BOOL
            
            # Define DispatchMessageW function signature
            # LRESULT is typically ctypes.c_long on 64-bit, ctypes.c_int on 32-bit
            # Using ctypes.c_long for compatibility
            self._user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
            self._user32.DispatchMessageW.restype = ctypes.c_long
            
            # Define PeekMessageW function signature
            self._user32.PeekMessageW.argtypes = [
                ctypes.POINTER(wintypes.MSG),  # lpMsg
                wintypes.HWND,                 # hWnd
                wintypes.UINT,                 # wMsgFilterMin
                wintypes.UINT,                 # wMsgFilterMax
                wintypes.UINT                  # wRemoveMsg
            ]
            self._user32.PeekMessageW.restype = wintypes.BOOL
            
            # Windows message constants
            self.WM_HOTKEY = 0x0312
            self.PM_REMOVE = 0x0001
        else:
            self._user32 = None
            self._kernel32 = None
    
    def register_hotkey(self, hotkey: str, callback: Callable[[], None]):
        """
        Register a global hotkey using Win32 RegisterHotKey API.
        
        Args:
            hotkey: Hotkey string in UI format (e.g., "Ctrl+W", "F1")
            callback: Callback function called when hotkey is pressed
        """
        if platform.system() != "Windows":
            logger.error("⌨️  [KeyboardListener] ❌ Only Windows is supported")
            return
        
        logger.info(f"⌨️  [KeyboardListener] 📝 Registering hotkey: {hotkey}")
        logger.debug(f"⌨️  [KeyboardListener]   - Callback: {callback}")
        logger.debug(f"⌨️  [KeyboardListener]   - Current registered hotkeys: {list(self._hotkeys.keys())}")
        
        # Convert UI format to Win32 format
        modifiers, vk_code = ui_to_win32_hotkey(hotkey)
        if modifiers is None or vk_code is None:
            logger.error(f"⌨️  [KeyboardListener] ❌ Could not convert hotkey: {hotkey}")
            return
        
        logger.debug(f"⌨️  [KeyboardListener]   - Converted: modifiers=0x{modifiers:X}, vk_code=0x{vk_code:X}")
        
        # Generate unique ID for this hotkey
        hotkey_id = self._next_hotkey_id
        self._next_hotkey_id += 1
        
        # Prepare command for worker thread
        done_event = threading.Event()
        command: Dict[str, Any] = {
            "type": "register",
            "hotkey": hotkey,
            "hotkey_id": hotkey_id,
            "modifiers": modifiers,
            "vk_code": vk_code,
            "callback": callback,
            "result": None,
            "error_code": None,
            "done_event": done_event,
        }
        
        # Enqueue command and ensure worker is running
        self._command_queue.put(command)
        if not self._is_listening:
            self._start_message_loop()
        
        # Wait for worker to complete registration (short timeout to avoid hangs)
        done_event.wait(timeout=1.0)
        
        result = command["result"]
        error_code = command["error_code"]
        if not result:
            # Registration failed (worker thread already logged GetLastError if possible)
            if error_code is not None:
                logger.error(f"⌨️  [KeyboardListener] ❌ Failed to register hotkey '{hotkey}': Error code {error_code}")
                if error_code == 1409:  # ERROR_HOTKEY_ALREADY_REGISTERED
                    logger.error("⌨️  [KeyboardListener]   - Hotkey already registered by another application")
            else:
                logger.error(f"⌨️  [KeyboardListener] ❌ Failed to register hotkey '{hotkey}': unknown error")
            return
        
        # Store hotkey info (only after worker thread succeeded)
        self._hotkeys[hotkey] = {
            "hotkey_id": hotkey_id,
            "modifiers": modifiers,
            "vk_code": vk_code,
            "callback": callback,
        }
        
        logger.info(f"⌨️  [KeyboardListener] ✅ Successfully registered hotkey '{hotkey}' (ID: {hotkey_id})")
        print(f"[KeyboardListener] ✅ Registered hotkey: '{hotkey}' (ID: {hotkey_id})")
    
    def unregister_hotkey(self, hotkey: str):
        """
        Unregister a global hotkey.
        
        Args:
            hotkey: Hotkey string to unregister (must match the original registration format)
        """
        if platform.system() != "Windows" or not self._user32:
            return
        
        # Try exact match first
        if hotkey in self._hotkeys:
            hotkey_info = self._hotkeys[hotkey]
            hotkey_id = hotkey_info['hotkey_id']
            
            done_event = threading.Event()
            command: Dict[str, Any] = {
                "type": "unregister",
                "hotkey": hotkey,
                "hotkey_id": hotkey_id,
                "result": None,
                "error_code": None,
                "done_event": done_event,
            }
            self._command_queue.put(command)
            done_event.wait(timeout=1.0)
            
            result = command["result"]
            error_code = command["error_code"]
            if result:
                logger.info(f"⌨️  [KeyboardListener] ✅ Unregistered hotkey: {hotkey} (ID: {hotkey_id})")
                print(f"[KeyboardListener] Unregistered hotkey: {hotkey}")
            elif error_code is not None:
                logger.warning(f"⌨️  [KeyboardListener] ⚠️  Error unregistering hotkey '{hotkey}': Error code {error_code}")
            else:
                logger.warning(f"⌨️  [KeyboardListener] ⚠️  Error unregistering hotkey '{hotkey}'")
            
            del self._hotkeys[hotkey]
        else:
            # Try case-insensitive match
            hotkey_lower = hotkey.lower()
            found_key = None
            for key in list(self._hotkeys.keys()):
                if key.lower() == hotkey_lower:
                    found_key = key
                    break
            
            if found_key:
                hotkey_info = self._hotkeys[found_key]
                hotkey_id = hotkey_info['hotkey_id']
                
                done_event = threading.Event()
                command = {
                    "type": "unregister",
                    "hotkey": found_key,
                    "hotkey_id": hotkey_id,
                    "result": None,
                    "error_code": None,
                    "done_event": done_event,
                }
                self._command_queue.put(command)
                done_event.wait(timeout=1.0)
                
                result = command["result"]
                error_code = command["error_code"]
                if result:
                    logger.info(f"⌨️  [KeyboardListener] ✅ Unregistered hotkey: {found_key} (matched {hotkey})")
                    print(f"[KeyboardListener] Unregistered hotkey: {found_key} (matched {hotkey})")
                elif error_code is not None:
                    logger.warning(
                        f"⌨️  [KeyboardListener] ⚠️  Error unregistering hotkey '{found_key}': Error code {error_code}"
                    )
                else:
                    logger.warning(f"⌨️  [KeyboardListener] ⚠️  Error unregistering hotkey '{found_key}'")
                
                del self._hotkeys[found_key]
        
        # Update listening state
        if not self._hotkeys:
            self._stop_message_loop()
    
    def _start_message_loop(self):
        """Start message loop thread to process hotkey messages."""
        if self._is_listening:
            return
        
        self._is_listening = True
        self._stop_event.clear()
        
        # Start message loop thread
        self._message_thread = threading.Thread(target=self._message_loop, daemon=True)
        self._message_thread.start()
        logger.info("⌨️  [KeyboardListener] ✅ Started message loop thread")
    
    def _stop_message_loop(self):
        """Stop message loop thread."""
        if not self._is_listening:
            return
        
        self._is_listening = False
        self._stop_event.set()
        
        # Wait for thread to finish
        if self._message_thread and self._message_thread.is_alive():
            self._message_thread.join(timeout=1.0)
        
        logger.info("⌨️  [KeyboardListener] ✅ Stopped message loop thread")
    
    def _message_loop(self):
        """Message loop for processing hotkey messages (required for RegisterHotKey)."""
        try:
            msg = wintypes.MSG()
            while self._is_listening and not self._stop_event.is_set():
                # First, process any pending register/unregister commands
                self._process_pending_commands()
                
                # PeekMessage (non-blocking) to check for messages
                bRet = self._user32.PeekMessageW(
                    ctypes.byref(msg),
                    None,
                    0,
                    0,
                    self.PM_REMOVE
                )
                
                if bRet:
                    if msg.message == self.WM_HOTKEY:
                        # Hotkey was pressed
                        hotkey_id = int(msg.wParam)
                        hotkey_info = self._hotkeys_by_id.get(hotkey_id)
                        if hotkey_info:
                            hotkey = hotkey_info.get("ui_hotkey", f"ID:{hotkey_id}")
                            callback = hotkey_info.get("callback")
                            logger.info(f"⌨️  [KeyboardListener] ⚡⚡⚡ HOTKEY TRIGGERED ⚡⚡⚡: {hotkey}")
                            print(f"[KeyboardListener] ⚡⚡⚡ HOTKEY TRIGGERED ⚡⚡⚡: {hotkey}")
                            if callback:
                                try:
                                    callback()
                                    logger.info(f"⌨️  [KeyboardListener] ✅ Callback executed successfully for: {hotkey}")
                                except Exception as e:
                                    logger.error(f"⌨️  [KeyboardListener] ❌ Error in hotkey callback for {hotkey}: {e}")
                                    import traceback
                                    logger.error(traceback.format_exc())
                    else:
                        # Translate and dispatch other messages
                        self._user32.TranslateMessage(ctypes.byref(msg))
                        self._user32.DispatchMessageW(ctypes.byref(msg))
                else:
                    # No message, sleep briefly to avoid high CPU usage
                    import time
                    time.sleep(0.01)  # 10ms
        except Exception as e:
            logger.error(f"⌨️  [KeyboardListener] ❌ Error in message loop: {e}", exc_info=True)
        finally:
            self._is_listening = False
    
    def _process_pending_commands(self):
        """
        Process pending register/unregister commands from the command queue.
        
        This method MUST be called from the worker thread that owns the
        message loop and the Win32 hotkey registrations.
        """
        if not self._user32:
            # Win32 APIs not available, drain queue and signal failure
            try:
                while True:
                    cmd = self._command_queue.get_nowait()
                    cmd["result"] = False
                    cmd["error_code"] = None
                    done_event = cmd.get("done_event")
                    if done_event:
                        done_event.set()
            except Empty:
                return
        
        try:
            while True:
                try:
                    cmd: Dict[str, Any] = self._command_queue.get_nowait()
                except Empty:
                    break
                
                cmd_type = cmd.get("type")
                done_event = cmd.get("done_event")
                
                if cmd_type == "register":
                    hotkey_id = cmd.get("hotkey_id")
                    modifiers = cmd.get("modifiers")
                    vk_code = cmd.get("vk_code")
                    ui_hotkey = cmd.get("hotkey")
                    callback = cmd.get("callback")
                    
                    try:
                        result = self._user32.RegisterHotKey(None, hotkey_id, modifiers, vk_code)
                        cmd["result"] = bool(result)
                        if result:
                            # Store mapping for WM_HOTKEY lookup
                            self._hotkeys_by_id[hotkey_id] = {
                                "ui_hotkey": ui_hotkey,
                                "callback": callback,
                            }
                        else:
                            if self._kernel32:
                                cmd["error_code"] = self._kernel32.GetLastError()
                    except Exception:
                        cmd["result"] = False
                        if self._kernel32:
                            try:
                                cmd["error_code"] = self._kernel32.GetLastError()
                            except Exception:
                                cmd["error_code"] = None
                    finally:
                        if done_event:
                            done_event.set()
                
                elif cmd_type == "unregister":
                    hotkey_id = cmd.get("hotkey_id")
                    try:
                        result = self._user32.UnregisterHotKey(None, hotkey_id)
                        cmd["result"] = bool(result)
                        if result and hotkey_id in self._hotkeys_by_id:
                            del self._hotkeys_by_id[hotkey_id]
                        if not result and self._kernel32:
                            cmd["error_code"] = self._kernel32.GetLastError()
                    except Exception:
                        cmd["result"] = False
                        if self._kernel32:
                            try:
                                cmd["error_code"] = self._kernel32.GetLastError()
                            except Exception:
                                cmd["error_code"] = None
                    finally:
                        if done_event:
                            done_event.set()
                
                else:
                    # Unknown command type – mark as done to avoid deadlocks
                    cmd["result"] = False
                    if done_event:
                        done_event.set()
        except Exception as e:
            logger.error(f"⌨️  [KeyboardListener] ❌ Error processing hotkey commands: {e}", exc_info=True)
    
    def stop_all(self):
        """Stop all listeners and clear hotkeys."""
        # Unregister all hotkeys
        for hotkey in list(self._hotkeys.keys()):
            self.unregister_hotkey(hotkey)
        
        self._hotkeys.clear()
        self._is_listening = False
    
    def is_listening(self) -> bool:
        """Check if listener is active.
        
        Returns:
            bool: True if listening, False otherwise
        """
        return self._is_listening
