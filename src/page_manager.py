"""
Page Manager - The Backbone for Witch's Weapon.
Central state machine for page/homepage switching.

Architecture:
    ┌────────────────────┐
    │   PageManager      │
    │  (Singleton)       │
    └─────────┬──────────┘
              ↓
    ┌───────────────────────────────┐
    │ Page Registry (Data-Driven)   │
    │ Home | Gacha | Character | …  │
    └─────────┬──────────┬──────────┘
              ↓          ↓
    ┌───────────────┐  ┌───────────────┐
    │ HomePageView  │  │ GachaPageView │
    └───────────────┘  └───────────────┘
"""

from .page_state import PageID, PageState
from .page import PageContext
from .transition_service import TransitionService
import time

class PageManager:
    """
    Central backbone for page/homepage switching.
    Singleton pattern - only one instance globally.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PageManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.ui = None
        self.pages = {}  # PageID -> IPage instance
        self.page_registry = {}  # PageID -> page config
        self.current_page = None
        self.previous_page = None
        self.transition_service = None
        self.input_locked = False
        self.is_modal_open = False
        self.tutorial_manager = None
        self.navigation_rules = {}  # Define allowed page transitions
        self.page_access_locks = {}  # PageID -> bool (locked or not)
    
    def initialize(self, ui_feedback, transition_service: TransitionService = None):
        """Initialize PageManager with dependencies."""
        self.ui = ui_feedback
        self.transition_service = transition_service or TransitionService(ui_feedback)
        self.ui.display_message("[PageManager] Initialized.")
    
    def register_page(self, page_id: PageID, page_instance):
        """Register a page with the manager."""
        if page_id in self.pages:
            self.ui.display_message(f"[PageManager] Page {page_id.value} already registered.")
            return
        
        self.pages[page_id] = page_instance
        self.page_access_locks[page_id] = False  # Unlocked by default
        self.ui.display_message(f"[PageManager] Registered page: {page_id.value}")
    
    def register_pages(self, pages_dict: dict):
        """Register multiple pages at once."""
        for page_id, page_instance in pages_dict.items():
            self.register_page(page_id, page_instance)
    
    def get_page(self, page_id: PageID):
        """Get a page instance by ID."""
        return self.pages.get(page_id)
    
    def set_navigation_rules(self, rules: dict):
        """
        Set navigation rules to prevent illegal page jumps.
        Example: {PageID.HOME: [PageID.GACHA, PageID.CHARACTER]}
        """
        self.navigation_rules = rules
    
    def can_navigate(self, from_page: PageID, to_page: PageID) -> bool:
        """Check if navigation is allowed by rules."""
        if not self.navigation_rules:
            return True  # No rules = all navigation allowed
        
        allowed_destinations = self.navigation_rules.get(from_page, [])
        return to_page in allowed_destinations
    
    def lock_page(self, page_id: PageID):
        """Lock a page (live-ops, tutorial, etc)."""
        self.page_access_locks[page_id] = True
        self.ui.display_message(f"[PageManager] Page {page_id.value} locked.")
    
    def unlock_page(self, page_id: PageID):
        """Unlock a page."""
        self.page_access_locks[page_id] = False
        self.ui.display_message(f"[PageManager] Page {page_id.value} unlocked.")
    
    def is_page_accessible(self, page_id: PageID) -> bool:
        """Check if page is accessible."""
        page = self.get_page(page_id)
        if not page:
            return False
        
        # Check explicit lock
        if self.page_access_locks.get(page_id, False):
            return False
        
        # Check page's own lock logic
        if page.is_page_locked():
            return False
        
        # If tutorial manager exists, check if it's overriding navigation
        if self.tutorial_manager and self.tutorial_manager.is_active():
            if not self.tutorial_manager.allows_page(page_id):
                return False
        
        return True
    
    def request_page(self, page_id: PageID, context: PageContext = None) -> bool:
        """
        Request to switch to a page.
        This is the main entry point for page switching.
        """
        # Validation checks
        if self.input_locked:
            self.ui.display_message("[PageManager] Input locked. Cannot switch pages.")
            return False
        
        if self.is_modal_open:
            self.ui.display_message("[PageManager] Modal is open. Cannot switch pages.")
            return False
        
        if not self.is_page_accessible(page_id):
            self.ui.display_message(f"[PageManager] Page {page_id.value} is not accessible.")
            return False
        
        if self.current_page and not self.can_navigate(self.current_page.page_id_enum, page_id):
            self.ui.display_message(f"[PageManager] Navigation from {self.current_page.page_id_enum.value} to {page_id.value} not allowed.")
            return False
        
        # If already on this page, no-op
        if self.current_page and self.current_page.page_id_enum == page_id:
            self.ui.display_message(f"[PageManager] Already on page {page_id.value}.")
            return True
        
        # Attempt switch
        return self._switch_page(page_id, context)
    
    def _switch_page(self, page_id: PageID, context: PageContext = None) -> bool:
        """
        Internal page switch logic.
        Orchestrates: exit old page -> transition -> enter new page.
        """
        # Lock input during transition
        self.input_locked = True
        self.ui.display_message(f"[PageManager] Switching to {page_id.value}...")
        
        try:
            # Exit current page
            if self.current_page:
                if not self.current_page.can_exit():
                    self.ui.display_message("[PageManager] Current page cannot exit.")
                    self.input_locked = False
                    return False
                
                self.current_page.set_state(PageState.EXITING)
                self.transition_service.play_exit_transition(self.current_page.page_id_enum)
                self.current_page.on_exit()
                self.current_page.set_visible(False)
                self.previous_page = self.current_page
            
            # Wait for transition to complete
            if self.current_page:
                exit_key = f"exit_{self.current_page.page_id_enum.value}"
                while not self.transition_service.is_transition_complete(exit_key):
                    time.sleep(0.01)  # Small sleep to prevent CPU spin
            
            # Enter new page
            new_page = self.get_page(page_id)
            if not new_page:
                self.ui.display_message(f"[PageManager] Page {page_id.value} not found!")
                self.input_locked = False
                return False
            
            new_page.set_state(PageState.ENTERING)
            self.transition_service.play_enter_transition(page_id)
            
            if context is None:
                context = PageContext()
            
            new_page.on_enter(context)
            new_page.set_visible(True)
            self.current_page = new_page
            
            # Wait for enter transition to complete
            enter_key = f"enter_{page_id.value}"
            while not self.transition_service.is_transition_complete(enter_key):
                time.sleep(0.01)
            
            self.ui.display_message(f"[PageManager] Successfully switched to {page_id.value}.")
            return True
        
        except Exception as e:
            self.ui.display_message(f"[PageManager] ERROR during page switch: {str(e)}")
            return False
        
        finally:
            # Unlock input
            self.input_locked = False
    
    def get_current_page(self):
        """Get the currently active page."""
        return self.current_page
    
    def get_current_page_id(self) -> PageID:
        """Get the ID of the current page."""
        return self.current_page.page_id_enum if self.current_page else None
    
    def set_modal_state(self, is_open: bool):
        """Set if a modal is open (blocks page switching)."""
        self.is_modal_open = is_open
    
    def set_tutorial_manager(self, tutorial_manager):
        """Set tutorial manager for override support."""
        self.tutorial_manager = tutorial_manager
    
    def render_current_page(self):
        """Render the current page."""
        if self.current_page and self.current_page.is_visible:
            self.current_page.render()
    
    def update_current_page(self, delta_time: float = 1.0):
        """Update the current page."""
        if self.current_page and self.current_page.is_visible:
            self.current_page.update(delta_time)
    
    def handle_input(self, input_action: str):
        """Handle user input by forwarding to current page."""
        if self.input_locked:
            return
        
        if self.current_page and self.current_page.is_visible:
            self.current_page.handle_input(input_action)
    
    def get_page_stack_info(self) -> str:
        """Debug: Get current page stack info."""
        current = self.current_page.page_id_enum.value if self.current_page else "None"
        previous = self.previous_page.page_id_enum.value if self.previous_page else "None"
        return f"Current: {current}, Previous: {previous}, Modal Open: {self.is_modal_open}, Input Locked: {self.input_locked}"
