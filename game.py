"""
Main Game class for the board game.
"""

from typing import List, Optional
from .track import Track
from .player import Player
from .piece import Piece
from .game_state import GameState, GamePhase


class Game:
    """Main game class that orchestrates the board game."""

    def __init__(self, num_spaces: int = 50):
        """
        Initialize the game.
        
        Args:
            num_spaces: Number of spaces on the board track
        """
        self.track = Track(num_spaces)
        self.state = GameState()
        self.piece_counter = 0

    def add_player(self, name: str) -> Player:
        """
        Add a player to the game.
        
        Args:
            name: Player's name
            
        Returns:
            The created Player object
        """
        player_id = len(self.state.players)
        player = Player(player_id, name)
        self.state.add_player(player)
        return player

    def create_piece(self, player_id: int, piece_type: str = "pawn") -> Piece:
        """
        Create a piece for a player.
        
        Args:
            player_id: ID of the owning player
            piece_type: Type of piece to create
            
        Returns:
            The created Piece object
        """
        piece = Piece(self.piece_counter, piece_type, player_id)
        self.piece_counter += 1
        
        # Add to player
        player = self.state.players[player_id]
        player.add_piece(piece)
        
        return piece

    def start_game(self) -> None:
        """Start the game and change state to ACTIVE."""
        if self.state.players:
            self.state.set_phase(GamePhase.ACTIVE)
            self.state.players[0].is_active = True

    def end_turn(self) -> None:
        """End the current player's turn and move to the next player."""
        current_player = self.state.get_current_player()
        if current_player:
            current_player.is_active = False
            self.state.next_turn()
            next_player = self.state.get_current_player()
            if next_player:
                next_player.is_active = True

    def finish_game(self) -> None:
        """End the game."""
        self.state.set_phase(GamePhase.FINISHED)

    def get_player(self, player_id: int) -> Optional[Player]:
        """Get a player by ID."""
        if 0 <= player_id < len(self.state.players):
            return self.state.players[player_id]
        return None

    def get_player_score(self, player_id: int) -> int:
        """Get a player's current score."""
        player = self.get_player(player_id)
        return player.score if player else 0

    def __repr__(self) -> str:
        return (f"Game(track={self.track}, players={len(self.state.players)}, "
                f"phase={self.state.phase.value})")
