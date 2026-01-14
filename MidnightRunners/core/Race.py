"""
Race class for setting up and performing turns until a race is done.
"""

from copy import deepcopy
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardView import PrintBoardState, PrintChangeList, DisplayBoardAfterRace, DisplayRacerPositions
from MidnightRunners.core.AbstractRacer import AbstractRacer
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.StateChange import ChangeSet
from MidnightRunners.core.Track import TrackVersion, Track
from MidnightRunners.core.Player import Player
from MidnightRunners.core.Turn import GetNextTurnPhase, TurnPhase

num_turns_limit = 50  # Limit number of turns to avoid infinite loops

class Race:
    def __init__(self, track_version: TrackVersion, player_to_racer_map: dict):
        self.num_players = len(player_to_racer_map)
        self.player_to_racer_map = player_to_racer_map
        if track_version == TrackVersion.MILD:
            self.track = Track(TrackVersion.MILD)
        else:
            self.track = Track(TrackVersion.WILD)

        self.full_race_change_list = []
        self.current_turn_change_list = []

        # Create map from player enum to racer name, which does not have the full Racer object
        player_to_racer_name_map = {player: racer.name for player, racer in player_to_racer_map.items()}
        self.board_state = BoardState(self.num_players, self.track, player_to_racer_name_map)

        self.turn_order = [Player.P1, Player.P2, Player.P3, Player.P4, Player.P5, Player.P6][:self.num_players]
        self.num_turns_taken = 0

    def do_race(self):
        self.trigger_before_race_powers()
        self.full_race_change_list = []
        while (not self.board_state.race_is_finished) and self.num_turns_taken < num_turns_limit: # limit turns to avoid infinite loops
            changes = []
            changes.append(self.go_to_next_turn_phase(self.board_state.current_turn_phase))
            changes = self.check_triggers(changes)
            self.board_state.apply_change_list(changes)
            self.turn_order = list(self.board_state.turn_order)
            self.full_race_change_list.extend(changes)
            self.current_turn_change_list.extend(changes)
        self.go_to_next_turn()  # Finalize last turn
        DisplayBoardAfterRace(self.board_state)
        return self.full_race_change_list
        # GameGUI().test_window()

    def go_to_next_turn_phase(self, current_phase: TurnPhase) -> ChangeSet:
        """Advance to the next turn phase, returning a newly created Change object."""
        next_phase = GetNextTurnPhase(current_phase)
        phase_change = ChangeSet()

        # If next phase is BETWEEN_TURNS, also advance turn order
        if next_phase == TurnPhase.PH0_BETWEEN_TURNS:
            self.go_to_next_turn()
            phase_change.add_turn_sequence_change(self.turn_order)
            phase_change.add_message(f"Next turn: player {self.turn_order[0].name}")
            print(f"=== [Turn {self.num_turns_taken + 1}] Processing turn... ================================================")

        phase_change.add_message(f"Advancing turn phase from {current_phase.name} to {next_phase.name}.")
        phase_change.add_turn_phase_change(current_phase, next_phase)

        return phase_change

    def check_triggers(self, changes) -> list:
        """Check for any triggers based on the given change, return updated change list."""
        while True:
            any_changes_found = False
            for player in self.turn_order:
                racer = self.player_to_racer_map[player]
                # Don't process racers that have already finished or been eliminated
                if self.board_state.first_place_racer == racer or \
                   self.board_state.second_place_racer == racer or \
                   racer.name in self.board_state.eliminated_racers:
                    continue
                changes, racer_had_triggers = racer.trig_changes(self.board_state, changes)
                any_changes_found = any_changes_found or racer_had_triggers
                if racer_had_triggers:
                    changes, _ = self.track.trig_changes(self.board_state, changes)

            changes, _ = self.track.trig_changes(self.board_state, changes)

            if self.apply_changes_to_copy(self.board_state, changes).race_is_finished:
                break
            if not any_changes_found:
                break
            if self.board_state_loop_detected(changes):
                break
        return changes

    def board_state_loop_detected(self, changes: list) -> bool:
        """Check if the given changes contain a board state loop"""
        if len(changes) < 2: # Need at least two changes to form a loop
            return False
        last_board_state = self.apply_changes_to_copy(self.board_state, changes)
        iter_bs = deepcopy(self.board_state)
        for change in changes[:-1]:
            iter_bs.apply_change_list([change])
            if iter_bs == last_board_state:
                ##### NOTE: Disabled detailed loop printing for cleaner output #####
                # print("------------- !!! Detected board state loop! !!! -------------")
                # PrintBoardState(self.board_state, title="!!! Board state before applying changes:")
                # PrintBoardState(iter_bs, title=f"!!! Board state equal to last state, with index {str(changes.index(change))}:")
                # PrintBoardState(last_board_state, title="!!! Board state after applying changes:")
                # PrintChangeList(changes)
                return True
        return False

    def are_further_triggers_relevant(self, changes: list) -> bool:
        """Check if the race is finished or whether there is a loop detected"""
        last_board_state = self.apply_changes_to_copy(self.board_state, changes)
        return not (last_board_state.race_is_finished or self.board_state_loop_detected(changes))

    def trigger_before_race_powers(self) -> BoardState:
        """Trigger any before-race powers each racer may have."""
        for racer in self.player_to_racer_map.values():
            self.board_state = racer.before_race_effect(self.board_state)

    def go_to_next_turn(self):
        """Cycle turn order list to the next player."""
        self.num_turns_taken += 1
        self.turn_order.append(self.turn_order.pop(0))
        # Check if upcoming turn(s) can be skipped
        while self.is_player_out_of_the_race(self.turn_order[0]):
            self.turn_order.append(self.turn_order.pop(0))
        current_player = self.board_state.turn_order[0]
        current_racer = self.player_to_racer_map[current_player]
        # TODO Logging this here is not nice timing, should see if it can be moved to a more sensible spot
        PrintChangeList(self.current_turn_change_list, title=f"=== [Turn {self.num_turns_taken}] On {current_player.name}'s/{current_racer.name}'s turn the following happened:")
        DisplayRacerPositions(self.board_state, title=f"  Leading to these positions:")
        self.current_turn_change_list = []

    def is_player_out_of_the_race(self, player) -> bool:
        """Check if a player is no longer in the race, i.e., finished or eliminated."""
        racer_name = self.board_state.player_to_racer_name_map[player]
        finished = self.board_state.first_place_racer == racer_name or \
                   self.board_state.second_place_racer == racer_name
        eliminated = racer_name in self.board_state.eliminated_racers
        return finished or eliminated

    def apply_changes_to_copy(self, bs: BoardState, changes: list) -> BoardState:
        """Apply a list of changes to a copy of the board state and get the result."""
        temp_bs = deepcopy(bs)
        temp_bs.apply_change_list(changes)
        return temp_bs
