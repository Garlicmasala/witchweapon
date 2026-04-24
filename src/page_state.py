"""
Page State Management for Witch's Weapon.
Defines page lifecycle and state transitions.
"""

from enum import Enum

class PageID(Enum):
    """Unique identifier for each page."""
    HOME = "home"
    COMBAT = "combat"
    UPGRADE = "upgrade"
    GACHA = "gacha"
    INTERACT = "interact"
    CHARACTER = "character"
    INVENTORY = "inventory"

class PageState(Enum):
    """Page lifecycle state."""
    INACTIVE = "inactive"
    ENTERING = "entering"
    ACTIVE = "active"
    EXITING = "exiting"
