"""
Transition Service for Witch's Weapon.
Handles page enter/exit animations and timing.
"""

from .page_state import PageID
import time

class TransitionService:
    """Manages page transition animations and timing."""
    
    def __init__(self, ui_feedback):
        self.ui = ui_feedback
        self.transition_duration = 0.5  # seconds
        self.transitions_in_progress = {}  # PageID -> transition start time
        self.transition_type = "fade"  # Can be 'fade', 'slide', 'instant'
    
    def play_enter_transition(self, page_id: PageID):
        """Start enter transition for a page."""
        self.transitions_in_progress[f"enter_{page_id.value}"] = time.time()
        
        if self.transition_type == "fade":
            self.ui.display_message(f"[TRANSITION] Fading in {page_id.value}...")
        elif self.transition_type == "slide":
            self.ui.display_message(f"[TRANSITION] Sliding in {page_id.value}...")
        else:
            self.ui.display_message(f"[TRANSITION] Entering {page_id.value}...")
    
    def play_exit_transition(self, page_id: PageID):
        """Start exit transition for a page."""
        self.transitions_in_progress[f"exit_{page_id.value}"] = time.time()
        
        if self.transition_type == "fade":
            self.ui.display_message(f"[TRANSITION] Fading out {page_id.value}...")
        elif self.transition_type == "slide":
            self.ui.display_message(f"[TRANSITION] Sliding out {page_id.value}...")
        else:
            self.ui.display_message(f"[TRANSITION] Exiting {page_id.value}...")
    
    def is_transition_complete(self, transition_key: str) -> bool:
        """Check if a transition has completed."""
        if transition_key not in self.transitions_in_progress:
            return True
        
        elapsed = time.time() - self.transitions_in_progress[transition_key]
        if elapsed >= self.transition_duration:
            del self.transitions_in_progress[transition_key]
            return True
        return False
    
    def is_any_transition_active(self) -> bool:
        """Check if any transition is in progress."""
        return len(self.transitions_in_progress) > 0
    
    def set_transition_type(self, transition_type: str):
        """Set the transition animation type."""
        if transition_type in ["fade", "slide", "instant"]:
            self.transition_type = transition_type
    
    def clear_all_transitions(self):
        """Clear all active transitions."""
        self.transitions_in_progress.clear()
