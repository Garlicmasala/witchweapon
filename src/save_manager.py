"""
Save Manager for Witch's Weapon.
Handles saving and loading character and weapon data to JSON.
"""

import json
import os

class SaveManager:
    def __init__(self, save_file="save_data.json"):
        self.save_file = save_file

    def save_game(self, player, weapon_manager, upgrade_manager, currency_manager=None, gacha_manager=None, appearance_manager=None):
        # US: Data persistence - save/load to JSON
        data = {
            "player": {
                "level": player.level,
                "exp": player.exp,
                "exp_to_next": player.exp_to_next,
                "max_level": player.max_level,
                "base_hp": player.base_hp,
                "base_atk": player.base_atk,
                "base_def": player.base_def,
                "enhanced_hp": player.enhanced_hp,
                "enhanced_atk": player.enhanced_atk,
                "enhanced_def": player.enhanced_def,
                "health": player.health,
                "mana": player.mana,
                "position": player.position,
                "current_weapon": player.current_weapon.name if player.current_weapon else None,
                "ultimate_cooldown": player.ultimate_cooldown
            },
            "weapons": {},
            "materials": upgrade_manager.get_materials(),
            "breakthrough_level": upgrade_manager.breakthrough_level,
            "currency": currency_manager.get_balances() if currency_manager else {},
            "gacha": gacha_manager.get_state() if gacha_manager else {},
            "appearance": appearance_manager.to_dict() if appearance_manager else {}
        }
        for name, weapon in weapon_manager.weapons.items():
            data["weapons"][name] = {
                "name": weapon.name,
                "base_damage": weapon.base_damage,
                "duration": weapon.duration,
                "current_duration": weapon.current_duration,
                "rarity": weapon.rarity.name if hasattr(weapon, 'rarity') else None,
                "affection": weapon.affection,
                "affection_level": weapon.affection_level,
                "affection_to_next": weapon.affection_to_next,
                "atk_bonus": weapon.atk_bonus,
                "def_bonus": weapon.def_bonus,
                "enhanced_damage": weapon.enhanced_damage,
                "enhancement_level": weapon.enhancement_level
            }
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=4)
        print("Game saved.")

    def load_game(self, player, weapon_manager, upgrade_manager, currency_manager=None, gacha_manager=None, appearance_manager=None):
        # US: Data persistence - save/load to JSON
        if not os.path.exists(self.save_file):
            print("No save file found.")
            return False
        with open(self.save_file, 'r') as f:
            data = json.load(f)
        # Load player
        p_data = data["player"]
        player.level = p_data["level"]
        player.exp = p_data["exp"]
        player.exp_to_next = p_data["exp_to_next"]
        player.max_level = p_data["max_level"]
        player.base_hp = p_data["base_hp"]
        player.base_atk = p_data["base_atk"]
        player.base_def = p_data["base_def"]
        player.enhanced_hp = p_data["enhanced_hp"]
        player.enhanced_atk = p_data["enhanced_atk"]
        player.enhanced_def = p_data["enhanced_def"]
        player.max_health = player.calculate_max_health()
        player.health = min(p_data["health"], player.max_health)
        player.mana = p_data["mana"]
        player.movement.position = p_data["position"]
        player.ultimate_cooldown = p_data["ultimate_cooldown"]
        # Load weapons
        weapon_manager.weapons = {}
        for name, w_data in data["weapons"].items():
            from src.weapon_manager import Weapon, Rarity
            rarity = Rarity[w_data["rarity"]] if w_data["rarity"] else Rarity.R
            weapon = Weapon(name, w_data["base_damage"], w_data["duration"], rarity)
            weapon.current_duration = w_data["current_duration"]
            weapon.affection = w_data["affection"]
            weapon.affection_level = w_data["affection_level"]
            weapon.affection_to_next = w_data["affection_to_next"]
            weapon.atk_bonus = w_data["atk_bonus"]
            weapon.def_bonus = w_data["def_bonus"]
            weapon.enhanced_damage = w_data["enhanced_damage"]
            weapon.enhancement_level = w_data["enhancement_level"]
            weapon_manager.weapons[name] = weapon
        if p_data["current_weapon"]:
            player.switch_weapon(p_data["current_weapon"])
        # Load upgrades
        upgrade_manager.materials = data["materials"]
        upgrade_manager.breakthrough_level = data["breakthrough_level"]
        # Load currency
        if currency_manager and "currency" in data:
            currency_manager.balances = data["currency"]
        # Load gacha
        if gacha_manager and "gacha" in data:
            gacha_manager.load_state(data["gacha"])
        # Load appearance
        if appearance_manager and "appearance" in data:
            appearance_manager.load_from_dict(data["appearance"])
        print("Game loaded.")
        return True