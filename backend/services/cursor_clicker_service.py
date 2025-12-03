"""
Cursor Position Clicker Service

Handles continuous clicking at the current cursor position.
Uses pywin32 for high-performance mouse clicking on Windows.
Uses SendInput API for better compatibility with game windows.
"""

import threading
import time
import logging
from typing import Optional
import ctypes
from ctypes import wintypes

logger = logging.getLogger(__name__)

# Enable debug mode by default - set to False to disable verbose logging
DEBUG_MODE = True

# Windows API constants for SendInput
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040


def perform_native_click(x: int, y: int, button: str, times: int = 1):
    """
    Perform native mouse click(s) at the specified position.
    
    Uses multiple methods in order of preference for maximum compatibility:
    1. SendInput API (primary method - most efficient, works with Raw Input/DirectInput games)
    2. mouse_event (fallback for regular applications)
    3. pynput (last resort)
    
    SendInput is preferred because:
    - Directly injects into input stream (most efficient)
    - Works with games using Raw Input/DirectInput
    - No need to get window handles or calculate relative coordinates
    - Recommended by Microsoft for input simulation
    
    Args:
        x: X coordinate (not used for cursor position mode, but kept for API compatibility)
        y: Y coordinate (not used for cursor position mode, but kept for API compatibility)
        button: Mouse button ("left", "right", or "middle")
        times: Number of times to click (default: 1)
    """
    # Get actual cursor position for logging
    try:
        import win32api
        actual_x, actual_y = win32api.GetCursorPos()
    except:
        actual_x, actual_y = x, y
    
    # Method 1: Try SendInput (primary method - most efficient)
    try:
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)
            ]
        
        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [("mi", MOUSEINPUT)]
            _anonymous_ = ("_input",)
            _fields_ = [
                ("type", wintypes.DWORD),
                ("_input", _INPUT)
            ]
        
        button_down_map = {
            "left": MOUSEEVENTF_LEFTDOWN,
            "right": MOUSEEVENTF_RIGHTDOWN,
            "middle": MOUSEEVENTF_MIDDLEDOWN
        }
        button_up_map = {
            "left": MOUSEEVENTF_LEFTUP,
            "right": MOUSEEVENTF_RIGHTUP,
            "middle": MOUSEEVENTF_MIDDLEUP
        }
        
        down_flag = button_down_map.get(button, MOUSEEVENTF_LEFTDOWN)
        up_flag = button_up_map.get(button, MOUSEEVENTF_LEFTUP)
        
        user32 = ctypes.windll.user32
        SendInput = user32.SendInput
        SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
        SendInput.restype = wintypes.UINT
        
        for i in range(times):
            input_down = INPUT()
            input_down.type = INPUT_MOUSE
            input_down.mi = MOUSEINPUT(0, 0, 0, down_flag, 0, ctypes.c_void_p(0))
            result_down = SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
            if result_down == 0:
                raise Exception(f"SendInput failed: returned {result_down}")
            
            time.sleep(0.005)
            
            input_up = INPUT()
            input_up.type = INPUT_MOUSE
            input_up.mi = MOUSEINPUT(0, 0, 0, up_flag, 0, ctypes.c_void_p(0))
            result_up = SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))
            if result_up == 0:
                raise Exception(f"SendInput failed: returned {result_up}")
            
            if i < times - 1:
                time.sleep(0.01)
        
        if DEBUG_MODE:
            logger.info(f"✅ [SendInput] 成功點擊: 位置 ({actual_x}, {actual_y}), 按鈕: {button}, 次數: {times}")
        return True
    except Exception as e:
        if DEBUG_MODE:
            logger.warning(f"⚠️ [SendInput] 失敗: {e}, 嘗試 mouse_event...")
    
    # Method 2: Try mouse_event (fallback)
    try:
        import win32api
        import win32con
        
        button_down_map = {
            "left": win32con.MOUSEEVENTF_LEFTDOWN,
            "right": win32con.MOUSEEVENTF_RIGHTDOWN,
            "middle": win32con.MOUSEEVENTF_MIDDLEDOWN
        }
        button_up_map = {
            "left": win32con.MOUSEEVENTF_LEFTUP,
            "right": win32con.MOUSEEVENTF_RIGHTUP,
            "middle": win32con.MOUSEEVENTF_MIDDLEUP
        }
        
        down_flag = button_down_map.get(button, win32con.MOUSEEVENTF_LEFTDOWN)
        up_flag = button_up_map.get(button, win32con.MOUSEEVENTF_LEFTUP)
        
        for i in range(times):
            win32api.mouse_event(down_flag, 0, 0, 0, 0)
            time.sleep(0.005)
            win32api.mouse_event(up_flag, 0, 0, 0, 0)
            if i < times - 1:
                time.sleep(0.01)
        
        if DEBUG_MODE:
            logger.info(f"✅ [mouse_event] 成功點擊: 位置 ({actual_x}, {actual_y}), 按鈕: {button}, 次數: {times}")
        return True
    except Exception as e:
        if DEBUG_MODE:
            logger.warning(f"⚠️ [mouse_event] 失敗: {e}, 嘗試 pynput...")
    
    # Method 3: Last resort - use pynput
    try:
        from pynput.mouse import Controller, Button
        
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        
        mouse = Controller()
        mouse_button = button_map.get(button, Button.left)
        
        for i in range(times):
            mouse.click(mouse_button, 1)
            if i < times - 1:
                time.sleep(0.01)
        
        if DEBUG_MODE:
            logger.info(f"✅ [pynput] 成功點擊: 位置 ({actual_x}, {actual_y}), 按鈕: {button}, 次數: {times}")
        return True
    except ImportError:
        if DEBUG_MODE:
            logger.error(f"❌ [pynput] 失敗: 無法導入 pynput 模組")
        return False
    except Exception as e:
        if DEBUG_MODE:
            logger.error(f"❌ [pynput] 失敗: {e}")
        return False


