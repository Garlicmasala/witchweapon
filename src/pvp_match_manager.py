"""
PvP Match Manager - Main orchestrator for PvP matches.
Manages match state, teams, score, and win conditions.
"""

import time
from typing import List, Dict, Optional, Tuple
from enum import Enum
from copy import deepcopy

from .pvp_ruleset import PvPRuleset
from .pvp_arena import Arena, ArenaSize, ArenaRegistry
from .pvp_buff_director import BuffDirector


class MatchState(Enum):
    """Match lifecycle states."""
    STARTING = "starting"      # Pre-match (10s)
    ACTIVE = "active"          # Combat ongoing
    OVERTIME = "overtime"      # Sudden death
    ENDED = "ended"            # Match complete


class MatchMode(Enum):
    """Match modes."""
    FREE = "free"              # Unranked, no point changes
    LADDER = "ladder"          # Ranked, points awarded


class Team:
    """Represents a team in the match."""
    
    def __init__(self, team_id: int, players: List, arena: Arena):
        self.team_id = team_id
        self.players = players  # List of Player objects
        self.arena = arena
        self.score = 0
        self.eliminations = 0
        self.deaths = 0
        self.active_players = set(p.name for p in players)

    def get_alive_players(self) -> List:
        """Get players still in the match."""
        return [p for p in self.players if p.name in self.active_players and p.health > 0]

    def is_eliminated(self) -> bool:
        """Check if entire team is defeated."""
        return len(self.get_alive_players()) == 0

    def eliminate_player(self, player_name: str):
        """Mark player as eliminated."""
        if player_name in self.active_players:
            self.active_players.discard(player_name)
            self.deaths += 1

    def add_score(self, points: int):
        """Add points to team score."""
        self.score += points

    def to_dict(self) -> Dict:
        """Serialize team state."""
        return {
            "team_id": self.team_id,
            "players": [p.name for p in self.players],
            "alive_players": list(self.active_players),
            "score": self.score,
            "eliminations": self.eliminations,
            "deaths": self.deaths,
        }


