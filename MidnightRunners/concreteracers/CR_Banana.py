from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState


class Banana(AbstractRacer):
    def __init__(self, ask_for_input: bool = False):
        super().__init__(RacerName.BANANA, ask_for_move_input=ask_for_input)
