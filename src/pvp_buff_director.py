"""
PvP Buff Director - Manages spawn timing, pickup, and lifecycle of buffs/debuffs.
Handles spawn rules, buff availability, and anti-stacking.
"""

import time
import random
from typing import Dict, List, Optional, Tuple
from .pvp_buff_system import Buff, BuffRegistry, DebuffZone, DebuffZoneRegistry, BuffType
from .pvp_arena import Arena


class BuffSpawnRules:
    """Configurable spawn timing and rules."""
    
    def __init__(self, mode: str = "free"):
        self.mode = mode  # "free" or "ladder"
        
        if mode == "free":
            self.spawn_interval_min = 30  # 30-45s between spawns
            self.spawn_interval_max = 45
            self.buff_density = 3  # More buffs active
        else:  # ladder
            self.spawn_interval_min = 60  # 60-90s between spawns
            self.spawn_interval_max = 90
            self.buff_density = 2  # Fewer, more tactical
        
        self.max_active_buffs = self.buff_density
        self.buff_stack_limit = 1  # Can't have same buff twice
        self.pickup_cooldown = 5.0  # Seconds before player can pickup same buff again


class BuffDirector:
    """Orchestrates buff spawning and management during a match."""
    
    def __init__(self, arena: Arena, mode: str = "free"):
        self.arena = arena
        self.mode = mode
        self.rules = BuffSpawnRules(mode)
        
        # Active buffs on the map
        self.active_buffs: Dict[str, Buff] = {}  # buff_id -> Buff
        self.buff_counter = 0  # For generating unique IDs
        
        # Track player buff pickup history
        self.player_buff_pickups: Dict[str, Dict[str, float]] = {}  # player -> {buff_name: time_picked}
        
        # Spawn timing
        self.last_spawn_time = time.time()
        self.next_spawn_time = self.last_spawn_time + random.uniform(
            self.rules.spawn_interval_min, 
            self.rules.spawn_interval_max
        )
        
        # Debuff zones
        self.debuff_zones: Dict[str, DebuffZone] = {}  # zone_id -> DebuffZone
        self.debuff_counter = 0
        
        # Initialize static debuff zones
        self._spawn_initial_debuff_zones()

    def _spawn_initial_debuff_zones(self):
        """Create permanent debuff zones at fixed locations."""
        for position in self.arena.get_debuff_zone_locations():
            zone_name = random.choice(DebuffZoneRegistry.list_zones())
            zone = DebuffZoneRegistry.create_zone(zone_name, position, duration=None)
            if zone:
                zone_id = f"debuff_{self.debuff_counter}"
                self.debuff_zones[zone_id] = zone
                self.debuff_counter += 1

    def update(self, current_time: float, losing_team_boost: bool = False):
        """
        Main update loop - called each frame.
        
        Args:
            current_time: Current match time
            losing_team_boost: If True, spawn buffs closer to losing team
        """
        # Remove expired buffs
        self._cleanup_expired_buffs()
        self._cleanup_expired_debuff_zones()
        
        # Spawn new buffs if needed
        if current_time >= self.next_spawn_time:
            self._spawn_buff(losing_team_boost)
            self.next_spawn_time = current_time + random.uniform(
                self.rules.spawn_interval_min,
                self.rules.spawn_interval_max
            )

    def _cleanup_expired_buffs(self):
        """Remove buffs that have expired."""
        expired_ids = []
        for buff_id, buff in self.active_buffs.items():
            if buff.is_expired():
                expired_ids.append(buff_id)
        
        for buff_id in expired_ids:
            del self.active_buffs[buff_id]

    def _cleanup_expired_debuff_zones(self):
        """Remove debuff zones that have timed out."""
        expired_ids = []
        for zone_id, zone in self.debuff_zones.items():
            if zone.is_expired():
                expired_ids.append(zone_id)
        
        for zone_id in expired_ids:
            del self.debuff_zones[zone_id]

    def _spawn_buff(self, losing_team_boost: bool = False):
        """Spawn a new buff if we haven't hit the limit."""
        if len(self.active_buffs) >= self.rules.max_active_buffs:
            return  # Too many active already
        
        # Choose buff type (weighted towards mobility/offensive in free mode)
        buff_type_weights = {
            BuffType.MOBILITY: 0.4,
            BuffType.OFFENSIVE: 0.4,
            BuffType.DEFENSIVE: 0.2,
        }
        buff_type = random.choices(
            list(buff_type_weights.keys()),
            weights=list(buff_type_weights.values())
        )[0]
        
        # Get random buff of that type
        buff = BuffRegistry.get_random_buff(buff_type)
        if not buff:
            return
        
        # Choose spawn location
        spawn_zones = self.arena.get_buff_spawn_zones()
        if not spawn_zones:
            return
        
        spawn_position = random.choice(spawn_zones)
        if losing_team_boost:
            # Slightly randomize position to favor losing team (can be implemented)
            pass
        
        # Generate unique ID
        buff_id = f"buff_{self.buff_counter}"
        self.buff_counter += 1
        
        buff.spawned_time = time.time()
        self.active_buffs[buff_id] = buff

    def pickup_buff(self, player_name: str, buff_id: str) -> Tuple[bool, str]:
        """
        Attempt to pick up a buff.
        
        Args:
            player_name: Name of player picking up
            buff_id: ID of buff to pick up
        
        Returns:
            (success, message)
        """
        if buff_id not in self.active_buffs:
            return False, "Buff not found or already claimed"
        
        buff = self.active_buffs[buff_id]
        
        if buff.claimed_by is not None:
            return False, f"{buff.claimed_by} already claimed this buff"
        
        # Check pickup cooldown
        if player_name not in self.player_buff_pickups:
            self.player_buff_pickups[player_name] = {}
        
        pickups = self.player_buff_pickups[player_name]
        if buff.name in pickups:
            time_since_pickup = time.time() - pickups[buff.name]
            if time_since_pickup < self.rules.pickup_cooldown:
                return False, f"Can't pick up {buff.name} again for {self.rules.pickup_cooldown - time_since_pickup:.1f}s"
        
        # All checks passed - claim the buff
        buff.claim(player_name)
        pickups[buff.name] = time.time()
        return True, f"Picked up {buff.name}!"

    def apply_buff_effects(self, player, buff: Buff) -> Dict:
        """
        Apply buff effects to a player.
        Returns dict of applied effects for UI/logging.
        """
        applied_effects = {}
        
        for effect_key, effect_value in buff.effects.items():
            if effect_key == "jump_height_multiplier":
                applied_effects["jump_height"] = effect_value
            elif effect_key == "air_control_multiplier":
                applied_effects["air_control"] = effect_value
            elif effect_key == "skill_damage_multiplier":
                applied_effects["skill_damage"] = effect_value
            elif effect_key == "shield_amount":
                if hasattr(player, "shield"):
                    player.shield = effect_value
                applied_effects["shield"] = effect_value
            elif effect_key == "hp_regen_per_second":
                applied_effects["regen"] = effect_value
            elif effect_key == "damage_multiplier":
                applied_effects["damage_mod"] = effect_value
            # Add more effect applications as needed
        
        return applied_effects

    def get_debuff_at_position(self, position: Tuple[float, float, float]) -> Optional[DebuffZone]:
        """Get debuff zone affecting this position."""
        for zone in self.debuff_zones.values():
            if zone.is_affecting(position):
                return zone
        return None

    def get_active_buffs(self) -> List[Dict]:
        """Get serialized list of active buffs for UI."""
        return [buff.to_dict() for buff in self.active_buffs.values()]

    def get_debuff_zones(self) -> List[Dict]:
        """Get serialized list of debuff zones for UI."""
        return [zone.to_dict() for zone in self.debuff_zones.values()]

    def get_buff_status(self, player_name: str) -> Dict[str, float]:
        """Get duration remaining on all buffs for a player."""
        status = {}
        for buff in self.active_buffs.values():
            if buff.claimed_by == player_name:
                status[buff.name] = buff.get_remaining_duration()
        return status

    def to_dict(self) -> Dict:
        """Serialize buff states for network sync."""
        return {
            "active_buffs": {bid: buff.to_dict() for bid, buff in self.active_buffs.items()},
            "debuff_zones": {zid: zone.to_dict() for zid, zone in self.debuff_zones.items()},
            "next_spawn_time": self.next_spawn_time,
        }
