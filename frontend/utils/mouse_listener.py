"""
Global Mouse Event Listener
Handles global mouse click events for recording click paths.

Uses Windows API SetWindowsHookEx for high-performance mouse event listening.
Much more efficient than pynput for Windows platforms.
"""

import platform
import threading
import ctypes
from ctypes import wintypes, Structure, POINTER, WINFUNCTYPE
from typing import Callable, Optional

# Windows API constants
WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
WM_MBUTTONDOWN = 0x0207
HC_ACTION = 0

# Windows API types
class MSLLHOOKSTRUCT(Structure):
    """Low-level mouse input structure."""
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

# Windows API handle types
HHOOK = ctypes.c_void_p  # Hook handle
HINSTANCE = wintypes.HANDLE  # Module instance handle

# Hook procedure type
# LRESULT is typically ctypes.c_long on 64-bit, ctypes.c_int on 32-bit
# Using ctypes.c_long for compatibility
HOOKPROC = WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)


class MouseListener:
    """Global mouse event listener using Windows API."""
    
    def __init__(self):
        """Initialize mouse listener."""
        self._hook_id = None
        self._on_click_callback: Optional[Callable[[int, int, str], None]] = None
        self._is_listening = False
        self._hook_proc = None
        self._user32 = None
        self._kernel32 = None
    
    def start_listening(self, on_click: Callable[[int, int, str], None]):
        """Start listening for mouse clicks using Windows API.
        
        Args:
            on_click: Callback function(x, y, button) called when mouse is clicked
        """
        # If already listening, stop first to ensure clean state
        if self._is_listening:
            try:
                self.stop_listening()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error stopping previous listener: {e}")
                # Reset state manually
                self._is_listening = False
                self._hook_id = None
        
        # Only works on Windows
        if platform.system() != "Windows":
            raise NotImplementedError("MouseListener currently only supports Windows")
        
        self._on_click_callback = on_click
        self._is_listening = True
        
        # Load Windows DLLs
        # Use windll (stdcall calling convention) for Windows API
        self._user32 = ctypes.windll.user32
        self._kernel32 = ctypes.windll.kernel32
        
        # Define GetLastError function signature
        self._kernel32.GetLastError.argtypes = []
        self._kernel32.GetLastError.restype = wintypes.DWORD
        
        # Define SetWindowsHookExW function signature
        self._user32.SetWindowsHookExW.argtypes = [
            ctypes.c_int,      # idHook
            HOOKPROC,          # lpfn
            HINSTANCE,         # hMod
            wintypes.DWORD     # dwThreadId
        ]
        self._user32.SetWindowsHookExW.restype = HHOOK
        
        # Define CallNextHookEx function signature (use ANSI version for compatibility)
        self._user32.CallNextHookEx.argtypes = [
            HHOOK,             # hhk
            ctypes.c_int,      # nCode
            wintypes.WPARAM,   # wParam
            wintypes.LPARAM    # lParam
        ]
        self._user32.CallNextHookEx.restype = ctypes.c_long
        
        # Define UnhookWindowsHookEx function signature
        # Note: UnhookWindowsHookEx is available in both ANSI and Unicode versions
        # We use the ANSI version (no W suffix) which is the standard
        try:
            # Try to get the function directly
            unhook_func = getattr(self._user32, 'UnhookWindowsHookEx')
            unhook_func.argtypes = [HHOOK]
            unhook_func.restype = wintypes.BOOL
        except AttributeError:
            # If not found, try with W suffix (shouldn't happen, but handle gracefully)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("UnhookWindowsHookEx not found, trying UnhookWindowsHookExW")
            try:
                unhook_func = getattr(self._user32, 'UnhookWindowsHookExW')
                unhook_func.argtypes = [HHOOK]
                unhook_func.restype = wintypes.BOOL
            except AttributeError:
                logger.error("Neither UnhookWindowsHookEx nor UnhookWindowsHookExW found")
        
        # Define GetModuleHandleW function signature
        self._kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        self._kernel32.GetModuleHandleW.restype = HINSTANCE
        
        # Store references in lists to avoid closure issues
        self._callback_ref = [self._on_click_callback]
        self._listening_ref = [self._is_listening]
        self._call_next_hook_ref = [self._user32.CallNextHookEx]
        
        # Define hook procedure
        def low_level_mouse_proc(nCode, wParam, lParam):
            """Low-level mouse hook procedure."""
            try:
                # Check if we're still listening and references are valid
                if (nCode >= HC_ACTION and 
                    hasattr(self, '_listening_ref') and 
                    self._listening_ref and 
                    len(self._listening_ref) > 0 and 
                    self._listening_ref[0]):
                    
                    # Extract mouse data
                    hook_struct = ctypes.cast(lParam, POINTER(MSLLHOOKSTRUCT)).contents
                    x, y = hook_struct.pt.x, hook_struct.pt.y
                    
                    # Determine button
                    button_name = None
                    if wParam == WM_LBUTTONDOWN:
                        button_name = "left"
                    elif wParam == WM_RBUTTONDOWN:
                        button_name = "right"
                    elif wParam == WM_MBUTTONDOWN:
                        button_name = "middle"
                    
                    # Call callback if button detected and callback is still valid
                    if (button_name and 
                        hasattr(self, '_callback_ref') and 
                        self._callback_ref and 
                        len(self._callback_ref) > 0 and 
                        self._callback_ref[0]):
                        try:
                            self._callback_ref[0](x, y, button_name)
                        except Exception as e:
                            # Log but don't crash if callback fails
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error in mouse click callback: {e}")
            except Exception as e:
                # Log but don't crash if there's an error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in mouse hook procedure: {e}")
            
            # Always call next hook, even if we had an error
            try:
                if (hasattr(self, '_call_next_hook_ref') and 
                    self._call_next_hook_ref and 
                    len(self._call_next_hook_ref) > 0 and 
                    self._call_next_hook_ref[0]):
                    return self._call_next_hook_ref[0](None, nCode, wParam, lParam)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calling next hook: {e}")
            
            # Fallback: return 0 if we can't call next hook
            return 0
        
        # Create hook procedure - must keep reference to prevent garbage collection
        self._hook_proc = HOOKPROC(low_level_mouse_proc)
        
        # Get module handle (None means current module)
        hmod = self._kernel32.GetModuleHandleW(None)
        if not hmod:
            # Get last error for debugging
            error_code = self._kernel32.GetLastError()
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"GetModuleHandleW returned NULL. Error code: {error_code}")
            # Continue anyway, as NULL might be acceptable for some hooks
        
        # Install hook
        self._hook_id = self._user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            self._hook_proc,
            hmod,
            0
        )
        
        if not self._hook_id:
            # Get last error for debugging
            error_code = self._kernel32.GetLastError()
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to install mouse hook. Error code: {error_code}")
            raise RuntimeError(f"Failed to install mouse hook. Error code: {error_code}. "
                             f"This may require administrator privileges.")
        
        # For low-level hooks (WH_MOUSE_LL), we need a message loop
        # Run it in a separate thread to avoid blocking
        self._message_thread = threading.Thread(target=self._message_loop, daemon=True)
        self._message_thread.start()
    
    def _message_loop(self):
        """Message loop for processing hook messages (required for WH_MOUSE_LL)."""
        try:
            msg = wintypes.MSG()
            while self._is_listening:
                # PeekMessage (non-blocking) to check for messages
                bRet = self._user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0x0001)  # PM_REMOVE
                if bRet:
                    self._user32.TranslateMessage(ctypes.byref(msg))
                    self._user32.DispatchMessageW(ctypes.byref(msg))
                else:
                    # No message, sleep briefly to avoid high CPU usage
                    import time
                    time.sleep(0.001)  # 1ms
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in mouse hook message loop: {e}")
    
    def stop_listening(self):
        """Stop listening for mouse clicks."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not self._is_listening:
            return
        
        try:
            # First, set listening flag to False to prevent new callbacks
            self._is_listening = False
            
            # Update listening reference (must be done before uninstalling hook)
            try:
                if hasattr(self, '_listening_ref'):
                    self._listening_ref[0] = False
            except Exception as e:
                logger.warning(f"Error updating listening_ref: {e}")
            
            # Uninstall hook (this will stop new hook callbacks)
            if self._hook_id and self._user32:
                try:
                    # Try to get UnhookWindowsHookEx function
                    # Use getattr to safely get the function
                    unhook_func = getattr(self._user32, 'UnhookWindowsHookEx', None)
                    if unhook_func is None:
                        # Fallback to W version if ANSI not available
                        unhook_func = getattr(self._user32, 'UnhookWindowsHookExW', None)
                    
                    if unhook_func:
                        result = unhook_func(self._hook_id)
                        if not result:
                            # Get error code for debugging
                            try:
                                if self._kernel32:
                                    error_code = self._kernel32.GetLastError()
                                    logger.warning(f"UnhookWindowsHookEx returned False. Error code: {error_code}")
                            except Exception as e2:
                                logger.warning(f"Could not get error code: {e2}")
                    else:
                        logger.error("UnhookWindowsHookEx function not found in user32.dll")
                except Exception as e:
                    logger.error(f"Error uninstalling hook: {e}", exc_info=True)
                finally:
                    self._hook_id = None
        except Exception as e:
            logger.error(f"Critical error in stop_listening: {e}", exc_info=True)
            # Ensure state is reset even on error
            self._is_listening = False
            self._hook_id = None
        
        # Wait for message thread to finish (with timeout)
        # This ensures any pending hook callbacks complete before we clear references
        if hasattr(self, '_message_thread'):
            try:
                if self._message_thread.is_alive():
                    self._message_thread.join(timeout=1.0)  # Wait up to 1 second
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error joining message thread: {e}")
        
        # Clear callback reference (but keep hook_proc until thread is done)
        # Don't clear hook_proc immediately as it might still be in use by the hook
        self._on_click_callback = None
        if hasattr(self, '_callback_ref'):
            try:
                if self._callback_ref and len(self._callback_ref) > 0:
                    self._callback_ref[0] = None
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error clearing callback_ref: {e}")
        
        # Clear hook_proc after thread is done to prevent memory leaks
        # But only if we're sure the thread has finished
        if hasattr(self, '_message_thread'):
            try:
                if not self._message_thread.is_alive():
                    # Thread is done, safe to clear hook_proc
                    self._hook_proc = None
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error checking thread status: {e}")
        
        # Clear call_next_hook_ref if thread is done
        if hasattr(self, '_call_next_hook_ref'):
            try:
                if hasattr(self, '_message_thread') and not self._message_thread.is_alive():
                    if self._call_next_hook_ref and len(self._call_next_hook_ref) > 0:
                        self._call_next_hook_ref[0] = None
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error clearing call_next_hook_ref: {e}")
    
    def is_listening(self) -> bool:
        """Check if listener is active.
        
        Returns:
            bool: True if listening, False otherwise
        """
        return self._is_listening

