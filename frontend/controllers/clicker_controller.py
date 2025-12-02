"""
Clicker Controller
Connects GUI and backend service
"""

from backend.services.clicker_service import ClickerService


class ClickerController:
    """Clicker Controller that connects the view and the service."""
    
    def __init__(self):
        """Initialize controller and create service instance."""
        self.service = ClickerService()
    
    def handle_button_click(self) -> str:
        """
        Handle button click event.
        
        Returns:
            str: Message received from the service.
        """
        return self.service.get_hello_message()


