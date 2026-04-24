# Witch's Weapon Combat System Simulation

A Python implementation of the Witch's Weapon combat system, adapted from Unity concepts to Python classes and simulations.

## Features

- Player movement and positioning
- Weapon management with slots and switching
- Auto-attack and targeting
- Skill system with cooldowns
- Ultimate abilities
- Enemy AI and states
- Damage calculation
- UI feedback via console
- Combat simulation loop
- Character level progression and EXP
- Weapon synchronization bonuses
- Affection/Bond system for weapons
- Stat enhancement system
- Breakthrough system for level caps
- Upgrade UI with previews and feedback
- Data persistence (save/load)
- Gacha draw system with banners
- Currency management for draws
- Rarity and drop rates
- Pity/guarantee system
- Duplicate handling and conversion
- 3D character interactions and movement
- Companion follow behavior and idle animations
- Dialogue system with scripted and LLM fallback
- Face-to-face dialogue and gestures
- Non-blocking ambient dialogue
- Cinematic dialogue locks

## How to Run

1. Ensure Python 3 is installed.
2. Clone or download the project.
3. Run `python main.py` from the project root.

The simulation will start, and you can input commands to control the player.

## Project Structure

- `src/`: Source code directory
  - `player.py`: Player class
  - `player_movement.py`: Movement mechanics
  - `enemy.py`: Enemy class
  - `weapon_manager.py`: Weapon management
  - `skill_system.py`: Skills and abilities
  - `combat_manager.py`: Combat logic
  - `ui_feedback.py`: User interface feedback
  - `upgrade_manager.py`: Upgrade system logic
  - `save_manager.py`: Data persistence
  - `gacha_manager.py`: Gacha draw system
  - `currency_manager.py`: Currency management
  - `companion.py`: Companion characters
  - `dialogue_manager.py`: Dialogue system
  - `llm_provider.py`: LLM fallback provider
- `main.py`: Entry point
- `requirements.txt`: Dependencies (none)
- `README.md`: This file

## User Stories Implemented

- As a player, I want to move in the game world...
- As a player, I want to switch weapons...
- As a player, I want auto-attack...
- As a player, I want my character to level up through combat...
- As a player, I want my character to become stronger when using well-upgraded weapons...
- As a player, I want to build affection with a weapon...
- As a player, I want to enhance my character stats using materials...
- As a player, I want to perform breakthroughs to exceed normal limits...
- As a player, I want to perform gacha draws to obtain new weapons...
- As a player, I want different banner types for varied draws...
- As a player, I want pity system for fair high-rarity chances...
- As a player, I want duplicates converted to useful materials...
- As a player, I want characters to perform idle movements...
- As a player, I want companions to follow me naturally...
- As a player, I want to trigger dialogues by approaching characters...
- As a player, I want face-to-face conversations...
- As a player, I want scripted dialogues with branches...
- As a player, I want LLM-generated dialogue as fallback...
- As a player, I want to move during ambient dialogues...
- And more, referenced in code comments.
