from copy import deepcopy
from typing import override
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState, Player


class Banana(AbstractRacer):
    def __init__(self, player_name: Player, ask_for_input: bool = False):
        super().__init__(player_name, RacerName.BANANA, ask_for_move_input=ask_for_input)

    def get_my_move_from_change(self, change):
        for pos_change in change.position_changes:
            if pos_change.racer_name == self.name:
                return pos_change # Since only one position change per racer per change set
        return None

    def get_power_changes(self, bs, changes):
        power_activated = False
        temp_bs = deepcopy(bs)
        new_changes = []

        # Go through all the changes
        for i in range(len(changes)):
            change = changes[i]
            if self.name in change.racers_processed:
                new_changes.append(deepcopy(change))
                continue
            change.racers_processed.add(self.name)
            new_changes.append(deepcopy(change))

            # Determine my current and new positions
            my_current_pos = temp_bs.racer_name_to_position_map[self.name]
            my_move = self.get_my_move_from_change(change)
            my_new_pos = my_current_pos
            if not my_move is None:
                my_new_pos = my_move.new_position

            # Check for other racers that pass me
            for pos_change in change.position_changes:
                if pos_change.racer_name != self.name:
                    old_pos = pos_change.old_position
                    new_pos = pos_change.new_position
                    if (old_pos < my_current_pos < new_pos) and (old_pos < my_new_pos < new_pos):
                        new_changes[-1].add_trip_change(pos_change.racer_name, False, True)
                        new_changes[-1].add_message(f"{pos_change.racer_name.value} passes {self.name.value} and trips!")
                        new_changes[-1].racers_processed = set([self.name])
                        power_activated = True

            # Apply the change to the temp board state for next iteration
            temp_bs.apply_change_list([new_changes[-1]])

        return new_changes, power_activated
