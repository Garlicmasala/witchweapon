"""
PvP Ruleset - Defines damage scaling and ability restrictions for PvP mode.
Prevents one-shot builds and ensures competitive integrity.
"""

class PvPRuleset:
    """Applies PvP-specific modifications to combat parameters."""
    
    def __init__(self):
        # Damage scaling multipliers (PvP vs PvE)
        self.pvp_damage_multiplier = 0.75  # 25% damage reduction in PvP
        self.skill_damage_multiplier = 0.8  # Skills do 80% of normal damage
        
        # Crowd control limits
        self.cc_diminishing_returns_threshold = 3  # After 3 CC effects, reduced duration
        self.cc_diminishing_returns_multiplier = 0.6  # Subsequent CC is 60% effective
        
        # Ability restrictions
        self.flight_stamina_limit = 15.0  # Max 15s continuous flight
        self.flight_stamina_per_second = 1.0  # 1% stamina per second
        self.summon_limit = 2  # Max 2 summons at once
        
        # PvP stat caps (prevent extreme min-maxing)
        self.max_crit_chance = 0.5  # Max 50% crit chance
        self.max_dodge_chance = 0.4  # Max 40% dodge chance
        
        # Buff stacking rules
        self.buff_stack_limit = 1  # Can't stack same buff twice
        self.buff_pickup_cooldown = 5.0  # 5s before same player can pickup again

    def apply_damage_scaling(self, base_damage, damage_type="attack"):
        """
        Apply PvP damage scaling.
        
        Args:
            base_damage: Raw damage value
            damage_type: "attack", "skill", or "ultimate"
        
        Returns:
            PvP-adjusted damage
        """
        if damage_type == "skill":
            return int(base_damage * self.pvp_damage_multiplier * self.skill_damage_multiplier)
        elif damage_type == "ultimate":
            return int(base_damage * self.pvp_damage_multiplier)  # Ultimates get normal scaling
        else:  # attack
            return int(base_damage * self.pvp_damage_multiplier)

    def validate_cc_effect(self, target, cc_active_count, original_duration):
        """
        Calculate CC duration with diminishing returns.
        
        Args:
            target: Target character
            cc_active_count: Number of CC effects already active
            original_duration: Base CC duration
        
        Returns:
            Adjusted duration, or 0 to prevent CC
        """
        if cc_active_count >= self.cc_diminishing_returns_threshold:
            # Start reducing effectiveness
            reduction = 0.5 ** (cc_active_count - self.cc_diminishing_returns_threshold)
            return max(1, int(original_duration * reduction))
        return original_duration

    def validate_flight(self, current_stamina, stamina_drain=1.0):
        """
        Check if flight can continue (stamina-based limit).
        
        Args:
            current_stamina: Current flight stamina (0-100)
            stamina_drain: Stamina drained per second
        
        Returns:
            Boolean if flight can continue
        """
        return current_stamina > 0

    def validate_summon(self, active_summons):
        """Check if another summon can be created."""
        return len(active_summons) < self.summon_limit

    def get_stat_cap(self, stat_type):
        """Get the maximum value for a stat."""
        if stat_type == "crit_chance":
            return self.max_crit_chance
        elif stat_type == "dodge_chance":
            return self.max_dodge_chance
        return None

    def to_dict(self):
        """Serialize ruleset for network sync."""
        return {
            "pvp_damage_multiplier": self.pvp_damage_multiplier,
            "skill_damage_multiplier": self.skill_damage_multiplier,
            "cc_diminishing_returns_threshold": self.cc_diminishing_returns_threshold,
            "flight_stamina_limit": self.flight_stamina_limit,
            "summon_limit": self.summon_limit,
            "max_crit_chance": self.max_crit_chance,
            "max_dodge_chance": self.max_dodge_chance,
        }
