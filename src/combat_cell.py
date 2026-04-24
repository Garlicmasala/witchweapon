"""
Combat Cell definition for Witch's Weapon PvE 3D maps.
"""

from enum import Enum
from typing import List, Tuple

class HeightTier(Enum):
    GROUND = 0
    ELEVATED = 1
    AIR = 2
    BOSS = 3

class CombatCell:
    """A combat-ready area with activation rules and vertical tiers."""
    
    def __init__(self, cell_id: str, bounds: Tuple[Tuple[float, float, float], Tuple[float, float, float]],
                 height_tiers: List[HeightTier], enemy_spawn_points: List[Tuple[float, float, float]],
                 entry_conditions: dict = None, exit_conditions: dict = None, story_node_id: str = None):
        self.cell_id = cell_id
        self.bounds = bounds  # ((x_min, y_min, z_min), (x_max, y_max, z_max))
        self.height_tiers = height_tiers
        self.enemy_spawn_points = enemy_spawn_points
        self.entry_conditions = entry_conditions or {}
        self.exit_conditions = exit_conditions or {}
        self.story_node_id = story_node_id
        self.is_active = False
        self.is_cleared = False
    
    def contains_position(self, position: Tuple[float, float, float]) -> bool:
        """Check whether a point is inside the cell bounds."""
        (x_min, y_min, z_min), (x_max, y_max, z_max) = self.bounds
        x, y, z = position
        return x_min <= x <= x_max and y_min <= y <= y_max and z_min <= z <= z_max
    
    def activate(self):
        """Activate this combat cell."""
        if not self.is_active and not self.is_cleared:
            self.is_active = True
    
    def deactivate(self):
        """Deactivate this combat cell."""
        self.is_active = False
    
    def clear(self):
        """Mark the combat cell as cleared."""
        self.is_active = False
        self.is_cleared = True
    
    def get_height_tier(self, position: Tuple[float, float, float]) -> HeightTier:
        """Return the height tier for a position inside the cell."""
        if not self.contains_position(position):
            return None
        x_min, y_min, z_min = self.bounds[0]
        x_max, y_max, z_max = self.bounds[1]
        y_ratio = (position[1] - y_min) / max(1.0, y_max - y_min)
        if y_ratio < 0.25:
            return HeightTier.GROUND
        if y_ratio < 0.55:
            return HeightTier.ELEVATED
        if y_ratio < 0.85:
            return HeightTier.AIR
        return HeightTier.BOSS
    
    def can_enter(self, player_state: dict) -> bool:
        """Check whether the player can enter this cell."""
        for key, requirement in self.entry_conditions.items():
            if player_state.get(key) != requirement:
                return False
        return True
    
    def should_exit(self, player_state: dict) -> bool:
        """Check whether the player should exit this cell."""
        for key, requirement in self.exit_conditions.items():
            if player_state.get(key) == requirement:
                return True
        return False
