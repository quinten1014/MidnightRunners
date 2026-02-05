from copy import deepcopy
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState
from MidnightRunners.core.Player import Player
from MidnightRunners.core.StateChange import MoveType

class Gunk(AbstractRacer):
    def __init__(self, player_name: Player, ask_for_input: bool = False):
        super().__init__(player_name, RacerName.GUNK, ask_for_move_input=ask_for_input)


    def get_power_changes(self, bs, changes):
        before_bs = deepcopy(bs)
        power_triggered = False

        # Go through all the changes
        for i in range(len(changes)):
            change = changes[i]
            if self.name in change.racers_processed or change.racer_flags.get("move_decreased", False):
                before_bs.apply_change_list([change])
                continue
            change.racers_processed.add(self.name)

            # For each main move from racer other than Gunk, decrease movement by 1
            # TODO: Fix the case where Banana looks at a position change first, thinking that it was passed and tripping a racer
            # then Gunk looks at the same position change and decreases movement, meaning Banana was not actually passed.
            # IDEA: Since we return early if Gunk triggers, we just have to clear all other data from the change
            for pos_change in change.position_changes:
                if pos_change.racer_name != self.name and pos_change.move_type == MoveType.MAIN:
                    power_triggered = True
                    change.racers_processed = set([self.name]) # Reset other racers so they can be processed again
                    change.trip_changes = [] # Reset trip changes since they might not be valid
                    change.eliminate_changes = [] # Reset eliminate changes since they might not be valid
                    change.point_changes = [] # Reset point changes since they might not be valid
                    if len(change.change_messages) > 0:
                        change.change_messages = [change.change_messages[0]] # Clear any further messages except for the movement message since that is still valid
                    change.processed_by_track = False # Also reset track, so it picks up on the -1 movement
                    change.racer_flags["move_decreased"] = True # Gunk should not decrease main movement twice
                    new_position = bs.track.GetNewSpace(pos_change.new_position, -1)
                    pos_change.new_position = new_position
                    change.add_message(f"{pos_change.racer_name.value}'s movement is decreased by 1 from {self.name.value}.")
                    return changes[0:i+1], True # Return early since all other changes after this could be invalid now

            before_bs.apply_change_list([change])
        return changes, power_triggered