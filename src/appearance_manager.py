"""
Appearance Manager for Witch's Weapon.
Unified manager for armory, weaponry, fashion layers.
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional
from .armory_system import ArmorySystem, ArmorySlotType
from .fashion_system import FashionSystem, FashionCategory
from .weapon_customization import WeaponCustomization
from .wardrobe_menu import WardrobeMenu, PreviewContext

class AppearanceCategory(Enum):
    WEAPON_SKIN = "Weapon Skin"
    OUTFIT = "Outfit"
    ACCESSORY = "Accessory"

class AppearanceManager:
    def __init__(self, ui_feedback):
        self.ui = ui_feedback
        self.armory_system = ArmorySystem()
        self.fashion_system = FashionSystem()
        self.weapon_system = WeaponCustomization()
        self.wardrobe_menu = WardrobeMenu(
            self.armory_system,
            self.fashion_system,
            self.weapon_system,
            ui_feedback
        )
        self.preview_context = PreviewContext.PVE

    def show_wardrobe_menu(self):
        self.wardrobe_menu.show_menu()

    def set_preview_context(self, context: str):
        try:
            self.preview_context = PreviewContext(context)
            self.wardrobe_menu.preview_context = self.preview_context
        except ValueError:
            pass

    def get_current_weapon_identity(self, weapon_name: str):
        return self.weapon_system.get_weapon_identity(weapon_name)

    def get_armory_loadout(self):
        return self.armory_system.get_equipped_summary(self.preview_context.value)

    def get_fashion_equipped(self):
        return self.fashion_system.get_equipped_summary()

    def get_available_armory_slots(self):
        return list(ArmorySlotType)

    def add_cosmetic_from_gacha(self, banner_item):
        # Add to appropriate system based on category
        if banner_item.item_category in ["weapon", "weapon_skin"]:
            # For now, add as weapon skin
            from .weapon_customization import WeaponSkin, WeaponSkinType
            from .weapon_manager import Rarity
            skin = WeaponSkin(
                banner_item.name,
                WeaponSkinType.SKIN,
                banner_item.rarity,
                banner_item.bonuses,
                banner_item.description
            )
            # Assume for current weapon or generic
            self.weapon_system.add_weapon_skin("Sword", skin)  # Default to Sword
        elif banner_item.item_category in ["outfit", "accessory", "cosmetic"]:
            # Add to fashion
            cat_map = {
                "outfit": FashionCategory.OUTFIT,
                "accessory": FashionCategory.ACCESSORY,
                "cosmetic": FashionCategory.EFFECT
            }
            category = cat_map.get(banner_item.item_category, FashionCategory.ACCESSORY)
            from .fashion_system import FashionItem
            item = FashionItem(
                banner_item.name,
                category,
                banner_item.rarity,
                banner_item.bonuses,
                banner_item.description
            )
            self.fashion_system.add_item(item)
        # Armory items would come from other sources

    def to_dict(self):
        return {
            "armory": self.armory_system.get_armory_state(),
            "fashion": self.fashion_system.get_fashion_state(),
            "weapons": self.weapon_system.get_weapon_state(),
            "preview_context": self.preview_context.name
        }

    def load_from_dict(self, data):
        if "armory" in data:
            self.armory_system.load_armory_state(data["armory"])
        if "fashion" in data:
            self.fashion_system.load_fashion_state(data["fashion"])
        if "weapons" in data:
            self.weapon_system.load_weapon_state(data["weapons"])
        if "preview_context" in data:
            self.set_preview_context(data["preview_context"])

    # Legacy methods for compatibility
    def add_item(self, item):
        # Assume fashion item for legacy
        self.fashion_system.add_item(item)

    def has_item(self, name):
        return (name in self.fashion_system.owned_items or
                name in self.armory_system.owned_items or
                any(name in skins for skins in self.weapon_system.weapon_skins.values()))

    def get_item(self, name):
        if name in self.fashion_system.owned_items:
            return self.fashion_system.owned_items[name]
        return None

    def equip_item(self, name):
        if self.fashion_system.equip_item(name):
            return True
        return False

    def get_equipped_name(self, category):
        if isinstance(category, str):
            # Legacy
            return "None"
        return "None"

    def get_total_bonus(self, stat_name):
        # Simplified
        armory_mods = self.armory_system.get_total_stats(self.preview_context.value)
        fashion_bonuses = self.fashion_system.get_synergy_bonuses()
        total = armory_mods.get(stat_name, 0) + fashion_bonuses.get(f"synergy_{stat_name.lower()}", 0)
        return total

    def get_inventory_summary(self):
        summary = {}
        for cat in FashionCategory:
            summary[cat.value] = [item.name for item in self.fashion_system.get_items_by_category(cat)]
        return summary
