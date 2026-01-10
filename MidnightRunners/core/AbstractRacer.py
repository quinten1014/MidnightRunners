"""
AbstractRacer class for representing generic racers in a race.
"""

import random

from MidnightRunners.core.BoardState import BoardState

class AbstractRacer:
    def __init__(self, name: str):
        self.name = name
        self.tripped = False

    def before_race_effect(self, board_state) -> BoardState:
        """Trigger any before-race effects this racer may have."""
        # Note that by default, racers are already placed on the start (0) space
        return board_state

    def main_move(self, board_state) -> BoardState:
        """Default main move is just rolling D6 and moving forward that many spaces."""
        if self.tripped:
            # If tripped, skip this turn and reset tripped status
            self.tripped = False
            return board_state
        else:
            roll = random.randint(1, 6)
            current_position = board_state.racer_name_to_position_map[self.name]
            new_position = current_position + roll
            # Ensure within track bounds
            new_position = max(0, min(new_position, board_state.track.FIXED_TRACK_LENGTH))
            board_state.racer_name_to_position_map[self.name] = new_position
        return board_state