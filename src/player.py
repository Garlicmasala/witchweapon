"""
Player class for Witch's Weapon combat system.
Handles movement, weapon management, skills, combat actions, and interactions.
"""

from .player_movement import PlayerMovement

class Player:
    def __init__(self, weapon_manager, skill_system, ui_feedback, currency_manager, appearance_manager):
        self.weapon_manager = weapon_manager
        self.skill_system = skill_system
        self.ui = ui_feedback
        self.currency_manager = currency_manager
        self.appearance_manager = appearance_manager
        self.name = "Player"  # For dialogue
        self.movement = PlayerMovement(ui_feedback)
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100  # Base exp for level 2
        self.max_level = 20  # Initial level cap
        self.base_hp = 100
        self.base_atk = 10
        self.base_def = 5
        self.enhanced_hp = 0
        self.enhanced_atk = 0
        self.enhanced_def = 0
        self.max_health = self.calculate_max_health()
        self.health = self.max_health
        self.mana = 50
        self.current_weapon = None
        self.skills = ["Fireball", "Heal"]  # Example skills
        self.ultimate_cooldown = 0
        self.switch_weapon("Basic Sword")  # Default weapon
        # New for Epic 9
        self.dialogue_state = None  # Active dialogue ID
        self.interaction_cooldown = 0

    @property
    def position(self):
        return self.movement.get_position()

    @property
    def atk(self):
        # US: Character level progression - stat scaling
        weapon_bonus = self.current_weapon.atk_bonus if self.current_weapon else 0
        appearance_mods = self.appearance_manager.get_combat_modifiers("PvE") if self.appearance_manager else {}
        appearance_bonus = appearance_mods.get("ATK", 0)
        return self.base_atk + (self.level - 1) * 2 + self.enhanced_atk + weapon_bonus + appearance_bonus

    @property
    def defense(self):
        # US: Character level progression - stat scaling
        weapon_bonus = self.current_weapon.def_bonus if self.current_weapon else 0
        appearance_mods = self.appearance_manager.get_combat_modifiers("PvE") if self.appearance_manager else {}
        appearance_bonus = appearance_mods.get("DEF", 0)
        return self.base_def + (self.level - 1) * 1 + self.enhanced_def + weapon_bonus + appearance_bonus

    def calculate_max_health(self):
        # US: Character level progression - stat scaling
        return self.base_hp + (self.level - 1) * 10 + self.enhanced_hp

    def gain_exp(self, amount):
        # US: Character level progression - EXP gain
        self.exp += amount
        self.ui.display_message(f"Gained {amount} EXP. Total: {self.exp}/{self.exp_to_next}")
        while self.exp >= self.exp_to_next and self.level < self.max_level:
            self.level_up()

    def level_up(self):
        # US: Character level progression - level-ups
        self.exp -= self.exp_to_next
        self.level += 1
        self.exp_to_next = int(self.exp_to_next * 1.2)  # Increase exp requirement
        old_max_health = self.max_health
        self.max_health = self.calculate_max_health()
        self.health += (self.max_health - old_max_health)  # Heal on level up
        self.ui.display_message(f"Level up! Now level {self.level}. HP restored by {self.max_health - old_max_health}.")

    def move(self, direction):
        self.movement.move(direction)

    def switch_weapon(self, weapon_name):
        # US: As a player, I want to switch weapons to adapt to different combat situations.
        if self.weapon_manager.has_weapon(weapon_name):
            self.current_weapon = self.weapon_manager.get_weapon(weapon_name)
            self.ui.display_message(f"Switched to weapon: {weapon_name}")
        else:
            self.ui.display_message(f"Weapon {weapon_name} not available.")

    def auto_attack(self, enemy):
        # US: As a player, I want auto-attack to deal damage automatically when in range.
        if self.current_weapon:
            damage = self.current_weapon.calculate_damage(self.atk)
            enemy.take_damage(damage)
            self.ui.display_message(f"Auto-attacked for {damage} damage.")
            # Gain affection for weapon usage
            old_level = self.current_weapon.affection_level
            self.current_weapon.gain_affection(1)
            if self.current_weapon.affection_level > old_level:
                self.ui.display_message(f"{self.current_weapon.name} affection level up to {self.current_weapon.affection_level}! ATK +1, DEF +1.")

    def use_skill(self, skill_name, enemy):
        # US: As a player, I want to use skills for special abilities.
        skill = self.skill_system.get_skill(skill_name)
        if skill and skill.can_use(self.mana):
            self.mana -= skill.mana_cost
            damage = skill.damage
            if damage > 0:
                enemy.take_damage(damage)
            else:
                self.health = min(self.max_health, self.health - damage)  # Heal
            skill.use()
            self.ui.display_message(f"Used skill {skill_name} for {damage} damage.")
        else:
            self.ui.display_message("Cannot use skill.")

    def use_ultimate(self, enemy):
        # US: As a player, I want to use ultimate abilities for powerful effects.
        if self.ultimate_cooldown == 0 and self.mana >= 30:
            self.mana -= 30
            damage = 50 + self.atk  # Scale with ATK
            enemy.take_damage(damage)
            self.ultimate_cooldown = 5  # Turns
            self.ui.display_message(f"Used ultimate for {damage} damage.")
        else:
            self.ui.display_message("Ultimate not ready.")

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        if self.health <= 0:
            self.ui.display_message("Player defeated!")

    def update_cooldowns(self):
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= 1
        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= 1

    def start_dialogue(self, dialogue_id):
        """Start a dialogue."""
        self.dialogue_state = dialogue_id

    def end_dialogue(self):
        """End active dialogue."""
        self.dialogue_state = None

    def can_interact(self):
        """Check if player can interact (cooldown)."""
        return self.interaction_cooldown == 0

    def interact(self, target):
        """Interact with a target (companion, NPC)."""
        if self.can_interact():
            target.interact(self)
            self.interaction_cooldown = 5  # 5 turns cooldown
        else:
            self.ui.display_message("Interaction on cooldown.")