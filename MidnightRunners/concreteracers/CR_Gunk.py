from MidnightRunners.concreteracers.RacerList import RacerName
from MidnightRunners.core import AbstractRacer, BoardState


class Gunk(AbstractRacer):
    def __init__(self, ask_for_input: bool = False):
        super().__init__(RacerName.GUNK, ask_for_move_input=ask_for_input)