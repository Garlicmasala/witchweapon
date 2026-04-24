"""
World map backbone for Witch's Weapon PvE simulation.
Manages region chunks, active combat cells, and world streaming.
"""

from typing import List, Tuple
from .region_chunk import RegionChunk
from .combat_cell import CombatCell
from .traversal_system import TraversalNode

class WorldMapRoot:
    """Root object for the PvE map system."""
    
    def __init__(self, ui_feedback):
        self.ui = ui_feedback
        self.region_chunks = []
        self.active_chunks = []
        self.player_chunk = None
        self.player_position = (0.0, 0.0, 0.0)
        self.load_radius = 30.0
    
    def register_chunk(self, chunk: RegionChunk):
        self.region_chunks.append(chunk)
        self.ui.display_message(f"[WorldMap] Registered chunk: {chunk.chunk_id}")
    
    def update_player_position(self, position: Tuple[float, float, float]):
        self.player_position = position
        self.update_active_chunks()
    
    def update_active_chunks(self):
        self.active_chunks = []
        for chunk in self.region_chunks:
            if chunk.contains_position(self.player_position) or self._chunk_within_radius(chunk, self.player_position, self.load_radius):
                if not chunk.is_loaded:
                    chunk.load()
                    self.ui.display_message(f"[WorldMap] Loaded chunk: {chunk.chunk_id}")
                self.active_chunks.append(chunk)
            elif chunk.is_loaded:
                chunk.unload()
                self.ui.display_message(f"[WorldMap] Unloaded chunk: {chunk.chunk_id}")
    
    def get_active_combat_cells(self):
        cells = []
        for chunk in self.active_chunks:
            cells.extend(chunk.combat_zones)
        return cells
    
    def get_traversal_nodes_nearby(self) -> List[TraversalNode]:
        nodes = []
        for chunk in self.active_chunks:
            nodes.extend(chunk.traversal_nodes)
        return nodes
    
    def get_chunk_for_position(self, position: Tuple[float, float, float]):
        for chunk in self.region_chunks:
            if chunk.contains_position(position):
                return chunk
        return None
    
    def _chunk_within_radius(self, chunk: RegionChunk, position: Tuple[float, float, float], radius: float) -> bool:
        (x_min, y_min, z_min), (x_max, y_max, z_max) = chunk.bounds
        px, py, pz = position
        dx = max(x_min - px, 0, px - x_max)
        dy = max(y_min - py, 0, py - y_max)
        dz = max(z_min - pz, 0, pz - z_max)
        return (dx*dx + dy*dy + dz*dz) ** 0.5 <= radius
    
    def find_cell_for_position(self, position: Tuple[float, float, float]):
        for cell in self.get_active_combat_cells():
            if cell.contains_position(position):
                return cell
        return None
