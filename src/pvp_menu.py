"""
PvP Menu - UI for accessing PvP Free Mode and Ladder (future).
Integrates with Page Manager for seamless navigation.
"""

from typing import Dict, Optional
from .pvp_matchmaking import PvPMatchmaker, MatchmakingMode


class PvPMenu:
    """PvP main menu and mode selection."""
    
    def __init__(self, ui_feedback, player, matchmaker: PvPMatchmaker):
        self.ui = ui_feedback
        self.player = player
        self.matchmaker = matchmaker
        self.current_menu = "main"

    def display_main_menu(self):
        """Display PvP main menu."""
        self.current_menu = "main"
        self.ui.display_message("\n" + "="*40)
        self.ui.display_message("⚔️ PVP ARENA ⚔️")
        self.ui.display_message("="*40)
        self.ui.display_message("1. Free Mode (Unranked)")
        self.ui.display_message("2. Practice Mode (vs AI)")
        self.ui.display_message("3. Match History")
        self.ui.display_message("4. Back to Main Menu")
        self.ui.display_message("="*40)

    def display_free_mode_menu(self):
        """Display Free Mode options."""
        self.current_menu = "free_mode"
        self.ui.display_message("\n" + "="*40)
        self.ui.display_message("FREE MODE - UNRANKED")
        self.ui.display_message("="*40)
        self.ui.display_message("Practice, test builds, no risk!")
        self.ui.display_message(f"\nQueue Status: {self.matchmaker.get_queue_size(MatchmakingMode.CASUAL)} player(s)")
        self.ui.display_message("\n1. Queue for 1v1")
        self.ui.display_message("2. Back")
        self.ui.display_message("="*40)

    def display_practice_mode_menu(self):
        """Display Practice Mode options."""
        self.current_menu = "practice"
        self.ui.display_message("\n" + "="*40)
        self.ui.display_message("PRACTICE MODE - vs AI")
        self.ui.display_message("="*40)
        self.ui.display_message("Hone your skills against AI opponents")
        self.ui.display_message(f"Your Level: {self.player.level}")
        self.ui.display_message("\n1. Start Practice Match")
        self.ui.display_message("2. Back")
        self.ui.display_message("="*40)

    def display_match_history(self):
        """Display player's recent match history."""
        self.current_menu = "history"
        history = self.matchmaker.get_match_history(limit=10)
        
        self.ui.display_message("\n" + "="*40)
        self.ui.display_message("MATCH HISTORY")
        self.ui.display_message("="*40)
        
        if not history:
            self.ui.display_message("No matches yet. Play your first match!")
        else:
            for i, match in enumerate(history, 1):
                result_emoji = "✓" if match["winner"] == "player" else "✗"
                self.ui.display_message(
                    f"{i}. {result_emoji} {match['player_score']} - {match['opponent_score']} "
                    f"({match['mode']}) {match['duration']:.1f}s"
                )
        
        self.ui.display_message("\n1. Back to PvP Menu")
        self.ui.display_message("="*40)

    def handle_input(self, choice: str):
        """
        Handle user menu selection.
        
        Returns:
            str: Next menu to display, or None if action handled
        """
        if self.current_menu == "main":
            if choice == "1":
                return "free_mode"
            elif choice == "2":
                return "practice"
            elif choice == "3":
                return "history"
            elif choice == "4":
                return None  # Back to main
            else:
                self.ui.display_message("Invalid choice")
                return None

        elif self.current_menu == "free_mode":
            if choice == "1":
                self._queue_free_mode()
                return None
            elif choice == "2":
                return "main"
            else:
                self.ui.display_message("Invalid choice")
                return None

        elif self.current_menu == "practice":
            if choice == "1":
                self._start_practice_match()
                return None
            elif choice == "2":
                return "main"
            else:
                self.ui.display_message("Invalid choice")
                return None

        elif self.current_menu == "history":
            if choice == "1":
                return "main"
            else:
                self.ui.display_message("Invalid choice")
                return None

        return None

    def _queue_free_mode(self):
        """Queue player for Free Mode match."""
        success, message = self.matchmaker.queue_for_match(
            self.player,
            mode=MatchmakingMode.CASUAL,
            team_size=1,
            ui_feedback=self.ui
        )
        
        if success:
            self.ui.display_message(message)
            # Check if match was created
            if self.matchmaker.get_active_matches_count() > 0:
                self.ui.display_message("Match starting...")
        else:
            self.ui.display_message(f"Queue failed: {message}")

    def _start_practice_match(self):
        """Start a practice match vs AI."""
        success, message = self.matchmaker.queue_for_match(
            self.player,
            mode=MatchmakingMode.PRACTICE,
            team_size=1,
            ui_feedback=self.ui
        )
        
        if success:
            self.ui.display_message(message)
        else:
            self.ui.display_message(f"Failed to start: {message}")

    def display_current_menu(self):
        """Display the current menu."""
        if self.current_menu == "main":
            self.display_main_menu()
        elif self.current_menu == "free_mode":
            self.display_free_mode_menu()
        elif self.current_menu == "practice":
            self.display_practice_mode_menu()
        elif self.current_menu == "history":
            self.display_match_history()

    def to_dict(self) -> Dict:
        """Serialize menu state."""
        return {
            "current_menu": self.current_menu,
            "queue_size": self.matchmaker.get_queue_size(MatchmakingMode.CASUAL),
            "active_matches": self.matchmaker.get_active_matches_count(),
        }
