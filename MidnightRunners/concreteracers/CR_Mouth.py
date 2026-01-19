from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState, Player


class Mouth(AbstractRacer):
    def __init__(self, player_name: Player, ask_for_input: bool = False):
        super().__init__(player_name, RacerName.MOUTH, ask_for_move_input=ask_for_input)