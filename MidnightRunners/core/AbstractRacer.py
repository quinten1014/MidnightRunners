"""
AbstractRacer class for representing generic racers in a race.
"""

from MidnightRunners.core.BoardState import BoardState

class AbstractRacer:
    def __init__(self, name: str):
        self.name = name

    def before_race_effect(self, board_state) -> BoardState:
        """Trigger any before-race effects this racer may have."""
        # Note that by default, racers are already placed on the start (0) space
        return board_state

    def main_move(self, board_state) -> BoardState:
        """Default main move is just rolling D6 and moving forward that many spaces."""
        # board_state.advance_racer(self, dice_roll=6)  # Placeholder for actual dice roll logic
        return board_state