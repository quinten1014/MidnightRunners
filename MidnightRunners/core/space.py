"""
Space class for the board game.
"""

from typing import Optional, List


class Space:
    """Represents a single space on the track."""

    def __init__(self, space_id: int, space_type: str):
        """
        Initialize a space.
        
        Args:
            space_id: Unique identifier for the space
            space_type: Type of space (e.g., "normal", "special", "safe")
        """
        self.space_id = space_id
        self.space_type = space_type
        self.occupied_by: List[int] = []  # List of piece IDs
        self.properties = {}  # Extensible properties dict

    def add_piece(self, piece_id: int) -> None:
        """Add a piece to this space."""
        if piece_id not in self.occupied_by:
            self.occupied_by.append(piece_id)

    def remove_piece(self, piece_id: int) -> None:
        """Remove a piece from this space."""
        if piece_id in self.occupied_by:
            self.occupied_by.remove(piece_id)

    def is_empty(self) -> bool:
        """Check if the space is unoccupied."""
        return len(self.occupied_by) == 0

    def set_property(self, key: str, value) -> None:
        """Set a custom property for this space."""
        self.properties[key] = value

    def get_property(self, key: str, default=None):
        """Get a custom property from this space."""
        return self.properties.get(key, default)

    def __repr__(self) -> str:
        return f"Space({self.space_id}, {self.space_type}, occupied={len(self.occupied_by)})"
