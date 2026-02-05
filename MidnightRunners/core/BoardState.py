import copy
from enum import Enum

from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.Track import Track
from MidnightRunners.core.Player import Player
from MidnightRunners.core.Turn import TurnPhase

class BoardState:
    def __init__(self, num_players: int, track: Track, player_to_racer_name_map: dict):
        self.track = track

        self.turn_order = [Player.P1, Player.P2, Player.P3, Player.P4, Player.P5, Player.P6][:num_players]
        self.current_turn_phase = TurnPhase.PH0_BETWEEN_TURNS
        self.current_turn_number = 0
        self.player_to_racer_name_map = player_to_racer_name_map

        self.first_place_racer = None
        self.second_place_racer = None
        self.eliminated_racers = set()
        self.race_is_finished = False
        self.pts_reward_first_place = 3
        self.pts_reward_second_place = 1

        self.racer_name_to_position_map = {racer: 0 for racer in player_to_racer_name_map.values()}
        self.racer_trip_map = {racer: False for racer in player_to_racer_name_map.values()}
        self.player_points_map = {player: 0 for player in self.turn_order}

    def __eq__(self, other: BoardState):
        if not isinstance(other, BoardState):
            return NotImplemented
        return (
            self.turn_order == other.turn_order and
            self.current_turn_phase == other.current_turn_phase and
            self.player_to_racer_name_map == other.player_to_racer_name_map and
            self.first_place_racer == other.first_place_racer and
            self.second_place_racer == other.second_place_racer and
            self.race_is_finished == other.race_is_finished and
            self.racer_name_to_position_map == other.racer_name_to_position_map and
            self.racer_trip_map == other.racer_trip_map and
            self.player_points_map == other.player_points_map
        )

    def apply_change_list(self, changes: list):
        """Apply a list of changes to the board state."""
        for change in changes:
            for pos_change in change.position_changes:
                self.racer_name_to_position_map[pos_change.racer_name] = pos_change.new_position
            for trip_change in change.trip_changes:
                self.racer_trip_map[trip_change.racer_name] = trip_change.tripped_after
            for eliminate_change in change.eliminate_changes:
                # TODO: Set eliminated racers' positions to something like -2 so we can still display them on the board in a different section
                self.eliminated_racers.add(eliminate_change.racer_name)
            for point_change in change.point_changes:
                self.player_points_map[point_change.player] += point_change.points_delta
            for turn_phase_change in change.turn_phase_changes:
                self.current_turn_phase = turn_phase_change.new_phase
                if turn_phase_change.new_phase == TurnPhase.PH1_START_OF_TURN:
                    self.current_turn_number += 1
            for turn_sequence_change in change.turn_sequence_changes:
                self.turn_order = list(turn_sequence_change.new_turn_order)
            for finished_racer in change.finished_racers:
                if self.first_place_racer == None:
                    self.first_place_racer = finished_racer
                    self.player_points_map[self.get_player_by_racer(finished_racer)] += self.pts_reward_first_place
                elif self.second_place_racer == None:
                    self.second_place_racer = finished_racer
                    self.player_points_map[self.get_player_by_racer(finished_racer)] += self.pts_reward_second_place
                self.race_is_finished = (self.first_place_racer is not None) and (self.second_place_racer is not None)
                self.racer_name_to_position_map[finished_racer] = -1  # Indicate finished racers with position -1

    def get_player_by_racer(self, racer_name: RacerName) -> Player:
        """Get the player corresponding to the given racer name."""
        for player, r_name in self.player_to_racer_name_map.items():
            if r_name == racer_name:
                return player
        return None