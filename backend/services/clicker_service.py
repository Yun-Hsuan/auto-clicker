"""
Clicker backend service.
Handles business logic for Orange Clicker.
"""

from frontend.i18n.translation_manager import t


class ClickerService:
    """Clicker service class that handles business logic."""

    def get_hello_message(self) -> str:
        """Get the localized Hello World message."""
        return t("backend.hello", default="Hello World")

    def process_message(self, message: str) -> str:
        """
        Process a message (example method).

        Args:
            message: Input message.

        Returns:
            str: Processed message.
        """
        return f"Processed message: {message}"