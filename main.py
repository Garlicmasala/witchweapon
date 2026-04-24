#!/usr/bin/env python3
"""
Main entry point for the Witch's Weapon combat system simulation.
"""

from src.combat_manager import CombatManager
from src.player import Player
from src.enemy import Enemy
from src.weapon_manager import WeaponManager
from src.skill_system import SkillSystem
from src.ui_feedback import UIFeedback
from src.upgrade_manager import UpgradeManager
from src.save_manager import SaveManager
from src.currency_manager import CurrencyManager
from src.gacha_manager import GachaManager
from src.appearance_manager import AppearanceManager
from src.companion import Companion
from src.dialogue_manager import DialogueManager
from src.llm_provider import LLMProvider
from src.world_map import WorldMapRoot
from src.region_chunk import RegionChunk
from src.combat_cell import CombatCell, HeightTier
from src.traversal_system import TraversalSystem, TraversalNode, TraversalMode
from src.enemy_director import EnemyDirector, EnemyMobility
from src.world_state_controller import WorldStateController
from src.pvp_matchmaking import PvPMatchmaker
from src.pvp_menu import PvPMenu
from src.visual_novel import VisualNovelManager
from src.daily_missions import DailyMissionManager
import time
import random

def main():
    # Initialize components
    ui = UIFeedback()
    weapon_manager = WeaponManager()
    appearance_manager = AppearanceManager(ui)  # Temp, will update later
    skill_system = SkillSystem()
    upgrade_manager = UpgradeManager(ui)
    currency_manager = CurrencyManager()
    gacha_manager = GachaManager(weapon_manager, upgrade_manager, currency_manager, ui, appearance_manager)
    save_manager = SaveManager()
    llm_provider = LLMProvider()
    dialogue_manager = DialogueManager(ui, llm_provider)
    player = Player(weapon_manager, skill_system, ui, currency_manager, appearance_manager)

    # Initialize companions
    companion = Companion("Familiar Spirit", ui, dialogue_manager)
    companions = [companion]

    traversal_system = TraversalSystem(ui)
    visual_novel_manager = VisualNovelManager(ui)
    visual_novel_manager.load_story_graph(VisualNovelManager.create_default_story_graph())
    daily_mission_manager = DailyMissionManager(currency_manager)
    enemy_director = EnemyDirector(ui, visual_novel_manager)
    world_map = WorldMapRoot(ui)
    world_state = WorldStateController(ui, world_map, enemy_director, visual_novel_manager)
    
    # Initialize PvP
    pvp_matchmaker = PvPMatchmaker()
    pvp_menu = PvPMenu(ui, player, pvp_matchmaker, daily_mission_manager)
    setup_example_map(world_map, traversal_system, enemy_director, ui)

    # Now update appearance_manager with daily_mission_manager
    appearance_manager = AppearanceManager(ui, daily_mission_manager)
    # Update gacha_manager and player with appearance_manager
    gacha_manager.appearance_manager = appearance_manager
    player.appearance_manager = appearance_manager
    visual_novel_manager.daily_mission_manager = daily_mission_manager
    setup_example_map(world_map, traversal_system, enemy_director, ui)

    # Try to load save
    save_manager.load_game(player, weapon_manager, upgrade_manager, currency_manager, gacha_manager, appearance_manager, visual_novel_manager, daily_mission_manager)

    ui.display_message("Welcome to Witch's Weapon Combat Simulation!")

    while True:
        print("\n--- Main Menu ---")
        print("1. Start Combat")
        print("2. Upgrade")
        print("3. Gacha")
        print("4. Interact")
        print("5. Armory & Wardrobe")
        print("6. World Map")
        print("7. PvP Arena")
        print("8. Daily Missions")
        print("9. Save")
        print("10. Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            enemy = Enemy("Goblin", 100, ui)
            combat_manager = CombatManager(player, enemy, ui, upgrade_manager)
            ui.display_message("Enemy: Goblin with 100 HP.")
            run_combat(player, enemy, combat_manager, ui, companions, dialogue_manager, daily_mission_manager)
            # Update daily missions
            if enemy.is_defeated():
                daily_mission_manager.on_combat_stage_cleared()
                daily_mission_manager.on_enemy_defeated()
            if visual_novel_manager.has_pending_story():
                visual_novel_manager.play_next_interlude()
        elif choice == "2":
            show_upgrade_menu(player, upgrade_manager, ui)
        elif choice == "3":
            show_gacha_menu(gacha_manager, ui)
        elif choice == "4":
            show_interaction_menu(player, companions, dialogue_manager, ui)
        elif choice == "5":
            appearance_manager.show_wardrobe_menu()
        elif choice == "6":
            show_world_map_menu(player, world_map, traversal_system, world_state, ui)
        elif choice == "7":
            show_pvp_menu(pvp_menu, player)
        elif choice == "8":
            show_daily_missions_menu(daily_mission_manager, ui)
        elif choice == "9":
            save_manager.save_game(player, weapon_manager, upgrade_manager, currency_manager, gacha_manager, appearance_manager, visual_novel_manager, daily_mission_manager)
        elif choice == "10":
            save_manager.save_game(player, weapon_manager, upgrade_manager, currency_manager, gacha_manager, appearance_manager, visual_novel_manager, daily_mission_manager)
            break
        else:
            ui.display_message("Invalid choice.")


def setup_example_map(world_map, traversal_system, enemy_director, ui):
    # Example map setup for vertical traversal and combat cells
    chunk = RegionChunk(
        "chunk_1",
        ((-10.0, 0.0, -10.0), (10.0, 15.0, 10.0))
    )
    cell = CombatCell(
        "cell_1",
        ((-5.0, 0.0, -5.0), (5.0, 12.0, 5.0)),
        [HeightTier.GROUND, HeightTier.ELEVATED, HeightTier.AIR],
        [(-2.0, 0.0, -2.0), (2.0, 5.0, 2.0)],
        story_node_id="interlude_1"
    )
    chunk.add_combat_cell(cell)

    node_a = TraversalNode("jump_pad_1", (0.0, 0.0, 2.0), "jump_pad", energy_cost=10, allowed_modes=[TraversalMode.GROUND])
    node_b = TraversalNode("wind_updraft_1", (3.0, 2.0, 3.0), "wind_updraft", energy_cost=5, allowed_modes=[TraversalMode.AIR_GLIDE, TraversalMode.AIR_FLY])
    chunk.add_traversal_node(node_a)
    chunk.add_traversal_node(node_b)

    world_map.register_chunk(chunk)
    traversal_system.register_nodes([node_a, node_b])

    enemy1 = Enemy("Sky Wisp", 60, ui, mobility=EnemyMobility.FLYER, position=[2, 8, 0])
    enemy2 = Enemy("Cliff Raider", 80, ui, mobility=EnemyMobility.CLIMBER, position=[-1, 3, -2])
    enemy_director.assign_enemies_to_cell(cell, [enemy1, enemy2])

    ui.display_message("[WorldMap] Example map setup completed.")


def run_combat(player, enemy, combat_manager, ui, companions, dialogue_manager, daily_mission_manager):
    # Simulation loop
    while not combat_manager.is_battle_over():
        ui.display_status(player, enemy)
        # Update companions
        for comp in companions:
            comp.update()
            comp.interact(player)
        dialogue_manager.update_cooldowns()
        action = input("Choose action (move, attack, switch_weapon, use_skill, ultimate, interact, dialogue_continue, dialogue_branch <option>, dialogue_end): ").strip().lower()
        if action == "move":
            direction = input("Direction (up, down, left, right, forward, back): ").strip().lower()
            player.move(direction)
        elif action == "attack":
            combat_manager.auto_attack()
        elif action == "switch_weapon":
            weapon_name = input("Weapon to switch to: ").strip()
            if player.switch_weapon(weapon_name):
                daily_mission_manager.on_weapon_switched()
        elif action == "use_skill":
            skill_name = input("Skill to use: ").strip()
            if player.use_skill(skill_name, enemy):
                daily_mission_manager.on_weapon_skill_used()
        elif action == "ultimate":
            if player.use_ultimate(enemy):
                daily_mission_manager.on_weapon_ultimate_used()
        elif action == "interact":
            if companions:
                player.interact(companions[0])  # Interact with first companion
        elif action.startswith("dialogue_continue"):
            if player.dialogue_state:
                dialogue_manager.continue_dialogue(player.dialogue_state)
        elif action.startswith("dialogue_branch"):
            parts = action.split()
            if len(parts) > 1 and player.dialogue_state:
                branch = parts[1]
                dialogue_manager.choose_branch(player.dialogue_state, branch)
        elif action == "dialogue_end":
            if player.dialogue_state:
                dialogue_manager.end_dialogue(player.dialogue_state)
                player.end_dialogue()
        else:
            ui.display_message("Invalid action.")

        # Enemy turn (simple AI)
        if not combat_manager.is_battle_over():
            enemy.attack(player)

        # Update turn
        combat_manager.update_turn()
        player.update_cooldowns()

def show_upgrade_menu(player, upgrade_manager, ui):
    # US: Upgrade UI - console-based preview, confirmation, feedback
    while True:
        ui.display_upgrade_menu(player, upgrade_manager)
        if player.current_weapon:
            ui.display_weapon_info(player.current_weapon)
        choice = input("Choose upgrade option: ").strip()
        if choice == "1":
            if upgrade_manager.enhance_stat(player, "HP"):
                ui.display_message("HP enhanced successfully.")
            else:
                ui.display_message("Enhancement failed.")
        elif choice == "2":
            if upgrade_manager.enhance_stat(player, "ATK"):
                ui.display_message("ATK enhanced successfully.")
            else:
                ui.display_message("Enhancement failed.")
        elif choice == "3":
            if upgrade_manager.enhance_stat(player, "DEF"):
                ui.display_message("DEF enhanced successfully.")
            else:
                ui.display_message("Enhancement failed.")
        elif choice == "4":
            if upgrade_manager.breakthrough(player):
                ui.display_message("Breakthrough successful.")
            else:
                ui.display_message("Breakthrough failed.")
        elif choice == "5" and player.current_weapon:
            if upgrade_manager.enhance_weapon(player.current_weapon):
                ui.display_message("Weapon enhanced successfully.")
            else:
                ui.display_message("Weapon enhancement failed.")
        elif choice == "6" and player.current_weapon:
            # US: Affection/Bond system - gain through gifts
            gift_amount = 10  # Example
            old_level = player.current_weapon.affection_level
            player.current_weapon.gain_affection(gift_amount)
            if player.current_weapon.affection_level > old_level:
                ui.display_message(f"Gifted to {player.current_weapon.name}. Affection level up to {player.current_weapon.affection_level}!")
            else:
                ui.display_message(f"Gifted to {player.current_weapon.name}. Affection increased.")
        elif choice == "7":
            break
        else:
            ui.display_message("Invalid choice.")

        time.sleep(1)  # Simulate time


def display_draw_result(result, ui):
    ui.display_message(f"Result: {result.item_name} ({result.rarity.name}) - {result.item_category}")
    if result.is_duplicate:
        ui.display_message(f"Duplicate converted to: {result.conversion}")


def show_gacha_menu(gacha_manager, ui):
    # US: Gacha Banner Configuration - display active banners
    while True:
        ui.display_message("--- Gacha Menu ---")
        active_banners = gacha_manager.get_active_banners()
        if not active_banners:
            ui.display_message("No active banners.")
            break
        for i, banner in enumerate(active_banners, 1):
            ui.display_message(f"{i}. {banner.name} ({banner.banner_type.value})")
        ui.display_message(f"{len(active_banners)+1}. View Currency")
        ui.display_message(f"{len(active_banners)+2}. Back")
        choice = input("Choose banner: ").strip()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(active_banners):
                banner = active_banners[choice_num - 1]
                show_banner_menu(banner, gacha_manager, ui)
            elif choice_num == len(active_banners) + 1:
                ui.display_message("Currency Balances:")
                balances = gacha_manager.currency_manager.get_balances()
                for curr, amt in balances.items():
                    ui.display_message(f"{curr}: {amt}")
            elif choice_num == len(active_banners) + 2:
                break
            else:
                ui.display_message("Invalid choice.")
        except ValueError:
            ui.display_message("Invalid choice.")

def show_banner_menu(banner, gacha_manager, ui):
    # US: Random Draw Execution - single/multi draws
    while True:
        ui.display_message(f"--- {banner.name} ---")
        ui.display_message(f"Type: {banner.banner_type.value}")
        ui.display_message(f"Single Draw Cost: {banner.single_cost}")
        ui.display_message(f"Multi Draw Cost: {banner.multi_cost}")
        ui.display_message(f"Pity: {gacha_manager.get_pity(banner.name)} / {banner.pity_threshold}")
        ui.display_message("1. Single Draw")
        ui.display_message("2. Multi Draw (10)")
        ui.display_message("3. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            result = gacha_manager.perform_single_draw(banner.name)
            if result:
                display_draw_result(result, ui)
        elif choice == "2":
            results = gacha_manager.perform_multi_draw(banner.name)
            if results:
                for result in results:
                    display_draw_result(result, ui)
        elif choice == "3":
            break
        else:
            ui.display_message("Invalid choice.")

def show_armory_menu(player, appearance_manager, ui):
    while True:
        ui.display_armory_menu(appearance_manager)
        choice = input("Choose: ").strip()
        if choice == "1":
            equip_appearance_category(appearance_manager, ui, "outfit")
        elif choice == "2":
            equip_appearance_category(appearance_manager, ui, "weapon_skin")
        elif choice == "3":
            equip_appearance_category(appearance_manager, ui, "accessory")
        elif choice == "4":
            item_name = input("Appearance item to preview: ").strip()
            item = appearance_manager.get_item(item_name)
            if item:
                ui.display_appearance_item(item)
            else:
                ui.display_message("Item not found.")
        elif choice == "5":
            break
        else:
            ui.display_message("Invalid choice.")


def equip_appearance_category(appearance_manager, ui, category_key):
    category_map = {
        "outfit": "Outfit",
        "weapon_skin": "Weapon Skin",
        "accessory": "Accessory"
    }
    category_value = category_map.get(category_key)
    if not category_value:
        ui.display_message("Invalid category.")
        return
    inventory = appearance_manager.get_inventory_summary().get(category_value, [])
    if not inventory:
        ui.display_message(f"No items available for {category_value}.")
        return
    ui.display_message(f"Available {category_value} items: {', '.join(inventory)}")
    item_name = input("Enter item name to equip: ").strip()
    if not appearance_manager.equip_item(item_name):
        ui.display_message("Could not equip item.")


def show_world_map_menu(player, world_map, traversal_system, world_state, ui):
    while True:
        ui.display_message("--- World Map Menu ---")
        ui.display_message(f"Player Position: {player.position}")
        ui.display_message(f"Traversal Mode: {traversal_system.get_current_mode().value}")
        ui.display_message(f"Stamina: {traversal_system.stamina:.1f}/{traversal_system.max_stamina}")
        ui.display_message("1. Move Player")
        ui.display_message("2. Switch Traversal Mode")
        ui.display_message("3. Use Nearby Traversal Node")
        ui.display_message("4. Show Active Combat Cells")
        ui.display_message("5. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            direction = input("Direction (up, down, left, right, forward, back): ").strip().lower()
            player.move(direction)
            world_state.update_world_state(player.position, player)
            traversal_system.update_nearby_nodes(player.position)
            traversal_system.update_stamina(1.0)
        elif choice == "2":
            ui.display_message("Available modes: ground, jump, air_glide, air_fly, climb, skill_based")
            mode_input = input("Mode: ").strip().lower()
            try:
                mode = TraversalMode(mode_input)
                if not traversal_system.set_traversal_mode(mode):
                    ui.display_message("Cannot switch to that mode now.")
            except ValueError:
                ui.display_message("Invalid traversal mode.")
        elif choice == "3":
            if not traversal_system.active_nodes_nearby:
                ui.display_message("No traversal nodes nearby.")
                continue
            for i, node in enumerate(traversal_system.active_nodes_nearby, 1):
                ui.display_message(f"{i}. {node.node_id} ({node.node_type}) - Cost: {node.energy_cost}")
            choice_num = input("Choose node to use: ").strip()
            try:
                index = int(choice_num) - 1
                if 0 <= index < len(traversal_system.active_nodes_nearby):
                    node = traversal_system.active_nodes_nearby[index]
                    traversal_system.use_traversal_node(node)
                else:
                    ui.display_message("Invalid node choice.")
            except ValueError:
                ui.display_message("Invalid choice.")
        elif choice == "4":
            cells = world_map.get_active_combat_cells()
            if not cells:
                ui.display_message("No active combat cells.")
            for cell in cells:
                ui.display_message(f"Cell {cell.cell_id} active; cleared: {cell.is_cleared}")
                ui.display_message(f"Height tiers: {[tier.name for tier in cell.height_tiers]}")
        elif choice == "5":
            break
        else:
            ui.display_message("Invalid choice.")


def show_interaction_menu(player, companions, dialogue_manager, ui):
    # US: Epic 9 - 3D Character Interactions
    while True:
        ui.display_message("--- Interaction Menu ---")
        ui.display_message(f"Player Position: {player.position}")
        for i, comp in enumerate(companions, 1):
            ui.display_message(f"{i}. Interact with {comp.name} at {comp.get_position()}")
        ui.display_message(f"{len(companions)+1}. Move Companions")
        ui.display_message(f"{len(companions)+2}. Back")
        choice = input("Choose: ").strip()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(companions):
                comp = companions[choice_num - 1]
                player.interact(comp)
            elif choice_num == len(companions) + 1:
                show_companion_movement_menu(companions, player, ui)
            elif choice_num == len(companions) + 2:
                break
            else:
                ui.display_message("Invalid choice.")
        except ValueError:
            ui.display_message("Invalid choice.")

def show_companion_movement_menu(companions, player, ui):
    while True:
        ui.display_message("--- Companion Movement ---")
        for i, comp in enumerate(companions, 1):
            ui.display_message(f"{i}. {comp.name} - State: {comp.state}")
        ui.display_message(f"{len(companions)+1}. Back")
        choice = input("Choose companion to command: ").strip()
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(companions):
                comp = companions[choice_num - 1]
                command = input("Command (follow, stop, move <direction>): ").strip().lower()
                if command == "follow":
                    # Assume player is target, but for simplicity, just toggle
                    if comp.state == "following":
                        comp.stop_following()
                    else:
                        comp.follow(player)
                elif command == "stop":
                    comp.stop_following()
                elif command.startswith("move"):
                    parts = command.split()
                    if len(parts) > 1:
                        comp.move(parts[1])
        except ValueError:
            ui.display_message("Invalid choice.")

def show_pvp_menu(pvp_menu, player):
    """PvP Arena menu with Free Mode and Practice options."""
    while True:
        pvp_menu.display_current_menu()
        choice = input("Choose: ").strip()
        next_menu = pvp_menu.handle_input(choice)
        
        if next_menu is None:
            break
        elif next_menu != "main":
            pvp_menu.current_menu = next_menu

def show_daily_missions_menu(daily_mission_manager, ui):
    """Daily Missions overview and management menu."""
    while True:
        status = daily_mission_manager.get_completion_status()
        missions = status["missions"]
        
        print("\n--- Daily Missions ---")
        print(f"Completed: {status['completed_count']}/{status['total_count']}")
        if status["all_completed"] and not status["bonus_claimed"]:
            print("🎉 All missions completed! Bonus available.")
        elif status["bonus_claimed"]:
            print("✅ Bonus claimed!")
        
        for i, mission in enumerate(missions, 1):
            status_icon = "✅" if mission.completed else "⏳"
            claim_icon = "💰" if mission.completed and not mission.claimed else ""
            optional_icon = "(Optional)" if mission.optional else ""
            progress = f"{mission.progress}/{mission.target}"
            print(f"{i}. {status_icon} {mission.title} {optional_icon}")
            print(f"   {mission.description} - Progress: {progress} {claim_icon}")
            if mission.reward.currency:
                print(f"   Reward: {mission.reward.amount} {mission.reward.currency}")
        
        print("\nOptions:")
        print("1-5. Claim reward for mission")
        print("6. Claim completion bonus")
        print("7. Back to main menu")
        
        choice = input("Choose: ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            idx = int(choice) - 1
            if idx < len(missions):
                mission = missions[idx]
                if mission.completed and not mission.claimed:
                    if daily_mission_manager.claim_reward(mission.id):
                        ui.display_message(f"Claimed reward: {mission.reward.amount} {mission.reward.currency}")
                    else:
                        ui.display_message("Failed to claim reward.")
                else:
                    ui.display_message("Mission not completed or already claimed.")
            else:
                ui.display_message("Invalid mission number.")
        elif choice == "6":
            if daily_mission_manager.claim_completion_bonus():
                ui.display_message("Claimed completion bonus: 100 Gacha Gems!")
            else:
                ui.display_message("Bonus not available.")
        elif choice == "7":
            break
        else:
            ui.display_message("Invalid choice.")

if __name__ == "__main__":
    main()