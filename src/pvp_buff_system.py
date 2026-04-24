"""
PvP Buff System - Manages buffs and debuffs in PvP matches.
Buffs are temporary, visible, contested resources spawned on the map.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
import time


class BuffType(Enum):
    """Categories of buffs."""
    MOBILITY = "Mobility"
    OFFENSIVE = "Offensive"
    DEFENSIVE = "Defensive"


class DebuffType(Enum):
    """Categories of debuffs (zone-based)."""
    CORRUPTION = "Corruption"
    GRAVITY = "Gravity"
    SILENCE = "Silence"


class Buff:
    """Represents a single buff effect."""
    
    def __init__(self, name: str, buff_type: BuffType, duration: float, effects: Dict):
        self.name = name
        self.buff_type = buff_type
        self.duration = duration  # Seconds
        self.max_duration = duration
        self.effects = effects  # Dict of stat: value mappings
        self.spawned_time = None  # When buff appeared
        self.claimed_by = None  # Player who picked it up (if None, available)
        self.claimed_time = None

    def is_expired(self):
        """Check if buff duration has elapsed."""
        if self.claimed_time is None:
            return False  # Not claimed, doesn't expire
        return time.time() - self.claimed_time >= self.duration

    def claim(self, player_name: str):
        """Mark buff as claimed by a player."""
        self.claimed_by = player_name
        self.claimed_time = time.time()

    def release(self):
        """Release buff when duration ends or manually."""
        self.claimed_by = None
        self.claimed_time = None

    def get_remaining_duration(self):
        """Get seconds remaining on buff."""
        if self.claimed_time is None:
            return self.duration
        elapsed = time.time() - self.claimed_time
        return max(0, self.duration - elapsed)

    def to_dict(self):
        """Serialize buff for network/UI."""
        return {
            "name": self.name,
            "type": self.buff_type.value,
            "duration": self.duration,
            "effects": self.effects,
            "claimed_by": self.claimed_by,
            "remaining": self.get_remaining_duration()
        }


class DebuffZone:
    """Represents a debuff zone on the map."""
    
    def __init__(self, name: str, debuff_type: DebuffType, position: Tuple[float, float, float], 
                 radius: float, effects: Dict, duration: Optional[float] = None):
        self.name = name
        self.debuff_type = debuff_type
        self.position = position  # (x, y, z)
        self.radius = radius
        self.effects = effects
        self.duration = duration  # None = permanent, otherwise timeout
        self.spawned_time = time.time()
        self.active = True

    def is_expired(self):
        """Check if permanent debuff zone has timed out."""
        if self.duration is None:
            return False
        return time.time() - self.spawned_time >= self.duration

    def is_affecting(self, position: Tuple[float, float, float]):
        """Check if a position is within debuff radius."""
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        dz = position[2] - self.position[2]
        distance = (dx**2 + dy**2 + dz**2) ** 0.5
        return distance <= self.radius

    def get_remaining_duration(self):
        """Get seconds remaining on debuff zone."""
        if self.duration is None:
            return float('inf')
        elapsed = time.time() - self.spawned_time
        return max(0, self.duration - elapsed)

    def to_dict(self):
        """Serialize debuff zone for network/UI."""
        return {
            "name": self.name,
            "type": self.debuff_type.value,
            "position": self.position,
            "radius": self.radius,
            "effects": self.effects,
            "remaining": self.get_remaining_duration()
        }


class BuffRegistry:
    """Defines all available buffs."""
    
    # Mobility Buffs
    BUFFS = {
        "Wind Surge": Buff("Wind Surge", BuffType.MOBILITY, 10.0, {
            "jump_height_multiplier": 1.3,
            "air_control_multiplier": 1.2
        }),
        "Phase Dash": Buff("Phase Dash", BuffType.MOBILITY, 0.0, {
            "dash_charges": 1,
            "dash_distance": 15.0
        }),
        "Gravity Break": Buff("Gravity Break", BuffType.MOBILITY, 8.0, {
            "fall_speed_multiplier": 0.5,
            "float_enabled": True
        }),
        
        # Offensive Buffs
        "Arcane Overload": Buff("Arcane Overload", BuffType.OFFENSIVE, 10.0, {
            "skill_damage_multiplier": 1.2
        }),
        "Crit Focus": Buff("Crit Focus", BuffType.OFFENSIVE, 0.0, {
            "next_attack_crit": True
        }),
        "Execution Mark": Buff("Execution Mark", BuffType.OFFENSIVE, 8.0, {
            "low_health_damage_bonus": 0.15
        }),
        
        # Defensive Buffs
        "Aegis Shield": Buff("Aegis Shield", BuffType.DEFENSIVE, 0.0, {
            "shield_amount": 50.0,
            "shield_breakable": True
        }),
        "Cleanse Aura": Buff("Cleanse Aura", BuffType.DEFENSIVE, 5.0, {
            "remove_debuffs": True,
            "debuff_immunity": True
        }),
        "Regeneration Node": Buff("Regeneration Node", BuffType.DEFENSIVE, 10.0, {
            "hp_regen_per_second": 3.0
        }),
    }

    @classmethod
    def get_buff(cls, name: str) -> Optional[Buff]:
        """Get a buff by name (creates a fresh copy)."""
        if name in cls.BUFFS:
            original = cls.BUFFS[name]
            # Create a copy to avoid sharing state
            return Buff(original.name, original.buff_type, original.duration, original.effects.copy())
        return None

    @classmethod
    def get_random_buff(cls, buff_type: Optional[BuffType] = None) -> Buff:
        """Get a random buff, optionally filtered by type."""
        import random
        if buff_type:
            buffs = [b for b in cls.BUFFS.values() if b.buff_type == buff_type]
        else:
            buffs = list(cls.BUFFS.values())
        
        if not buffs:
            return None
        original = random.choice(buffs)
        return Buff(original.name, original.buff_type, original.duration, original.effects.copy())

    @classmethod
    def list_buffs(cls, buff_type: Optional[BuffType] = None) -> List[str]:
        """List all buff names, optionally filtered by type."""
        if buff_type:
            return [name for name, buff in cls.BUFFS.items() if buff.buff_type == buff_type]
        return list(cls.BUFFS.keys())


class DebuffZoneRegistry:
    """Defines standard debuff zones."""
    
    # Zone templates (use position from spawn logic)
    ZONE_TEMPLATES = {
        "Corruption Field": {
            "debuff_type": DebuffType.CORRUPTION,
            "radius": 8.0,
            "effects": {
                "damage_multiplier": 0.85  # -15% damage
            }
        },
        "Gravity Well": {
            "debuff_type": DebuffType.GRAVITY,
            "radius": 10.0,
            "effects": {
                "movement_multiplier": 0.7,
                "jump_height_multiplier": 0.6
            }
        },
        "Silence Mist": {
            "debuff_type": DebuffType.SILENCE,
            "radius": 7.0,
            "effects": {
                "skills_disabled": True,
                "basic_attacks_only": True
            }
        },
    }

    @classmethod
    def create_zone(cls, name: str, position: Tuple[float, float, float], 
                   duration: Optional[float] = None) -> Optional[DebuffZone]:
        """Create a debuff zone from template."""
        if name not in cls.ZONE_TEMPLATES:
            return None
        
        template = cls.ZONE_TEMPLATES[name]
        return DebuffZone(
            name=name,
            debuff_type=template["debuff_type"],
            position=position,
            radius=template["radius"],
            effects=template["effects"],
            duration=duration
        )

    @classmethod
    def list_zones(cls) -> List[str]:
        """List all available debuff zone templates."""
        return list(cls.ZONE_TEMPLATES.keys())
