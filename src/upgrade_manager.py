"""
Upgrade Manager for Witch's Weapon.
Handles stat enhancements, breakthroughs, and materials.
"""

class UpgradeManager:
    def __init__(self, ui_feedback):
        self.ui = ui_feedback
        # US: Stat enhancement - using materials
        self.materials = {
            "Iron Ore": 10,
            "Magic Crystal": 5,
            "Rare Gem": 2
        }
        # Costs for enhancements
        self.enhancement_costs = {
            "HP": {"Iron Ore": 2, "Magic Crystal": 1},
            "ATK": {"Iron Ore": 1, "Magic Crystal": 2},
            "DEF": {"Iron Ore": 1, "Magic Crystal": 1, "Rare Gem": 1}
        }
        # US: Breakthrough system - raises level cap
        self.breakthrough_costs = {
            1: {"Rare Gem": 1},  # To raise cap to 30
            2: {"Rare Gem": 2},  # To 40
            3: {"Rare Gem": 3}   # To 50
        }
        self.breakthrough_level = 0  # How many breakthroughs done

    def enhance_stat(self, player, stat):
        # US: Stat enhancement - fixed increases with limits
        if stat not in self.enhancement_costs:
            self.ui.display_message("Invalid stat to enhance.")
            return False
        costs = self.enhancement_costs[stat]
        if not self.has_materials(costs):
            self.ui.display_message("Not enough materials.")
            return False
        self.consume_materials(costs)
        if stat == "HP":
            player.enhanced_hp += 20
            player.max_health = player.calculate_max_health()
            player.health = min(player.health, player.max_health)
        elif stat == "ATK":
            player.enhanced_atk += 5
        elif stat == "DEF":
            player.enhanced_def += 3
        self.ui.display_message(f"Enhanced {stat}. Materials consumed.")
        return True

    def breakthrough(self, player):
        # US: Breakthrough system - raises level cap
        if self.breakthrough_level >= len(self.breakthrough_costs):
            self.ui.display_message("Max breakthroughs reached.")
            return False
        costs = self.breakthrough_costs[self.breakthrough_level + 1]
        if not self.has_materials(costs):
            self.ui.display_message("Not enough materials for breakthrough.")
            return False
        self.consume_materials(costs)
        self.breakthrough_level += 1
        old_cap = player.max_level
        player.max_level += 10  # Raise cap by 10 each time
        self.ui.display_message(f"Breakthrough successful! Level cap raised from {old_cap} to {player.max_level}.")
        return True

    def enhance_weapon(self, weapon):
        # US: Stat enhancement for weapons
        costs = {"Iron Ore": 3, "Magic Crystal": 1}
        if not self.has_materials(costs):
            self.ui.display_message("Not enough materials to enhance weapon.")
            return False
        self.consume_materials(costs)
        if weapon.enhance_weapon():
            self.ui.display_message(f"Enhanced {weapon.name}.")
            return True
        return False

    def has_materials(self, costs):
        for mat, amt in costs.items():
            if self.materials.get(mat, 0) < amt:
                return False
        return True

    def consume_materials(self, costs):
        for mat, amt in costs.items():
            self.materials[mat] -= amt

    def add_materials(self, mat_dict):
        for mat, amt in mat_dict.items():
            self.materials[mat] = self.materials.get(mat, 0) + amt

    def get_materials(self):
        return self.materials.copy()