"""
Skill System for Witch's Weapon combat system.
Manages skills, cooldowns, and effects.
"""

class Skill:
    def __init__(self, name, damage, mana_cost, cooldown):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.current_cooldown = 0

    def can_use(self, mana):
        return self.current_cooldown == 0 and mana >= self.mana_cost

    def use(self):
        self.current_cooldown = self.cooldown

    def update_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class SkillSystem:
    def __init__(self):
        self.skills = {
            "Fireball": Skill("Fireball", 25, 10, 2),
            "Heal": Skill("Heal", -20, 15, 3)  # Negative damage for heal
        }

    def get_skill(self, name):
        return self.skills.get(name)

    def update_cooldowns(self):
        for skill in self.skills.values():
            skill.update_cooldown()