"""
Gacha manager for Witch's Weapon.
Handles banner configuration, deterministic draw execution, pity, duplicate conversion, and result presentation.
"""

from datetime import datetime, timedelta
from enum import Enum
import random

from .weapon_manager import Weapon, Rarity

class BannerType(Enum):
    STANDARD = "Standard"
    LIMITED = "Limited"
    GUARANTEED = "Guaranteed"

class BannerItem:
    def __init__(self, name, rarity, base_damage=0, duration=0, item_category="weapon", bonuses=None, description=""):
        self.name = name
        self.rarity = rarity
        self.base_damage = base_damage
        self.duration = duration
        self.item_category = item_category
        self.bonuses = bonuses or {}
        self.description = description

class BannerEntry:
    def __init__(self, item, rate):
        self.item = item
        self.rate = rate

class Banner:
    def __init__(self, name, banner_type, start_time, end_time, visual_asset, entries, single_cost, multi_cost, pity_threshold, guaranteed_rarity, multi_guarantee_rarity=None):
        self.name = name
        self.banner_type = banner_type
        self.start_time = start_time
        self.end_time = end_time
        self.visual_asset = visual_asset
        self.entries = entries
        self.single_cost = single_cost
        self.multi_cost = multi_cost
        self.pity_threshold = pity_threshold
        self.guaranteed_rarity = guaranteed_rarity
        self.multi_guarantee_rarity = multi_guarantee_rarity
        self.validate_rates()

    def is_active(self, current_time=None):
        current_time = current_time or datetime.utcnow()
        if self.start_time and current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        return True

    def validate_rates(self):
        total_rate = sum(entry.rate for entry in self.entries)
        if abs(total_rate - 100.0) > 1e-6:
            raise ValueError(f"Banner {self.name} rates must sum to 100, got {total_rate}")

    def draw_weighted(self, rng):
        roll = rng.uniform(0, 100)
        current = 0.0
        for entry in self.entries:
            current += entry.rate
            if roll <= current:
                return entry.item
        return self.entries[-1].item

    def draw_by_rarity(self, rarity, rng):
        filtered = [entry for entry in self.entries if entry.item.rarity == rarity]
        if not filtered:
            return self.draw_weighted(rng)
        total = sum(entry.rate for entry in filtered)
        roll = rng.uniform(0, total)
        current = 0.0
        for entry in filtered:
            current += entry.rate
            if roll <= current:
                return entry.item
        return filtered[-1].item

class DrawResult:
    def __init__(self, item_name, rarity, item_category="weapon", is_duplicate=False, conversion=None):
        self.item_name = item_name
        self.rarity = rarity
        self.item_category = item_category
        self.is_duplicate = is_duplicate
        self.conversion = conversion or {}

