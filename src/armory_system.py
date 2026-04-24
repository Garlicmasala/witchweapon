"""
Armory System for Witch's Weapon.
Handles functional gear with PvE/PvP stat rules.
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional
from .weapon_manager import Rarity

class ArmorySlotType(Enum):
    HELMET = "Helmet"
    CHEST = "Chest"
    GLOVES = "Gloves"
    BOOTS = "Boots"
    ACCESSORY = "Accessory"

class ArmoryItem:
    def __init__(self, name: str, slot: ArmorySlotType, rarity: Rarity, pve_stats: Dict[str, float], pvp_stats: Dict[str, float], description: str = ""):
        self.name = name
        self.slot = slot
        self.rarity = rarity
        self.pve_stats = pve_stats.copy()
        self.pvp_stats = pvp_stats.copy()
        self.description = description

    def get_stats_for_context(self, context: str) -> Dict[str, float]:
        if context == "PvP":
            return self.pvp_stats
        else:
            return self.pve_stats

    def to_dict(self):
        return {
            "name": self.name,
            "slot": self.slot.name,
            "rarity": self.rarity.name,
            "pve_stats": self.pve_stats,
            "pvp_stats": self.pvp_stats,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            ArmorySlotType[data["slot"]],
            Rarity[data["rarity"]],
            data["pve_stats"],
            data["pvp_stats"],
            data.get("description", "")
        )

class ArmorySystem:
    def __init__(self):
        self.owned_items: Dict[str, ArmoryItem] = {}
        self.equipped: Dict[ArmorySlotType, str] = {}
        self.initialize_default_armory()

    def initialize_default_armory(self):
        self.owned_items.clear()
        self.equipped.clear()

        # Default items
        self.add_item(ArmoryItem(
            "Leather Cap",
            ArmorySlotType.HELMET,
            Rarity.R,
            {"DEF": 5, "HP": 10},
            {"DEF": 3, "HP": 5},
            "Basic leather head protection."
        ))
        self.add_item(ArmoryItem(
            "Cloth Tunic",
            ArmorySlotType.CHEST,
            Rarity.R,
            {"DEF": 8, "HP": 15},
            {"DEF": 5, "HP": 8},
            "Simple cloth armor for the torso."
        ))
        self.add_item(ArmoryItem(
            "Leather Gloves",
            ArmorySlotType.GLOVES,
            Rarity.R,
            {"ATK": 3, "DEF": 2},
            {"ATK": 2, "DEF": 1},
            "Basic hand protection."
        ))
        self.add_item(ArmoryItem(
            "Boots",
            ArmorySlotType.BOOTS,
            Rarity.R,
            {"DEF": 4, "HP": 8},
            {"DEF": 2, "HP": 4},
            "Sturdy footwear."
        ))
        self.add_item(ArmoryItem(
            "Ring",
            ArmorySlotType.ACCESSORY,
            Rarity.R,
            {"ATK": 2, "DEF": 2},
            {"ATK": 1, "DEF": 1},
            "A simple accessory."
        ))

        # Equip defaults
        for slot in ArmorySlotType:
            default_name = self.get_default_item_name(slot)
            if default_name:
                self.equipped[slot] = default_name

    def get_default_item_name(self, slot: ArmorySlotType) -> Optional[str]:
        defaults = {
            ArmorySlotType.HELMET: "Leather Cap",
            ArmorySlotType.CHEST: "Cloth Tunic",
            ArmorySlotType.GLOVES: "Leather Gloves",
            ArmorySlotType.BOOTS: "Boots",
            ArmorySlotType.ACCESSORY: "Ring"
        }
        return defaults.get(slot)

    def add_item(self, item: ArmoryItem):
        self.owned_items[item.name] = item

    def equip_item(self, name: str) -> bool:
        item = self.owned_items.get(name)
        if not item:
            return False
        self.equipped[item.slot] = name
        return True

    def get_equipped_item(self, slot: ArmorySlotType) -> Optional[ArmoryItem]:
        name = self.equipped.get(slot)
        return self.owned_items.get(name) if name else None

    def get_total_stats(self, context: str) -> Dict[str, float]:
        total = {"HP": 0, "ATK": 0, "DEF": 0}
        for slot in ArmorySlotType:
            item = self.get_equipped_item(slot)
            if item:
                stats = item.get_stats_for_context(context)
                for stat, value in stats.items():
                    total[stat] += value
        return total

    def get_equipped_summary(self, context: str) -> Tuple[str, Dict[str, float]]:
        equipped_names = [f"{slot.value}: {self.equipped.get(slot, 'None')}" for slot in ArmorySlotType]
        summary = " | ".join(equipped_names)
        modifiers = self.get_total_stats(context)
        return summary, modifiers

    def get_armory_state(self) -> Dict:
        return {
            "owned": {name: item.to_dict() for name, item in self.owned_items.items()},
            "equipped": {slot.name: name for slot, name in self.equipped.items()}
        }

    def load_armory_state(self, state: Dict):
        self.owned_items.clear()
        owned = state.get("owned", {})
        for name, item_data in owned.items():
            item = ArmoryItem.from_dict(item_data)
            self.add_item(item)
        self.equipped = {
            ArmorySlotType[slot_name]: item_name
            for slot_name, item_name in state.get("equipped", {}).items()
        }
