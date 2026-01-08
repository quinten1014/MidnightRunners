"""
Track class for the board game.
"""

from typing import Optional
from .space import Space


class Track:
    """Represents a linear game track."""

    def __init__(self, num_spaces: int):
        """
        Initialize a linear track.
        
        Args:
            num_spaces: Number of spaces in the track
        """
        self.num_spaces = num_spaces
        self.spaces: dict[int, Space] = {}
        self._initialize_spaces()

    def _initialize_spaces(self) -> None:
        """Create spaces for the track."""
        for space_id in range(self.num_spaces):
            self.spaces[space_id] = Space(space_id, "normal")

    def get_space(self, space_id: int) -> Optional[Space]:
        """Get a space by ID."""
        return self.spaces.get(space_id)

    def get_total_spaces(self) -> int:
        """Get the total number of spaces on the track."""
        return len(self.spaces)

    def set_space_type(self, space_id: int, space_type: str) -> None:
        """Change the type of a space."""
        if space_id in self.spaces:
            self.spaces[space_id].space_type = space_type

    def __repr__(self) -> str:
        return f"Track({self.num_spaces} spaces)"
