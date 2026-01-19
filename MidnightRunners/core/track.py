from enum import Enum
from re import match

from MidnightRunners.core import BoardState
from MidnightRunners.core.BoardView import PrintChangeList
from MidnightRunners.core.StateChange import ChangeSet, MoveType, PositionChange, TripChange

class TrackVersion(Enum):
    MILD = "Mild Miles"
    WILD = "Wild Wilds"

# Represent start space (0) up to and including finish space (30)
# Note that -1 represents being off the board
FIXED_TRACK_LENGTH = 31

# Define special properties that spaces on the track can have
class SpecialSpaceProperties(Enum):
    START = "Start"
    FINISH = "Finish"
    ARROW_PLUS_1 = "Arrow +1"
    ARROW_PLUS_2 = "Arrow +2"
    ARROW_PLUS_3 = "Arrow +3"
    ARROW_MINUS_1 = "Arrow -1"
    ARROW_MINUS_2 = "Arrow -2"
    ARROW_MINUS_4 = "Arrow -4"
    STAR1 = "Star 1"
    TRIP = "Trip"

class Track:
    def __init__(self, track_version: TrackVersion):
        self.track_version = track_version
        self.space_properties = [[] for _ in range(FIXED_TRACK_LENGTH)]
        self.space_properties[0].append(SpecialSpaceProperties.START)
        self.space_properties[30].append(SpecialSpaceProperties.FINISH)

        if track_version == TrackVersion.WILD:
            self.space_properties[1].append(SpecialSpaceProperties.STAR1)
            self.space_properties[5].append(SpecialSpaceProperties.TRIP)
            self.space_properties[7].append(SpecialSpaceProperties.ARROW_PLUS_3)
            self.space_properties[11].append(SpecialSpaceProperties.ARROW_PLUS_1)
            self.space_properties[13].append(SpecialSpaceProperties.STAR1)
            self.space_properties[16].append(SpecialSpaceProperties.ARROW_MINUS_4)
            self.space_properties[17].append(SpecialSpaceProperties.TRIP)
            self.space_properties[23].append(SpecialSpaceProperties.ARROW_PLUS_2)
            self.space_properties[24].append(SpecialSpaceProperties.ARROW_MINUS_2)
            self.space_properties[26].append(SpecialSpaceProperties.TRIP)

    @staticmethod
    def GetNewSpace(old_space_index, delta):
        """Get the new space index after applying delta to old index, ensuring within track bounds."""
        new_index = old_space_index + delta
        new_index = max(0, min(new_index, FIXED_TRACK_LENGTH - 1))
        return new_index

    def trig_changes(self, bs: BoardState, changes: list) -> tuple[list, bool]:
        """Apply a change to the track state."""
        changes_after_processing = changes.copy()
        special_space_triggered = False
        new_changes_to_add = []

        for change in changes:
            if change.processed_by_track:
                continue
            change.processed_by_track = True

            for pos_change in change.position_changes:
                racer_name, _, landed_pos = pos_change.racer_name, pos_change.old_position, pos_change.new_position
                player_name = bs.get_player_by_racer(racer_name)
                landing_space_properties = self.space_properties[landed_pos]

                for property in landing_space_properties:
                    # Getting here means there is at least one property to process
                    special_space_triggered = True
                    new_change = ChangeSet()
                    new_change.add_message(f"{racer_name.value} landed on special space {landed_pos} with property {property.name}.")
                    if property == SpecialSpaceProperties.TRIP and not bs.racer_trip_map[pos_change.racer_name]:
                        # Avoid double-tripping
                        new_change.add_trip_change(pos_change.racer_name, False, True)
                        new_change.add_message(f"{racer_name.value} is tripped.")
                    elif property == SpecialSpaceProperties.STAR1:
                        new_change.add_point_change(player_name, 1)
                        new_change.add_message(f"{player_name.value} gains 1 point.")
                    elif property == SpecialSpaceProperties.FINISH:
                        new_change.add_finished_racer(racer_name)
                        new_change.add_message(f"{racer_name.value} finished!")
                    else:
                        pos_after_move = landed_pos
                        match(property):
                            case SpecialSpaceProperties.ARROW_PLUS_1: pos_after_move = self.GetNewSpace(landed_pos, 1)
                            case SpecialSpaceProperties.ARROW_PLUS_2: pos_after_move = self.GetNewSpace(landed_pos, 2)
                            case SpecialSpaceProperties.ARROW_PLUS_3: pos_after_move = self.GetNewSpace(landed_pos, 3)
                            case SpecialSpaceProperties.ARROW_MINUS_1: pos_after_move = self.GetNewSpace(landed_pos, -1)
                            case SpecialSpaceProperties.ARROW_MINUS_2: pos_after_move = self.GetNewSpace(landed_pos, -2)
                            case SpecialSpaceProperties.ARROW_MINUS_4: pos_after_move = self.GetNewSpace(landed_pos, -4)
                        pos_change = PositionChange(racer_name, landed_pos, pos_after_move)
                        pos_change.set_move_type(MoveType.TRACK)
                        new_change.add_pos_change_obj(pos_change)

                        new_change.add_message(f"{racer_name.value} moves to space {pos_after_move}.")
                    new_changes_to_add.append(new_change)

        changes_after_processing.extend(new_changes_to_add)
        # PrintChangeList(changes_after_processing, title="--- Track added changes resulting in: ---") if special_space_triggered else None
        return changes_after_processing, special_space_triggered