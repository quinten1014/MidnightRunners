"""
Midnight Runners - Board Game
Entry point for the game
"""

from MidnightRunners.concreteracers.CR_Banana import Banana
from MidnightRunners.concreteracers.CR_Gunk import Gunk
from MidnightRunners.concreteracers.CR_Mouth import Mouth
from MidnightRunners.concreteracers.CR_Romantic import Romantic
from MidnightRunners.core import Race
from MidnightRunners.core.Track import TrackVersion
from MidnightRunners.concreteracers import *
from MidnightRunners.core.Player import Player


def main():
    """Main entry point for the game."""
    race = Race(track_version=TrackVersion.MILD,
                player_to_racer_map={
                    Player.P1: Banana(),
                    Player.P2: Romantic(),
                    Player.P3: Gunk(),
                    Player.P4: Mouth()
                })

    # Display game info
    print("=== Midnight Runners ===")
    print(f"Race: {race.num_players} players on {race.track.track_version.value} track")
    print()

    # Display players
    print("Players:")
    for player, racer in race.board_state.player_to_racer_name_map.items():
        print(f" Player name: {player}")
        print(f"  Position {racer}: {race.board_state.racer_name_to_position_map[racer]}")

    race.do_race()

if __name__ == "__main__":
    main()
