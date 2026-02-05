from copy import deepcopy
from typing import override
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState, Player
from MidnightRunners.core.StateChange import ChangeSet


class Suckerfish(AbstractRacer):
    def __init__(self, player_name: Player, ask_for_input: bool = False):
        super().__init__(player_name, RacerName.SUCKERFISH, ask_for_move_input=ask_for_input)

    def get_my_move_from_change(self, change):
        for pos_change in change.position_changes:
            if pos_change.racer_name == self.name:
                return pos_change # Since only one position change per racer per change set
        return None

    def get_power_changes(self, bs, changes):
        power_activated = False
        before_bs = deepcopy(bs)
        new_changes = []
        changes_from_power = []

        # Go through all the changes
        for i in range(len(changes)):
            change = changes[i]
            if self.name in change.racers_processed:
                new_changes.append(deepcopy(change))
                continue
            change.racers_processed.add(self.name)
            new_changes.append(deepcopy(change))

            # Determine my current position
            my_current_pos = before_bs.racer_name_to_position_map[self.name]
            after_bs = deepcopy(before_bs)
            after_bs.apply_change_list([change])

            # Find other racers that moved from my initial position
            racers_moved_from_my_pos = []
            for pos_change in change.position_changes:
                if pos_change.racer_name != self.name and pos_change.old_position == my_current_pos and pos_change.new_position != my_current_pos:
                    racers_moved_from_my_pos.append((pos_change.racer_name, pos_change.new_position))

            # Apply the change to the temp board state for next iteration
            before_bs.apply_change_list([new_changes[-1]])

            if len(racers_moved_from_my_pos) == 0:
                # No racers moved from my position, nothing to do
                continue

            # Create board state options
            bs_options = []
            # Option 1: Do not activate power
            bs_options.append(after_bs)
            # Option 2..N: Activate power, one option for each racer that moved from my position
            for _, new_pos in racers_moved_from_my_pos:
                bs_option = deepcopy(after_bs)
                bs_option.racer_name_to_position_map[self.name] = new_pos
                bs_options.append(bs_option)
            # Let AI choose
            chosen_index = self.ai.choose_path(after_bs, bs_options)

            if chosen_index != 0:
                power_activated = True
                my_power_move = ChangeSet()

                # Move myself to the new position
                chosen_racer_name, chosen_new_pos = racers_moved_from_my_pos[chosen_index - 1]
                my_power_move.add_message(f"{self.name.value} moves along with {chosen_racer_name.value} to space {chosen_new_pos}!")
                my_power_move.add_pos_change(self.name, after_bs.racer_name_to_position_map[self.name], chosen_new_pos)
                changes_from_power.append(my_power_move)
                before_bs.apply_change_list([changes_from_power[-1]])

        new_changes = new_changes + changes_from_power
        return new_changes, power_activated