class PvPMatchManager:
    """Main match orchestrator."""
    
    def __init__(self, player_team: List, opponent_team: List, mode: MatchMode = MatchMode.FREE,
                 arena: Optional[Arena] = None, ui_feedback=None, currency_manager=None):
        self.player_team = Team(0, player_team, arena or self._get_default_arena(len(player_team)))
        self.opponent_team = Team(1, opponent_team, self.player_team.arena)
        
        self.mode = mode
        self.arena = self.player_team.arena
        self.ui = ui_feedback
        self.currency_manager = currency_manager
        
        # Match timeline
        self.match_state = MatchState.STARTING
        self.match_start_time = time.time()
        self.match_duration = 0.0  # Elapsed match time
        self.max_match_duration = 5 * 60  # 5 minutes
        self.overtime_duration = 0.0
        self.max_overtime = 2 * 60  # 2 minute overtime
        
        # Gameplay
        self.ruleset = PvPRuleset()
        self.buff_director = BuffDirector(self.arena, "free" if mode == MatchMode.FREE else "ladder")
        self.turn_count = 0
        
        # Match data
        self.kill_log: List[Dict] = []
        self.round_end_reason = None

    def _get_default_arena(self, team_size: int) -> Arena:
        """Select arena based on team size."""
        if team_size == 1:
            return ArenaRegistry.get_arena_for_size(ArenaSize.SMALL) or ArenaRegistry.get_arena("Crystal Spire")
        elif team_size == 2:
            return ArenaRegistry.get_arena_for_size(ArenaSize.MEDIUM) or ArenaRegistry.get_arena("Ancient Colosseum")
        else:
            return ArenaRegistry.get_arena_for_size(ArenaSize.LARGE) or ArenaRegistry.get_arena("Void Expanse")

    def start_match(self):
        """Initialize and start the match."""
        # Place teams at spawn points
        for i, player in enumerate(self.player_team.players):
            spawn = self.arena.get_spawn_point(0, i)
            if hasattr(player, 'movement'):
                player.movement.set_position(spawn)
            else:
                # Fallback for testing
                player.position = spawn
        
        for i, player in enumerate(self.opponent_team.players):
            spawn = self.arena.get_spawn_point(1, i)
            if hasattr(player, 'movement'):
                player.movement.set_position(spawn)
            else:
                player.position = spawn
        
        # Reset health
        for player in self.player_team.players + self.opponent_team.players:
            player.health = player.max_health
        
        self.match_state = MatchState.ACTIVE
        if self.ui:
            self.ui.display_message("Match started! Fight!")

    def update(self, delta_time: float = 0.016):
        """
        Main match update loop.
        
        Args:
            delta_time: Time since last update (default 60 FPS = 0.016s)
        """
        if self.match_state == MatchState.ENDED:
            return
        
        self.match_duration = time.time() - self.match_start_time
        self.turn_count += 1
        
        # Update buffs
        losing_team_boost = self._get_losing_team() is not None
        self.buff_director.update(self.match_duration, losing_team_boost)
        
        # Update player states (health regen, cooldowns, etc)
        self._update_players()
        
        # Apply active buff effects
        self._apply_buff_effects()
        
        # Check win conditions
        self._check_win_conditions()

    def _update_players(self):
        """Update player state each turn."""
        for team in [self.player_team, self.opponent_team]:
            for player in team.players:
                if player.health <= 0:
                    team.eliminate_player(player.name)
                # Update cooldowns
                if hasattr(player, 'update_cooldowns'):
                    player.update_cooldowns()
                # Update weapon durations
                if hasattr(player, 'weapon_manager') and hasattr(player.weapon_manager, 'update_durations'):
                    player.weapon_manager.update_durations()
                # Update skill cooldowns
                if hasattr(player, 'skill_system') and hasattr(player.skill_system, 'update_cooldowns'):
                    player.skill_system.update_cooldowns()

    def _apply_buff_effects(self):
        """Apply active buff effects to players."""
        for team in [self.player_team, self.opponent_team]:
            for player in team.get_alive_players():
                # Get buffs claimed by this player
                buff_status = self.buff_director.get_buff_status(player.name)
                
                # Apply each buff's effects
                for buff_id, buff in self.buff_director.active_buffs.items():
                    if buff.claimed_by == player.name:
                        # Apply effects (simplified)
                        if "hp_regen_per_second" in buff.effects:
                            regen = buff.effects["hp_regen_per_second"] * 0.016  # Per frame
                            player.health = min(player.max_health, player.health + regen)
                        
                        # Add more effect applications as match complexity grows

    def _check_win_conditions(self):
        """Check if match should end."""
        # Check time limit
        if self.match_duration >= self.max_match_duration:
            if self.player_team.score == self.opponent_team.score:
                self.match_state = MatchState.OVERTIME
            else:
                self._end_match()
                return
        
        # Check team elimination
        if self.player_team.is_eliminated():
            self._end_match("opponent_eliminated_player_team")
            return
        
        if self.opponent_team.is_eliminated():
            self._end_match("player_team_eliminated_opponent")
            return
        
        # Check overtime limit
        if self.match_state == MatchState.OVERTIME:
            self.overtime_duration = self.match_duration - self.max_match_duration
            if self.overtime_duration >= self.max_overtime:
                self._end_match("overtime_limit")
                return

    def _end_match(self, reason: str = "normal"):
        """End the match and calculate results."""
        self.match_state = MatchState.ENDED
        self.round_end_reason = reason
        
        if self.ui:
            self._display_match_result()

    def _get_losing_team(self) -> Optional[Team]:
        """Identify the losing team for comeback buffs."""
        if self.player_team.score < self.opponent_team.score:
            return self.player_team
        elif self.opponent_team.score < self.player_team.score:
            return self.opponent_team
        return None

    def _display_match_result(self):
        """Show match results to player."""
        player_team_alive = len(self.player_team.get_alive_players()) > 0
        opponent_team_alive = len(self.opponent_team.get_alive_players()) > 0
        
        if player_team_alive and not opponent_team_alive:
            self.ui.display_message("=== VICTORY ===")
            self.ui.display_message(f"Final Score: {self.player_team.score} - {self.opponent_team.score}")
        elif opponent_team_alive and not player_team_alive:
            self.ui.display_message("=== DEFEAT ===")
            self.ui.display_message(f"Final Score: {self.player_team.score} - {self.opponent_team.score}")
        else:
            if self.player_team.score > self.opponent_team.score:
                self.ui.display_message("=== VICTORY ===")
            elif self.opponent_team.score > self.player_team.score:
                self.ui.display_message("=== DEFEAT ===")
            else:
                self.ui.display_message("=== DRAW ===")
            self.ui.display_message(f"Final Score: {self.player_team.score} - {self.opponent_team.score}")

    def get_match_state(self) -> Dict:
        """Serialize current match state."""
        return {
            "state": self.match_state.value,
            "duration": self.match_duration,
            "player_team": self.player_team.to_dict(),
            "opponent_team": self.opponent_team.to_dict(),
            "buffs": self.buff_director.get_active_buffs(),
            "debuffs": self.buff_director.get_debuff_zones(),
            "turn": self.turn_count,
        }

    def to_dict(self) -> Dict:
        """Serialize entire match for persistence."""
        return {
            "mode": self.mode.value,
            "arena": self.arena.name,
            "state": self.get_match_state(),
            "ruleset": self.ruleset.to_dict(),
            "kill_log": self.kill_log,
        }