class GachaManager:
    def __init__(self, weapon_manager, upgrade_manager, currency_manager, ui_feedback, appearance_manager, seed=None):
        # US: Gacha Banner Configuration - initialize banners with drop pools, rates, pity
        self.weapon_manager = weapon_manager
        self.upgrade_manager = upgrade_manager
        self.currency_manager = currency_manager
        self.ui = ui_feedback
        self.appearance_manager = appearance_manager
        self.rng = random.Random(seed)
        self.banners = {}
        self.pity_counters = {}
        self.setup_banners()

    def setup_banners(self):
        now = datetime.utcnow()
        standard = Banner(
            name="Standard Banner",
            banner_type=BannerType.STANDARD,
            start_time=None,
            end_time=None,
            visual_asset="standard_banner",
            entries=[
                BannerEntry(BannerItem("Basic Sword", Rarity.R, 10), 38.0),
                BannerEntry(BannerItem("Iron Dagger", Rarity.R, 9), 38.0),
                BannerEntry(BannerItem("Magic Wand", Rarity.SR, 15), 12.0),
                BannerEntry(BannerItem("Fire Staff", Rarity.SR, 20), 5.0),
                BannerEntry(BannerItem("Witch's Glimmer", Rarity.SR, item_category="weapon_skin", bonuses={"ATK": 2}, description="A shimmering weapon skin that makes spells feel sharper."), 4.0),
                BannerEntry(BannerItem("Starlight Tome", Rarity.SSR, 35), 3.0)
            ],
            single_cost={"Gacha Gem": 100},
            multi_cost={"Gacha Gem": 900},
            pity_threshold=90,
            guaranteed_rarity=Rarity.SSR,
            multi_guarantee_rarity=Rarity.SR
        )
        event = Banner(
            name="Event Banner",
            banner_type=BannerType.LIMITED,
            start_time=now - timedelta(days=1),
            end_time=now + timedelta(days=7),
            visual_asset="event_banner",
            entries=[
                BannerEntry(BannerItem("Wind Spear", Rarity.R, 11), 33.0),
                BannerEntry(BannerItem("Crystal Blade", Rarity.R, 10), 33.0),
                BannerEntry(BannerItem("Moon Staff", Rarity.SR, 18), 17.0),
                BannerEntry(BannerItem("Abyss Rod", Rarity.SR, 22), 7.0),
                BannerEntry(BannerItem("Spellbound Shawl", Rarity.SR, item_category="accessory", bonuses={"DEF": 3}, description="A radiant shawl that bolsters defensive resolve."), 4.0),
                BannerEntry(BannerItem("Supernova Lance", Rarity.SSR, 40), 6.0)
            ],
            single_cost={"Gacha Gem": 120},
            multi_cost={"Gacha Gem": 1080},
            pity_threshold=80,
            guaranteed_rarity=Rarity.SSR,
            multi_guarantee_rarity=Rarity.SR
        )
        guarantee = Banner(
            name="Step-Up Banner",
            banner_type=BannerType.GUARANTEED,
            start_time=now - timedelta(days=1),
            end_time=now + timedelta(days=14),
            visual_asset="step_up_banner",
            entries=[
                BannerEntry(BannerItem("Celestial Bow", Rarity.R, 12), 31.0),
                BannerEntry(BannerItem("Aether Wand", Rarity.R, 12), 31.0),
                BannerEntry(BannerItem("Nova Staff", Rarity.SR, 20), 20.0),
                BannerEntry(BannerItem("Starlight Mantle", Rarity.SR, item_category="outfit", bonuses={"ATK": 2, "DEF": 1}, description="A luminous mantle that enhances both offense and defense."), 4.0),
                BannerEntry(BannerItem("Phoenix Blade", Rarity.SSR, 45), 9.0),
                BannerEntry(BannerItem("Eclipse Spear", Rarity.SSR, 55), 5.0)
            ],
            single_cost={"Gacha Gem": 150},
            multi_cost={"Gacha Gem": 1350},
            pity_threshold=70,
            guaranteed_rarity=Rarity.SSR,
            multi_guarantee_rarity=Rarity.SR
        )
        self.banners = {
            standard.name: standard,
            event.name: event,
            guarantee.name: guarantee
        }
        for name in self.banners:
            self.pity_counters[name] = 0

    def get_active_banners(self):
        return [banner for banner in self.banners.values() if banner.is_active()]

    def get_banner(self, name):
        return self.banners.get(name)

    def perform_single_draw(self, banner_name):
        # US: Currency & Cost Management - validate and consume cost
        banner = self.get_banner(banner_name)
        if not banner or not banner.is_active():
            self.ui.display_message("Banner not available.")
            return None
        if not self.currency_manager.can_afford(banner.single_cost):
            self.ui.display_message("Insufficient currency for single draw.")
            return None
        result = self.execute_draws(banner, 1)[0]
        self.currency_manager.consume(banner.single_cost)
        return result

    def perform_multi_draw(self, banner_name, count=10):
        banner = self.get_banner(banner_name)
        if not banner or not banner.is_active():
            self.ui.display_message("Banner not available.")
            return []
        if not self.currency_manager.can_afford(banner.multi_cost):
            self.ui.display_message("Insufficient currency for multi draw.")
            return []
        results = self.execute_draws(banner, count, multi_draw=True)
        self.currency_manager.consume(banner.multi_cost)
        return results

    def execute_draws(self, banner, count, multi_draw=False):
        results = []
        sr_obtained = False
        for _ in range(count):
            result = self.draw_once(banner)
            if result.rarity == Rarity.SR or result.rarity == Rarity.SSR:
                sr_obtained = True
            results.append(result)
        if multi_draw and banner.multi_guarantee_rarity and not sr_obtained:
            guarantee_item = self.draw_rarity(banner, banner.multi_guarantee_rarity)
            result = self.process_result(guarantee_item, force_add=True)
            results[-1] = result
        return results

    def draw_once(self, banner):
        # US: Pity/Guarantee System - check pity and guarantee high-rarity
        pity = self.pity_counters.get(banner.name, 0)
        if pity >= banner.pity_threshold:
            item = self.draw_rarity(banner, banner.guaranteed_rarity)
            self.pity_counters[banner.name] = 0
        else:
            item = banner.draw_weighted(self.rng)
            if item.rarity == banner.guaranteed_rarity:
                self.pity_counters[banner.name] = 0
            else:
                self.pity_counters[banner.name] = pity + 1
        result = self.process_result(item)
        return result

    def draw_rarity(self, banner, rarity):
        return banner.draw_by_rarity(rarity, self.rng)

    def process_result(self, item, force_add=False):
        # US: Duplicate Handling - detect and convert to materials/shards
        if item.item_category == "cosmetic":
            owned = self.appearance_manager.has_item(item.name)
            if owned and not force_add:
                conversion = self.get_duplicate_conversion(item.rarity)
                self.upgrade_manager.add_materials(conversion)
                return DrawResult(item.name, item.rarity, item_category=item.item_category, is_duplicate=True, conversion=conversion)
            self.appearance_manager.add_cosmetic_from_gacha(item)
            return DrawResult(item.name, item.rarity, item_category=item.item_category, is_duplicate=False)

        owned = self.weapon_manager.has_weapon(item.name)
        if owned and not force_add:
            conversion = self.get_duplicate_conversion(item.rarity)
            self.upgrade_manager.add_materials(conversion)
            return DrawResult(item.name, item.rarity, item_category=item.item_category, is_duplicate=True, conversion=conversion)
        new_weapon = Weapon(item.name, item.base_damage, item.duration, rarity=item.rarity)
        self.weapon_manager.add_weapon(new_weapon)
        return DrawResult(item.name, item.rarity, item_category=item.item_category, is_duplicate=False)

    def get_duplicate_conversion(self, rarity):
        if rarity == Rarity.SSR:
            return {"Rare Gem": 1, "Magic Crystal": 2}
        if rarity == Rarity.SR:
            return {"Magic Crystal": 1}
        return {"Iron Ore": 1}

    def get_pity(self, banner_name):
        return self.pity_counters.get(banner_name, 0)

    def get_state(self):
        return {
            "pity_counters": self.pity_counters.copy()
        }

    def load_state(self, state):
        self.pity_counters = state.get("pity_counters", self.pity_counters)
