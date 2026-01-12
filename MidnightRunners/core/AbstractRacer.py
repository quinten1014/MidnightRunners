import random

from MidnightRunners.core.BoardState import BoardState
from MidnightRunners.core.BoardView import PrintChangeList
from MidnightRunners.core.RacerAI import RandomRacerAI
from MidnightRunners.core.StateChange import ChangeSet, MoveType, PositionChange
from MidnightRunners.core.Track import Track
from MidnightRunners.core.Turn import TurnPhase


class AbstractRacer:
    def __init__(self, name: str):
        self.name = name
        self.tripped = False
        self.ai = RandomRacerAI()

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
            main_move_change.add_message(f"{self.name} is tripped and skips their main move this turn.")
        else:
            # Else, roll D6 and move forward
            roll = random.randint(1, 6)
            current_position = board_state.racer_name_to_position_map[self.name]
            new_position = Track.GetNewSpace(current_position, roll)
            pos_change = PositionChange(self.name, current_position, new_position)
            pos_change.set_move_type(MoveType.MAIN)
            pos_change.set_intended_movement(roll)
            pos_change.add_dice_roll(self.name, roll)
            main_move_change.add_pos_change(pos_change)
            main_move_change.add_message(f"{self.name} rolls a {roll} for their main move and moves {roll} spaces.")

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
        # PrintChangeList(changes, title=f"--- Checking triggers for racer {self.name}, initially: ---")
        for change in changes:
            if len(change.turn_phase_changes) > 0: # If this is a turn phase change
                # Skip if this racer has already processed this change
                if self.name in change.racers_processed:
                    continue
                change.racers_processed.add(self.name)

                my_turn_changes = []
                if self.check_for_start_turn_moment(bs, change):
                    my_turn_changes = self.get_start_of_turn_changes(bs)
                elif self.check_for_before_main_move_moment(bs, change):
                    my_turn_changes = self.get_before_main_move_changes(bs)
                elif self.check_for_main_move_moment(bs, change):
                    my_turn_changes = self.get_main_move_changes(bs)
                elif self.check_for_end_turn_moment(bs, change):
                    my_turn_changes = self.get_end_of_turn_changes(bs)
                if len(my_turn_changes) > 0:
                    had_my_turn_triggers = True
                new_changes.extend(my_turn_changes)

        changes.extend(new_changes)
        # PrintChangeList(changes, title=f"--- Changes after checking basic phase triggers for racer {self.name} ---")

        changes, had_power_triggers = self.get_power_changes(bs, changes)
        # PrintChangeList(changes, title=f"--- Changes after checking power triggers for racer {self.name} ---")

        return changes, (had_my_turn_triggers or had_power_triggers)