"""
PvP Matchmaking - Handles matchmaking for Free Mode (MVP).
Simple MMR-agnostic matching for now, with infrastructure for future Ladder mode.
"""

import random
import time
from typing import List, Optional, Tuple, Dict
from enum import Enum

from .pvp_match_manager import PvPMatchManager, MatchMode


class MatchmakingMode(Enum):
    """Matchmaking strategy."""
    CASUAL = "casual"          # Free Mode: loose matching
    RANKED = "ranked"          # Ladder: strict MMR-based
    PRACTICE = "practice"      # Solo vs AI


class AIOpponent:
    """Represents an AI-controlled opponent for practice matches."""
    
    def __init__(self, name: str, level: int = 5):
        self.name = name
        self.level = level
        self.health = 60 + level * 10
        self.max_health = self.health
        self.atk = 8 + level * 1
        self.defense = 3 + level * 1
        self.position = (0, 10, 0)
        self.skills = ["Fireball", "Power Slash"]
        self.current_weapon = None
        self.dialogue_state = None
        self.interaction_cooldown = 0
        
        # AI-specific
        self.ai_strategy = random.choice(["aggressive", "defensive", "balanced"])
        self.action_delay = random.uniform(0.5, 1.5)

    def update_cooldowns(self):
        """Stub for compatibility."""
        pass

    def to_dict(self):
        """Serialize AI opponent."""
        return {
            "name": self.name,
            "level": self.level,
            "strategy": self.ai_strategy,
        }


class PvPMatchmaker:
    """Handles matchmaking for PvP matches."""
    
    def __init__(self):
        self.queues = {
            MatchmakingMode.CASUAL: [],
            MatchmakingMode.PRACTICE: [],
        }
        self.active_matches: List[PvPMatchManager] = []
        self.match_history: List[Dict] = []

    def queue_for_match(self, player, mode: MatchmakingMode = MatchmakingMode.CASUAL,
                       team_size: int = 1, ui_feedback=None) -> Tuple[bool, str]:
        """
        Queue player for a match.
        
        Args:
            player: Player object
            mode: Matchmaking mode (casual or practice)
            team_size: 1v1, 2v2, or 3v3 (MVP only supports 1v1)
            ui_feedback: UI feedback manager
        
        Returns:
            (success, message)
        """
        if team_size != 1:
            return False, "MVP only supports 1v1 matches"
        
        if mode == MatchmakingMode.PRACTICE:
            # Create immediate practice match vs AI
            ai_opponent = self._create_ai_opponent(player.level)
            match = self._create_match([player], [ai_opponent], mode, ui_feedback)
            match.start_match()
            self.active_matches.append(match)
            return True, f"Practice match started vs {ai_opponent.name} (AI)"
        
        elif mode == MatchmakingMode.CASUAL:
            # Add to queue and check if we can form a match
            self.queues[mode].append({
                "player": player,
                "queued_time": time.time(),
                "ui": ui_feedback,
            })
            
            # Try to match if we have enough players
            if len(self.queues[mode]) >= 2:  # For 1v1, we need 2 players
                return self._attempt_match_casual()
            
            return True, "Queued for casual match..."
        
        return False, "Invalid matchmaking mode"

    def _create_ai_opponent(self, player_level: int) -> AIOpponent:
        """Create an AI opponent based on player level."""
        # Simple scaling - AI level is close to player level
        ai_level = max(1, player_level + random.randint(-1, 2))
        ai_names = ["Shadow", "Echo", "Specter", "Phantom", "Wraith"]
        return AIOpponent(random.choice(ai_names), ai_level)

    def _attempt_match_casual(self) -> Tuple[bool, str]:
        """Try to form a casual match from queued players."""
        queue = self.queues[MatchmakingMode.CASUAL]
        
        if len(queue) < 2:
            return False, "Not enough players queued"
        
        # Simple matching: take first two from queue
        player1_data = queue.pop(0)
        player2_data = queue.pop(0)
        
        player1 = player1_data["player"]
        player2 = player2_data["player"]
        ui = player1_data["ui"] or player2_data["ui"]
        
        # Create match
        match = self._create_match([player1], [player2], MatchmakingMode.CASUAL, ui)
        match.start_match()
        self.active_matches.append(match)
        
        if ui:
            ui.display_message(f"Match found! Starting 1v1 vs {player2.name}")
        
        return True, "Match found and started!"

    def _create_match(self, player_team: List, opponent_team: List, mode: MatchmakingMode,
                     ui_feedback=None) -> PvPMatchManager:
        """Create a new PvP match."""
        pvp_mode = MatchMode.FREE if mode == MatchmakingMode.CASUAL or mode == MatchmakingMode.PRACTICE else MatchMode.LADDER
        
        match = PvPMatchManager(
            player_team=player_team,
            opponent_team=opponent_team,
            mode=pvp_mode,
            ui_feedback=ui_feedback,
            currency_manager=player_team[0].currency_manager if player_team else None
        )
        
        return match

    def update_matches(self):
        """Update all active matches."""
        for match in self.active_matches:
            match.update()
            
            # Remove ended matches
            if match.match_state.value == "ended":
                self._process_match_result(match)

    def _process_match_result(self, match: PvPMatchManager):
        """Process match results and rewards."""
        # Store in history
        self.match_history.append({
            "timestamp": time.time(),
            "mode": match.mode.value,
            "player_score": match.player_team.score,
            "opponent_score": match.opponent_team.score,
            "winner": "player" if match.player_team.score > match.opponent_team.score else "opponent",
            "duration": match.match_duration,
        })
        
        # Award rewards to player
        player = match.player_team.players[0]
        
        # Practice mode rewards: no currency
        if match.mode == MatchMode.FREE:
            # Small currency reward for participation
            base_reward = 50
            if match.player_team.score > match.opponent_team.score:
                reward = int(base_reward * 1.5)  # 75 for win
                if player.currency_manager:
                    player.currency_manager.add_currency("Practice Currency", reward)
            else:
                reward = base_reward  # 50 for loss
                if player.currency_manager:
                    player.currency_manager.add_currency("Practice Currency", reward)
            
            if player.ui:
                player.ui.display_message(f"Match Complete! Earned {reward} Practice Currency")
        
        # Remove from active matches
        self.active_matches.remove(match)

    def get_queue_size(self, mode: MatchmakingMode) -> int:
        """Get number of players in queue."""
        return len(self.queues.get(mode, []))

    def get_active_matches_count(self) -> int:
        """Get number of ongoing matches."""
        return len(self.active_matches)

    def get_match_history(self, limit: int = 10) -> List[Dict]:
        """Get recent match history."""
        return self.match_history[-limit:]

    def to_dict(self) -> Dict:
        """Serialize matchmaker state."""
        return {
            "casual_queue": len(self.queues[MatchmakingMode.CASUAL]),
            "active_matches": len(self.active_matches),
            "match_history": self.get_match_history(),
        }
