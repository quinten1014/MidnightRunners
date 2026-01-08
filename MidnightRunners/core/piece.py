"""
Piece class for the board game.
"""

from typing import Optional


class Piece:
    """Represents a game piece (token, pawn, etc.)."""

    def __init__(self, piece_id: int, piece_type: str, player_id: int):
        """
        Initialize a piece.
        
        Args:
            piece_id: Unique identifier for the piece
            piece_type: Type of piece (e.g., "pawn", "runner")
            player_id: ID of the player who owns this piece
        """
        self.piece_id = piece_id
        self.piece_type = piece_type
        self.player_id = player_id
        self.tile_id: Optional[int] = None  # Current position on board
        self.is_active = True

    def move_to(self, tile_id: int) -> None:
        """Move the piece to a specific tile."""
        self.tile_id = tile_id

    def __repr__(self) -> str:
        return f"Piece({self.piece_id}, {self.piece_type}, player={self.player_id})"
