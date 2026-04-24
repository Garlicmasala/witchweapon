"""
World state controller for Witch's Weapon PvE world.
Handles map events, dynamic encounters, and overall world rules.
"""

from typing import List, Tuple
from .combat_cell import CombatCell
from .world_map import WorldMapRoot
from .enemy_director import EnemyDirector

class WorldStateController:
    """Central controller for world-level state and events."""
    
    def __init__(self, ui_feedback, world_map: WorldMapRoot, enemy_director: EnemyDirector):
        self.ui = ui_feedback
        self.world_map = world_map
        self.enemy_director = enemy_director
        self.dynamic_events = []
        self.active_event = None
        self.time_of_day = "day"
    
    def update_world_state(self, player_position: Tuple[float, float, float], player=None, delta_time: float = 1.0):
        self.world_map.update_player_position(player_position)
        cell = self.world_map.find_cell_for_position(player_position)
        if cell and not cell.is_active and not cell.is_cleared:
            self.ui.display_message(f"[WorldState] Player entered combat cell {cell.cell_id}")
            cell.activate()
            self.enemy_director.on_player_enter_cell(cell, player)
        self._process_dynamic_events(delta_time)
    
    def _process_dynamic_events(self, delta_time: float):
        if self.active_event:
            self.ui.display_message(f"[WorldState] Active event: {self.active_event}")
    
    def trigger_event(self, event_name: str, cell: CombatCell):
        self.active_event = event_name
        self.ui.display_message(f"[WorldState] Triggered event: {event_name} in {cell.cell_id}")
    
    def complete_event(self):
        self.ui.display_message(f"[WorldState] Completed event: {self.active_event}")
        self.active_event = None
