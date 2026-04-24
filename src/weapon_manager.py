"""
Weapon Manager for Witch's Weapon combat system.
Manages weapon slots, switching, and weapon data.
"""

import random
from enum import Enum

class Rarity(Enum):
    R = "R"
    SR = "SR"
    SSR = "SSR"

class Weapon:
    def __init__(self, name, damage, duration=0, rarity=Rarity.R):
        self.name = name
        self.base_damage = damage
        self.duration = duration  # For temporary weapons
        self.current_duration = duration
        self.rarity = rarity
        # US: Affection/Bond system - per-weapon affection levels
        self.affection = 0
        self.affection_level = 1
        self.affection_to_next = 50  # Base for level 2
        # US: Weapon synchronization bonuses
        self.atk_bonus = 0
        self.def_bonus = 0
        # US: Stat enhancement - fixed increases with limits
        self.enhanced_damage = 0
        self.enhancement_level = 0
        self.max_enhancement = 5

    def calculate_damage(self, player_atk=0):
        # US: As a weapon, I want damage calculation based on type and modifiers.
        # US: Weapon synchronization bonuses
        base = self.base_damage + self.enhanced_damage + player_atk
        return base + random.randint(0, 5)

    def gain_affection(self, amount):
        # US: Affection/Bond system - gain through usage
        self.affection += amount
        while self.affection >= self.affection_to_next and self.affection_level < 10:  # Max affection level 10
            self.affection_level_up()

    def affection_level_up(self):
        # US: Affection/Bond system - milestone rewards
        self.affection -= self.affection_to_next
        self.affection_level += 1
        self.affection_to_next = int(self.affection_to_next * 1.5)
        # Reward: increase bonuses
        self.atk_bonus += 1
        self.def_bonus += 1

    def enhance_weapon(self):
        # US: Stat enhancement - fixed stat increases
        if self.enhancement_level < self.max_enhancement:
            self.enhancement_level += 1
            self.enhanced_damage += 5
            return True
        else:
            return False

    def update_duration(self):
        if self.current_duration > 0:
            self.current_duration -= 1
            if self.current_duration == 0:
                return True  # Expired
        return False

class WeaponManager:
    def __init__(self):
        self.weapons = {
            "Basic Sword": Weapon("Basic Sword", 10, rarity=Rarity.R),
            "Magic Wand": Weapon("Magic Wand", 15, rarity=Rarity.SR),
            "Fire Staff": Weapon("Fire Staff", 20, duration=3, rarity=Rarity.SR)  # Temporary
        }
        self.slots = ["Basic Sword", "Magic Wand"]  # Available slots

    def has_weapon(self, name):
        return name in self.weapons

    def get_weapon(self, name):
        return self.weapons.get(name)

    def add_weapon(self, weapon):
        self.weapons[weapon.name] = weapon

    def update_durations(self):
        expired = []
        for name, weapon in self.weapons.items():
            if weapon.update_duration():
                expired.append(name)
        for name in expired:
            del self.weapons[name]