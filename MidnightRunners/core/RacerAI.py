from abc import ABC, abstractmethod
import random

from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import BoardState
from MidnightRunners.core.Player import Player

class IRacerAI:
    def __init__(self, player_name: Player, racer_name: RacerName):
        self.player_name = player_name
        self.racer_name = racer_name

    @abstractmethod
    def decide_reroll(self, bs: BoardState, reroll_count: int, rolled_value: int) -> bool:
        """Decide whether to reroll based on the current board state."""
        return False

    @abstractmethod
    def choose_path(self, bs: BoardState, bs_options: list) -> int:
        """Choose a path from available paths based on the current board state."""
        return bs_options[0]

class RandomRacerAI(IRacerAI):
    def __init__(self):
        super().__init__()

    def decide_reroll(self, bs: BoardState, reroll_count: int, rolled_value: int) -> bool:
        """Randomly decides to reroll or not."""
        if random.choice([True, False]):
            return True
        return False

    def choose_path(self, bs: BoardState, bs_options: list) -> int:
        """Randomly chooses one of the available board state options."""
        return bs_options[0]

class NaiveRacerAI(IRacerAI):
    def __init__(self):
        super().__init__()

    def decide_reroll(self, bs: BoardState, reroll_count: int, rolled_value: int) -> bool:
        """Rerolls when the rolled value is less than 4."""
        if rolled_value < 4:
            return True
        return False

    def choose_path(self, bs: BoardState, bs_options: list) -> int:
        """Chooses the option with the highest points first, then the furthest position ahead."""
        selected_index = 0
        best_index = 0
        highest_points_found = bs_options[0].player_points_map[self.player_name]
        furthest_position_found = bs_options[0].racer_name_to_position_map[self.racer_name]

        while selected_index < len(bs_options):
            option = bs_options[selected_index]
            my_points = option.player_points_map[self.player_name]
            my_position = option.racer_name_to_position_map[self.racer_name]
            if my_points > highest_points_found or (my_points == highest_points_found and my_position > furthest_position_found):
                highest_points_found = my_points
                furthest_position_found = my_position
                best_index = selected_index
            selected_index += 1
        return best_index