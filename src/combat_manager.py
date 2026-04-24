"""
Combat Manager for Witch's Weapon combat system.
Orchestrates combat between player and enemies.
"""

class CombatManager:
    def __init__(self, player, enemy, ui_feedback, upgrade_manager=None):
        self.player = player
        self.enemy = enemy
        self.ui = ui_feedback
        self.upgrade_manager = upgrade_manager
        self.battle_ended = False

    def auto_attack(self):
        # US: As a combat system, I want auto-attack to trigger when in range.
        distance = self.calculate_distance()
        if distance <= 2:  # In range
            self.player.auto_attack(self.enemy)
        else:
            self.ui.display_message("Enemy out of range for auto-attack.")

    def calculate_distance(self):
        # Simple distance
        dx = self.player.position[0] - self.enemy.position[0]
        dy = self.player.position[1] - self.enemy.position[1]
        return (dx**2 + dy**2)**0.5

    def is_battle_over(self):
        if self.enemy.is_defeated() and not self.battle_ended:
            self.battle_ended = True
            exp_gain = 50  # Example exp for defeating enemy
            self.player.gain_exp(exp_gain)
            if self.upgrade_manager:
                self.upgrade_manager.add_materials({"Iron Ore": 2, "Magic Crystal": 1})  # Example materials
                self.ui.display_message("Gained materials from battle.")
        return self.player.health <= 0 or self.enemy.is_defeated()

    def update_turn(self):
        # Update cooldowns, durations, etc.
        self.player.update_cooldowns()
        self.player.weapon_manager.update_durations()
        self.player.skill_system.update_cooldowns()