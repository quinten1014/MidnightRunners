
from MidnightRunners.core import BoardState
from MidnightRunners.core.StateChange import ChangeSet

@staticmethod
def PrintChangeList(changes: list, title: str = "Change List"):
    print(title)
    for change in changes:
        for msg in change.change_messages:
            print(f"   {msg}")

@staticmethod
def PrintBoardState(bs: BoardState, title: str = "Board State"):
    print(title)
    print(f"  Turn Order: {[player.value for player in bs.turn_order]}")
    print(f"  Racer Order: {[bs.player_to_racer_name_map[p] for p in bs.turn_order]}")
    print(f"  Current Turn Phase: {bs.current_turn_phase}")
    # print(f"  Racer Positions: {bs.racer_name_to_position_map}")
    DisplayRacerPositions(bs)
    # print(f"  Racer Trips: {bs.racer_trip_map}")
    print(f"  Player Points: {bs.player_points_map}")
    print(f"  First Place Racer: {bs.first_place_racer}")
    print(f"  Second Place Racer: {bs.second_place_racer}")

@staticmethod
def DisplayRacerPositions(bs: BoardState, title: str = "Racer Positions"):
    print(title)
    for racer, position in bs.racer_name_to_position_map.items():
        if bs.racer_trip_map[racer]:
            print(f"   {racer}: {position} (tripped)")
        else:
            print(f"   {racer}: {position}")

@staticmethod
def DisplayBoardAfterRace(bs: BoardState):
    print(f"=== Race finished in {bs.current_turn_number} turns! ===")
    for racer, position in bs.racer_name_to_position_map.items():
        print(f"   {racer} finished at position {position}")
    print(f"   1st place: {bs.first_place_racer}")
    print(f"   2nd place: {bs.second_place_racer}")
    for racer, points in bs.player_points_map.items():
        print(f"   {racer} scored {points} points")