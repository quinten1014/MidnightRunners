
from MidnightRunners.core import BoardState
from MidnightRunners.core.StateChange import ChangeSet

@staticmethod
def PrintChangeList(changes: list, title: str = "Change List"):
    print(title)
    for change in changes:
        for msg in change.change_messages:
            print(f"   - {msg}")

@staticmethod
def PrintBoardState(bs: BoardState, title: str = "Board State"):
    print(title)
    print(f"  Turn Order: {[player.value for player in bs.turn_order]}")
    print(f"  Racer Order: {[bs.player_to_racer_name_map[p] for p in bs.turn_order]}")
    print(f"  Current Turn Phase: {bs.current_turn_phase}")
    DisplayRacerPositions(bs)
    print(f"  Player Points: {bs.player_points_map}")
    print(f"  First Place Racer: {bs.first_place_racer}")
    print(f"  Second Place Racer: {bs.second_place_racer}")

@staticmethod
def DisplayRacerPositions(bs: BoardState, title: str = "Racer Positions"):
    print(title)
    max_name_length = max(len(racer.value) for racer in bs.racer_name_to_position_map.keys())
    for racer, position in bs.racer_name_to_position_map.items():
        stretch_whitespace = ' ' * (max_name_length - len(racer.value)) + ' '
        player = bs.get_player_by_racer(racer)
        points = bs.player_points_map[player]
        if bs.racer_trip_map[racer]:
            print(f"\t{player.value}[{points} pts] - {racer.value}:{stretch_whitespace}{position} (tripped)")
        else:
            print(f"\t{player.value}[{points} pts] - {racer.value}:{stretch_whitespace}{position}")

@staticmethod
def DisplayBoardAfterRace(bs: BoardState):
    print(f"=== Race finished in {bs.current_turn_number} turns! ===")
    for racer, position in bs.racer_name_to_position_map.items():
        print(f"   {racer.value} ({bs.get_player_by_racer(racer).value}) finished at position {position}")
    print(f"   1st place: {bs.first_place_racer}")
    print(f"   2nd place: {bs.second_place_racer}")
    for racer, points in bs.player_points_map.items():
        print(f"   {racer.value} scored {points} points")