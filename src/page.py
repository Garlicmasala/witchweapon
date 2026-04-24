"""
Base Page class for Witch's Weapon.
All pages inherit from this interface.
"""

from abc import ABC, abstractmethod
from .page_state import PageID, PageState

class PageContext:
    """Context passed to pages when entering."""
    def __init__(self, **kwargs):
        self.data = kwargs

class IPage(ABC):
    """Interface that all pages must implement."""
    
    def __init__(self, page_id: PageID, ui_feedback):
        self.page_id = page_id
        self.ui = ui_feedback
        self.state = PageState.INACTIVE
        self.is_visible = False
    
    @property
    def page_id_enum(self) -> PageID:
        """Return the page ID."""
        return self.page_id
    
    @abstractmethod
    def on_enter(self, context: PageContext = None):
        """Called when page becomes active."""
        pass
    
    @abstractmethod
    def on_exit(self):
        """Called when page is deactivated."""
        pass
    
    @abstractmethod
    def render(self):
        """Render the page UI."""
        pass
    
    def set_visible(self, visible: bool):
        """Set page visibility."""
        self.is_visible = visible
        if visible:
            self.state = PageState.ACTIVE
        else:
            self.state = PageState.INACTIVE
    
    def update(self, delta_time: float = 1.0):
        """Update page logic each frame."""
        pass
    
    def handle_input(self, input_action: str):
        """Handle user input. Can be overridden by subclasses."""
        pass
    
    def is_page_locked(self) -> bool:
        """Check if page access is locked (live-ops, tutorial, etc)."""
        return False
    
    def can_exit(self) -> bool:
        """Validate if page can be exited (e.g., unsaved data)."""
        return True
    
    def get_state(self) -> PageState:
        """Get current page state."""
        return self.state
    
    def set_state(self, new_state: PageState):
        """Set page state."""
        self.state = new_state
