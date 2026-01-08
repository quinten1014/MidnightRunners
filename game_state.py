"""
GameState class for managing game state.
"""

from enum import Enum
from typing import List
from .player import Player


class GamePhase(Enum):
    """Enum for different game phases."""
    SETUP = "setup"
    ACTIVE = "active"
    END = "end"
    FINISHED = "finished"


class GameState:
    """Manages the state of the game."""

    def __init__(self):
        """Initialize the game state."""
        self.phase = GamePhase.SETUP
        self.current_turn = 0
        self.current_player_index = 0
        self.players: List[Player] = []
        self.move_history: List[dict] = []

    def add_player(self, player: Player) -> None:
        """Add a player to the game."""
        self.players.append(player)

    def get_current_player(self) -> Player:
        """Get the currently active player."""
        if self.players:
            return self.players[self.current_player_index]
        return None

    def next_turn(self) -> None:
        """Advance to the next player's turn."""
        if self.players:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.current_turn += 1

    def set_phase(self, phase: GamePhase) -> None:
        """Set the current game phase."""
        self.phase = phase

    def record_move(self, player_id: int, action: str, details: dict) -> None:
        """Record a move in the game history."""
        self.move_history.append({
            "turn": self.current_turn,
            "player_id": player_id,
            "action": action,
            "details": details
        })

    def __repr__(self) -> str:
        return (f"GameState(phase={self.phase.value}, turn={self.current_turn}, "
                f"players={len(self.players)})")
