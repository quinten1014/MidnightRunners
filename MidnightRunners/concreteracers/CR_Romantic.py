from copy import deepcopy
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import ChangeSet, MoveType, PositionChange


class Romantic(AbstractRacer):
    def __init__(self, player_name: Player, ask_for_input: bool = False):
        super().__init__(player_name, RacerName.ROMANTIC, ask_for_move_input=ask_for_input)


    def get_power_changes(self, bs, changes):
        new_changes = []
        before_bs = deepcopy(bs)
        power_triggered = False

        # Go through all the changes
        for i in range(len(changes)):
            change = changes[i]
            if self.name in change.racers_processed:
                new_changes.append(deepcopy(change))
                before_bs.apply_change_list([change])
                continue
            change.racers_processed.add(self.name)
            new_changes.append(deepcopy(change))

            # Get board state before and after
            after_bs = deepcopy(before_bs)
            after_bs.apply_change_list([change])

            # Check if there are spaces with exactly 2 racers
            position_to_racers_before = {}
            position_to_racers_after = {}

            # Map positions to lists of racers for the before state
            for racer_name, position in before_bs.racer_name_to_position_map.items():
                if position not in position_to_racers_before:
                    position_to_racers_before[position] = []
                position_to_racers_before[position].append(racer_name)

            # Map positions to lists of racers for the after state
            for racer_name, position in after_bs.racer_name_to_position_map.items():
                if position not in position_to_racers_after:
                    position_to_racers_after[position] = []
                position_to_racers_after[position].append(racer_name)

            # Find spaces that have exactly 2 racers in the after state, where at least one of those moved there
            spaces_with_two_racers = []
            for position, racers in position_to_racers_after.items():
                if len(racers) == 2:
                    if before_bs.racer_name_to_position_map[racers[0]] != position \
                    or before_bs.racer_name_to_position_map[racers[1]] != position:
                        spaces_with_two_racers.append((position, racers))

            # For each pair of racers created with change, I move 2 spaces forward
            for space, racers in spaces_with_two_racers:
                power_triggered = True
                my_power_move = ChangeSet()
                my_old_pos = after_bs.racer_name_to_position_map[self.name]
                my_new_pos = my_old_pos + 2
                my_power_move.add_pos_change(self.name, my_old_pos, my_new_pos)
                my_power_move.add_message(f"{racers[0].name} and {racers[1].name} arrived together on space {space}, {self.name.value} moves 2!")
                new_changes.append(my_power_move)
                before_bs.apply_change_list([my_power_move])


            before_bs.apply_change_list([change])
        return new_changes, power_triggered