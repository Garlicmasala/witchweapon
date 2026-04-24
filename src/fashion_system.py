"""
Fashion System for Witch's Weapon.
Handles pure visual overrides with synergy bonuses.
"""

from enum import Enum
from typing import Dict, List, Optional
from .weapon_manager import Rarity

class FashionCategory(Enum):
    OUTFIT = "Outfit"
    ACCESSORY = "Accessory"
    EFFECT = "Effect"

class FashionItem:
    def __init__(self, name: str, category: FashionCategory, rarity: Rarity, synergy_bonuses: Dict[str, float], description: str = "", visual_overrides: Dict[str, str] = None):
        self.name = name
        self.category = category
        self.rarity = rarity
        self.synergy_bonuses = synergy_bonuses.copy()
        self.description = description
        self.visual_overrides = visual_overrides or {}

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category.name,
            "rarity": self.rarity.name,
            "synergy_bonuses": self.synergy_bonuses,
            "description": self.description,
            "visual_overrides": self.visual_overrides
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            FashionCategory[data["category"]],
            Rarity[data["rarity"]],
            data["synergy_bonuses"],
            data.get("description", ""),
            data.get("visual_overrides", {})
        )

class FashionSystem:
    def __init__(self):
        self.owned_items: Dict[str, FashionItem] = {}
        self.equipped: Dict[FashionCategory, str] = {}
        self.initialize_default_fashion()

    def initialize_default_fashion(self):
        self.owned_items.clear()
        self.equipped.clear()

        # Default fashion items
        self.add_item(FashionItem(
            "Witch's Robe",
            FashionCategory.OUTFIT,
            Rarity.R,
            {"synergy_def": 5},
            "Classic witch attire.",
            {"robe_color": "black", "robe_style": "flowing"}
        ))
        self.add_item(FashionItem(
            "Crystal Pendant",
            FashionCategory.ACCESSORY,
            Rarity.R,
            {"synergy_atk": 3},
            "A glowing crystal accessory.",
            {"pendant_glow": "blue"}
        ))
        self.add_item(FashionItem(
            "Sparkle Effect",
            FashionCategory.EFFECT,
            Rarity.R,
            {"synergy_hp": 10},
            "Magical sparkles around the character.",
            {"particle_effect": "sparkles"}
        ))

        # Equip defaults
        self.equipped = {
            FashionCategory.OUTFIT: "Witch's Robe",
            FashionCategory.ACCESSORY: "Crystal Pendant",
            FashionCategory.EFFECT: "Sparkle Effect"
        }

    def add_item(self, item: FashionItem):
        self.owned_items[item.name] = item

    def equip_item(self, name: str) -> bool:
        item = self.owned_items.get(name)
        if not item:
            return False
        self.equipped[item.category] = name
        return True

    def get_equipped_item(self, category: FashionCategory) -> Optional[FashionItem]:
        name = self.equipped.get(category)
        return self.owned_items.get(name) if name else None

    def get_equipped_summary(self) -> str:
        equipped_names = [f"{cat.value}: {self.equipped.get(cat, 'None')}" for cat in FashionCategory]
        return " | ".join(equipped_names)

    def get_synergy_bonuses(self) -> Dict[str, float]:
        total = {}
        for item in self.owned_items.values():
            if self.equipped.get(item.category) == item.name:
                for bonus, value in item.synergy_bonuses.items():
                    total[bonus] = total.get(bonus, 0) + value
        return total

    def get_visual_overrides(self) -> Dict[str, str]:
        overrides = {}
        for item in self.owned_items.values():
            if self.equipped.get(item.category) == item.name:
                overrides.update(item.visual_overrides)
        return overrides

    def get_fashion_state(self) -> Dict:
        return {
            "owned": {name: item.to_dict() for name, item in self.owned_items.items()},
            "equipped": {cat.name: name for cat, name in self.equipped.items()}
        }

    def load_fashion_state(self, state: Dict):
        self.owned_items.clear()
        owned = state.get("owned", {})
        for name, item_data in owned.items():
            item = FashionItem.from_dict(item_data)
            self.add_item(item)
        self.equipped = {
            FashionCategory[cat_name]: item_name
            for cat_name, item_name in state.get("equipped", {}).items()
        }
