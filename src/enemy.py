"""
Enemy class for Witch's Weapon combat system.
Represents enemies with health, states, and AI behavior.
"""

import random
from enum import Enum

class EnemyMobility(Enum):
    GROUND = "ground"
    JUMPER = "jumper"
    CLIMBER = "climber"
    FLYER = "flyer"
    TELEPORTER = "teleporter"

class Enemy:
    def __init__(self, name, health, ui_feedback, mobility: EnemyMobility = EnemyMobility.GROUND, position=None):
        self.name = name
        self.max_health = health
        self.health = health
        self.ui = ui_feedback
        self.state = "normal"  # normal, stunned, active, defeated
        self.mobility = mobility
        self.position = position or [5, 5, 0]
        self.nav_layers = ["ground"] if mobility == EnemyMobility.GROUND else ["ground", "air"]

    def take_damage(self, damage):
        # US: As an enemy, I want to take damage and change states accordingly.
        self.health -= damage
        if self.health <= 0:
            self.state = "defeated"
            self.ui.display_message(f"{self.name} defeated!")
        elif self.health < self.max_health * 0.5:
            self.state = "weakened"
            self.ui.display_message(f"{self.name} is weakened.")
        self.ui.display_message(f"{self.name} took {damage} damage. HP: {self.health}")

    def attack(self, player):
        # Simple AI attack
        if self.state != "defeated":
            damage = random.randint(5, 15)
            if self.mobility == EnemyMobility.FLYER:
                damage += 2
            player.take_damage(damage)
            self.ui.display_message(f"{self.name} attacked for {damage} damage.")

    def is_defeated(self):
        return self.health <= 0

    def get_navigation_layers(self):
        return self.nav_layers
