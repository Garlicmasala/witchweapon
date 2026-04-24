"""
Wardrobe Menu for Witch's Weapon.
UI for the unified Combat Wardrobe screen.
"""

from enum import Enum
from typing import Dict, List, Optional
from .armory_system import ArmorySlotType
from .fashion_system import FashionCategory
from .weapon_customization import WeaponSkinType

class PreviewContext(Enum):
    PVE = "PvE"
    PVP = "PvP"

class WardrobeMenu:
    def __init__(self, armory_system, fashion_system, weapon_system, ui_feedback, daily_mission_manager=None):
        self.armory = armory_system
        self.fashion = fashion_system
        self.weapon = weapon_system
        self.ui = ui_feedback
        self.daily_mission_manager = daily_mission_manager
        self.preview_context = PreviewContext.PVE

    def show_menu(self):
        while True:
            self.display_main_menu()
            choice = input("Choose: ").strip()
            if choice == "1":
                self.show_armory_section()
            elif choice == "2":
                self.show_fashion_section()
            elif choice == "3":
                self.show_weapon_skins_section()
            elif choice == "4":
                self.toggle_preview_context()
            elif choice == "5":
                self.show_preview()
            elif choice == "6":
                break
            else:
                self.ui.display_message("Invalid choice.")

    def display_main_menu(self):
        self.ui.display_message("--- Combat Wardrobe ---")
        self.ui.display_message(f"Preview Context: {self.preview_context.value}")
        self.ui.display_message("1. Armory (Functional Gear)")
        self.ui.display_message("2. Fashion (Visual Style)")
        self.ui.display_message("3. Weapon Skins")
        self.ui.display_message("4. Toggle PvE/PvP Preview")
        self.ui.display_message("5. Show Current Loadout")
        self.ui.display_message("6. Back")

    def show_armory_section(self):
        while True:
            self.ui.display_message("--- Armory Section ---")
            summary, modifiers = self.armory.get_equipped_summary(self.preview_context.value)
            self.ui.display_message(f"Equipped: {summary}")
            self.ui.display_message(f"Total Modifiers ({self.preview_context.value}): {modifiers}")
            self.ui.display_message("Available Slots:")
            for i, slot in enumerate(ArmorySlotType, 1):
                self.ui.display_message(f"{i}. {slot.value}")
            self.ui.display_message(f"{len(ArmorySlotType)+1}. Back")
            choice = input("Choose slot to change: ").strip()
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(ArmorySlotType):
                    slot = list(ArmorySlotType)[choice_num - 1]
                    self.change_armory_item(slot)
                elif choice_num == len(ArmorySlotType) + 1:
                    break
                else:
                    self.ui.display_message("Invalid choice.")
            except ValueError:
                self.ui.display_message("Invalid choice.")

    def change_armory_item(self, slot: ArmorySlotType):
        owned_items = [item for item in self.armory.owned_items.values() if item.slot == slot]
        if not owned_items:
            self.ui.display_message(f"No items available for {slot.value}.")
            return
        self.ui.display_message(f"Available {slot.value} items:")
        for i, item in enumerate(owned_items, 1):
            stats = item.get_stats_for_context(self.preview_context.value)
            self.ui.display_message(f"{i}. {item.name} ({item.rarity.name}) - {stats}")
        self.ui.display_message(f"{len(owned_items)+1}. Back")
        choice = input("Choose item: ").strip()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(owned_items):
                item = owned_items[choice_num - 1]
                if self.armory.equip_item(item.name):
                    self.ui.display_message(f"Equipped {item.name}.")
                else:
                    self.ui.display_message("Failed to equip.")
            elif choice_num == len(owned_items) + 1:
                pass
            else:
                self.ui.display_message("Invalid choice.")
        except ValueError:
            self.ui.display_message("Invalid choice.")

    def show_fashion_section(self):
        while True:
            self.ui.display_message("--- Fashion Section ---")
            summary = self.fashion.get_equipped_summary()
            self.ui.display_message(f"Equipped: {summary}")
            bonuses = self.fashion.get_synergy_bonuses()
            self.ui.display_message(f"Synergy Bonuses: {bonuses}")
            self.ui.display_message("Available Categories:")
            for i, cat in enumerate(FashionCategory, 1):
                self.ui.display_message(f"{i}. {cat.value}")
            self.ui.display_message(f"{len(FashionCategory)+1}. Back")
            choice = input("Choose category: ").strip()
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(FashionCategory):
                    cat = list(FashionCategory)[choice_num - 1]
                    self.change_fashion_item(cat)
                elif choice_num == len(FashionCategory) + 1:
                    break
                else:
                    self.ui.display_message("Invalid choice.")
            except ValueError:
                self.ui.display_message("Invalid choice.")

    def change_fashion_item(self, category: FashionCategory):
        owned_items = [item for item in self.fashion.owned_items.values() if item.category == category]
        if not owned_items:
            self.ui.display_message(f"No items available for {category.value}.")
            return
        self.ui.display_message(f"Available {category.value} items:")
        for i, item in enumerate(owned_items, 1):
            self.ui.display_message(f"{i}. {item.name} ({item.rarity.name}) - {item.synergy_bonuses}")
        self.ui.display_message(f"{len(owned_items)+1}. Back")
        choice = input("Choose item: ").strip()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(owned_items):
                item = owned_items[choice_num - 1]
                if self.fashion.equip_item(item.name):
                    self.ui.display_message(f"Equipped {item.name}.")
                    if self.daily_mission_manager:
                        self.daily_mission_manager.on_fashion_equipped()
                else:
                    self.ui.display_message("Failed to equip.")
            elif choice_num == len(owned_items) + 1:
                pass
            else:
                self.ui.display_message("Invalid choice.")
        except ValueError:
            self.ui.display_message("Invalid choice.")

    def show_weapon_skins_section(self):
        weapon_name = input("Enter weapon name to customize: ").strip()
        available_skins = self.weapon.get_available_skins(weapon_name)
        if not available_skins:
            self.ui.display_message(f"No skins available for {weapon_name}.")
            return
        self.ui.display_message(f"Available skins for {weapon_name}:")
        for i, skin_name in enumerate(available_skins, 1):
            skin = self.weapon.weapon_skins[weapon_name][skin_name]
            self.ui.display_message(f"{i}. {skin_name} ({skin.skin_type.value}) - {skin.bonuses}")
        self.ui.display_message(f"{len(available_skins)+1}. Back")
        choice = input("Choose skin: ").strip()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(available_skins):
                skin_name = available_skins[choice_num - 1]
                if self.weapon.equip_skin(weapon_name, skin_name):
                    self.ui.display_message(f"Equipped {skin_name} on {weapon_name}.")
                else:
                    self.ui.display_message("Failed to equip skin.")
            elif choice_num == len(available_skins) + 1:
                pass
            else:
                self.ui.display_message("Invalid choice.")
        except ValueError:
            self.ui.display_message("Invalid choice.")

    def toggle_preview_context(self):
        if self.preview_context == PreviewContext.PVE:
            self.preview_context = PreviewContext.PVP
        else:
            self.preview_context = PreviewContext.PVE
        self.ui.display_message(f"Preview context switched to {self.preview_context.value}.")

    def show_preview(self):
        self.ui.display_message("--- Current Loadout Preview ---")
        armory_summary, armory_mods = self.armory.get_equipped_summary(self.preview_context.value)
        self.ui.display_message(f"Armory ({self.preview_context.value}): {armory_summary}")
        self.ui.display_message(f"Armory Modifiers: {armory_mods}")
        fashion_summary = self.fashion.get_equipped_summary()
        self.ui.display_message(f"Fashion: {fashion_summary}")
        fashion_bonuses = self.fashion.get_synergy_bonuses()
        self.ui.display_message(f"Fashion Synergy (visual only): {fashion_bonuses}")
        self.ui.display_message(f"Preview Context: {self.preview_context.value}")
        self.ui.display_message(f"PvP Legal Fashion: {'Yes' if self._fashion_is_pvp_legal() else 'No'}")
        self.ui.display_message(f"PvP Legal Weapon Skins: {'Yes' if self._weapon_skins_are_pvp_legal() else 'No'}")
        self.ui.display_message("Weapon Skins: Check individual weapons")

    def _fashion_is_pvp_legal(self) -> bool:
        for category, item_name in self.fashion.equipped.items():
            item = self.fashion.owned_items.get(item_name)
            if item and not item.allowed_in_pvp:
                return False
        return True

    def _weapon_skins_are_pvp_legal(self) -> bool:
        for weapon_name, skin_name in self.weapon.equipped_skins.items():
            if not self.weapon.is_skin_pvp_legal(weapon_name, skin_name):
                return False
        return True
