"""
BoardState class for managing state of track and racers during a race.
"""

import copy
from enum import Enum

from MidnightRunners.concreteracers.ConcreteRacerNames import RacerName
from MidnightRunners.core.Track import Track
from MidnightRunners.core.Player import Player

class BoardState:
    def __init__(self, num_players: int, track: Track, player_to_racer_name_map: dict):
        self.num_players = num_players
        self.track = track

        self.turn_order = [Player.P1, Player.P2, Player.P3, Player.P4, Player.P5, Player.P6][:num_players]
        self.current_turn_index = 0
        self.player_to_racer_name_map = player_to_racer_name_map

        self.racer_name_to_position_map = {racer: 0 for racer in player_to_racer_name_map.values()}

    def move_racer_to_space(self, racer_name: RacerName, target_space: int):
        """Move the specified racer to the given target space."""
        if racer_name in self.racer_name_to_position_map:
            # Ensure within track bounds
            target_space = max(0, min(target_space, Track.FIXED_TRACK_LENGTH))
            self.racer_name_to_position_map[racer_name] = target_space