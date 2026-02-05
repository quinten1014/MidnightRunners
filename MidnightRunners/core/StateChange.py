from enum import Enum
from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core.Player import Player
from MidnightRunners.core.Turn import TurnPhase

class MoveType(Enum):
    POWER = "Power Move"
    MAIN = "Main Move"
    TRACK = "Track Move"

class PositionChange:
    def __init__(self, racer_name: RacerName, old_position: int, new_position: int, warped: bool = False):
        self.racer_name = racer_name
        self.old_position = old_position
        self.new_position = new_position
        self.warped = warped

        # Defaults
        self.intended_movement = new_position - old_position
        self.move_type = MoveType.POWER
        self.applicable_dice_rolls = {}

    def set_move_type(self, move_type: MoveType):
        self.move_type = move_type

    def set_intended_movement(self, num_spaces: int):
        self.intended_movement = num_spaces

    def add_dice_roll(self, racer_name: RacerName, dice_roll: int):
        if racer_name not in self.applicable_dice_rolls:
            self.applicable_dice_rolls[racer_name] = []
        self.applicable_dice_rolls[racer_name].append(dice_roll)

class TripChange:
    def __init__(self, racer_name: RacerName, tripped_before: bool, tripped_after: bool):
        self.racer_name = racer_name
        self.tripped_before = tripped_before
        self.tripped_after = tripped_after

class EliminateChange:
    def __init__(self, racer_name: RacerName):
        self.racer_name = racer_name

class PointChange:
    def __init__(self, player: Player, points_delta: int):
        self.player = player
        self.points_delta = points_delta

class TurnPhaseChange:
    def __init__(self, old_phase: TurnPhase, new_phase: TurnPhase):
        self.old_phase = old_phase
        self.new_phase = new_phase

class TurnSequenceChange:
    def __init__(self, new_turn_order: list):
        self.new_turn_order = new_turn_order

class ChangeSet:
    def __init__(self):
        self.position_changes = [] # All pos changes in a set are moves that happen simultaneously
        self.trip_changes = []
        self.point_changes = []
        self.turn_phase_changes = []
        self.turn_sequence_changes = []
        self.eliminate_changes = []
        self.finished_racers = []
        self.change_messages = []
        self.processed_by_track = False
        self.racers_processed = set()
        # Flags that can be set specifically by racers, if the racers_processed set is not enough information or
        # if racers_processed reset should not affect some logic
        self.racer_flags = {}

    def add_message(self, message: str):
        self.change_messages.append(message)

    def add_pos_change(self, racer_name: RacerName, old_position: int, new_position: int, warped: bool = False):
        pos_change = PositionChange(racer_name, old_position, new_position, warped)
        self.position_changes.append(pos_change)

    def add_pos_change_obj(self, pos_change: PositionChange):
        self.position_changes.append(pos_change)

    def add_trip_change(self, racer_name: RacerName, tripped_before: bool, tripped_after: bool):
        trip_change = TripChange(racer_name, tripped_before, tripped_after)
        self.trip_changes.append(trip_change)

    def add_point_change(self, player: Player, points_delta: int):
        point_change = PointChange(player, points_delta)
        self.point_changes.append(point_change)

    def add_turn_phase_change(self, old_phase: TurnPhase, new_phase: TurnPhase):
        turn_phase_change = TurnPhaseChange(old_phase, new_phase)
        self.turn_phase_changes.append(turn_phase_change)

    def add_turn_sequence_change(self, new_turn_order: list):
        turn_sequence_change = TurnSequenceChange(new_turn_order)
        self.turn_sequence_changes.append(turn_sequence_change)

    def add_finished_racer(self, racer_name: RacerName):
        self.finished_racers.append(racer_name)

    def add_eliminate_change(self, racer_name: RacerName):
        eliminate_change = EliminateChange(racer_name)
        self.eliminate_changes.append(eliminate_change)