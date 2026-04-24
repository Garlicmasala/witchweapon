"""
PvP Arena System - Defines arena layouts and buff spawn points.
Supports small vertical arenas for 1v1, 2v2, 3v3 matches.
"""

from typing import List, Tuple, Dict, Optional
from enum import Enum


class ArenaSize(Enum):
    """Arena size classifications."""
    SMALL = "small"      # 1v1
    MEDIUM = "medium"    # 2v2
    LARGE = "large"      # 3v3


class Arena:
    """Represents a single PvP arena with spawn points and buff locations."""
    
    def __init__(self, name: str, size: ArenaSize, bounds: Dict, spawn_points: List[Tuple[float, float, float]]):
        self.name = name
        self.size = size
        self.bounds = bounds  # {"x": (min, max), "y": (min, max), "z": (min, max)}
        self.spawn_points = spawn_points
        self.buff_zones = []  # Buff spawn locations
        self.debuff_zones = []  # Fixed debuff zone locations
        self.hazard_zones = []  # Non-damaging obstacles
        self.vertical_traversal = []  # Platforms, walls for vertical play

    def get_spawn_point(self, team_index: int, player_index: int) -> Tuple[float, float, float]:
        """Get spawn position for a player."""
        idx = team_index * 3 + player_index  # Support up to 3v3
        if idx < len(self.spawn_points):
            return self.spawn_points[idx]
        # Fallback to first spawn
        return self.spawn_points[0] if self.spawn_points else (0, 10, 0)

    def is_in_bounds(self, position: Tuple[float, float, float]) -> bool:
        """Check if position is within arena bounds."""
        x, y, z = position
        x_in = self.bounds["x"][0] <= x <= self.bounds["x"][1]
        y_in = self.bounds["y"][0] <= y <= self.bounds["y"][1]
        z_in = self.bounds["z"][0] <= z <= self.bounds["z"][1]
        return x_in and y_in and z_in

    def get_buff_spawn_zones(self) -> List[Tuple[float, float, float]]:
        """Get all buff spawn location options."""
        return self.buff_zones

    def get_debuff_zone_locations(self) -> List[Tuple[float, float, float]]:
        """Get fixed debuff zone spawn points."""
        return self.debuff_zones

    def to_dict(self) -> Dict:
        """Serialize arena for client."""
        return {
            "name": self.name,
            "size": self.size.value,
            "bounds": self.bounds,
            "spawn_points": self.spawn_points,
            "buff_zones": self.buff_zones,
            "debuff_zones": self.debuff_zones,
        }


class ArenaRegistry:
    """Defines all available arenas."""
    
    ARENAS = {
        # Small Arena - 1v1
        "Crystal Spire": Arena(
            name="Crystal Spire",
            size=ArenaSize.SMALL,
            bounds={"x": (-30, 30), "y": (-5, 50), "z": (-30, 30)},
            spawn_points=[
                (15, 20, 0),   # Team 1, Player 1
                (-15, 20, 0),  # Team 2, Player 1
            ]
        ),
        
        # Medium Arena - 2v2
        "Ancient Colosseum": Arena(
            name="Ancient Colosseum",
            size=ArenaSize.MEDIUM,
            bounds={"x": (-50, 50), "y": (-5, 60), "z": (-50, 50)},
            spawn_points=[
                (30, 20, 0), (35, 20, -5),      # Team 1
                (-30, 20, 0), (-35, 20, -5),    # Team 2
            ]
        ),
        
        # Large Arena - 3v3
        "Void Expanse": Arena(
            name="Void Expanse",
            size=ArenaSize.LARGE,
            bounds={"x": (-80, 80), "y": (-5, 80), "z": (-80, 80)},
            spawn_points=[
                (40, 25, 10), (45, 25, 0), (40, 25, -10),    # Team 1
                (-40, 25, 10), (-45, 25, 0), (-40, 25, -10), # Team 2
            ]
        ),
    }
    
    @classmethod
    def _setup_buff_zones(cls):
        """Initialize buff spawn zones for each arena."""
        # Crystal Spire - 1v1
        cls.ARENAS["Crystal Spire"].buff_zones = [
            (0, 30, 0),    # Center high
            (15, 25, 15),  # Side platforms
            (-15, 25, -15),
            (0, 15, 25),   # Far back
        ]
        cls.ARENAS["Crystal Spire"].debuff_zones = [
            (0, 15, 0),    # Center arena floor
        ]
        
        # Ancient Colosseum - 2v2
        cls.ARENAS["Ancient Colosseum"].buff_zones = [
            (0, 35, 0),     # Center high
            (30, 30, 30),   # Quadrants
            (-30, 30, 30),
            (30, 30, -30),
            (-30, 30, -30),
        ]
        cls.ARENAS["Ancient Colosseum"].debuff_zones = [
            (20, 20, 0),    # Side zones
            (-20, 20, 0),
        ]
        
        # Void Expanse - 3v3
        cls.ARENAS["Void Expanse"].buff_zones = [
            (0, 40, 0),      # Center high
            (50, 35, 50),    # Corners
            (-50, 35, 50),
            (50, 35, -50),
            (-50, 35, -50),
            (0, 50, 50),     # Off-center heights
            (0, 50, -50),
        ]
        cls.ARENAS["Void Expanse"].debuff_zones = [
            (30, 25, 0),     # Scattered zones
            (-30, 25, 0),
            (0, 25, 30),
            (0, 25, -30),
        ]

    @classmethod
    def get_arena(cls, name: str) -> Optional[Arena]:
        """Get an arena by name."""
        return cls.ARENAS.get(name)

    @classmethod
    def get_arena_for_size(cls, size: ArenaSize) -> Optional[Arena]:
        """Get a random arena of the specified size."""
        import random
        arenas = [a for a in cls.ARENAS.values() if a.size == size]
        return random.choice(arenas) if arenas else None

    @classmethod
    def list_arenas(cls, size: Optional[ArenaSize] = None) -> List[str]:
        """List available arenas, optionally by size."""
        if size:
            return [name for name, arena in cls.ARENAS.items() if arena.size == size]
        return list(cls.ARENAS.keys())


# Initialize buff zones on module load
ArenaRegistry._setup_buff_zones()
