from copy import deepcopy
import random

from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.BoardView import PrintChangeList
from MidnightRunners.core.StateChange import ChangeSet, MoveType, PositionChange, TurnPhaseChange
from MidnightRunners.core.Track import Track
from MidnightRunners.core.Turn import TurnPhase
from gui.input_dialogs import DiceRollInputDialog


class AbstractRacer:
    def __init__(self, name: str, ask_for_move_input: bool = False):
        self.name = name
        self.tripped = False
        self.ask_for_move_input = ask_for_move_input

    def before_race_effect(self, board_state) -> BoardState:
        """Trigger any before-race effects this racer may have."""
        # Note that by default, racers are already placed on the start (0) space
        return board_state

    def main_move(self, board_state) -> list:
        """Default main move is just rolling D6 and moving forward that many spaces."""
        change_list = []
        main_move_change = ChangeSet()
        if board_state.racer_trip_map[self.name]:
            # If tripped, skip this turn and reset tripped status
            main_move_change.add_trip_change(self.name, True, False)
            main_move_change.add_message(f"{self.name.value} is tripped and skips their main move this turn.")
        else:
            # Else, roll D6 and move forward
            if self.ask_for_move_input:
                # Try to use GUI dialog first
                roll = DiceRollInputDialog.get_roll_value(self.name.value, min_value=1, max_value=6)
            else:
                roll = random.randint(1, 6)
                if self.name == RacerName.BANANA:
                    roll = 6  # Banana always rolls 6 for testing purposes
                else:
                    roll = 1
            current_position = board_state.racer_name_to_position_map[self.name]
            new_position = Track.GetNewSpace(current_position, roll)
            pos_change = PositionChange(self.name, current_position, new_position)
            pos_change.set_move_type(MoveType.MAIN)
            pos_change.set_intended_movement(roll)
            pos_change.add_dice_roll(self.name, roll)
            main_move_change.add_pos_change(pos_change)
            main_move_change.add_message(f"{self.name.value} rolls a {roll} for their main move and moves {roll} spaces.")

        change_list.append(main_move_change)
        return change_list

    def get_start_of_turn_changes(self, board_state) -> list:
        """Get any changes that should occur at the start of this racer's turn (default none)."""
        return []
    def get_before_main_move_changes(self, board_state) -> list:
        """Get any changes that should occur at the start of this racer's turn (default none)."""
        return []
    def get_main_move_changes(self, board_state) -> list:
        """Get any changes that should occur at the start of this racer's turn (default none)."""
        return self.main_move(board_state)
    def get_end_of_turn_changes(self, board_state) -> list:
        """Get any changes that should occur at the start of this racer's turn (default none)."""
        return []

    def get_power_changes(self, bs: BoardState, changes: list) -> tuple[list, bool]:
        """Get any power-related changes for this racer (default none)."""
        return changes, False

    def check_for_start_turn_moment(self, bs: BoardState, change: ChangeSet) -> bool:
        """Check if this racer is starting their turn."""
        is_it_my_turn = self.name == bs.player_to_racer_name_map[bs.turn_order[0]]
        is_turn_phase_start = change.turn_phase_changes[0].new_phase == TurnPhase.PH1_START_OF_TURN
        return is_it_my_turn and is_turn_phase_start

    def check_for_before_main_move_moment(self, bs: BoardState, change: ChangeSet) -> bool:
        """Check if this racer is about to do their main move."""
        is_it_my_turn = self.name == bs.player_to_racer_name_map[bs.turn_order[0]]
        is_turn_phase_before_main_move = change.turn_phase_changes[0].new_phase == TurnPhase.PH2_BEFORE_MAIN_MOVE
        return is_it_my_turn and is_turn_phase_before_main_move

    def check_for_main_move_moment(self, bs: BoardState, change: ChangeSet) -> bool:
        """Check if this racer is doing their main move."""
        is_it_my_turn = self.name == bs.player_to_racer_name_map[bs.turn_order[0]]
        is_turn_phase_main_move = change.turn_phase_changes[0].new_phase == TurnPhase.PH3_MAIN_MOVE
        return is_it_my_turn and is_turn_phase_main_move

    def check_for_end_turn_moment(self, bs: BoardState, change: ChangeSet) -> bool:
        """Check if this racer is ending their turn."""
        is_it_my_turn = self.name == bs.player_to_racer_name_map[bs.turn_order[0]]
        is_turn_phase_end_turn = change.turn_phase_changes[0].new_phase == TurnPhase.PH4_END_OF_TURN
        return is_it_my_turn and is_turn_phase_end_turn

    def trig_changes(self, bs: BoardState, changes: list) -> tuple[list, bool]:
        """Trigger any effects based on the given change list."""
        new_changes = []
        had_my_turn_triggers = False
        bs_copy = deepcopy(bs)

        for change in changes:
            if change.turn_phase_changes: # If this is a turn phase change
                # Skip if this racer has already processed this change
                if self.name in change.racers_processed:
                    continue
                change.racers_processed.add(self.name)
                my_turn_changes = []
                if self.check_for_start_turn_moment(bs_copy, change):
                    # print(f"DEBUG: START TURN TRIGGERED FOR {self.name.value}")
                    my_turn_changes = self.get_start_of_turn_changes(bs_copy)
                elif self.check_for_before_main_move_moment(bs_copy, change):
                    # print(f"DEBUG: BEFORE MAIN MOVE TRIGGERED FOR {self.name.value}")
                    my_turn_changes = self.get_before_main_move_changes(bs_copy)
                elif self.check_for_main_move_moment(bs_copy, change):
                    # print(f"DEBUG: MAIN MOVE TRIGGERED FOR {self.name.value}")
                    my_turn_changes = self.get_main_move_changes(bs_copy)
                elif self.check_for_end_turn_moment(bs_copy, change):
                    # print(f"DEBUG: END TURN TRIGGERED FOR {self.name.value}")
                    my_turn_changes = self.get_end_of_turn_changes(bs_copy)
                if my_turn_changes:
                    had_my_turn_triggers = True
                new_changes.extend(my_turn_changes)

        changes.extend(new_changes)
        changes, had_power_triggers = self.get_power_changes(bs_copy, changes)

        return changes, (had_my_turn_triggers or had_power_triggers)