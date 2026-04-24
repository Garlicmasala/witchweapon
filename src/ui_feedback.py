"""
UI Feedback for Witch's Weapon combat system.
Handles visual feedback, messages, and status displays.
"""

from .appearance_manager import AppearanceCategory

class UIFeedback:
    def display_message(self, message):
        # US: As a player, I want visual feedback for actions and events.
        print(f"[INFO] {message}")

    def display_status(self, player, enemy):
        print(f"\n--- Status ---")
        print(f"Player HP: {player.health}, Mana: {player.mana}, Position: {player.position}")
        print(f"Current Weapon: {player.current_weapon.name if player.current_weapon else 'None'}")
        print(f"Outfit: {player.appearance_manager.get_equipped_name(AppearanceCategory.OUTFIT)}")
        print(f"Weapon Skin: {player.appearance_manager.get_equipped_name(AppearanceCategory.WEAPON_SKIN)}")
        print(f"Enemy: {enemy.name}, HP: {enemy.health}, State: {enemy.state}")
        print("---------------\n")

    def display_damage(self, target, damage):
        print(f"{target} took {damage} damage!")

    def display_upgrade_menu(self, player, upgrade_manager):
        # US: Upgrade UI - console-based preview
        print("\n--- Upgrade Menu ---")
        print(f"Player Level: {player.level}/{player.max_level}, EXP: {player.exp}/{player.exp_to_next}")
        print(f"HP: {player.health}/{player.max_health} (+{player.enhanced_hp})")
        print(f"ATK: {player.atk} (+{player.enhanced_atk})")
        print(f"DEF: {player.defense} (+{player.enhanced_def})")
        print(f"Materials: {upgrade_manager.get_materials()}")
        print("Options:")
        print("1. Enhance HP")
        print("2. Enhance ATK")
        print("3. Enhance DEF")
        print("4. Breakthrough")
        if player.current_weapon:
            print(f"5. Enhance Weapon ({player.current_weapon.name})")
            print("6. Gift to Weapon")
        print("7. Back")

    def display_weapon_info(self, weapon):
        print(f"\nWeapon: {weapon.name}")
        print(f"Damage: {weapon.base_damage + weapon.enhanced_damage} (+{weapon.enhanced_damage})")
        print(f"Affection: {weapon.affection}/{weapon.affection_to_next} (Level {weapon.affection_level})")
        print(f"Bonuses: ATK +{weapon.atk_bonus}, DEF +{weapon.def_bonus}")
        print(f"Enhancement: +{weapon.enhancement_level}/{weapon.max_enhancement}")

    def display_armory_menu(self, appearance_manager):
        print("\n--- Armory & Wardrobe ---")
        print(f"Equipped Outfit: {appearance_manager.get_equipped_name(AppearanceCategory.OUTFIT)}")
        print(f"Equipped Weapon Skin: {appearance_manager.get_equipped_name(AppearanceCategory.WEAPON_SKIN)}")
        print(f"Equipped Accessory: {appearance_manager.get_equipped_name(AppearanceCategory.ACCESSORY)}")
        inventory = appearance_manager.get_inventory_summary()
        for category, items in inventory.items():
            print(f"{category}: {', '.join(items)}")
        print("Options:")
        print("1. Equip Outfit")
        print("2. Equip Weapon Skin")
        print("3. Equip Accessory")
        print("4. Preview Appearance Item")
        print("5. Back")

    def display_appearance_item(self, item):
        print(f"\nAppearance Item: {item.name}")
        print(f"Category: {item.category.value}")
        print(f"Rarity: {item.rarity.name}")
        print(f"Bonuses: {item.bonuses}")
        print(f"Description: {item.description}")
        print(f"Visual Asset: {item.visual_asset}")