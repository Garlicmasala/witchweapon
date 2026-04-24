"""
Weapon Customization for Witch's Weapon.
Handles skins, effects, animations for weapons.
"""

from enum import Enum
from typing import Dict, List, Optional
from .weapon_manager import Rarity

class WeaponSkinType(Enum):
    SKIN = "Skin"
    EFFECT = "Effect"
    ANIMATION = "Animation"
    STANCE = "Stance"

class WeaponSkin:
    def __init__(self, name: str, skin_type: WeaponSkinType, rarity: Rarity, bonuses: Dict[str, float], description: str = "", visual_changes: Dict[str, str] = None, allowed_in_pvp: bool = True):
        self.name = name
        self.skin_type = skin_type
        self.rarity = rarity
        self.bonuses = bonuses.copy()
        self.description = description
        self.visual_changes = visual_changes or {}
        self.allowed_in_pvp = allowed_in_pvp

    def to_dict(self):
        return {
            "name": self.name,
            "skin_type": self.skin_type.name,
            "rarity": self.rarity.name,
            "bonuses": self.bonuses,
            "description": self.description,
            "visual_changes": self.visual_changes,
            "allowed_in_pvp": self.allowed_in_pvp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            WeaponSkinType[data["skin_type"]],
            Rarity[data["rarity"]],
            data["bonuses"],
            data.get("description", ""),
            data.get("visual_changes", {}),
            data.get("allowed_in_pvp", True)
        )

class WeaponCustomization:
    def __init__(self):
        self.weapon_skins: Dict[str, Dict[str, WeaponSkin]] = {}  # weapon_name -> {skin_name: skin}
        self.equipped_skins: Dict[str, str] = {}  # weapon_name -> skin_name
        self.initialize_default_skins()

    def initialize_default_skins(self):
        self.weapon_skins.clear()
        self.equipped_skins.clear()

        # Default skins for default weapons
        self.add_weapon_skin("Sword", WeaponSkin(
            "Iron Blade",
            WeaponSkinType.SKIN,
            Rarity.R,
            {"ATK": 2},
            "Basic iron appearance.",
            {"blade_color": "gray", "hilt_color": "brown"}
        ))
        self.equipped_skins["Sword"] = "Iron Blade"

    def add_weapon_skin(self, weapon_name: str, skin: WeaponSkin):
        if weapon_name not in self.weapon_skins:
            self.weapon_skins[weapon_name] = {}
        self.weapon_skins[weapon_name][skin.name] = skin

    def equip_skin(self, weapon_name: str, skin_name: str) -> bool:
        if weapon_name not in self.weapon_skins or skin_name not in self.weapon_skins[weapon_name]:
            return False
        self.equipped_skins[weapon_name] = skin_name
        return True

    def get_equipped_skin(self, weapon_name: str) -> Optional[WeaponSkin]:
        skin_name = self.equipped_skins.get(weapon_name)
        if skin_name and weapon_name in self.weapon_skins:
            return self.weapon_skins[weapon_name].get(skin_name)
        return None

    def get_weapon_identity(self, weapon_name: str) -> str:
        skin = self.get_equipped_skin(weapon_name)
        if skin:
            return f"{weapon_name} ({skin.name})"
        return weapon_name

    def is_skin_pvp_legal(self, weapon_name: str, skin_name: str) -> bool:
        if weapon_name not in self.weapon_skins:
            return False
        skin = self.weapon_skins[weapon_name].get(skin_name)
        return bool(skin and skin.allowed_in_pvp)

    def get_weapon_bonuses(self, weapon_name: str, context: str = "PvE") -> Dict[str, float]:
        skin = self.get_equipped_skin(weapon_name)
        if not skin:
            return {}
        if context == "PvP":
            return {}
        return skin.bonuses if skin else {}

    def get_equipped_visual_changes(self, weapon_name: str, context: str = "PvE") -> Dict[str, str]:
        skin = self.get_equipped_skin(weapon_name)
        if not skin:
            return {}
        if context == "PvP" and not skin.allowed_in_pvp:
            return {}
        return skin.visual_changes

    def get_available_skins(self, weapon_name: str) -> List[str]:
        if weapon_name in self.weapon_skins:
            return list(self.weapon_skins[weapon_name].keys())
        return []

    def get_weapon_state(self) -> Dict:
        return {
            "skins": {
                weapon: {name: skin.to_dict() for name, skin in skins.items()}
                for weapon, skins in self.weapon_skins.items()
            },
            "equipped": self.equipped_skins.copy()
        }

    def load_weapon_state(self, state: Dict):
        self.weapon_skins.clear()
        skins_data = state.get("skins", {})
        for weapon, skin_dict in skins_data.items():
            for name, skin_data in skin_dict.items():
                skin = WeaponSkin.from_dict(skin_data)
                self.add_weapon_skin(weapon, skin)
        self.equipped_skins = state.get("equipped", {})
