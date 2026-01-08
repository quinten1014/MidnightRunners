"""
Player class for the board game.
"""

from typing import List
from .piece import Piece


class Player:
    """Represents a player in the board game."""

    def __init__(self, player_id: int, name: str):
        """
        Initialize a player.
        
        Args:
            player_id: Unique identifier for the player
            name: Player's display name
        """
        self.player_id = player_id
        self.name = name
        self.pieces: List[Piece] = []
        self.score = 0
        self.is_active = False

    def add_piece(self, piece: "Piece") -> None:
        """Add a piece to the player's collection."""
        self.pieces.append(piece)

    def remove_piece(self, piece: "Piece") -> None:
        """Remove a piece from the player's collection."""
        if piece in self.pieces:
            self.pieces.remove(piece)

    def add_score(self, points: int) -> None:
        """Add points to the player's score."""
        self.score += points

    def __repr__(self) -> str:
        return f"Player({self.player_id}, {self.name}, score={self.score})"
