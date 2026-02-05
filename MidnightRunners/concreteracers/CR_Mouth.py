from copy import deepcopy
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState, Player
from MidnightRunners.core.StateChange import ChangeSet


class Mouth(AbstractRacer):
    def __init__(self, player_name: Player, ask_for_input: bool = False):
        super().__init__(player_name, RacerName.MOUTH, ask_for_move_input=ask_for_input)

    def get_my_move_from_change(self, change):
        for pos_change in change.position_changes:
            if pos_change.racer_name == self.name:
                return pos_change  # Since only one position change per racer per change set
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
                before_bs.apply_change_list([change])
                continue
            change.racers_processed.add(self.name)
            new_changes.append(deepcopy(change))

            # Get board state after this change
            after_bs = deepcopy(before_bs)
            after_bs.apply_change_list([change])

            # Check if I moved this change
            my_move = self.get_my_move_from_change(change)
            if my_move is not None:
                my_new_pos = my_move.new_position

                # Count other racers on my new position
                racers_on_my_space = []
                for racer_name, position in after_bs.racer_name_to_position_map.items():
                    if racer_name != self.name and position == my_new_pos:
                        racers_on_my_space.append(racer_name)

                # If exactly one other racer is on this space, eliminate them
                if len(racers_on_my_space) == 1:
                    power_activated = True
                    change.racers_processed.add(self.name)
                    elimination_change = ChangeSet()
                    victim = racers_on_my_space[0]
                    elimination_change.add_eliminate_change(victim)
                    elimination_change.racers_processed.add(self.name)
                    elimination_change.add_message(f"{self.name.value} lands on space {my_new_pos} with {victim.value} and eliminates them!")
                    changes_from_power.append(elimination_change)
                    # before_bs.apply_change_list([elimination_change])

            # Apply the change to the temp board state for next iteration
            before_bs.apply_change_list([change])

        new_changes = new_changes + changes_from_power
        return new_changes, power_activated