"""
Race class for setting up and performing turns until a race is done.
"""

from MidnightRunners.core.AbstractRacer import AbstractRacer
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.Track import TrackVersion, Track
from MidnightRunners.core.Player import Player

class Race:
    def __init__(self, track_version: TrackVersion, player_to_racer_map: dict):
        self.num_players = len(player_to_racer_map)
        self.player_to_racer_map = player_to_racer_map
        if track_version == TrackVersion.MILD:
            self.track = Track(TrackVersion.MILD)
        else:
            self.track = Track(TrackVersion.WILD)

        # Create map from player enum to racer name, which does not have the full Racer object
        player_to_racer_name_map = {player: racer.name for player, racer in player_to_racer_map.items()}
        self.board_state = BoardState(self.num_players, self.track, player_to_racer_name_map)

        self.turn_order = [Player.P1, Player.P2, Player.P3, Player.P4, Player.P5, Player.P6][:self.num_players]
        self.current_round = 0
        self.current_turn_index = 0

    def setup_race(self):
        """Put all racers in starting positions, trigger any before race effects."""
        self.board_state = self.board_state.trigger_before_race_powers(self.board_state)
        pass

    def trigger_before_race_powers(self) -> BoardState:
        """Trigger any before-race powers each racer may have."""
        for racer in self.player_to_racer_map.values():
            self.board_state = racer.before_race_effect(self.board_state)

    def execute_turn(self):
        """Execute the current player's turn."""
        current_player = self.turn_order[self.current_turn_index]
        current_racer = self.player_to_racer_map[current_player]

        pass

    def go_to_next_turn(self):
        """Update internal state to reflect moving to the next player's turn."""
        self.current_turn_index = (self.current_turn_index + 1) % self.num_players
        if self.current_turn_index == 0:
            self.current_round += 1