class CursorClickerService:
    """
    Service for performing continuous mouse clicks at cursor position.
    
    This service handles:
    - Starting/stopping continuous clicking
    - Managing click intervals and counts
    - Thread-safe click execution
    """
    
    def __init__(self):
        """Initialize cursor clicker service."""
        self._is_clicking = False
        self._click_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Click settings
        self._interval_ms = 100  # Default 100ms
        self._button = "left"  # Default left button
        self._click_count = 0  # 0 = infinite
        self._current_click_count = 0
    
    def start_clicking(self, interval_ms: int, button: str, click_count: int = 0):
        """
        Start continuous clicking at current cursor position.
        
        Args:
            interval_ms: Time interval between clicks in milliseconds
            button: Mouse button ("left", "right", or "middle")
            click_count: Number of clicks (0 = infinite)
        """
        if self._is_clicking:
            if DEBUG_MODE:
                logger.warning("⚠️ 點擊已在進行中，忽略重複啟動")
            return
        
        self._interval_ms = interval_ms
        self._button = button
        self._click_count = click_count
        self._current_click_count = 0
        self._stop_event.clear()
        self._is_clicking = True
        
        # Start click thread
        self._click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self._click_thread.start()
        if DEBUG_MODE:
            count_text = "無限" if click_count == 0 else str(click_count)
            logger.info(f"🚀 啟動點擊: 間隔={interval_ms}ms, 按鈕={button}, 次數={count_text}")
    
    def stop_clicking(self):
        """Stop continuous clicking."""
        if not self._is_clicking:
            return
        
        self._is_clicking = False
        self._stop_event.set()
        
        if self._click_thread and self._click_thread.is_alive():
            self._click_thread.join(timeout=1.0)
        
        if DEBUG_MODE:
            logger.info(f"🛑 停止點擊: 總共點擊 {self._current_click_count} 次")
    
    def is_clicking(self) -> bool:
        """Check if clicking is currently active.
        
        Returns:
            bool: True if clicking, False otherwise
        """
        return self._is_clicking
    
    def _click_loop(self):
        """Main click loop running in separate thread."""
        try:
            if DEBUG_MODE:
                logger.info(f"🔄 開始點擊循環: 間隔={self._interval_ms}ms, 按鈕={self._button}, 次數={'無限' if self._click_count == 0 else self._click_count}")
            
            while self._is_clicking and not self._stop_event.is_set():
                # Get current cursor position
                x, y = self._get_cursor_position()
                
                # Perform click at current position
                self._perform_click(x, y, self._button)
                
                # Increment click count
                self._current_click_count += 1
                
                # Check if we've reached the click count limit
                if self._click_count > 0 and self._current_click_count >= self._click_count:
                    if DEBUG_MODE:
                        logger.info(f"✅ 達到點擊次數限制: {self._click_count}/{self._current_click_count}")
                    self._is_clicking = False
                    break
                
                # Wait for interval (with early exit if stop event is set)
                if not self._stop_event.wait(timeout=self._interval_ms / 1000.0):
                    # Timeout occurred, continue clicking
                    continue
                else:
                    # Stop event was set, exit loop
                    if DEBUG_MODE:
                        logger.info(f"🛑 點擊循環已停止")
                    break
        except Exception as e:
            logger.error(f"❌ 點擊循環錯誤: {e}")
        finally:
            self._is_clicking = False
            if DEBUG_MODE:
                logger.info(f"🏁 點擊循環結束: 總共點擊 {self._current_click_count} 次")
    
    def _get_cursor_position(self) -> tuple[int, int]:
        """
        Get current cursor position.
        
        Returns:
            tuple: (x, y) coordinates
        """
        try:
            import win32api
            return win32api.GetCursorPos()
        except ImportError:
            # Fallback to pynput if pywin32 not available
            try:
                from pynput.mouse import Controller
                mouse = Controller()
                pos = mouse.position
                return (int(pos[0]), int(pos[1]))
            except ImportError:
                logger.error("Neither pywin32 nor pynput available for getting cursor position")
                return (0, 0)
        except Exception as e:
            logger.error(f"Error getting cursor position: {e}")
            return (0, 0)
    
    def _perform_click(self, x: int, y: int, button: str):
        """
        Perform a native mouse click at the specified position.
        
        Uses native click method (pywin32 or pynput) for high performance.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ("left", "right", or "middle")
        """
        # Use the standalone native click function (1 click per interval)
        perform_native_click(x, y, button, times=1)


