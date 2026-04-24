"""
Traversal System for Witch's Weapon 3D Maps.
Handles movement modes, traversal nodes, and vertical traversal mechanics.

Inspired by Genshin Impact (climbing, gliding) and Marvel Rivals (vertical combat).
"""

from enum import Enum
from typing import List, Tuple

class TraversalMode(Enum):
    """Possible player traversal modes."""
    GROUND = "ground"
    JUMP = "jump"
    AIR_GLIDE = "air_glide"
    AIR_FLY = "air_fly"
    CLIMB = "climb"
    SKILL_BASED = "skill_based"  # e.g., teleport, dash

class TraversalNode:
    """A point in the world that enables special traversal."""
    
    def __init__(self, node_id: str, position: Tuple[float, float, float], 
                 node_type: str, energy_cost: float = 0, allowed_modes: List[TraversalMode] = None):
        self.node_id = node_id
        self.position = position  # (x, y, z)
        self.node_type = node_type  # "jump_pad", "wind_updraft", "climb_ledge", "grapple", "fly_zone"
        self.energy_cost = energy_cost
        self.allowed_modes = allowed_modes or [TraversalMode.GROUND]
        self.is_active = True
    
    def can_use(self, current_mode: TraversalMode, available_energy: float) -> bool:
        """Check if this node can be used given current state."""
        return self.is_active and current_mode in self.allowed_modes and available_energy >= self.energy_cost
    
    def get_exit_velocity(self) -> Tuple[float, float, float]:
        """Get the velocity imparted by using this node."""
        if self.node_type == "jump_pad":
            return (0, 10, 0)  # Upward boost
        elif self.node_type == "wind_updraft":
            return (0, 8, 0)  # Slower upward
        elif self.node_type == "fly_zone":
            return (0, 5, 0)  # Gentle lift
        return (0, 0, 0)

class TraversalSystem:
    """
    Manages player traversal in 3D space.
    Handles mode transitions, traversal node interactions, and stamina.
    """
    
    def __init__(self, ui_feedback):
        self.ui = ui_feedback
        self.current_mode = TraversalMode.GROUND
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen_rate = 5  # per second
        self.traversal_nodes = {}  # NodeID -> TraversalNode
        self.active_nodes_nearby = []  # Nodes within interaction range
    
    def register_traversal_node(self, node: TraversalNode):
        """Register a traversal node in the world."""
        self.traversal_nodes[node.node_id] = node
        self.ui.display_message(f"[Traversal] Registered node: {node.node_id} ({node.node_type})")
    
    def register_nodes(self, nodes: List[TraversalNode]):
        """Register multiple traversal nodes."""
        for node in nodes:
            self.register_traversal_node(node)
    
    def update_nearby_nodes(self, player_position: Tuple[float, float, float], 
                           interaction_range: float = 5.0):
        """Find traversal nodes near the player."""
        self.active_nodes_nearby = []
        
        for node in self.traversal_nodes.values():
            if not node.is_active:
                continue
            
            # Calculate distance
            dx = player_position[0] - node.position[0]
            dy = player_position[1] - node.position[1]
            dz = player_position[2] - node.position[2]
            distance = (dx**2 + dy**2 + dz**2)**0.5
            
            if distance <= interaction_range:
                self.active_nodes_nearby.append(node)
    
    def set_traversal_mode(self, mode: TraversalMode) -> bool:
        """Attempt to change traversal mode."""
        # Validate mode change
        if not self.can_switch_to_mode(mode):
            return False
        
        self.current_mode = mode
        self.ui.display_message(f"[Traversal] Mode: {mode.value}")
        return True
    
    def can_switch_to_mode(self, mode: TraversalMode) -> bool:
        """Check if mode change is valid."""
        # Ground always available
        if mode == TraversalMode.GROUND:
            return True
        
        # Jumping requires stamina
        if mode == TraversalMode.JUMP:
            return self.stamina >= 10
        
        # Air modes require stamina
        if mode in [TraversalMode.AIR_GLIDE, TraversalMode.AIR_FLY]:
            return self.stamina >= 5
        
        # Climbing requires stamina
        if mode == TraversalMode.CLIMB:
            return self.stamina >= 8
        
        return False
    
    def use_traversal_node(self, node: TraversalNode) -> bool:
        """Attempt to use a traversal node."""
        if not node.can_use(self.current_mode, self.stamina):
            self.ui.display_message(f"[Traversal] Cannot use node {node.node_id}. Insufficient resources.")
            return False
        
        # Consume energy
        self.stamina -= node.energy_cost
        
        # Apply effects
        exit_vel = node.get_exit_velocity()
        self.ui.display_message(f"[Traversal] Used {node.node_type}! Velocity: {exit_vel}")
        
        return True
    
    def update_stamina(self, delta_time: float = 1.0):
        """Regenerate stamina over time."""
        if self.current_mode == TraversalMode.GROUND:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate * delta_time)
    
    def consume_stamina(self, amount: float) -> bool:
        """Consume stamina for an action."""
        if self.stamina < amount:
            return False
        
        self.stamina -= amount
        return True
    
    def get_current_mode(self) -> TraversalMode:
        """Get current traversal mode."""
        return self.current_mode
    
    def get_stamina_percent(self) -> float:
        """Get stamina as percentage."""
        return (self.stamina / self.max_stamina) * 100
