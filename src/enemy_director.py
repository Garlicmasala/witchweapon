"""
Enemy Director for Witch's Weapon PvE world.
Manages enemy activation and spawn logic based on combat cells.
"""

from enum import Enum
from typing import List, Tuple
from .enemy import Enemy
from .combat_cell import CombatCell
from .player import Player

class EnemyMobility(Enum):
    GROUND = "ground"
    JUMPER = "jumper"
    CLIMBER = "climber"
    FLYER = "flyer"
    TELEPORTER = "teleporter"

class EnemyDirector:
    """Controls enemy activation, spawning, and area-based engagement."""
    
    def __init__(self, ui_feedback):
        self.ui = ui_feedback
        self.enemies: List[Enemy] = []
        self.cell_assignments = {}  # CombatCell -> List[Enemy]
        self.active_cell = None
    
    def assign_enemies_to_cell(self, cell: CombatCell, enemies: List[Enemy]):
        self.cell_assignments[cell] = enemies
        self.ui.display_message(f"[EnemyDirector] Assigned {len(enemies)} enemies to {cell.cell_id}")
    
    def on_player_enter_cell(self, cell: CombatCell, player: Player):
        if self.active_cell == cell:
            return
        if cell in self.cell_assignments:
            self.active_cell = cell
            enemies = self.cell_assignments[cell]
            for enemy in enemies:
                enemy.state = "active"
                self.ui.display_message(f"[EnemyDirector] Enemy {enemy.name} activated in cell {cell.cell_id}")
    
    def update_enemies(self, player: Player, delta_time: float = 1.0):
        if not self.active_cell:
            return
        enemies = self.cell_assignments.get(self.active_cell, [])
        for enemy in enemies:
            if enemy.is_defeated():
                continue
            self._update_enemy_behavior(enemy, player, delta_time)
            if self.active_cell.should_exit({"player_alive": player.health > 0}):
                self.active_cell.deactivate()
                self.active_cell = None
    
    def _update_enemy_behavior(self, enemy: Enemy, player: Player, delta_time: float):
        if enemy.state != "active":
            return
        if enemy.mobility == EnemyMobility.FLYER:
            self.ui.display_message(f"[EnemyDirector] {enemy.name} is hovering and engaging aerially.")
        elif enemy.mobility == EnemyMobility.CLIMBER:
            self.ui.display_message(f"[EnemyDirector] {enemy.name} is climbing to maintain height advantage.")
        elif enemy.mobility == EnemyMobility.JUMPER:
            self.ui.display_message(f"[EnemyDirector] {enemy.name} is making sudden vertical jumps.")
        enemy.attack(player)
    
    def clear_cell(self, cell: CombatCell):
        if cell in self.cell_assignments:
            for enemy in self.cell_assignments[cell]:
                enemy.state = "defeated"
            cell.clear()
            self.ui.display_message(f"[EnemyDirector] Cell {cell.cell_id} cleared.")
