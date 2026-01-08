"""
Midnight Runners - Board Game
Entry point for the game
"""

from MidnightRunners.core import Game


def main():
    """Main entry point for the game."""
    # Create a game instance with 50 spaces
    game = Game(num_spaces=50)
    
    # Add players
    player1 = game.add_player("Alice")
    player2 = game.add_player("Bob")
    
    # Create pieces for each player
    piece1 = game.create_piece(player1.player_id, "runner")
    piece2 = game.create_piece(player2.player_id, "runner")
    
    # Place pieces on the track
    start_space = game.track.get_space(0)
    if start_space:
        start_space.add_piece(piece1.piece_id)
        piece1.move_to(0)
    
    # Start the game
    game.start_game()
    
    # Display game info
    print("=== Midnight Runners ===")
    print(f"Game: {game}")
    print(f"Track: {game.track}")
    print(f"Game State: {game.state}")
    print()
    
    # Display players
    print("Players:")
    for player in game.state.players:
        print(f"  - {player}")
        for piece in player.pieces:
            print(f"    - {piece}")
    
    print()
    print(f"Current Player: {game.state.get_current_player().name}")
    print(f"Game Phase: {game.state.phase.value}")


if __name__ == "__main__":
    main()
