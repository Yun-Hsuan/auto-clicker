"""
UI Log Handler for Orange Clicker

Custom logging handler that sends log messages to the UI's debug log area.
"""

import logging
from PySide6.QtCore import QObject, Signal


class UILogHandler(QObject, logging.Handler):
    """
    Custom logging handler that emits log messages as Qt signals.
    This allows log messages to be displayed in the UI thread safely.
    """
    
    # Signal emitted when a log message is received
    log_message = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the UI log handler."""
        QObject.__init__(self, parent)
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        ))
    
    def emit(self, record):
        """
        Emit a log record as a Qt signal.
        
        Args:
            record: LogRecord instance from logging module
        """
        try:
            msg = self.format(record)
            # Emit signal (will be handled in UI thread)
            self.log_message.emit(msg)
        except Exception:
            # Ignore errors in logging handler to prevent infinite loops
            pass

