"""
Click Path Executor Service

Handles execution of recorded click paths.
Executes clicks in sequence: ClickStepItem -> DelayTimer -> ClickStepItem -> ...
"""

import threading
import time
import logging
from typing import Optional, List, Dict, Any

from backend.services.cursor_clicker_service import perform_native_click

logger = logging.getLogger(__name__)

# Enable debug mode by default - set to False to disable verbose logging
DEBUG_MODE = True


class ClickPathExecutorService:
    """
    Service for executing recorded click paths.
    
    This service handles:
    - Executing click sequences in order
    - Handling delays between steps
    - Supporting stop functionality
    - Thread-safe execution
    """
    
    def __init__(self):
        """Initialize click path executor service."""
        self._is_executing = False
        self._execution_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def start_execution(self, click_path: List[Dict[str, Any]]):
        """
        Start executing a click path.
        
        Args:
            click_path: List of step dictionaries, each containing:
                - x: X coordinate
                - y: Y coordinate
                - button: Mouse button ("left", "right", "middle")
                - click_count: Number of clicks for this step
                - delay: Delay time in milliseconds (before next step)
                - name: Step name (optional, for logging)
        """
        logger.info(f"🛤️  [ClickPathExecutor] ⚡ start_execution called")
        logger.debug(f"🛤️  [ClickPathExecutor]   - click_path type: {type(click_path)}")
        logger.debug(f"🛤️  [ClickPathExecutor]   - click_path is None: {click_path is None}")
        logger.debug(f"🛤️  [ClickPathExecutor]   - click_path length: {len(click_path) if click_path else 'N/A'}")
        
        # Validate click_path type
        if click_path is None:
            logger.error(f"🛤️  [ClickPathExecutor] ❌ click_path is None!")
            return
        
        if not isinstance(click_path, list):
            logger.error(f"🛤️  [ClickPathExecutor] ❌ click_path is not a list: type={type(click_path)}, value={click_path}")
            return
        
        if self._is_executing:
            logger.warning("🛤️  [ClickPathExecutor] ⚠️  Execution already in progress, ignoring duplicate start")
            return
        
        if len(click_path) == 0:
            logger.warning("🛤️  [ClickPathExecutor] ⚠️  Click path is empty, cannot execute")
            return
        
        # Validate each step structure
        logger.debug(f"🛤️  [ClickPathExecutor] 📋 Validating click_path structure...")
        for i, step in enumerate(click_path[:5]):  # Check first 5 steps
            logger.debug(f"🛤️  [ClickPathExecutor]   - Step {i}: type={type(step)}")
            if not isinstance(step, dict):
                logger.error(f"🛤️  [ClickPathExecutor] ❌ Step {i} is not a dict: type={type(step)}, value={step}")
                return
            # Check required fields
            required_fields = ['x', 'y', 'button']
            for field in required_fields:
                if field not in step:
                    logger.error(f"🛤️  [ClickPathExecutor] ❌ Step {i} missing required field '{field}': {step}")
                    return
            logger.debug(f"🛤️  [ClickPathExecutor]     - Step {i} valid: x={step.get('x')}, y={step.get('y')}, button={step.get('button')}")
        
        logger.info(f"🛤️  [ClickPathExecutor] ✅ click_path validation passed: {len(click_path)} steps")
        
        self._stop_event.clear()
        self._is_executing = True
        
        # Log click path details
        step_count = len(click_path)
        logger.info(f"🚀 [Click Path] Starting execution: {step_count} steps")
        if DEBUG_MODE:
            for i, step in enumerate(click_path, start=1):
                logger.debug(
                    f"  Step {i}: {step.get('name', f'Step {i}')} - "
                    f"({step.get('x', 0)}, {step.get('y', 0)}), "
                    f"Button: {step.get('button', 'left')}, "
                    f"Clicks: {step.get('click_count', 1)}, "
                    f"Delay: {step.get('delay', 0)}ms"
                )
        
        # Start execution thread
        self._execution_thread = threading.Thread(
            target=self._execution_loop,
            args=(click_path,),
            daemon=True
        )
        self._execution_thread.start()
    
    def stop_execution(self):
        """Stop click path execution."""
        if not self._is_executing:
            logger.debug("⚠️ [Click Path] Execution not in progress, no need to stop")
            return
        
        logger.info("🛑 [Click Path] Stopping execution...")
        self._is_executing = False
        self._stop_event.set()
        
        if self._execution_thread and self._execution_thread.is_alive():
            self._execution_thread.join(timeout=1.0)
        
        logger.info("🛑 [Click Path] Execution stopped")
    
    def is_executing(self) -> bool:
        """
        Check if click path execution is currently active.
        
        Returns:
            bool: True if executing, False otherwise
        """
        return self._is_executing
    
    def _execution_loop(self, click_path: List[Dict[str, Any]]):
        """
        Main execution loop running in separate thread.
        
        Args:
            click_path: List of step dictionaries to execute
        """
        try:
            logger.info(f"🔄 [Click Path] Starting execution loop: {len(click_path)} steps")
            
            for step_index, step in enumerate(click_path, start=1):
                # Check if execution should stop
                if not self._is_executing or self._stop_event.is_set():
                    logger.info(f"🛑 [Click Path] Execution stopped at step {step_index}/{len(click_path)}")
                    break
                
                # Extract step data
                x = step.get("x", 0)
                y = step.get("y", 0)
                button = step.get("button", "left")
                click_count = step.get("click_count", 1)
                delay_ms = step.get("delay", 0)
                step_name = step.get("name", f"Step {step_index}")
                
                logger.info(
                    f"📍 [Click Path] Executing {step_name} ({step_index}/{len(click_path)}): "
                    f"Position ({x}, {y}), "
                    f"Button: {button}, "
                    f"Click Count: {click_count}"
                )
                
                # Move cursor to position and perform clicks
                try:
                    import win32api
                    # Get current position for logging
                    current_x, current_y = win32api.GetCursorPos()
                    if DEBUG_MODE:
                        logger.debug(f"  Current cursor: ({current_x}, {current_y}) -> Target: ({x}, {y})")
                    
                    # Move to target position
                    win32api.SetCursorPos((x, y))
                    if DEBUG_MODE:
                        logger.debug(f"  Cursor moved to ({x}, {y})")
                    
                    # Small delay to ensure cursor has moved
                    time.sleep(0.01)
                    
                    # Perform clicks at the target position
                    logger.debug(f"  Performing {click_count} click(s) with {button} button...")
                    perform_native_click(x, y, button, times=click_count)
                    logger.debug(f"  ✅ Click(s) completed")
                    
                except ImportError:
                    # Fallback: use pynput if pywin32 not available
                    try:
                        from pynput.mouse import Controller
                        mouse = Controller()
                        logger.debug(f"  Moving cursor using pynput...")
                        mouse.position = (x, y)
                        time.sleep(0.01)
                        perform_native_click(x, y, button, times=click_count)
                        logger.debug(f"  ✅ Click(s) completed")
                    except ImportError:
                        logger.error("❌ [Click Path] Neither pywin32 nor pynput available for cursor movement")
                        perform_native_click(x, y, button, times=click_count)
                except Exception as e:
                    logger.error(f"❌ [Click Path] Error moving cursor or clicking: {e}")
                    # Try clicking anyway (might work if cursor is already close)
                    perform_native_click(x, y, button, times=click_count)
                
                # Wait for delay before next step (if not the last step)
                if step_index < len(click_path):
                    if delay_ms > 0:
                        logger.info(f"⏳ [Click Path] Waiting {delay_ms}ms before next step...")
                        # Wait with early exit if stop event is set
                        if self._stop_event.wait(timeout=delay_ms / 1000.0):
                            # Stop event was set, exit loop
                            logger.info(f"🛑 [Click Path] Execution stopped during delay")
                            break
                        logger.debug(f"  Delay completed, proceeding to next step")
                    else:
                        logger.debug(f"  No delay, proceeding immediately to next step")
            
            logger.info(f"✅ [Click Path] Execution completed: {len(click_path)} steps executed")
        
        except Exception as e:
            logger.error(f"❌ [Click Path] Error in execution loop: {e}", exc_info=True)
        finally:
            self._is_executing = False
            logger.info(f"🏁 [Click Path] Execution loop ended")

