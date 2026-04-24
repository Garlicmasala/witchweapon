"""
Region chunk support for Witch's Weapon 3D world streaming.
"""

from typing import List, Tuple
from .combat_cell import CombatCell
from .traversal_system import TraversalNode

class RegionChunk:
    """A vertical-aware chunk of the world map."""
    
    def __init__(self, chunk_id: str, bounds: Tuple[Tuple[float, float, float], Tuple[float, float, float]]):
        self.chunk_id = chunk_id
        self.bounds = bounds
        self.terrain_mesh = None
        self.navigation_layers = []
        self.combat_zones: List[CombatCell] = []
        self.traversal_nodes: List[TraversalNode] = []
        self.environment_triggers = []
        self.is_loaded = False
    
    def load(self):
        self.is_loaded = True
    
    def unload(self):
        self.is_loaded = False
    
    def contains_position(self, position: Tuple[float, float, float]) -> bool:
        (x_min, y_min, z_min), (x_max, y_max, z_max) = self.bounds
        x, y, z = position
        return x_min <= x <= x_max and y_min <= y <= y_max and z_min <= z <= z_max
    
    def add_combat_cell(self, cell: CombatCell):
        self.combat_zones.append(cell)
    
    def add_traversal_node(self, node: TraversalNode):
        self.traversal_nodes.append(node)
    
    def get_active_cells(self):
        return [cell for cell in self.combat_zones if cell.is_active and not cell.is_cleared]
